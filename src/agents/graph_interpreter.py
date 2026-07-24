"""Independent GraphInterpreter Agent generating multi-lingual personalized scientific narrative reports."""

import logging
from typing import Any

from src.models.chart import ChartExtraction
from src.models.user import UserProfile
from src.agents.recommendation_engine import PersonalizedRecommendations, RecommendationEngine

logger = logging.getLogger("GraphInterpreter")


class GraphInterpreter:
    """Agent producing professional scientific narrative reports tailored to UserProfile and PersonalizedRecommendations."""

    def __init__(self) -> None:
        self.recommendation_engine = RecommendationEngine()

    def interpret_chart(
        self,
        extraction: ChartExtraction,
        target_language: str = "fr",
        user_profile: UserProfile | None = None,
        recommendations: PersonalizedRecommendations | None = None,
    ) -> str:
        """Generates a personalized scientific narrative analysis report based on structured chart data and user profile.

        Args:
            extraction: Validated ChartExtraction model.
            target_language: Target output language ("fr" or "en").
            user_profile: UserProfile model for personalization.
            recommendations: Optional pre-computed PersonalizedRecommendations.

        Returns:
            Markdown formatted personalized scientific narrative report string.
        """
        lang = target_language.lower() if target_language in ["fr", "en"] else "fr"
        is_en = lang == "en"

        title = extraction.title or ("Analyse Statistique du Graphique" if not is_en else "Statistical Chart Analysis")
        c_type = extraction.chart_type.upper()
        logger.info(f"GraphInterpreter analyzing chart: '{title}' [lang={lang}]")

        # Compute recommendations if not supplied
        recs = recommendations or self.recommendation_engine.generate_recommendations(
            extraction=extraction,
            user_profile=user_profile,
            target_language=lang,
        )

        dps = extraction.data_points or []
        vals = [float(dp.value) for dp in dps if isinstance(dp.value, (int, float))]

        if not vals:
            if not is_en:
                return f"### RAPPORT D'INTERPRÉTATION AI BUSINESS ANALYST\n**Architecture du Graphique:** `{c_type}`\n\nAucune donnée numérique valide disponible pour l'analyse."
            else:
                return f"### AI BUSINESS ANALYST INTERPRETATION REPORT\n**Chart Architecture:** `{c_type}`\n\nNo valid numerical data points available for statistical analysis."

        max_val = max(vals)
        min_val = min(vals)
        sum_val = sum(vals)
        avg_val = sum_val / len(vals)
        delta_val = max_val - min_val

        max_label = next((dp.label for dp in dps if dp.value == max_val and dp.label is not None), "N/A")
        min_label = next((dp.label for dp in dps if dp.value == min_val and dp.label is not None), "N/A")

        job_str = (user_profile.fonction if user_profile else "Analyste / Décideur").strip() or "Analyste"
        sect_str = (user_profile.secteur_activite if user_profile else "Finance").strip() or "Finance"

        if not is_en:
            report_lines = [
                f"# RAPPORT AUTOMATIQUE D'INTERPRÉTATION SCIENTIFIQUE DU GRAPHIQUE - {title.upper()}",
                f"**Poste Cible:** `{job_str}` | **Secteur:** `{sect_str}` | **Architecture & Description du Contexte:** `{c_type}`",
                "",
                "---",
                "",
                "### 1. RÉSUMÉ EXÉCUTIF ET CADRAGE STRATÉGIQUE (Executive Summary)",
                recs.executive_summary,
                "",
                "### 2. DÉCOMPOSITION QUANTITATIVE ET FAITS OBSERVÉS",
            ]
            for dp in dps:
                lbl = dp.label or "[Illisible]"
                report_lines.append(f"- **{lbl}:** `{dp.value}` (Confiance d'extraction: {dp.confidence:.2%})")

            report_lines.extend([
                "",
                "### 3. TENDANCES ET STATISTIQUES CLÉS",
                f"- **Moyenne du portefeuille / secteur:** `{avg_val:.2f} unités`",
                f"- **Cumul total observé:** `{sum_val:.2f} unités`",
                f"- **Pic Maximum:** `{max_val:.2f}` (Catégorie: *{max_label}*)",
                f"- **Seuil Minimum:** `{min_val:.2f}` (Catégorie: *{min_label}*)",
                f"- **Écart d'amplitude (Max - Min):** `{delta_val:.2f} unités`",
                "",
                "### 4. RISQUES ET ANOMALIES IDENTIFIÉS",
            ])
            for r in recs.risks:
                report_lines.append(f"- ⚠️ **{r}**")

            report_lines.extend([
                "",
                "### 5. OPPORTUNITÉS DE CROISSANCE & DE RENTABILITÉ",
            ])
            for o in recs.opportunities:
                report_lines.append(f"- 🚀 **{o}**")

            report_lines.extend([
                "",
                "### 6. RECOMMANDATIONS PRIORITAIRES ET JUSTIFICATION",
            ])
            for rec in recs.priority_recommendations:
                report_lines.append(f"#### [{rec.priority.upper()}] {rec.title}")
                report_lines.append(f"{rec.description}")
                report_lines.append(f"_Rationale:_ {rec.rationale}")
                report_lines.append("")

            report_lines.extend([
                "### 7. PLAN D'ACTION ET PROCHAINES ÉTAPES",
            ])
            for step in recs.action_plan:
                report_lines.append(f"{step.step_number}. **{step.action}** (Impact attendu: *{step.expected_impact}*, Responsable: *{step.owner}*)")

            report_lines.extend([
                "",
                "---",
                f"_*Garde-fou et Déclaration d'Authenticité:* {recs.disclaimer}_",
            ])
        else:
            report_lines = [
                f"# AUTOMATIC SCIENTIFIC GRAPHIC INTERPRETATION REPORT - {title.upper()}",
                f"**Target Role:** `{job_str}` | **Industry Sector:** `{sect_str}` | **Description & Context Architecture:** `{c_type}`",
                "",
                "---",
                "",
                "### 1. EXECUTIVE SUMMARY & STRATEGIC BRIEFING",
                recs.executive_summary,
                "",
                "### 2. QUANTITATIVE BREAKDOWN & OBSERVED DATA",
            ]
            for dp in dps:
                lbl = dp.label or "[Unreadable]"
                report_lines.append(f"- **{lbl}:** `{dp.value}` (Extraction Confidence: {dp.confidence:.2%})")

            report_lines.extend([
                "",
                "### 3. STATISTICAL TRENDS & KEY METRICS (Trends)",
                f"- **Sector / Portfolio Mean:** `{avg_val:.2f} units`",
                f"- **Total Cumulative Sum:** `{sum_val:.2f} units`",
                f"- **Peak Maximum:** `{max_val:.2f}` (Category: *{max_label}*)",
                f"- **Floor Minimum:** `{min_val:.2f}` (Category: *{min_label}*)",
                f"- **Range Amplitude Gap:** `{delta_val:.2f} units`",
                "",
                "### 4. IDENTIFIED RISKS & ANOMALIES",
            ])
            for r in recs.risks:
                report_lines.append(f"- ⚠️ **{r}**")

            report_lines.extend([
                "",
                "### 5. GROWTH & PROFITABILITY OPPORTUNITIES",
            ])
            for o in recs.opportunities:
                report_lines.append(f"- 🚀 **{o}**")

            report_lines.extend([
                "",
                "### 6. PRIORITY RECOMMENDATIONS & RATIONALE",
            ])
            for rec in recs.priority_recommendations:
                report_lines.append(f"#### [{rec.priority.upper()}] {rec.title}")
                report_lines.append(f"{rec.description}")
                report_lines.append(f"_Rationale:_ {rec.rationale}")
                report_lines.append("")

            report_lines.extend([
                "### 7. ACTION PLAN & NEXT STEPS",
            ])
            for step in recs.action_plan:
                report_lines.append(f"{step.step_number}. **{step.action}** (Expected Impact: *{step.expected_impact}*, Owner: *{step.owner}*)")

            report_lines.extend([
                "",
                "---",
                f"_*Guardrail Rationale Statement:* {recs.disclaimer}_",
            ])

        return "\n".join(report_lines)
