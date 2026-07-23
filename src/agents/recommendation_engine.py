"""RecommendationEngine generating personalized strategic insights, risks, opportunities, and action plans."""

import logging
from typing import Any
from pydantic import BaseModel, Field

from src.models.chart import ChartExtraction
from src.models.user import UserProfile
from src.utils.anomaly_detector import AnomalyDetector
from src.utils.prompt_builder import PromptBuilder
from src.utils.stat_calculator import StatisticalEngine, StatisticalSummary

logger = logging.getLogger("RecommendationEngine")


class RecommendationItem(BaseModel):
    """Structured priority recommendation item."""

    id: str = Field(..., description="Unique identifier for recommendation")
    title: str = Field(..., description="Actionable title of the recommendation")
    description: str = Field(..., description="Detailed description and tactical recommendation")
    priority: str = Field(default="haute", description="Priority level ('haute', 'moyenne', 'basse')")
    rationale: str = Field(default="La recommandation est basée sur les données observées.", description="Data justification")
    category: str = Field(default="Strategie", description="Category (ex: Strategie, Performance, Risque)")


class ActionStep(BaseModel):
    """Step-by-step action item in the execution plan."""

    step_number: int = Field(..., description="Step sequence number")
    action: str = Field(..., description="Description of the action to execute")
    expected_impact: str = Field(..., description="Expected business or analytical impact")
    owner: str = Field(..., description="Role responsible for execution")


class PersonalizedRecommendations(BaseModel):
    """Complete personalized AI Business Analyst recommendations payload."""

    executive_summary: str = Field(..., description="Role-tailored executive summary")
    key_findings: list[str] = Field(default_factory=list, description="Fact-based observations from chart data")
    priority_recommendations: list[RecommendationItem] = Field(default_factory=list, description="Actionable recommendations")
    opportunities: list[str] = Field(default_factory=list, description="Strategic upside opportunities")
    risks: list[str] = Field(default_factory=list, description="Downside risks or anomalies")
    action_plan: list[ActionStep] = Field(default_factory=list, description="Step-by-step next steps for user role")
    disclaimer: str = Field(
        default="La recommandation est basée sur les données observées.",
        description="Mandatory guardrail rationale statement"
    )


class RecommendationEngine:
    """AI Business Analyst Recommendation Engine generating role and sector-tailored recommendations."""

    def __init__(self) -> None:
        pass

    def generate_recommendations(
        self,
        extraction: ChartExtraction,
        statistics: StatisticalSummary | None = None,
        anomalies: list[dict[str, Any]] | None = None,
        user_profile: UserProfile | None = None,
        target_language: str = "fr",
    ) -> PersonalizedRecommendations:
        """Generates role and sector personalized business insights, risks, and action steps."""
        is_en = target_language == "en"
        stats = statistics or StatisticalEngine.compute_summary(extraction)
        anoms = anomalies if anomalies is not None else AnomalyDetector.detect_anomalies(extraction)

        job_title = (user_profile.fonction if user_profile else "Analyste").strip() or "Analyste"
        sector = (user_profile.secteur_activite if user_profile else "Finance").strip() or "Finance"
        expertise = (user_profile.niveau_expertise if user_profile else "Intermédiaire").strip() or "Intermédiaire"

        # 1. Generate Key Findings from Extracted Data Points
        dps = extraction.data_points or []
        vals = [dp.value for dp in dps if isinstance(dp.value, (int, float))]
        labels = [dp.label for dp in dps if dp.label]

        key_findings = []
        if vals:
            max_val = max(vals)
            min_val = min(vals)
            max_label = labels[vals.index(max_val)] if len(labels) == len(vals) else "N/A"
            min_label = labels[vals.index(min_val)] if len(labels) == len(vals) else "N/A"

            if is_en:
                key_findings.append(f"Maximum observed value of {max_val} recorded for category '{max_label}'.")
                key_findings.append(f"Minimum observed value of {min_val} recorded for category '{min_label}'.")
                key_findings.append(f"Mean performance across {len(vals)} data points is {stats.mean:.2f}.")
            else:
                key_findings.append(f"Valeur maximale observée de {max_val} enregistrée pour la catégorie '{max_label}'.")
                key_findings.append(f"Valeur minimale observée de {min_val} enregistrée pour la catégorie '{min_label}'.")
                key_findings.append(f"La performance moyenne observée sur {len(vals)} points est de {stats.mean:.2f}.")

        # 2. Executive Summary Tailored to Role & Expertise
        if expertise.startswith("Débutant") or "Etudiant" in job_title or "Étudiant" in job_title:
            summary = (
                f"Ce graphique présente la distribution des données pour le secteur {sector}. "
                f"La moyenne générale s'élève à {stats.mean:.2f}, avec un écart d'amplitude de {stats.range_amplitude:.2f}. "
                f"Les explications ci-dessous ont été simplifiées pour vous permettre de comprendre facilement les tendances clés sans jargon technique complexe."
                if not is_en else
                f"This chart displays data distribution for the {sector} sector. "
                f"The overall mean is {stats.mean:.2f} with an amplitude range of {stats.range_amplitude:.2f}. "
                f"The explanations below are simplified for educational clarity."
            )
        elif "Directeur" in job_title or "CEO" in job_title or "DG" in job_title or "Chef" in job_title:
            summary = (
                f"Synthèse Exécutive pour la Direction ({job_title}) - Secteur {sector} : "
                f"L'analyse met en évidence un pic de performance à {stats.maximum:.2f} et un point de fragilité à {stats.minimum:.2f}. "
                f"L'écart-type de {stats.std_dev:.2f} indique la variabilité stratégique du portefeuille. "
                f"Les recommandations ci-dessous précisent le ROI attendu et les décisions d'arbitrage prioritaires."
                if not is_en else
                f"Executive Briefing for {job_title} ({sector} sector): "
                f"Analysis highlights a performance peak at {stats.maximum:.2f} and a vulnerability point at {stats.minimum:.2f}. "
                f"The standard deviation of {stats.std_dev:.2f} measures portfolio strategic variability."
            )
        elif "Marketing" in job_title or sector == "Marketing":
            summary = (
                f"Analyse de Performance Marketing ({job_title}) : "
                f"Les résultats montrent une dynamique de croissance maximale sur les leviers performants ({stats.maximum:.2f}). "
                f"La moyenne du canal s'établit à {stats.mean:.2f}. Les recommandations ciblent l'optimisation du budget et du CAC."
                if not is_en else
                f"Marketing Performance Analysis ({job_title}): "
                f"Results show peak campaign growth at {stats.maximum:.2f} with a channel mean of {stats.mean:.2f}."
            )
        else:
            summary = (
                f"Analyse Décisionnelle AI Business Analyst ({job_title} - {sector}) : "
                f"Moyenne globale : {stats.mean:.2f} | Écart-type : {stats.std_dev:.2f} | Amplitude : {stats.range_amplitude:.2f}. "
                f"Recommandations d'optimisation basées strictement sur les données chiffrées extraites du graphique."
                if not is_en else
                f"AI Business Analyst Briefing ({job_title} - {sector}): "
                f"Overall mean: {stats.mean:.2f} | StdDev: {stats.std_dev:.2f} | Range: {stats.range_amplitude:.2f}."
            )

        # 3. Opportunities & Risks Derivation
        opportunities = []
        risks = []

        if vals:
            high_performers = [dp.label for dp in dps if isinstance(dp.value, (int, float)) and dp.value >= stats.mean]
            low_performers = [dp.label for dp in dps if isinstance(dp.value, (int, float)) and dp.value < stats.mean]

            if high_performers:
                top_str = ", ".join(high_performers[:3])
                opp_txt = (
                    f"Capitaliser sur la surperformance des segments ({top_str}) situés au-dessus de la moyenne ({stats.mean:.2f})."
                    if not is_en else
                    f"Capitalize on outperforming segments ({top_str}) performing above average ({stats.mean:.2f})."
                )
                opportunities.append(opp_txt)

            if low_performers:
                low_str = ", ".join(low_performers[:3])
                risk_txt = (
                    f"Vigilance renforcée sur les sous-performances ({low_str}) sous la moyenne du secteur."
                    if not is_en else
                    f"Heightened risk on underperforming segments ({low_str}) below sector average."
                )
                risks.append(risk_txt)

        if anoms:
            for a in anoms[:2]:
                if hasattr(a, "label"):
                    label_a = a.label or "Inconnu"
                    val_a = getattr(a, "value", 0)
                elif isinstance(a, dict):
                    label_a = a.get("label", "Inconnu")
                    val_a = a.get("value", 0)
                else:
                    label_a = str(a)
                    val_a = 0

                risk_txt = (
                    f"Anomalie critique détectée sur la catégorie '{label_a}' avec une valeur de {val_a}."
                    if not is_en else
                    f"Critical statistical anomaly detected on '{label_a}' with value {val_a}."
                )
                risks.append(risk_txt)

        if not opportunities:
            opportunities.append("Renforcer les investissements sur les périodes de croissance observées." if not is_en else "Strengthen investments during observed growth periods.")
        if not risks:
            risks.append("Analyser les facteurs d'incertitude et la volatilité mesurée par l'écart-type." if not is_en else "Analyze volatility and uncertainty factors measured by standard deviation.")

        # 4. Priority Recommendations
        rec_list = []
        rec_list.append(
            RecommendationItem(
                id="rec_1",
                title="Consolidation des Segments Performants" if not is_en else "Consolidate High-Performing Segments",
                description=(
                    f"Allouer en priorité les ressources sur les catégories dépassant la moyenne ({stats.mean:.2f}) "
                    f"pour maximiser l'impact stratégique pour un poste de {job_title}."
                ) if not is_en else f"Allocate priority resources to categories above average ({stats.mean:.2f}).",
                priority="haute",
                rationale="La recommandation est basée sur les données observées (valeur maximale enregistrée à " + str(stats.maximum) + ").",
                category="Strategie",
            )
        )

        rec_list.append(
            RecommendationItem(
                id="rec_2",
                title="Plan de Redressement des Anomalies & Écarts" if not is_en else "Remediation Plan for Anomaly Gaps",
                description=(
                    f"Mener un audit approfondi sur la valeur minimale ({stats.minimum:.2f}) "
                    f"afin de combler l'écart d'amplitude de {stats.range_amplitude:.2f}."
                ) if not is_en else f"Conduct an in-depth audit on minimum value ({stats.minimum:.2f}) to close range amplitude gap of {stats.range_amplitude:.2f}.",
                priority="haute" if anoms else "moyenne",
                rationale="La recommandation est basée sur les données observées (amplitude minimale/maximale).",
                category="Performance",
            )
        )

        rec_list.append(
            RecommendationItem(
                id="rec_3",
                title="Suivi Continu des Indicateurs Métier" if not is_en else "Continuous Business KPI Tracking",
                description=(
                    f"Mettre en place un tableau de bord mensuel adapté aux priorités du secteur {sector}."
                ) if not is_en else f"Implement monthly dashboard tracking tailored to {sector} priorities.",
                priority="moyenne",
                rationale="La recommandation est basée sur les données observées.",
                category="Gouvernance",
            )
        )

        # 5. Step-by-Step Action Plan
        action_steps = [
            ActionStep(
                step_number=1,
                action=f"Valider l'exactitude des points de données extraits avec l'équipe {sector}." if not is_en else f"Validate extracted data points with the {sector} team.",
                expected_impact="Consolidation de la qualité des données de référence" if not is_en else "Consolidation of baseline data quality",
                owner=job_title,
            ),
            ActionStep(
                step_number=2,
                action=f"Lancer une analyse de cause racine sur la valeur minimale ({stats.minimum:.2f})." if not is_en else f"Initiate root cause analysis on minimum value ({stats.minimum:.2f}).",
                expected_impact="Réduction des écarts de variance et de la fragilité" if not is_en else "Reduction in variance and vulnerability",
                owner=job_title,
            ),
            ActionStep(
                step_number=3,
                action=f"Présenter le plan stratégique et le rapport PDF lors du comité d'arbitrage." if not is_en else "Present strategic plan and PDF report to decision committee.",
                expected_impact="Alignement décisionnel et prise de décision rapide" if not is_en else "Executive alignment and rapid decision-making",
                owner=job_title,
            ),
        ]

        return PersonalizedRecommendations(
            executive_summary=summary,
            key_findings=key_findings,
            priority_recommendations=rec_list,
            opportunities=opportunities,
            risks=risks,
            action_plan=action_steps,
            disclaimer="La recommandation est basée sur les données observées.",
        )
