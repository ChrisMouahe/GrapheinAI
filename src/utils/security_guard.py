"""NLP Security Guard module for detecting and blocking prompt injection attempts in ChartQA queries."""

import re
from src.models.exceptions import PromptInjectionDetectedError


class PromptInjectionGuard:
    """Security inspector detecting prompt injection, jailbreak, and adversarial system override patterns."""

    SUSPICIOUS_PATTERNS: list[str] = [
        r"ignore\s+(all\s+)?(previous\s+)?instructions",
        r"ignore\s+(all\s+)?rules",
        r"disregard\s+(previous\s+)?instructions",
        r"forget\s+(all\s+)?rules",
        r"override\s+(system\s+)?rules",
        r"system\s+prompt",
        r"developer\s+mode",
        r"developer\s+message",
        r"act\s+as\s+a",
        r"jailbreak",
        r"do\s+anything\s+now",
        r"\bdan\b",
        r"pretend\s+you\s+are",
        r"bypass\s+security",
    ]

    def __init__(self) -> None:
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS
        ]

    def get_detected_patterns(self, text: str) -> list[str]:
        """Returns list of matched injection pattern strings in text."""
        if not text or not isinstance(text, str):
            return []

        matched: list[str] = []
        for raw_pat, regex in zip(self.SUSPICIOUS_PATTERNS, self.compiled_patterns):
            if regex.search(text):
                matched.append(raw_pat)
        return matched

    def contains_injection(self, text: str) -> bool:
        """Returns True if text contains any prompt injection or jailbreak patterns."""
        return len(self.get_detected_patterns(text)) > 0

    def inspect_prompt(self, text: str) -> bool:
        """Inspects prompt text and raises PromptInjectionDetectedError if malicious patterns exist.

        Args:
            text: User input question or prompt string.

        Returns:
            True if text is safe and clean.

        Raises:
            PromptInjectionDetectedError: If a prompt injection attempt is detected.
        """
        detected = self.get_detected_patterns(text)
        if detected:
            raise PromptInjectionDetectedError(
                f"Security Alert: Potential prompt injection detected matching pattern(s): {detected}"
            )
        return True
