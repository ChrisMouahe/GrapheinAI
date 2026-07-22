"""Insight Agent module for generating data-backed business insights from chart extractions."""

import logging
from src.models.chart import ChartExtraction, InsightItem
from src.utils.anomaly_detector import AnomalyDetector
from src.utils.stat_calculator import StatisticalEngine

logger = logging.getLogger(__name__)


class InsightAgent:
    """Generates rigorous, data-backed business insights and observations from chart data."""

    def generate_insights(self, extraction: ChartExtraction) -> list[InsightItem]:
        """Analyzes chart data and returns a list of InsightItem objects."""
        data_points = extraction.data_points
        if not data_points:
            return []

        insights: list[InsightItem] = []
        summary = StatisticalEngine.compute_summary(extraction)
        anomalies = AnomalyDetector.detect_anomalies(extraction)

        values = extraction.get_numerical_values()
        if not values or summary.count == 0:
            return []

        total_sum = sum(values)

        # 1. Dominance / Highest Value Insight
        sorted_points = sorted(
            [dp for dp in data_points if isinstance(dp.value, (int, float))],
            key=lambda x: float(x.value),
            reverse=True,
        )

        if sorted_points:
            top = sorted_points[0]
            top_val = float(top.value)
            share_pct = (top_val / total_sum * 100) if total_sum > 0 else 0.0

            if share_pct >= 35.0 and len(sorted_points) > 1:
                insights.append(
                    InsightItem(
                        category="dominance",
                        statement=f"La catégorie '{top.label}' domine largement le graphique.",
                        evidence=f"Valeur de {top_val} représentant {share_pct:.1f}% de la somme totale.",
                    )
                )

        # 2. Ranking & Spread Insight
        if len(sorted_points) >= 2:
            top = sorted_points[0]
            bottom = sorted_points[-1]
            gap = float(top.value) - float(bottom.value)
            ratio = (float(top.value) / float(bottom.value)) if float(bottom.value) > 0 else None

            if ratio and ratio >= 1.5:
                insights.append(
                    InsightItem(
                        category="ratio",
                        statement=f"Un écart significatif sépare le produit/catégorie leader du plus faible.",
                        evidence=f"'{top.label}' ({top.value}) est {ratio:.1f}x plus élevé que '{bottom.label}' ({bottom.value}), avec un écart de {gap:.2f}.",
                    )
                )
            elif summary.range_amplitude and summary.mean and (summary.range_amplitude / summary.mean) <= 0.25:
                insights.append(
                    InsightItem(
                        category="stability",
                        statement="Les valeurs observées présentent une grande stabilité d'ensemble.",
                        evidence=f"Amplitude globale faible de {summary.range_amplitude:.2f} pour une moyenne de {summary.mean:.2f}.",
                    )
                )

        # 3. Trend Direction Insight (for Sequential / Line Data)
        if len(values) >= 3:
            increases = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
            decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i - 1])

            if increases >= len(values) - 1:
                insights.append(
                    InsightItem(
                        category="trend",
                        statement="Le graphique affiche une tendance haussière continue.",
                        evidence=f"Progression ininterrompue de {values[0]} jusqu'à {values[-1]}.",
                    )
                )
            elif decreases >= len(values) - 1:
                insights.append(
                    InsightItem(
                        category="trend",
                        statement="Le graphique affiche une tendance baissière régulière.",
                        evidence=f"Déclin ininterrompu de {values[0]} jusqu'à {values[-1]}.",
                    )
                )

        # 4. Anomaly-Driven Insights
        for anomaly in anomalies:
            insights.append(
                InsightItem(
                    category="anomaly",
                    statement=f"Observation d'une anomalie notable ({anomaly.anomaly_type.upper()}).",
                    evidence=anomaly.description,
                )
            )

        return insights

    @staticmethod
    def format_insights_text(insights: list[InsightItem]) -> str:
        """Formats list of InsightItem into readable Markdown string."""
        if not insights:
            return "Enseignements (Insights) : Aucune observation particulière."

        lines = ["Principaux enseignements analytiques (Insights) :"]
        for idx, item in enumerate(insights, 1):
            lines.append(f"{idx}. {item.statement} — [Preuve: {item.evidence}]")
        return "\n".join(lines)
