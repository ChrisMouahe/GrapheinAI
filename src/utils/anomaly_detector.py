"""Anomaly Detector module for finding spikes, drops, outliers, and trend breaks in chart data."""

import math
import statistics
from src.models.chart import AnomalyItem, ChartExtraction
from src.utils.stat_calculator import StatisticalEngine


class AnomalyDetector:
    """Detects statistical anomalies, spikes, drops, and trend shifts in chart datasets."""

    @staticmethod
    def detect_anomalies(extraction: ChartExtraction) -> list[AnomalyItem]:
        """Analyzes extraction data points and identifies statistical anomalies."""
        data_points = extraction.data_points
        if len(data_points) < 2:
            return []

        summary = StatisticalEngine.compute_summary(extraction)
        if not summary.mean or summary.std_dev is None:
            return []

        anomalies: list[AnomalyItem] = []
        mean = summary.mean
        std_dev = summary.std_dev

        # 1. Z-Score Outlier Detection
        for dp in data_points:
            try:
                val = float(dp.value)
            except (ValueError, TypeError):
                continue

            z_score = (val - mean) / std_dev if std_dev > 0 else 0.0

            if z_score >= 1.8:
                anomalies.append(
                    AnomalyItem(
                        anomaly_type="spike",
                        label=dp.label,
                        value=val,
                        description=f"Pic exceptionnel pour '{dp.label}' avec la valeur {val} (médiane: {summary.median}, z-score: +{z_score:.2f}).",
                        severity="HIGH" if z_score >= 2.3 else "MEDIUM",
                        z_score=round(z_score, 2),
                    )
                )
            elif z_score <= -1.8:
                anomalies.append(
                    AnomalyItem(
                        anomaly_type="drop",
                        label=dp.label,
                        value=val,
                        description=f"Chute remarquable pour '{dp.label}' avec la valeur {val} (moyenne: {mean:.2f}, z-score: {z_score:.2f}).",
                        severity="HIGH" if z_score <= -2.3 else "MEDIUM",
                        z_score=round(z_score, 2),
                    )
                )

        # 2. Sequential Trend Shift / Sudden Break Detection
        numeric_pts = []
        for dp in data_points:
            try:
                numeric_pts.append((dp.label, float(dp.value)))
            except (ValueError, TypeError):
                pass

        for i in range(1, len(numeric_pts)):
            prev_label, prev_val = numeric_pts[i - 1]
            curr_label, curr_val = numeric_pts[i]

            diff = curr_val - prev_val
            pct_change = (diff / abs(prev_val)) * 100 if prev_val != 0 else 0.0

            if abs(pct_change) >= 40.0 and abs(diff) >= (std_dev * 1.2 if std_dev > 0 else 10):
                direction = "hausse soudaine" if diff > 0 else "chute brute"
                anomalies.append(
                    AnomalyItem(
                        anomaly_type="trend_shift",
                        label=curr_label,
                        value=curr_val,
                        description=f"Rupture de tendance entre '{prev_label}' et '{curr_label}': {direction} de {pct_change:+.1f}% ({prev_val} ➔ {curr_val}).",
                        severity="HIGH" if abs(pct_change) >= 70.0 else "MEDIUM",
                        z_score=None,
                    )
                )

        return anomalies

    @staticmethod
    def format_anomalies_text(anomalies: list[AnomalyItem]) -> str:
        """Formats list of AnomalyItem into readable string for LLM context."""
        if not anomalies:
            return "Anomalies : Aucune anomalie ou rupture de tendance détectée."

        lines = ["Anomalies et ruptures détectées :"]
        for a in anomalies:
            lines.append(f"- [{a.severity}] {a.anomaly_type.upper()}: {a.description}")
        return "\n".join(lines)
