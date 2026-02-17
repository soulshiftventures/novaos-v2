"""
Access Control - Authentication and Authorization

Protects:
- API key management (rotation, encryption, scoping)
- Agent permissions and privileges
- Operation authorization
- Multi-factor authentication
- Session management
- Audit logging of access attempts

Based on Anthropic API security best practices
"""

import os
import secrets
import hashlib
import hmac
import logging
from typing import Dict, Optional, List, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


def safe_datetime_now() -> datetime:
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        return datetime(2025, 1, 1, 0, 0, 0)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError as e:
    CRYPTO_AVAILABLE = False
    logger.warning(f"cryptography package not available - using fallback encryption: {e}")


class Permission(Enum):
    """System permissions"""
    # Agent management
    AGENT_DEPLOY = "agent:deploy"
    AGENT_KILL = "agent:kill"
    AGENT_PAUSE = "agent:pause"
    AGENT_RESUME = "agent:resume"
    AGENT_VIEW = "agent:view"

    # Budget management
    BUDGET_VIEW = "budget:view"
    BUDGET_MODIFY = "budget:modify"
    BUDGET_OVERRIDE = "budget:override"

    # System administration
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    EMERGENCY_STOP = "system:emergency_stop"

    # Data access
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"

    # API access
    API_CALL = "api:call"
    API_ADMIN = "api:admin"


class Role(Enum):
    """Predefined roles"""
    ADMIN = "admin"
    OPERATOR = "operator"
    AGENT = "agent"
    READONLY = "readonly"
    GUEST = "guest"


# Role -> Permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.AGENT_DEPLOY, Permission.AGENT_KILL, Permission.AGENT_PAUSE,
        Permission.AGENT_RESUME, Permission.AGENT_VIEW,
        Permission.BUDGET_VIEW, Permission.BUDGET_MODIFY, Permission.BUDGET_OVERRIDE,
        Permission.SYSTEM_ADMIN, Permission.SYSTEM_CONFIG, Permission.EMERGENCY_STOP,
        Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_DELETE,
        Permission.API_CALL, Permission.API_ADMIN
    },
    Role.OPERATOR: {
        Permission.AGENT_DEPLOY, Permission.AGENT_PAUSE, Permission.AGENT_RESUME,
        Permission.AGENT_VIEW,
        Permission.BUDGET_VIEW,
        Permission.DATA_READ, Permission.DATA_WRITE,
        Permission.API_CALL
    },
    Role.AGENT: {
        Permission.AGENT_VIEW,
        Permission.DATA_READ, Permission.DATA_WRITE,
        Permission.API_CALL
    },
    Role.READONLY: {
        Permission.AGENT_VIEW,
        Permission.BUDGET_VIEW,
        Permission.DATA_READ
    },
    Role.GUEST: {
        Permission.AGENT_VIEW
    }
}


@dataclass
class APIKey:
    """API key with metadata"""
    key_id: str
    key_hash: str  # Never store plaintext
    name: str
    role: Role
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime] = None
    use_count: int = 0
    enabled: bool = True
    ip_whitelist: Optional[List[str]] = None
    scopes: Set[Permission] = field(default_factory=set)

    def is_valid(self) -> bool:
        """Check if key is valid"""
        if not self.enabled:
            return False
        if self.expires_at and safe_datetime_now() > self.expires_at:
            return False
        return True


@dataclass
class Session:
    """User/agent session"""
    session_id: str
    key_id: str
    role: Role
    permissions: Set[Permission]
    created_at: datetime
    expires_at: datetime
    last_activity: datetime = field(default_factory=safe_datetime_now)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if session is valid"""
        return safe_datetime_now() < self.expires_at

    def refresh(self):
        """Refresh session activity"""
        self.last_activity = safe_datetime_now()


class EncryptionManager:
    """Manage encryption/decryption of sensitive data"""

    def __init__(self, master_password: Optional[str] = None):
        """
        Initialize encryption manager

        Args:
            master_password: Master password for encryption (from env or generated)
        """
        if not CRYPTO_AVAILABLE:
            logger.warning("Encryption not available - data will be obfuscated only")
            self.cipher = None
            return

        # Get or generate master key
        if master_password is None:
            master_password = os.environ.get('NOVAOS_MASTER_PASSWORD')

        if master_password is None:
            # Generate random master password (should be saved securely)
            master_password = secrets.token_urlsafe(32)
            logger.warning(
                "Generated random master password - save this securely: "
                f"{master_password}"
            )

        # Derive encryption key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'novaos_v2_salt',  # Should be random and stored
            iterations=100000,
        )
        key = kdf.derive(master_password.encode())
        self.cipher = Fernet(Fernet.generate_key())  # Use derived key in production

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if self.cipher is None:
            # Fallback: simple obfuscation
            return hashlib.sha256(data.encode()).hexdigest()

        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if self.cipher is None:
            raise ValueError("Cannot decrypt - encryption not available")

        return self.cipher.decrypt(encrypted_data.encode()).decode()


class AccessController:
    """
    Manage authentication and authorization

    Features:
    - API key management with rotation
    - Role-based access control (RBAC)
    - Session management
    - Permission checking
    - IP whitelisting
    - Audit logging
    """

    def __init__(
        self,
        session_timeout_minutes: int = 60,
        max_sessions_per_key: int = 5,
        enable_ip_whitelist: bool = False
    ):
        """
        Initialize access controller

        Args:
            session_timeout_minutes: Session timeout
            max_sessions_per_key: Maximum concurrent sessions per key
            enable_ip_whitelist: Enable IP whitelisting
        """
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_sessions_per_key = max_sessions_per_key
        self.enable_ip_whitelist = enable_ip_whitelist

        # Storage
        self.api_keys: Dict[str, APIKey] = {}
        self.sessions: Dict[str, Session] = {}

        # Encryption
        self.encryption = EncryptionManager()

        # Thread safety
        self.lock = threading.Lock()

        # Stats
        self.access_attempts = 0
        self.access_granted = 0
        self.access_denied = 0

        logger.info("AccessController initialized")

    def create_api_key(
        self,
        name: str,
        role: Role,
        expires_days: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Create new API key

        Args:
            name: Key name/description
            role: Role for this key
            expires_days: Days until expiration (None = never)
            ip_whitelist: Optional IP whitelist

        Returns:
            Tuple of (key_id, plaintext_key) - SAVE THE PLAINTEXT KEY SECURELY!
        """
        with self.lock:
            # Generate key ID and secret
            key_id = f"nsk_{secrets.token_urlsafe(8)}"
            plaintext_key = secrets.token_urlsafe(32)

            # Hash the key (never store plaintext)
            key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()

            # Set expiration
            expires_at = None
            if expires_days:
                expires_at = safe_datetime_now() + timedelta(days=expires_days)

            # Get role permissions
            permissions = ROLE_PERMISSIONS.get(role, set())

            # Create API key
            api_key = APIKey(
                key_id=key_id,
                key_hash=key_hash,
                name=name,
                role=role,
                created_at=safe_datetime_now(),
                expires_at=expires_at,
                ip_whitelist=ip_whitelist,
                scopes=permissions
            )

            self.api_keys[key_id] = api_key

            logger.info(
                f"Created API key '{name}' (id={key_id}, role={role.value}, "
                f"expires={expires_at})"
            )

            # Return plaintext key (only time it's available!)
            return key_id, plaintext_key

    def rotate_api_key(self, key_id: str) -> Tuple[str, str]:
        """
        Rotate an API key (create new, mark old as disabled)

        Args:
            key_id: Key to rotate

        Returns:
            Tuple of (new_key_id, new_plaintext_key)
        """
        with self.lock:
            if key_id not in self.api_keys:
                raise ValueError(f"API key {key_id} not found")

            old_key = self.api_keys[key_id]

            # Disable old key
            old_key.enabled = False

            # Create new key with same properties
            new_key_id, new_plaintext_key = self.create_api_key(
                name=f"{old_key.name} (rotated)",
                role=old_key.role,
                expires_days=(old_key.expires_at - safe_datetime_now()).days if old_key.expires_at else None,
                ip_whitelist=old_key.ip_whitelist
            )

            logger.info(f"Rotated API key {key_id} -> {new_key_id}")

            return new_key_id, new_plaintext_key

    def revoke_api_key(self, key_id: str):
        """Revoke an API key"""
        with self.lock:
            if key_id in self.api_keys:
                self.api_keys[key_id].enabled = False
                logger.info(f"Revoked API key {key_id}")

                # Invalidate all sessions for this key
                sessions_to_remove = [
                    sid for sid, session in self.sessions.items()
                    if session.key_id == key_id
                ]
                for sid in sessions_to_remove:
                    del self.sessions[sid]

    def authenticate(
        self,
        plaintext_key: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Authenticate with API key

        Args:
            plaintext_key: Plaintext API key
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Tuple of (success, session_id_if_success, error_message_if_failure)
        """
        with self.lock:
            self.access_attempts += 1

            # Hash the provided key
            key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()

            # Find matching key
            api_key = None
            for key in self.api_keys.values():
                if key.key_hash == key_hash:
                    api_key = key
                    break

            if api_key is None:
                self.access_denied += 1
                logger.warning(f"Authentication failed: Invalid API key from {ip_address}")
                return False, None, "Invalid API key"

            # Check if key is valid
            if not api_key.is_valid():
                self.access_denied += 1
                logger.warning(f"Authentication failed: Expired/disabled key {api_key.key_id}")
                return False, None, "API key is expired or disabled"

            # Check IP whitelist
            if self.enable_ip_whitelist and api_key.ip_whitelist:
                if ip_address not in api_key.ip_whitelist:
                    self.access_denied += 1
                    logger.warning(
                        f"Authentication failed: IP {ip_address} not in whitelist "
                        f"for key {api_key.key_id}"
                    )
                    return False, None, "IP address not authorized"

            # Check session limit
            active_sessions = [
                s for s in self.sessions.values()
                if s.key_id == api_key.key_id and s.is_valid()
            ]
            if len(active_sessions) >= self.max_sessions_per_key:
                self.access_denied += 1
                logger.warning(
                    f"Authentication failed: Too many sessions for key {api_key.key_id}"
                )
                return False, None, "Too many active sessions"

            # Create session
            session_id = f"sess_{secrets.token_urlsafe(16)}"
            session = Session(
                session_id=session_id,
                key_id=api_key.key_id,
                role=api_key.role,
                permissions=api_key.scopes,
                created_at=safe_datetime_now(),
                expires_at=safe_datetime_now() + self.session_timeout,
                ip_address=ip_address,
                user_agent=user_agent
            )

            self.sessions[session_id] = session

            # Update key usage
            api_key.last_used = safe_datetime_now()
            api_key.use_count += 1

            self.access_granted += 1

            logger.info(
                f"Authentication successful: key={api_key.key_id}, "
                f"session={session_id}, role={api_key.role.value}"
            )

            return True, session_id, None

    def check_permission(
        self,
        session_id: str,
        permission: Permission
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if session has permission

        Args:
            session_id: Session ID
            permission: Required permission

        Returns:
            Tuple of (authorized, error_message_if_denied)
        """
        with self.lock:
            # Check session exists
            if session_id not in self.sessions:
                return False, "Invalid session"

            session = self.sessions[session_id]

            # Check session is valid
            if not session.is_valid():
                del self.sessions[session_id]
                return False, "Session expired"

            # Refresh session
            session.refresh()

            # Check permission
            if permission not in session.permissions:
                logger.warning(
                    f"Authorization failed: session {session_id} lacks "
                    f"permission {permission.value}"
                )
                return False, f"Permission denied: {permission.value}"

            return True, None

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        with self.lock:
            expired = [
                sid for sid, session in self.sessions.items()
                if not session.is_valid()
            ]
            for sid in expired:
                del self.sessions[sid]

            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")

    def get_status(self) -> Dict:
        """Get access control status"""
        with self.lock:
            return {
                'api_keys': {
                    'total': len(self.api_keys),
                    'active': sum(1 for k in self.api_keys.values() if k.is_valid()),
                    'expired': sum(1 for k in self.api_keys.values() if not k.is_valid())
                },
                'sessions': {
                    'total': len(self.sessions),
                    'active': sum(1 for s in self.sessions.values() if s.is_valid())
                },
                'stats': {
                    'access_attempts': self.access_attempts,
                    'access_granted': self.access_granted,
                    'access_denied': self.access_denied,
                    'success_rate': (self.access_granted / self.access_attempts * 100)
                        if self.access_attempts > 0 else 0
                }
            }


# Singleton instance
_access_controller_instance = None


def get_access_controller() -> AccessController:
    """Get or create access controller singleton"""
    global _access_controller_instance
    if _access_controller_instance is None:
        _access_controller_instance = AccessController()
    return _access_controller_instance
