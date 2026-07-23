"""Statistical Engine module for computing descriptive statistics on chart datasets."""

import math
import statistics
from src.models.chart import ChartExtraction, StatisticalSummary


class StatisticalEngine:
    """Calculates descriptive statistical metrics from extracted chart data points."""

    @staticmethod
    def compute_summary(extraction: ChartExtraction) -> StatisticalSummary:
        """Computes StatisticalSummary metrics from a ChartExtraction instance."""
        values = extraction.get_numerical_values()

        if not values:
            return StatisticalSummary(count=0)

        n = len(values)
        val_min = float(min(values))
        val_max = float(max(values))
        val_mean = float(statistics.mean(values))
        val_median = float(statistics.median(values))
        val_range = float(val_max - val_min)

        val_std = float(statistics.stdev(values)) if n > 1 else 0.0
        val_var = float(statistics.variance(values)) if n > 1 else 0.0

        return StatisticalSummary(
            minimum=round(val_min, 4),
            maximum=round(val_max, 4),
            mean=round(val_mean, 4),
            median=round(val_median, 4),
            std_dev=round(val_std, 4),
            variance=round(val_var, 4),
            range_amplitude=round(val_range, 4),
            count=n,
        )

    @staticmethod
    def format_summary_text(summary: StatisticalSummary) -> str:
        """Formats StatisticalSummary into clean readable Markdown/text for LLM prompt context."""
        if summary.count == 0:
            return "Statistiques : Aucune donnée numérique disponible."

        return (
            f"Statistiques du graphique (n={summary.count}) :\n"
            f"- Minimum : {summary.minimum}\n"
            f"- Maximum : {summary.maximum}\n"
            f"- Moyenne : {summary.mean}\n"
            f"- Médiane : {summary.median}\n"
            f"- Écart-type : {summary.std_dev}\n"
            f"- Variance : {summary.variance}\n"
            f"- Amplitude (Max - Min) : {summary.range_amplitude}"
        )
