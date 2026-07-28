"""RecommendationEngine generating personalized strategic insights using true AI Reasoning."""

import json
import logging
from typing import Any
from pydantic import BaseModel, Field

from src.models.chart import ChartExtraction
from src.models.user import UserProfile
from src.utils.anomaly_detector import AnomalyDetector
from src.utils.stat_calculator import StatisticalEngine, StatisticalSummary

# Importation de l'agent IA pour générer de vraies réponses dynamiques
from src.agents.reasoning_agent import ReasoningAgent

logger = logging.getLogger("RecommendationEngine")

class RecommendationItem(BaseModel):
    id: str = Field(..., description="Unique identifier for recommendation")
    title: str = Field(..., description="Actionable title of the recommendation")
    description: str = Field(..., description="Detailed description and tactical recommendation")
    priority: str = Field(default="haute", description="Priority level ('haute', 'moyenne', 'basse')")
    rationale: str = Field(default="La recommandation est basée sur les données observées.", description="Data justification")
    category: str = Field(default="Strategie", description="Category (ex: Strategie, Performance, Risque)")

class ActionStep(BaseModel):
    step_number: int = Field(..., description="Step sequence number")
    action: str = Field(..., description="Description of the action to execute")
    expected_impact: str = Field(..., description="Expected business or analytical impact")
    owner: str = Field(..., description="Role responsible for execution")

class PersonalizedRecommendations(BaseModel):
    executive_summary: str = Field(..., description="Role-tailored executive summary")
    key_findings: list[str] = Field(default_factory=list, description="Fact-based observations from chart data")
    priority_recommendations: list[RecommendationItem] = Field(default_factory=list, description="Actionable recommendations")
    opportunities: list[str] = Field(default_factory=list, description="Strategic upside opportunities")
    risks: list[str] = Field(default_factory=list, description="Downside risks or anomalies")
    action_plan: list[ActionStep] = Field(default_factory=list, description="Step-by-step next steps for user role")
    disclaimer: str = Field(default="La recommandation est basée sur l'IA et les données du graphique.", description="Mandatory guardrail rationale statement")

class RecommendationEngine:
    """AI Business Analyst Recommendation Engine via Gemini."""

    def __init__(self) -> None:
        self.ai_agent = ReasoningAgent() # Initialisation de l'IA

    def generate_recommendations(
        self,
        extraction: ChartExtraction,
        statistics: StatisticalSummary | None = None,
        anomalies: list[dict[str, Any]] | None = None,
        user_profile: UserProfile | None = None,
        target_language: str = "fr",
    ) -> PersonalizedRecommendations:
        """Génère des recommandations 100% uniques via l'IA en injectant le profil métier."""
        
        # 1. Extraction du contexte ultra-personnalisé
        job_title = (user_profile.fonction if user_profile else "Analyste").strip()
        sector = (user_profile.secteur_activite if user_profile else "Finance").strip()
        expertise = (user_profile.niveau_expertise if user_profile else "Intermédiaire").strip()
        
        stats = statistics or StatisticalEngine.compute_summary(extraction)
        data_json = json.dumps(extraction.model_dump(), ensure_ascii=False)

        # 2. Construction du Super-Prompt pour forcer le sur-mesure
        prompt = f"""
        Tu es un consultant expert en {sector}. Ton client a le profil suivant : 
        - Rôle : {job_title}
        - Niveau d'expertise : {expertise}
        
        Voici les données exactes du graphique qu'il analyse : 
        {data_json}
        
        Moyenne : {stats.mean:.2f} | Max : {stats.maximum:.2f} | Min : {stats.minimum:.2f}
        
        CONTRAINTES ABSOLUES :
        1. Ne fais AUCUNE phrase générique. Tes recommandations doivent utiliser le vocabulaire technique du secteur "{sector}" et s'adresser directement à un "{job_title}".
        2. Propose des stratégies d'optimisation applicables immédiatement dans la réalité de ce métier.
        3. Formate ta réponse UNIQUEMENT en JSON valide respectant exactement la structure suivante, sans aucun texte Markdown autour :
        {{
            "executive_summary": "Résumé de l'impact métier...",
            "key_findings": ["Fait 1", "Fait 2"],
            "priority_recommendations": [
                {{"id": "rec_1", "title": "Titre", "description": "Action", "priority": "haute", "rationale": "Pourquoi", "category": "Strategie"}}
            ],
            "opportunities": ["Opp 1"],
            "risks": ["Risque 1"],
            "action_plan": [
                {{"step_number": 1, "action": "Faire X", "expected_impact": "Impact Y", "owner": "{job_title}"}}
            ],
            "disclaimer": "Analyse générée par IA."
        }}
        """

        # 3. Appel à Gemini pour générer le JSON sur-mesure
        try:
            raw_response = self.ai_agent.gemini_service._call_text_api(prompt, temp=0.4)
            clean_json = self.ai_agent.gemini_service._clean_json(raw_response)
            parsed_data = json.loads(clean_json)
            return PersonalizedRecommendations(**parsed_data)
        except Exception as e:
            logger.error(f"Échec de l'IA pour les recommandations, fallback activé: {e}")
            # Fallback ultra-basique pour ne pas crasher l'app en cas d'erreur IA
            return PersonalizedRecommendations(
                executive_summary=f"Analyse des données pour le secteur {sector}.",
                key_findings=[f"Moyenne de {stats.mean:.2f}"],
                priority_recommendations=[],
                opportunities=[],
                risks=[],
                action_plan=[]
            )