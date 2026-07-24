"""Data validation and anomaly detection engine inspecting chart data points for errors, duplicates, and inverted axes."""

import logging
from typing import Any
from pydantic import BaseModel, Field

from src.models.chart import ChartExtraction, ExtractedDataPoint

logger = logging.getLogger("DataAnomalyDetector")


class DataAnomalyIssue(BaseModel):
    """Structured representation of a detected chart data anomaly."""

    severity: str = Field(..., description="'WARNING', 'ERROR', or 'CRITICAL'")
    category: str = Field(..., description="'MISSING_VALUE', 'DUPLICATE', 'OUTLIER', 'INVERTED_AXES', 'SUSPICIOUS_OCR'")
    title: str = Field(..., description="Human-readable title")
    message: str = Field(..., description="Detailed description of the anomaly")
    affected_items: list[str] = Field(default_factory=list, description="Labels or values affected")
    suggested_action: str = Field(..., description="Recommended fix or verification action")


class DataValidationResult(BaseModel):
    """Complete validation report summarizing detected anomalies and health score."""

    is_valid: bool = Field(default=True, description="True if no CRITICAL anomalies found")
    data_health_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Health score from 0.0 to 1.0")
    total_anomalies: int = Field(default=0, description="Count of detected anomalies")
    anomalies: list[DataAnomalyIssue] = Field(default_factory=list, description="List of detected anomaly issues")


class DataAnomalyDetector:
    """Engine inspecting ChartExtraction for missing values, outliers, duplicates, and structural anomalies."""

    def __init__(self) -> None:
        pass

    def inspect_extraction(self, extraction: ChartExtraction) -> DataValidationResult:
        """Inspects a ChartExtraction instance for data anomalies.

        Args:
            extraction: Target ChartExtraction object.

        Returns:
            DataValidationResult payload.
        """
        anomalies: list[DataAnomalyIssue] = []
        dps = extraction.data_points or []
        health_score = 1.0

        if not dps:
            anomalies.append(
                DataAnomalyIssue(
                    severity="CRITICAL",
                    category="MISSING_VALUE",
                    title="Aucune Donnée Extrait",
                    message="Le graphique ne contient aucun point de donnée utilisable.",
                    affected_items=[],
                    suggested_action="Vérifier la qualité de l'image importée ou ré-exécuter l'extraction.",
                )
            )
            return DataValidationResult(is_valid=False, data_health_score=0.0, total_anomalies=1, anomalies=anomalies)

        # 1. Missing Values or Unreadable Labels
        unreadable_labels = []
        null_values = []
        for dp in dps:
            if not dp.label or dp.label.strip() in ["[Illisible]", "Unreadable", "N/A", ""]:
                unreadable_labels.append(str(dp.value))
            if dp.value is None or (isinstance(dp.value, float) and (dp.value != dp.value)):
                null_values.append(dp.label or "[Sans nom]")

        if unreadable_labels:
            health_score -= 0.15
            anomalies.append(
                DataAnomalyIssue(
                    severity="WARNING",
                    category="SUSPICIOUS_OCR",
                    title="Libellés Non Reconnus",
                    message=f"{len(unreadable_labels)} libellé(s) n'ont pas pu être lus clairement par l'OCR.",
                    affected_items=unreadable_labels,
                    suggested_action="Éditer manuellement les libellés dans la Grille de Données (HITL).",
                )
            )

        if null_values:
            health_score -= 0.20
            anomalies.append(
                DataAnomalyIssue(
                    severity="ERROR",
                    category="MISSING_VALUE",
                    title="Valeurs Numériques Manquantes",
                    message=f"{len(null_values)} point(s) de donnée ne possèdent pas de valeur numérique valide.",
                    affected_items=null_values,
                    suggested_action="Saisir la valeur numérique correspondante dans la Grille de Données.",
                )
            )

        # 2. Duplicate Labels Check
        labels_seen = set()
        duplicate_labels = set()
        for dp in dps:
            lbl = (dp.label or "").strip().lower()
            if lbl:
                if lbl in labels_seen:
                    duplicate_labels.add(dp.label)
                else:
                    labels_seen.add(lbl)

        if duplicate_labels:
            health_score -= 0.10
            anomalies.append(
                DataAnomalyIssue(
                    severity="WARNING",
                    category="DUPLICATE",
                    title="Libellés En Doublon Détectés",
                    message=f"Libellés en doublon trouvés dans le graphique : {', '.join(duplicate_labels)}.",
                    affected_items=list(duplicate_labels),
                    suggested_action="Vérifier s'il s'agit d'un graphique groupé ou renommer les libellés.",
                )
            )

        # 3. Outlier / Inconsistent Numerical Values Detection
        num_vals = [dp.value for dp in dps if isinstance(dp.value, (int, float))]
        if len(num_vals) >= 4:
            mean = sum(num_vals) / len(num_vals)
            variance = sum((x - mean) ** 2 for x in num_vals) / len(num_vals)
            std_dev = variance ** 0.5

            if std_dev > 0:
                outliers = []
                for dp in dps:
                    if isinstance(dp.value, (int, float)):
                        z_score = abs(dp.value - mean) / std_dev
                        if z_score > 2.5:
                            outliers.append(f"{dp.label}: {dp.value}")

                if outliers:
                    health_score -= 0.15
                    anomalies.append(
                        DataAnomalyIssue(
                            severity="WARNING",
                            category="OUTLIER",
                            title="Valeurs Numériques Extrêmes (Outliers)",
                            message=f"Détection de {len(outliers)} valeur(s) s'écartant fortement de la moyenne ({mean:.2f}).",
                            affected_items=outliers,
                            suggested_action="Vérifier la cohérence de l'échelle ou de la virgule décimale.",
                        )
                    )

        # 4. Check Inverted Axes Heuristic
        # e.g., if numeric values are found in labels and strings are in values
        if any(isinstance(dp.label, (int, float)) for dp in dps):
            health_score -= 0.25
            anomalies.append(
                DataAnomalyIssue(
                    severity="ERROR",
                    category="INVERTED_AXES",
                    title="Suspicion d'Axes Inversés",
                    message="Les libellés contiennent des valeurs numériques brutes.",
                    affected_items=[],
                    suggested_action="Inverser les axes X et Y dans la Grille de Données.",
                )
            )

        health_score = max(0.0, round(health_score, 2))
        is_valid = not any(a.severity == "CRITICAL" for a in anomalies)

        return DataValidationResult(
            is_valid=is_valid,
            data_health_score=health_score,
            total_anomalies=len(anomalies),
            anomalies=anomalies,
        )
