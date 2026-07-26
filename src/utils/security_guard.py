import html
from pathlib import Path
import re
from src.models.exceptions import ChartValidationError, PromptInjectionDetectedError

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
MAGIC_BYTES = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "pdf": b"%PDF-",
    "webp": b"RIFF",
}

class PromptInjectionGuard:
    """Enterprise-grade security inspector performing magic bytes validation, and semantic prompt injection detection."""

    # Patterns fusionnés (Anglais + Français) et optimisés pour bloquer les variations
    SUSPICIOUS_PATTERNS: list[str] = [
        # 1. Tentatives d'amnésie et de contournement (FR/EN)
        r"(ignore|disregard|forget|override|bypass|oublie|outrepasse|contourne|désactive)[\s\W]*?(all|previous|system|toutes|les|tes)?[\s\W]*?(instructions|rules|prompt|security|règles|consignes|sécurité)",
        
        # 2. Prise de rôle forcée & Jailbreaks connus
        r"act\s+as",
        r"agis\s+comme",
        r"comporte[- ]toi\s+comme",
        r"do\s+anything\s+now",
        r"\bdan\b",
        r"jailbreak",
        r"developer\s+mode",
        r"mode\s+d[é|e]veloppeur",
        
        # 3. Fuite d'informations internes
        r"(system\s+message|system\s+prompt|instructions\s+syst[e|è]me)",
        r"(what\s+are\s+your\s+instructions|quelles\s+sont\s+tes\s+consignes)",
    ]

    def __init__(self) -> None:
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.SUSPICIOUS_PATTERNS
        ]

    def validate_file_upload(self, file_bytes: bytes, filename: str, max_size_mb: float = 20.0) -> bool:
        """Validates uploaded file size, extension, and magic bytes header."""
        if not file_bytes:
            raise ChartValidationError("Le fichier téléchargé est vide (0 octet).")

        max_bytes = max_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise ChartValidationError(f"La taille du fichier dépasse la limite autorisée ({max_size_mb} MB).")

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ChartValidationError(f"Extension de fichier '{ext}' non autorisée.")

        header = file_bytes[:12]
        is_valid_magic = (
            header.startswith(MAGIC_BYTES["png"])
            or header.startswith(MAGIC_BYTES["jpeg"])
            or header.startswith(MAGIC_BYTES["pdf"])
            or (header.startswith(MAGIC_BYTES["webp"]) and b"WEBP" in header)
        )

        if not is_valid_magic:
            raise ChartValidationError("Échec de la validation de sécurité (Magic Bytes non reconnus).")

        return True

    def sanitize_text(self, text: str) -> str:
        """Sanitizes user input string against HTML/XSS injection and path traversal attempts."""
        if not text:
            return ""

        # Correction de la faille de Path Traversal (Boucle de suppression)
        sanitized = text
        while "../" in sanitized or "..\\" in sanitized:
            sanitized = sanitized.replace("../", "").replace("..\\", "")
            
        # Escape HTML tags
        sanitized = html.escape(sanitized)
        return sanitized.strip()

    def get_detected_patterns(self, text: str) -> list[str]:
        """Returns list of matched injection pattern strings in text."""
        if not text or not isinstance(text, str):
            return []

        # Retrait des ponctuations superflues (Le "bruit blanc") avant vérification
        clean_text = re.sub(r'[^\w\s]', '', text)
        
        matched: list[str] = []
        for raw_pat, regex in zip(self.SUSPICIOUS_PATTERNS, self.compiled_patterns):
            if regex.search(text) or regex.search(clean_text):
                matched.append(raw_pat)
        return matched

    def contains_injection(self, text: str) -> bool:
        return len(self.get_detected_patterns(text)) > 0

    def inspect_prompt(self, text: str) -> bool:
        detected = self.get_detected_patterns(text)
        if detected:
            raise PromptInjectionDetectedError(
                "Alerte de Sécurité : Tentative de manipulation du prompt détectée."
            )
        return True