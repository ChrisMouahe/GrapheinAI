"""Question Intent Classifier module for ChartQA Conversational Analyst."""

import logging
import re
from typing import Any

from src.models.chart import QuestionIntent

logger = logging.getLogger(__name__)


class QuestionIntentClassifier:
    """Classifies user natural language questions into 11 specialized intent categories."""

    def __init__(self) -> None:
        self.rules: list[dict[str, Any]] = [
            {
                "intent": QuestionIntent.CALCULATION,
                "keywords": [
                    "calcule", "calculer", "somme", "total", "moyenne", "différence", "ratio",
                    "pourcentage", "taux", "croissance", "additionne", "soustrait", "multiplie",
                    "divise", "plus grand moins", "écart entre", "average", "sum", "difference",
                    "growth rate", "percentage", "+", "-", "*", "/"
                ],
                "patterns": [
                    r"\b(combien|quel|quelle)\s+est\s+(la\s+somme|le\s+total|la\s+moyenne|la\s+diff[eé]rence)\b",
                    r"\bcalcul(e|er|ation)?\b",
                    r"\b(growth|average|sum|total)\s+rate\b",
                    r"[\d\.]+\s*[\+\-\*/]\s*[\d\.]+"
                ],
                "weight": 1.2
            },
            {
                "intent": QuestionIntent.STATISTICS,
                "keywords": [
                    "statistique", "statistiques", "écart-type", "ecart type", "variance",
                    "médiane", "mediane", "amplitude", "min", "max", "minimum", "maximum",
                    "std dev", "standard deviation", "distribution", "dispersion"
                ],
                "patterns": [
                    r"\b([eé]cart-?type|variance|m[eé]diane|amplitude|distribution)\b",
                    r"\bstatistique(s)?\b"
                ],
                "weight": 1.3
            },
            {
                "intent": QuestionIntent.ANOMALY,
                "keywords": [
                    "anomalie", "anomalies", "pic", "pics", "chute", "chutes", "rupture",
                    "aberrante", "outlier", "soudain", "soudaine", "anormale", "anormal",
                    "drop", "spike", "outliers"
                ],
                "patterns": [
                    r"\b(anomalie|pic|chute|rupture|aberrant|outlier|soudain)\b",
                    r"\bobserve-t-on\s+une\s+anomalie\b"
                ],
                "weight": 1.3
            },
            {
                "intent": QuestionIntent.EXPLANATION,
                "keywords": [
                    "pourquoi", "explication", "expliquer", "cause", "raison", "comment se fait-il",
                    "why", "reason", "explain", "d'où vient"
                ],
                "patterns": [
                    r"\bpourquoi\b",
                    r"\bexpliqu(e|er|ation)\b",
                    r"\bquelle\s+est\s+la\s+raison\b"
                ],
                "weight": 1.25
            },
            {
                "intent": QuestionIntent.COMPARISON,
                "keywords": [
                    "meilleur", "pire", "plus grand", "plus petit", "plus élevé", "moins élevé",
                    "performent le mieux", "performent le moins", "deuxième", "seconde", "troisième",
                    "classer", "rang", "comparer", "comparaison", "best", "worst", "highest", "lowest"
                ],
                "patterns": [
                    r"\b(quel|quels|quelle|quelles)\s+est\s+le\s+(meilleur|pire|plus|moins)\b",
                    r"\bperforment\s+le\s+(mieux|moins)\b",
                    r"\bet\s+le\s+(deuxi[eè]me|troisi[eè]me|suivant)\b",
                    r"\bplus\s+(grand|[eé]lev[eé])\s+que\b"
                ],
                "weight": 1.2
            },
            {
                "intent": QuestionIntent.TREND,
                "keywords": [
                    "tendance", "tendances", "évolution", "evolution", "courbe", "augmente",
                    "diminue", "progression", "déclin", "hausse", "baisse", "trend", "overall trend"
                ],
                "patterns": [
                    r"\b(tendance|evolution|[eé]volution|progression|d[eé]clin)\b",
                    r"\b(augmente|diminue|haussi[eè]re|baissi[eè]re)\b"
                ],
                "weight": 1.15
            },
            {
                "intent": QuestionIntent.SUMMARY,
                "keywords": [
                    "résume", "resumer", "résumé", "décris", "decrire", "description",
                    "aperçu", "vue d'ensemble", "synthèse", "summary", "describe", "overview"
                ],
                "patterns": [
                    r"\b(r[eé]sum(e|er|é)|d[eé]cri(s|re)|synth[eè]se|aper[cç]u)\b",
                    r"\bd[eé]cris\s+ce\s+graphique\b",
                    r"\br[eé]sume\s+ce\s+graphique\b"
                ],
                "weight": 1.2
            },
            {
                "intent": QuestionIntent.INSIGHT,
                "keywords": [
                    "enseignement", "enseignements", "conclusion", "conclure", "remarquez",
                    "remarquer", "ressort", "ressortent", "faits marquants", "key takeaways",
                    "insight", "insights", "valeurs dominantes"
                ],
                "patterns": [
                    r"\b(enseignements?|conclu(sion|re)|remarquez|faits\s+marquants)\b",
                    r"\bque\s+peut-on\s+conclure\b",
                    r"\bquels?\s+[eé]l[eé]ments?\s+ressort(ent)?\b",
                    r"\bquelles?\s+sont\s+les\s+valeurs\s+dominantes\b"
                ],
                "weight": 1.2
            },
            {
                "intent": QuestionIntent.FORECAST_REQUEST,
                "keywords": [
                    "futur", "future", "prédiction", "prediction", "prévoir", "prevoir",
                    "estimation future", "prochain", "prochaine", "forecast", "predict"
                ],
                "patterns": [
                    r"\b(futur|pr[eé]diction|pr[eé]voir|forecast|prochain)\b"
                ],
                "weight": 1.1
            },
            {
                "intent": QuestionIntent.LOOKUP,
                "keywords": [
                    "valeur de", "chiffre de", "combien vaut", "donne moi la valeur",
                    "valeur pour", "combien pour", "lookup", "value of"
                ],
                "patterns": [
                    r"\bquel\s+est\s+le\s+(chiffre|montant|valeur)\s+de\b",
                    r"\bvaleur\s+de\s+[A-Za-z0-9_\-\s]+\b"
                ],
                "weight": 1.0
            }
        ]

    def classify(self, question: str) -> tuple[QuestionIntent, float]:
        """Classifies question into an intent and returns (QuestionIntent, confidence_score)."""
        if not question or not question.strip():
            return QuestionIntent.OTHER, 0.50

        q_clean = question.strip().lower()

        scores: dict[QuestionIntent, float] = {intent: 0.0 for intent in QuestionIntent}

        for rule in self.rules:
            intent = rule["intent"]
            weight = rule["weight"]

            for pattern in rule["patterns"]:
                if re.search(pattern, q_clean, re.IGNORECASE):
                    scores[intent] += 2.5 * weight

            for kw in rule["keywords"]:
                if kw in q_clean:
                    scores[intent] += 1.0 * weight

        best_intent = max(scores, key=lambda k: scores[k])
        best_score = scores[best_intent]

        if best_score == 0.0:
            return QuestionIntent.OTHER, 0.60

        confidence = min(0.99, max(0.65, 0.60 + (best_score / 5.0)))
        logger.info(f"Intent classified: '{question}' -> {best_intent.value} (conf={confidence:.2f})")
        return best_intent, confidence
