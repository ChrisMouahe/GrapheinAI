"""Independent GraphInterpreter Agent generating multi-lingual personalized scientific narrative reports."""

import logging
from typing import Any

from src.models.chart import ChartExtraction
from src.models.user import UserProfile
from src.agents.recommendation_engine import PersonalizedRecommendations, RecommendationEngine

logger = logging.getLogger("GraphInterpreter")

class GraphInterpreter:
    """Agent producing professional scientific narrative reports tailored to UserProfile."""

    def __init__(self) -> None:
        self.recommendation_engine = RecommendationEngine()

    def interpret_chart(
        self,
        extraction: ChartExtraction,
        target_language: str = "fr",
        user_profile: UserProfile | None = None,
        recommendations: PersonalizedRecommendations | None = None,
    ) -> str:
        lang = target_language.lower() if target_language in ["fr", "en"] else "fr"
        is_en = lang == "en"

        logger.info(f"GraphInterpreter analyzing chart [lang={lang}]")

        recs = recommendations or self.recommendation_engine.generate_recommendations(
            extraction=extraction,
            user_profile=user_profile,
            target_language=lang,
        )

        dps = extraction.data_points or []
        vals = [float(dp.value) for dp in dps if isinstance(dp.value, (int, float))]

        if not vals:
            return "Aucune donnée numérique valide disponible pour l'analyse." if not is_en else "No valid numerical data available."

        max_val, min_val, sum_val = max(vals), min(vals), sum(vals)
        avg_val = sum_val / len(vals)
        delta_val = max_val - min_val

        max_label = next((dp.label for dp in dps if dp.value == max_val and dp.label is not None), "N/A")
        min_label = next((dp.label for dp in dps if dp.value == min_val and dp.label is not None), "N/A")

        # Construction stricte des 4 sections demandées, sans redite des recommandations
        if not is_en:
            report_lines = [
                "### Résumé Exécutif et Cadrage Stratégique",
                recs.executive_summary,
                "",
                "### Tendances et Statistiques Clés",
                f"- **Moyenne:** `{avg_val:.2f}`",
                f"- **Cumul total:** `{sum_val:.2f}`",
                f"- **Maximum:** `{max_val:.2f}` (*{max_label}*)",
                f"- **Minimum:** `{min_val:.2f}` (*{min_label}*)",
                f"- **Écart d'amplitude:** `{delta_val:.2f}`",
                "",
                "### Risques et Anomalies Identifiés",
            ]
            for r in recs.risks:
                report_lines.append(f"- ⚠️ **{r}**")

            report_lines.extend([
                "",
                "### Opportunités de Croissance et de Rentabilité",
            ])
            for o in recs.opportunities:
                report_lines.append(f"- 🚀 **{o}**")

        else:
            report_lines = [
                "### Executive Summary & Strategic Briefing",
                recs.executive_summary,
                "",
                "### Statistical Trends & Key Metrics",
                f"- **Mean:** `{avg_val:.2f}`",
                f"- **Total Sum:** `{sum_val:.2f}`",
                f"- **Maximum:** `{max_val:.2f}` (*{max_label}*)",
                f"- **Minimum:** `{min_val:.2f}` (*{min_label}*)",
                f"- **Amplitude Gap:** `{delta_val:.2f}`",
                "",
                "### Identified Risks & Anomalies",
            ]
            for r in recs.risks:
                report_lines.append(f"- ⚠️ **{r}**")

            report_lines.extend([
                "",
                "### Growth & Profitability Opportunities",
            ])
            for o in recs.opportunities:
                report_lines.append(f"- 🚀 **{o}**")

        return "\n".join(report_lines)