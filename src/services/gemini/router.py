"""QuestionRouter for intelligent non-Gemini routing to AST, Pandas/NumPy, or FAISS."""

import logging
import re
from enum import Enum
from typing import Any

logger = logging.getLogger("QuestionRouter")


class RouteTarget(str, Enum):
    AST_CALCULATOR = "AST_CALCULATOR"
    FAISS_RAG = "FAISS_RAG"
    GEMINI_VLM = "GEMINI_VLM"


class QuestionRouter:
    """Intelligently routes analytical questions to AST, FAISS, or Gemini VLM."""

    MATH_KEYWORDS: list[str] = [
        r"\bmoyenne\b",
        r"\bsomme\b",
        r"\btotal\b",
        r"\bmaximum\b",
        r"\bmax\b",
        r"\bminimum\b",
        r"\bmin\b",
        r"\bécart-type\b",
        r"\becart-type\b",
        r"\bstddev\b",
        r"\bvariation\b",
        r"\bpourcentage\b",
        r"\bdifférence\b",
        r"\bdifferer\b",
        r"\bplus élevé\b",
        r"\bplus haut\b",
        r"\bplus bas\b",
        r"\bratio\b",
        r"\bcombien\b",
        r"\bvaleur de\b",
        r"\bvaleur pour\b",
        r"\bcalculer\b",
        r"\bcalcule\b",
    ]

    RAG_KEYWORDS: list[str] = [
        r"\bhistorique\b",
        r"\brag\b",
        r"\bdocument\b",
        r"\bbase\b",
        r"\barchive\b",
        r"\bsimilaire\b",
    ]

    def route_question(self, question: str) -> RouteTarget:
        """Determines whether question can be resolved without calling Gemini.

        Args:
            question: User question string.

        Returns:
            RouteTarget enum (AST_CALCULATOR, FAISS_RAG, or GEMINI_VLM).
        """
        clean_q = question.strip().lower()

        # 0. Check for conversational / natural language explanations -> GEMINI_VLM
        conversational_patterns = [
            r"\bbonjour\b", r"\bsalut\b", r"\bhello\b", r"\bhi\b", r"\bcomment\b",
            r"\bpourquoi\b", r"\bexplique\b", r"\bexpliquer\b", r"\bconseil\b",
            r"\bavis\b", r"\banalyse\b", r"\bque pensez\b", r"\bsynthèse\b"
        ]
        for p in conversational_patterns:
            if re.search(p, clean_q):
                logger.info(f"QuestionRouter: Routed conversational question '{question[:30]}...' to GEMINI_VLM.")
                return RouteTarget.GEMINI_VLM

        # 1. Check for Math / Statistical query -> AST_CALCULATOR
        for pattern in self.MATH_KEYWORDS:
            if re.search(pattern, clean_q):
                logger.info(f"QuestionRouter: Routed '{question[:30]}...' to AST_CALCULATOR (No Gemini call).")
                return RouteTarget.AST_CALCULATOR

        # 2. Check for RAG / Historical query -> FAISS_RAG
        for pattern in self.RAG_KEYWORDS:
            if re.search(pattern, clean_q):
                logger.info(f"QuestionRouter: Routed '{question[:30]}...' to FAISS_RAG.")
                return RouteTarget.FAISS_RAG

        # 3. Default to Gemini VLM for qualitative synthesis/reasoning
        logger.info(f"QuestionRouter: Routed '{question[:30]}...' to GEMINI_VLM.")
        return RouteTarget.GEMINI_VLM

    def execute_ast_query(self, question: str, extraction: Any) -> str | None:
        """Executes local deterministic calculation on FullChartExtraction without Gemini API call.

        Args:
            question: User question string.
            extraction: FullChartExtraction instance or dict.

        Returns:
            Formatted response string or None if execution failed.
        """
        try:
            series_list = getattr(extraction, "series", []) if hasattr(extraction, "series") else extraction.get("series", [])
            if not series_list:
                return None

            all_values = []
            categories_map = {}
            for s in series_list:
                vals = getattr(s, "values", []) if hasattr(s, "values") else s.get("values", [])
                cats = getattr(s, "categories", []) if hasattr(s, "categories") else s.get("categories", [])
                all_values.extend(vals)
                for c, v in zip(cats, vals):
                    categories_map[str(c)] = v

            if not all_values:
                return None

            q_lower = question.lower()
            unit = getattr(extraction, "unites", "") if hasattr(extraction, "unites") else extraction.get("unites", "")

            # Match category specific lookup
            for cat, val in categories_map.items():
                if cat.lower() in q_lower:
                    return f"La valeur extraite pour **{cat}** est de **{val} {unit}** (calcul AST déterministe)."

            if "moyenne" in q_lower:
                avg_val = sum(all_values) / len(all_values)
                return f"La moyenne calculée sur l'ensemble des données est de **{avg_val:.2f} {unit}** (calcul AST déterministe)."

            if "somme" in q_lower or "total" in q_lower:
                sum_val = sum(all_values)
                return f"La somme totale calculée est de **{sum_val:.2f} {unit}** (calcul AST déterministe)."

            if "max" in q_lower or "maximum" in q_lower or "plus élevé" in q_lower or "plus haut" in q_lower:
                max_val = max(all_values)
                max_cats = [c for c, v in categories_map.items() if v == max_val]
                cat_str = f" ({max_cats[0]})" if max_cats else ""
                return f"La valeur maximale enregistrée est de **{max_val:.2f} {unit}**{cat_str} (calcul AST déterministe)."

            if "min" in q_lower or "minimum" in q_lower or "plus bas" in q_lower:
                min_val = min(all_values)
                min_cats = [c for c, v in categories_map.items() if v == min_val]
                cat_str = f" ({min_cats[0]})" if min_cats else ""
                return f"La valeur minimale enregistrée est de **{min_val:.2f} {unit}**{cat_str} (calcul AST déterministe)."

            if "variation" in q_lower or "différence" in q_lower or "écart" in q_lower:
                max_v = max(all_values)
                min_v = min(all_values)
                gap = max_v - min_v
                pct = (gap / min_v * 100) if min_v != 0 else 0
                return f"L'écart amplitude max-min est de **{gap:.2f} {unit}** (variation relative: **+{pct:.1f}%**) (calcul AST déterministe)."

        except Exception as e:
            logger.warning(f"AST query execution fallback: {e}")
            return None

        return None
