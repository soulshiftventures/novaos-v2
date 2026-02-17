"""
Input Validator - Prompt Injection Defense

Protects against:
- Direct prompt injection
- Indirect prompt injection via data sources
- Jailbreak attempts
- Command injection
- Data exfiltration attempts

Based on OWASP LLM01:2025 Prompt Injection guidance
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    threat_level: ThreatLevel
    sanitized_input: str
    threats_detected: List[str]
    confidence: float  # 0.0 - 1.0


class InputValidator:
    """
    Multi-layer input validation and sanitization

    Defense strategies:
    1. Pattern detection (known attack signatures)
    2. Character filtering (dangerous characters)
    3. Length validation (unusually long inputs)
    4. Semantic analysis (instruction-like patterns)
    5. Whitelist enforcement (allowed formats)
    """

    # Known malicious patterns (regex)
    MALICIOUS_PATTERNS = [
        # Direct injection attempts
        r'ignore\s+(previous|prior|all|above)\s+instructions?',
        r'disregard\s+(previous|prior|all|above)',
        r'forget\s+(previous|prior|all|above)',
        r'new\s+instructions?:\s*',
        r'system\s*:\s*you\s+are',
        r'from\s+now\s+on',
        r'you\s+must\s+(now|always)',

        # Jailbreak attempts
        r'pretend\s+(you|to)\s+(are|be)',
        r'act\s+as\s+(if|though)',
        r'roleplay\s+as',
        r'DAN\s+mode',
        r'developer\s+mode',
        r'jailbreak',

        # Command injection
        r';\s*(rm|del|format|curl|wget)',
        r'\|\s*(rm|del|format|curl|wget)',
        r'&&\s*(rm|del|format|curl|wget)',
        r'`[^`]*`',  # Backtick command execution
        r'\$\([^\)]*\)',  # Command substitution

        # Data exfiltration attempts
        r'send\s+.+\s+to\s+https?://',
        r'post\s+.+\s+to\s+https?://',
        r'exfiltrate',
        r'extract\s+.+\s+(and\s+)?send',
        r'curl\s+.+\s+https?://',
        r'wget\s+.+\s+https?://',

        # API key extraction
        r'api[_\s-]?key',
        r'secret[_\s-]?key',
        r'access[_\s-]?token',
        r'auth[_\s-]?token',
        r'password',
        r'credentials',

        # File system access
        r'\.\./',  # Path traversal
        r'\/etc\/',
        r'\/root\/',
        r'\.ssh',
        r'\.env',

        # Prompt leaking
        r'show\s+(me\s+)?(your|the)\s+(system\s+)?prompt',
        r'what\s+(is|are)\s+your\s+(system\s+)?instructions',
        r'repeat\s+(your|the)\s+(system\s+)?prompt',
        r'print\s+(your|the)\s+(system\s+)?prompt',
    ]

    # Dangerous characters and sequences
    DANGEROUS_CHARS = [
        '<script', '</script',  # XSS
        'javascript:',
        'onerror=',
        'onload=',
        '${', '}',  # Template injection
        '{{', '}}',  # Template injection
        '<!--', '-->',  # HTML comments
    ]

    # Character substitution attacks (e.g., EchoLeak CVE-2025-32711)
    SUBSTITUTION_PATTERNS = [
        r'[\u0000-\u001F\u007F-\u009F]',  # Control characters
        r'[\u200B-\u200D\uFEFF]',  # Zero-width characters
        r'[\u2060-\u2069]',  # Word joiner, invisible separators
    ]

    def __init__(
        self,
        max_input_length: int = 10000,
        enable_semantic_analysis: bool = True,
        strict_mode: bool = False
    ):
        """
        Initialize input validator

        Args:
            max_input_length: Maximum allowed input length
            enable_semantic_analysis: Enable advanced semantic checks
            strict_mode: Block suspicious inputs (not just dangerous)
        """
        self.max_input_length = max_input_length
        self.enable_semantic_analysis = enable_semantic_analysis
        self.strict_mode = strict_mode

        # Compile patterns for efficiency
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), pattern)
            for pattern in self.MALICIOUS_PATTERNS
        ]

        self.substitution_regex = re.compile(
            '|'.join(self.SUBSTITUTION_PATTERNS),
            re.IGNORECASE
        )

        logger.info(f"InputValidator initialized (strict_mode={strict_mode})")

    def validate(self, input_text: str, context: str = "user_input") -> ValidationResult:
        """
        Validate and sanitize input

        Args:
            input_text: Text to validate
            context: Context of input (user_input, config, filename, etc.)

        Returns:
            ValidationResult with validation status and sanitized text
        """
        if not input_text:
            return ValidationResult(
                is_valid=True,
                threat_level=ThreatLevel.SAFE,
                sanitized_input="",
                threats_detected=[],
                confidence=1.0
            )

        threats_detected = []
        threat_level = ThreatLevel.SAFE
        confidence = 1.0

        # 1. Length validation
        if len(input_text) > self.max_input_length:
            threats_detected.append(f"Input too long ({len(input_text)} > {self.max_input_length})")
            threat_level = ThreatLevel.SUSPICIOUS
            input_text = input_text[:self.max_input_length]
            confidence = 0.9

        # 2. Check for character substitution attacks
        if self.substitution_regex.search(input_text):
            threats_detected.append("Character substitution attack detected")
            threat_level = ThreatLevel.DANGEROUS
            # Remove suspicious characters
            input_text = self.substitution_regex.sub('', input_text)
            confidence = 0.8

        # 3. Pattern matching for known attacks
        for compiled_pattern, pattern_str in self.compiled_patterns:
            matches = compiled_pattern.findall(input_text)
            if matches:
                threats_detected.append(f"Malicious pattern detected: {pattern_str[:50]}")
                threat_level = ThreatLevel.CRITICAL
                confidence = 0.95
                # Remove the malicious pattern
                input_text = compiled_pattern.sub('[FILTERED]', input_text)

        # 4. Check for dangerous characters/sequences
        for dangerous_seq in self.DANGEROUS_CHARS:
            if dangerous_seq.lower() in input_text.lower():
                threats_detected.append(f"Dangerous sequence detected: {dangerous_seq}")
                threat_level = ThreatLevel.DANGEROUS
                input_text = input_text.replace(dangerous_seq, '[FILTERED]')
                input_text = input_text.replace(dangerous_seq.upper(), '[FILTERED]')
                confidence = 0.85

        # 5. Semantic analysis (if enabled)
        if self.enable_semantic_analysis:
            semantic_threats = self._semantic_analysis(input_text, context)
            if semantic_threats:
                threats_detected.extend(semantic_threats)
                if threat_level == ThreatLevel.SAFE:
                    threat_level = ThreatLevel.SUSPICIOUS
                confidence = min(confidence, 0.7)

        # Determine if valid based on threat level and strict mode
        is_valid = (
            threat_level == ThreatLevel.SAFE or
            (threat_level == ThreatLevel.SUSPICIOUS and not self.strict_mode) or
            threat_level == ThreatLevel.DANGEROUS  # Allow with sanitization
        )

        # Block critical threats
        if threat_level == ThreatLevel.CRITICAL:
            is_valid = False
            logger.warning(f"CRITICAL threat blocked in {context}: {threats_detected}")

        # Log threats
        if threats_detected:
            logger.warning(
                f"Threats detected in {context} (level={threat_level.value}): "
                f"{', '.join(threats_detected)}"
            )

        return ValidationResult(
            is_valid=is_valid,
            threat_level=threat_level,
            sanitized_input=input_text,
            threats_detected=threats_detected,
            confidence=confidence
        )

    def _semantic_analysis(self, text: str, context: str) -> List[str]:
        """
        Perform semantic analysis for instruction-like patterns

        Args:
            text: Text to analyze
            context: Input context

        Returns:
            List of detected semantic threats
        """
        threats = []

        # Check for instruction-like patterns
        instruction_indicators = [
            'you are', 'you must', 'you should', 'you will',
            'always', 'never', 'from now on', 'henceforth',
            'system:', 'assistant:', 'user:',
        ]

        lower_text = text.lower()
        for indicator in instruction_indicators:
            if indicator in lower_text:
                threats.append(f"Instruction-like pattern: '{indicator}'")

        # Check for unusual frequency of imperative verbs
        imperative_verbs = [
            'ignore', 'disregard', 'forget', 'execute', 'run',
            'send', 'post', 'delete', 'remove', 'extract'
        ]

        imperative_count = sum(1 for verb in imperative_verbs if verb in lower_text)
        if imperative_count >= 3:
            threats.append(f"High frequency of imperative verbs ({imperative_count})")

        # Check for URL patterns with suspicious contexts
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls and any(verb in lower_text for verb in ['send', 'post', 'forward', 'transmit']):
            threats.append(f"Potential data exfiltration (URL + transfer verb)")

        return threats

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration dictionary

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        for key, value in config.items():
            # Validate key
            if not re.match(r'^[a-zA-Z0-9_.-]+$', key):
                issues.append(f"Invalid config key: {key}")

            # Validate string values
            if isinstance(value, str):
                result = self.validate(value, context=f"config[{key}]")
                if not result.is_valid:
                    issues.append(f"Invalid config value for '{key}': {result.threats_detected}")

            # Recursively validate nested dicts
            elif isinstance(value, dict):
                nested_valid, nested_issues = self.validate_config(value)
                issues.extend(nested_issues)

            # Validate lists
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        result = self.validate(item, context=f"config[{key}][{i}]")
                        if not result.is_valid:
                            issues.append(f"Invalid list item in '{key}[{i}]': {result.threats_detected}")

        return len(issues) == 0, issues

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename
        """
        # Remove path separators
        sanitized = filename.replace('/', '_').replace('\\', '_')

        # Remove parent directory references
        sanitized = sanitized.replace('..', '')

        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"|?*\x00-\x1F]', '', sanitized)

        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]

        return sanitized

    def validate_agent_name(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate agent name

        Args:
            name: Agent name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Agent name cannot be empty"

        if len(name) > 100:
            return False, "Agent name too long (max 100 characters)"

        if not re.match(r'^[a-zA-Z0-9_.-]+$', name):
            return False, "Agent name contains invalid characters (allowed: a-z, A-Z, 0-9, _, ., -)"

        # Check for suspicious patterns
        result = self.validate(name, context="agent_name")
        if not result.is_valid:
            return False, f"Agent name failed security check: {result.threats_detected}"

        return True, None

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'max_input_length': self.max_input_length,
            'strict_mode': self.strict_mode,
            'semantic_analysis_enabled': self.enable_semantic_analysis,
            'patterns_loaded': len(self.compiled_patterns),
            'dangerous_sequences': len(self.DANGEROUS_CHARS)
        }


# Singleton instance
_validator_instance = None


def get_input_validator(strict_mode: bool = False) -> InputValidator:
    """Get or create input validator singleton"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = InputValidator(strict_mode=strict_mode)
    return _validator_instance
