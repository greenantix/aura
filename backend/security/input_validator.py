import re
import os
from pathlib import Path
from typing import List, Union

class SecurityError(Exception):
    """Security-related error"""
    pass

class SecurityValidator:
    """Comprehensive input validation for Aura services"""

    # Secure patterns for different input types
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9/._-]+$')
    CODE_INJECTION_PATTERNS = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'subprocess\.',
        r'os\.system',
    ]

    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: List[str] = None) -> str:
        """Validate and sanitize file paths to prevent traversal attacks"""
        normalized = os.path.normpath(file_path)
        # Disallow absolute paths or path traversal
        if '..' in normalized or (normalized.startswith('/') and not allowed_dirs):
            raise SecurityError("Path traversal attempt detected")

        # Validate against allowed directories if provided
        if allowed_dirs:
            resolved_path = Path(normalized).resolve()
            allowed = any(
                str(resolved_path).startswith(str(Path(d).resolve()))
                for d in allowed_dirs
            )
            if not allowed:
                raise SecurityError("Access to path not permitted")
        return normalized

    @staticmethod
    def sanitize_code_input(code: str, max_length: int = 100000) -> str:
        """Sanitize code input to prevent injection attacks"""
        if len(code) > max_length:
            raise SecurityError("Code input exceeds maximum length")

        for pattern in SecurityValidator.CODE_INJECTION_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(f"Potentially dangerous code pattern detected: {pattern}")
        return code

    @staticmethod
    def validate_llm_prompt(prompt: str, max_length: int = 10000) -> str:
        """Validate LLM prompts for security"""
        if len(prompt) > max_length:
            raise SecurityError("Prompt exceeds maximum length")

        dangerous_phrases = [
            "ignore previous instructions",
            "system:",
            "assistant:",
            "jailbreak",
            "override safety"
        ]
        lower_prompt = prompt.lower()
        for phrase in dangerous_phrases:
            if phrase in lower_prompt:
                raise SecurityError("Potential prompt injection detected")
        return prompt