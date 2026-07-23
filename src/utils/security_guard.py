"""Security Guard module performing file validation, magic bytes checking, size limiting, and prompt injection detection."""

import html
from pathlib import Path
import re
from src.models.exceptions import ChartValidationError, PromptInjectionDetectedError

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

MAGIC_BYTES = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "pdf": b"%PDF-",
    "webp": b"RIFF",
}


class PromptInjectionGuard:
    """Security inspector performing magic bytes file validation, size enforcement, and prompt injection detection."""

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

    def validate_file_upload(self, file_bytes: bytes, filename: str, max_size_mb: float = 20.0) -> bool:
        """Validates uploaded file size, extension, and magic bytes header.

        Args:
            file_bytes: Raw binary content of the file.
            filename: Original filename.
            max_size_mb: Maximum allowed size in Megabytes.

        Returns:
            True if file passes security checks.

        Raises:
            ChartValidationError: If file violates size limits or magic bytes inspection.
        """
        if not file_bytes:
            raise ChartValidationError("Le fichier téléchargé est vide (0 octet).")

        max_bytes = max_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise ChartValidationError(f"La taille du fichier ({len(file_bytes)/1024/1024:.2f} MB) dépasse la limite autorisée ({max_size_mb} MB).")

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ChartValidationError(f"Extension de fichier '{ext}' non autorisée. Formats acceptés : .png, .jpg, .jpeg, .webp, .pdf")

        # Magic Bytes Inspection
        header = file_bytes[:12]
        is_valid_magic = (
            header.startswith(MAGIC_BYTES["png"])
            or header.startswith(MAGIC_BYTES["jpeg"])
            or header.startswith(MAGIC_BYTES["pdf"])
            or (header.startswith(MAGIC_BYTES["webp"]) and b"WEBP" in header)
        )

        if not is_valid_magic:
            raise ChartValidationError("Échec de la validation de sécurité des signatures d'en-tête (Magic Bytes non reconnus).")

        return True

    def sanitize_text(self, text: str) -> str:
        """Sanitizes user input string against HTML/XSS injection and path traversal attempts."""
        if not text:
            return ""

        # Remove path traversal tokens
        sanitized = text.replace("../", "").replace("..\\", "")
        # Escape HTML tags
        sanitized = html.escape(sanitized)
        return sanitized.strip()

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
        """Inspects prompt text and raises PromptInjectionDetectedError if malicious patterns exist."""
        detected = self.get_detected_patterns(text)
        if detected:
            raise PromptInjectionDetectedError(
                f"Security Alert: Potential prompt injection detected matching pattern(s): {detected}"
            )
        return True
