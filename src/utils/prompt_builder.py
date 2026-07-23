"""PromptBuilder Engine constructing context-aware VLM vision, narrative interpretation, and recommendation prompts."""

from typing import Any
from src.models.chart import ChartExtraction
from src.models.user import UserProfile


SECTOR_CONTEXTS: dict[str, dict[str, str]] = {
    "finance": {
        "title": "Finance & Investor Relations",
        "focus": "Marge financière, rentabilité, ROI, variance budgétaire, flux de trésorerie, et maîtrise des coûts.",
        "jargon": "EBITDA, ROI, variance, Capex, Opex, marge opérationnelle",
    },
    "marketing": {
        "title": "Marketing & Acquisition",
        "focus": "Taux de conversion, coût d'acquisition client (CAC), croissance des ventes, efficacité des campagnes, rétention.",
        "jargon": "CAC, LTV, taux de conversion, ROI campagne, panier moyen",
    },
    "sante": {
        "title": "Santé & Recherche Médicale",
        "focus": "Efficacité clinique, prise en charge patient, prévalence, taux de rémission, sécurité sanitaire.",
        "jargon": "P-value, significativité statistique, cohortes, efficacité clinique",
    },
    "education": {
        "title": "Éducation & Formation",
        "focus": "Taux de réussite, progression des étudiants, complétion des parcours, engagement et assiduité.",
        "jargon": "Percentiles, courbe de Gauss, médiane, taux d'assiduité",
    },
    "telecom": {
        "title": "Télécommunications & Réseaux",
        "focus": "Bande passante, revenu moyen par utilisateur (ARPU), taux de résiliation (churn), capacité réseau.",
        "jargon": "ARPU, Churn, SLA, Latence, Débit binaire",
    },
    "industrie": {
        "title": "Industrie & Production",
        "focus": "Rendement global (OEE), temps d'arrêt machine, débit de production, taux de rebut, chaîne logistique.",
        "jargon": "TRS/OEE, Cadence, Taux de défaut, Temps de cycle",
    },
    "banque": {
        "title": "Banque & Services Financiers",
        "focus": "Gestion des risques de crédit, ratio de solvabilité, marge d'intérêt, encours et liquidités.",
        "jargon": "Ratio NPL, Cost of Risk, Marge d'intérêt nette, Basel III",
    },
    "energie": {
        "title": "Énergie & Transition Écologique",
        "focus": "Consommation électrique, pointe de charge, part du renouvelable, empreinte carbone, efficacité.",
        "jargon": "MWh, Peak Load, Intensité carbone, Rendement",
    },
    "assurance": {
        "title": "Assurance & Gestion des Risques",
        "focus": "Ratio combiné, sinistralité, souscription, primes émises, indemnités versées.",
        "jargon": "Loss Ratio, Combined Ratio, Sinistralité, Prime moyenne",
    },
    "transport": {
        "title": "Transport & Logistique",
        "focus": "Taux de remplissage de la flotte, temps de livraison, consommation de carburant, ponctualité.",
        "jargon": "On-Time Delivery, Tonnes-Km, Coût de revient kilométrique",
    },
    "commerce": {
        "title": "Commerce & E-commerce",
        "focus": "Chiffre d'affaires par m², rotativité des stocks, panier moyen, fréquentation, conversion.",
        "jargon": "GMV, Taux de conversion retail, Panier moyen, Rotativité stock",
    },
    "administration": {
        "title": "Administration & Services Publics",
        "focus": "Exécution budgétaire, délai de traitement, satisfaction citoyenne, efficience du service.",
        "jargon": "Délai moyen de traitement, Taux d'exécution, Qualité de service",
    },
    "autre": {
        "title": "Analytique Générale",
        "focus": "Tendances globales, détection d'anomalies, optimisation opérationnelle, opportunités et risques.",
        "jargon": "Statistiques descriptives, tendances, écarts-types, moyennes",
    },
}


class PromptBuilder:
    """Centralized engine constructing context-aware VLM, interpretation, and recommendation prompts."""

    @staticmethod
    def _normalize_sector_key(sector: str | None) -> str:
        if not sector:
            return "autre"
        s = sector.lower().strip()
        if "finan" in s: return "finance"
        if "mark" in s: return "marketing"
        if "sant" or "med" in s: return "sante"
        if "educ" or "etud" in s: return "education"
        if "telecom" in s: return "telecom"
        if "indus" or "prod" in s: return "industrie"
        if "banq" in s: return "banque"
        if "energ" in s: return "energie"
        if "assur" in s: return "assurance"
        if "trans" or "logis" in s: return "transport"
        if "comm" or "retail" in s: return "commerce"
        if "admin" or "publ" in s: return "administration"
        return "autre"

    @classmethod
    def build_user_context_block(cls, user_profile: UserProfile | None, target_language: str = "fr") -> str:
        """Generates formatted prompt block containing complete user profile parameters and adaptation rules."""
        if not user_profile:
            return """
### CONTEXTE UTILISATEUR & PERSONNALISATION AI ###
- Profil: Utilisateur Standard
- Niveau d'expertise: Intermédiaire
- Style d'explication: Analytique et équilibré
"""

        sect_key = cls._normalize_sector_key(user_profile.secteur_activite)
        sect_meta = SECTOR_CONTEXTS.get(sect_key, SECTOR_CONTEXTS["autre"])
        sect_name = user_profile.secteur_autre if (user_profile.secteur_activite == "Autre" and user_profile.secteur_autre) else user_profile.secteur_activite or "Général"

        exp_level = (user_profile.niveau_expertise or "Intermédiaire").capitalize()
        lang_name = "Anglais" if target_language == "en" else "Français"

        # Define expertise guidance rules
        if exp_level.startswith("Débutant"):
            expertise_guidance = (
                "Fournis des explications claires, pédagogiques et très accessibles. "
                "Évite le jargon technique inutile. Définis brièvement les indicateurs statistiques (moyenne, écart-type). "
                "Utilise des analogies simples et des résumés vulgarisés."
            )
        elif exp_level.startswith("Expert"):
            expertise_guidance = (
                "Rédige une analyse technique et rigoureuse de haut niveau. "
                "Intègre les métriques avancées : variance, distribution, écarts-types, corrélations et détection fine des anomalies. "
                "Utilise un vocabulaire d'analyste senior sans avoir besoin de redéfinir les concepts de base."
            )
        elif exp_level.startswith("Avancé"):
            expertise_guidance = (
                "Fournis une analyse structurée et détaillée. Intègre des métriques statistiques précises "
                "et concentre-toi sur l'interprétation des tendances et de la variabilité des données."
            )
        else:
            expertise_guidance = (
                "Fournis des explications équilibrées, synthétiques et claires, "
                "accompagnées des principales métriques chiffrées."
            )

        return f"""
### CONTEXTE METIER ET PERSONNALISATION AI ###
- Identité: {user_profile.prenom} {user_profile.nom or user_profile.name}
- Entreprise / Organisation: {user_profile.entreprise or 'Non spécifiée'}
- Secteur d'activité: {sect_name} ({sect_meta['title']})
- Poste / Fonction: {user_profile.fonction or 'Analyste / Décideur'}
- Expérience professionnelle: {user_profile.annees_experience or 0} ans
- Niveau d'expertise en Analytics: {exp_level}
- Langue cible: {lang_name}

### ORIENTATION ET STYLE ADAPTÉ AU PROFIL ###
- Foyer d'intérêt sectoriel: {sect_meta['focus']}
- Vocabulaire métier recommandé: {sect_meta['jargon']}
- Consigne de niveau d'expertise ({exp_level}): {expertise_guidance}
- RÈGLE ABSOLUE ANTI-HALLUCINATION ET GARDE-FOU: Toutes les recommandations et conclusions doivent s'appuyer strictement sur les chiffres et faits observés dans le graphique. Tu dois systématiquement rappeler que : "La recommandation est basée sur les données observées." Ne jamais inventer de données.
"""

    @classmethod
    def build_vlm_reasoning_prompt(
        cls,
        question: str,
        chart_type: str,
        extraction: ChartExtraction | None,
        statistics_text: str | None,
        anomalies_text: str | None,
        insights_text: str | None,
        retrieved_examples: list[dict[str, Any]],
        target_language: str = "fr",
        user_profile: UserProfile | None = None,
    ) -> str:
        """Constructs rich VLM prompt with user profile context and adaptation instructions."""
        lang_str = "ENGLISH" if target_language == "en" else "FRENCH"
        context_block = cls.build_user_context_block(user_profile, target_language=target_language)

        prompt_parts: list[str] = [
            "### SYSTEM ROLE ###",
            "Tu es un AI Business Analyst et Copilote Décisionnel Senior. Ton rôle est d'analyser le graphique, d'extraire les faits chiffrés et de fournir des réponses stratégiques personnalisées.",
            f"IMPORTANT: Génère toutes tes explications et raisonnements strictement en {lang_str}.",
            "",
            context_block,
            "",
            "### METADATA QUESTION & INTENT ###",
            f"- Question Cible: {question}",
            f"- Type de Graphique: {chart_type}",
            f"- Langue: {lang_str}",
        ]

        if extraction and extraction.data_points:
            prompt_parts.append("\n### TABLEAU DES DONNÉES EXTRAITES ###")
            for dp in extraction.data_points:
                prompt_parts.append(f"  * Étiquette: '{dp.label}' | Valeur: {dp.value} (Confiance: {dp.confidence:.2f})")

        if statistics_text:
            prompt_parts.append(f"\n### DISTRIBUTION STATISTIQUE CALCULÉE ###\n{statistics_text}")

        if anomalies_text:
            prompt_parts.append(f"\n### ANOMALIES STATISTIQUES DÉTECTÉES ###\n{anomalies_text}")

        if insights_text:
            prompt_parts.append(f"\n### APERÇUS AUTOMATIQUES ###\n{insights_text}")

        if retrieved_examples:
            prompt_parts.append("\n### EXEMPLES DE RAISONNEMENT FAISS RAG ###")
            for idx, ex in enumerate(retrieved_examples, 1):
                prompt_parts.append(f"Exemple {idx}: {ex.get('question', '')} -> {ex.get('answer', '')}")

        prompt_parts.extend([
            "",
            "### REQUIRED JSON OUTPUT SCHEME ###",
            "Réponds strictement au format JSON suivant :",
            "```json",
            "{",
            '  "extracted_data": {',
            f'    "chart_type": "{chart_type}",',
            '    "title": "Titre du graphique ou null",',
            '    "x_label": "Axe X ou null",',
            '    "y_label": "Axe Y ou null",',
            '    "data_points": [{"label": "Étiquette", "value": 100.0, "confidence": 0.95}]',
            "  },",
            '  "reasoning": "Raisonnement étape par étape adapté au profil utilisateur.",',
            '  "calculation_expression": "Formule ou valeur déterministe (ex: 120 + 85) ou phrase de synthèse"',
            "}",
            "```",
        ])

        return "\n".join(prompt_parts)
