"""Language Manager module for internationalization (i18n) handling French (fr) and English (en)."""

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LanguageManager:
    """Manages translations, automatic language detection, and locale-specific number/date formatting."""

    SUPPORTED_LANGUAGES = ["fr", "en"]
    DEFAULT_LANGUAGE = "fr"

    def __init__(self, translations_dir: Path | str | None = None) -> None:
        if translations_dir is None:
            translations_dir = Path(__file__).parent / "translations"
        self.translations_dir = Path(translations_dir)

        self._translations: dict[str, dict[str, Any]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Loads fr.json and en.json dictionaries from disk."""
        for lang in self.SUPPORTED_LANGUAGES:
            filepath = self.translations_dir / f"{lang}.json"
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self._translations[lang] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load translation file '{filepath}': {e}")
                    self._translations[lang] = {}
            else:
                self._translations[lang] = {}

    def get_translation(self, key_path: str, lang: str = "fr", default: str | None = None) -> str:
        """Retrieves localized text string for a dot-separated key path (e.g., 'nav.dashboard')."""
        target_lang = lang.lower() if lang in self.SUPPORTED_LANGUAGES else self.DEFAULT_LANGUAGE
        dictionary = self._translations.get(target_lang, {})

        keys = key_path.split(".")
        current = dictionary

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                current = None
                break

        if isinstance(current, str):
            return current

        if default is not None:
            return default

        # Fallback to French if missing in English
        if target_lang != "fr" and "fr" in self._translations:
            fr_dict = self._translations["fr"]
            curr_fr = fr_dict
            for k in keys:
                if isinstance(curr_fr, dict) and k in curr_fr:
                    curr_fr = curr_fr[k]
                else:
                    curr_fr = None
                    break
            if isinstance(curr_fr, str):
                return curr_fr

        return key_path

    def t(self, key_path: str, lang: str = "fr", **kwargs: Any) -> str:
        """Shorthand translation retriever supporting string formatting interpolation."""
        text = self.get_translation(key_path, lang=lang)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                pass
        return text

    def detect_language(self, text: str) -> str:
        """Automatically detects whether input text is written in French (fr) or English (en)."""
        if not text or not text.strip():
            return self.DEFAULT_LANGUAGE

        clean_text = text.strip().lower()

        fr_keywords = [
            "quel", "quelle", "quels", "quelles", "est", "la", "le", "les", "du", "des",
            "pourquoi", "comment", "combien", "somme", "moyenne", "différence", "écart",
            "décris", "résume", "tendance", "anomalie", "enseignements", "ville", "ventes",
            "chiffre", "augmentation", "diminution", "meilleur", "pire", "deuxième", "troisième"
        ]

        en_keywords = [
            "what", "which", "where", "how", "why", "is", "are", "the", "sum", "total",
            "average", "avg", "mean", "difference", "growth", "rate", "trend", "describe",
            "summary", "anomaly", "highest", "lowest", "best", "worst", "second", "third",
            "chart", "graph", "value", "sales", "revenue"
        ]

        fr_score = 0
        en_score = 0

        for kw in fr_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_text):
                fr_score += 1

        for kw in en_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_text):
                en_score += 1

        if en_score > fr_score:
            return "en"
        return "fr"

    @staticmethod
    def format_number(val: float | int, lang: str = "fr") -> str:
        """Formats number according to locale (12 345,67 for fr vs 12,345.67 for en)."""
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            return str(val)

        if lang == "fr":
            # French: 12 345,67
            formatted = f"{val_f:,.2f}".replace(",", " ").replace(".", ",")
            if formatted.endswith(",00"):
                formatted = formatted[:-3]
            return formatted
        else:
            # English: 12,345.67
            formatted = f"{val_f:,.2f}"
            if formatted.endswith(".00"):
                formatted = formatted[:-3]
            return formatted
