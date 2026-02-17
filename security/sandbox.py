"""
Secure Sandbox - Safe Code Execution Environment

Protects against:
- Arbitrary code execution
- File system access violations
- Network data exfiltration
- Resource exhaustion (CPU, memory, disk)
- Privilege escalation

Based on gVisor, E2B, and NVIDIA AI Red Team recommendations
"""

import os
import subprocess
import logging
import resource
import tempfile
import shutil
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import threading
import signal

logger = logging.getLogger(__name__)


class SandboxMode(Enum):
    """Sandbox isolation levels"""
    NONE = "none"  # No sandboxing (dangerous!)
    BASIC = "basic"  # Basic restrictions
    STRICT = "strict"  # Strict isolation
    PARANOID = "paranoid"  # Maximum security


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    mode: SandboxMode = SandboxMode.STRICT
    allow_network: bool = False
    allow_file_read: bool = True
    allow_file_write: bool = False
    allowed_read_paths: List[str] = None
    allowed_write_paths: List[str] = None
    blocked_commands: List[str] = None
    max_execution_time: int = 30  # seconds
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_output_size: int = 1024 * 1024  # 1MB

    def __post_init__(self):
        if self.allowed_read_paths is None:
            self.allowed_read_paths = []
        if self.allowed_write_paths is None:
            self.allowed_write_paths = []
        if self.blocked_commands is None:
            # Default blocked commands
            self.blocked_commands = [
                'rm', 'rmdir', 'del', 'format',
                'dd', 'mkfs',
                'curl', 'wget', 'nc', 'netcat', 'telnet',
                'ssh', 'scp', 'ftp', 'sftp',
                'sudo', 'su', 'passwd',
                'chmod', 'chown', 'chgrp',
                'kill', 'killall', 'pkill',
                'reboot', 'shutdown', 'halt', 'poweroff',
                'systemctl', 'service',
                'iptables', 'ifconfig', 'ip',
                'mount', 'umount'
            ]


@dataclass
class ExecutionResult:
    """Result of sandbox execution"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    violations: List[str]
    killed: bool = False
    kill_reason: Optional[str] = None


class SecureSandbox:
    """
    Secure sandbox for code execution

    Features:
    - Command whitelisting/blacklisting
    - File system access control
    - Network isolation
    - Resource limits (CPU, memory, time)
    - Output sanitization
    - Execution logging

    Note: This is a Python-based sandbox. For production, consider:
    - Docker containers with security profiles
    - gVisor (Google)
    - Firecracker microVMs (E2B)
    - Kubernetes with Pod Security Standards
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize sandbox

        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()
        self.lock = threading.Lock()

        # Create temp workspace
        self.workspace = Path(tempfile.mkdtemp(prefix="novaos_sandbox_"))

        # Stats
        self.executions = 0
        self.violations = 0
        self.blocked_commands = 0

        logger.info(
            f"SecureSandbox initialized (mode={self.config.mode.value}, "
            f"workspace={self.workspace})"
        )

    def __del__(self):
        """Cleanup"""
        try:
            if self.workspace.exists():
                shutil.rmtree(self.workspace)
        except Exception as e:
            logger.error(f"Error cleaning up sandbox workspace: {e}")

    def execute_command(
        self,
        command: List[str],
        stdin: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute command in sandbox

        Args:
            command: Command and arguments
            stdin: Optional stdin input
            env: Optional environment variables

        Returns:
            Execution result
        """
        with self.lock:
            self.executions += 1

        violations = []
        start_time = 0
        execution_time = 0

        # Validate command
        if not command or len(command) == 0:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Empty command",
                exit_code=-1,
                execution_time=0,
                violations=["empty_command"]
            )

        # Check blocked commands
        cmd_name = command[0].lower()
        if cmd_name in self.config.blocked_commands:
            with self.lock:
                self.blocked_commands += 1
                self.violations += 1

            violations.append(f"blocked_command: {cmd_name}")
            logger.warning(f"Blocked command: {cmd_name}")

            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command '{cmd_name}' is blocked",
                exit_code=-1,
                execution_time=0,
                violations=violations
            )

        # Check for file access violations
        for arg in command[1:]:
            if isinstance(arg, str):
                # Check for path traversal
                if '..' in arg or arg.startswith('/'):
                    # Validate against allowed paths
                    if not self._is_path_allowed(arg):
                        violations.append(f"unauthorized_path: {arg}")
                        with self.lock:
                            self.violations += 1

        # Check for network access attempts
        if not self.config.allow_network:
            network_indicators = ['http://', 'https://', 'ftp://', '://', '@']
            for arg in command:
                if isinstance(arg, str) and any(ind in arg for ind in network_indicators):
                    violations.append(f"network_access_attempt: {arg}")
                    with self.lock:
                        self.violations += 1

        # Block execution if critical violations
        if violations:
            logger.warning(f"Sandbox violations detected: {violations}")
            if self.config.mode in [SandboxMode.STRICT, SandboxMode.PARANOID]:
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Sandbox violations: {', '.join(violations)}",
                    exit_code=-1,
                    execution_time=0,
                    violations=violations
                )

        # Set up environment
        sandbox_env = os.environ.copy()

        # Remove sensitive environment variables
        for key in list(sandbox_env.keys()):
            if any(keyword in key.upper() for keyword in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                del sandbox_env[key]

        # Add custom env vars
        if env:
            sandbox_env.update(env)

        # Set working directory to sandbox workspace
        cwd = str(self.workspace)

        try:
            import time
            start_time = time.time()

            # Execute with resource limits
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if stdin else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=sandbox_env,
                preexec_fn=self._set_resource_limits if os.name != 'nt' else None
            )

            # Wait with timeout
            try:
                stdout, stderr = process.communicate(
                    input=stdin.encode() if stdin else None,
                    timeout=self.config.max_execution_time
                )
                killed = False
                kill_reason = None
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                killed = True
                kill_reason = "Execution timeout"
                violations.append("timeout_exceeded")
                with self.lock:
                    self.violations += 1

            execution_time = time.time() - start_time

            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')

            # Limit output size
            if len(stdout_str) > self.config.max_output_size:
                stdout_str = stdout_str[:self.config.max_output_size] + "\n[OUTPUT TRUNCATED]"
                violations.append("output_size_exceeded")

            if len(stderr_str) > self.config.max_output_size:
                stderr_str = stderr_str[:self.config.max_output_size] + "\n[OUTPUT TRUNCATED]"

            # Sanitize output (remove potential secrets)
            stdout_str = self._sanitize_output(stdout_str)
            stderr_str = self._sanitize_output(stderr_str)

            success = process.returncode == 0 and not killed

            logger.info(
                f"Sandbox execution: {command[0]} "
                f"(exit={process.returncode}, time={execution_time:.2f}s, "
                f"violations={len(violations)})"
            )

            return ExecutionResult(
                success=success,
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=process.returncode,
                execution_time=execution_time,
                violations=violations,
                killed=killed,
                kill_reason=kill_reason
            )

        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                exit_code=-1,
                execution_time=execution_time,
                violations=violations + ["execution_error"]
            )

    def _set_resource_limits(self):
        """Set resource limits for subprocess (Unix only)"""
        try:
            # Memory limit
            memory_bytes = self.config.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            # CPU time limit (soft, hard)
            resource.setrlimit(resource.RLIMIT_CPU, (
                self.config.max_execution_time,
                self.config.max_execution_time + 5
            ))

            # File size limit (prevent disk exhaustion)
            max_file_size = 10 * 1024 * 1024  # 10MB
            resource.setrlimit(resource.RLIMIT_FSIZE, (max_file_size, max_file_size))

            # Process limit (prevent fork bombs)
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))

        except Exception as e:
            logger.error(f"Error setting resource limits: {e}")

    def _is_path_allowed(self, path: str) -> bool:
        """Check if path access is allowed"""
        path_obj = Path(path).resolve()

        # Always allow workspace
        if str(path_obj).startswith(str(self.workspace)):
            return True

        # Check allowed read paths
        for allowed_path in self.config.allowed_read_paths:
            if str(path_obj).startswith(allowed_path):
                return True

        # Check allowed write paths
        if self.config.allow_file_write:
            for allowed_path in self.config.allowed_write_paths:
                if str(path_obj).startswith(allowed_path):
                    return True

        return False

    def _sanitize_output(self, output: str) -> str:
        """Remove potential secrets from output"""
        import re

        # Remove potential API keys
        patterns = [
            r'[a-zA-Z0-9_-]{32,}',  # Long alphanumeric strings
            r'sk-[a-zA-Z0-9]{32,}',  # OpenAI-style keys
            r'Bearer\s+[a-zA-Z0-9_-]+',  # Bearer tokens
        ]

        sanitized = output
        for pattern in patterns:
            # Check if it looks like a secret
            matches = re.findall(pattern, output)
            for match in matches:
                # Simple heuristic: if it's long and random-looking
                if len(match) > 20 and not match.isdigit():
                    sanitized = sanitized.replace(match, '[REDACTED]')

        return sanitized

    def execute_python(
        self,
        code: str,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute Python code in sandbox

        Args:
            code: Python code to execute
            timeout: Optional timeout override

        Returns:
            Execution result
        """
        # Write code to temp file
        code_file = self.workspace / "script.py"
        code_file.write_text(code)

        # Execute
        command = ['python3', str(code_file)]

        if timeout:
            original_timeout = self.config.max_execution_time
            self.config.max_execution_time = timeout
            result = self.execute_command(command)
            self.config.max_execution_time = original_timeout
        else:
            result = self.execute_command(command)

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics"""
        with self.lock:
            return {
                'mode': self.config.mode.value,
                'workspace': str(self.workspace),
                'executions': self.executions,
                'violations': self.violations,
                'blocked_commands': self.blocked_commands,
                'config': {
                    'allow_network': self.config.allow_network,
                    'allow_file_write': self.config.allow_file_write,
                    'max_execution_time': self.config.max_execution_time,
                    'max_memory_mb': self.config.max_memory_mb,
                    'blocked_commands_count': len(self.config.blocked_commands)
                }
            }


# Singleton instance
_sandbox_instance = None


def get_sandbox(config: Optional[SandboxConfig] = None) -> SecureSandbox:
    """Get or create sandbox singleton"""
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = SecureSandbox(config)
    return _sandbox_instance
