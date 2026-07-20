"""ClassifierAgent for classifying ChartQA questions into SIMPLE vs. COMPLEX queries."""

json_import = True
import json
from pathlib import Path
from typing import Any
import joblib
import pandas as pd

from src.models.chart import ClassificationResult
from src.models.exceptions import ModelNotFoundError
from src.utils.feature_engineering import ChartQAFeatureEngineer


class ClassifierAgent:
    """Agent wrapping the trained Machine Learning model for complexity inference."""

    def __init__(
        self,
        model_path: Path | str = "models/best_classifier.joblib",
        metadata_path: Path | str = "models/classifier_metadata.json",
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.model: Any | None = None
        self.feature_names: list[str] = []
        self.feature_engineer = ChartQAFeatureEngineer()

        if self.model_path.exists():
            self.load_model(self.model_path, self.metadata_path)

    def load_model(
        self,
        model_path: Path | str | None = None,
        metadata_path: Path | str | None = None,
    ) -> None:
        """Loads trained ML model and metadata from disk.

        Raises:
            ModelNotFoundError: If model artifact file is missing.
        """
        m_path = Path(model_path) if model_path else self.model_path
        meta_path = Path(metadata_path) if metadata_path else self.metadata_path

        if not m_path.exists():
            raise ModelNotFoundError(f"Trained classifier model not found at: {m_path}")

        self.model = joblib.load(m_path)
        self.model_path = m_path

        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.feature_names = meta.get("feature_names", [])

    def predict(self, question: str, chart_type: str = "bar") -> ClassificationResult:
        """Predicts whether a question is SIMPLE (0) or COMPLEX (1).

        Args:
            question: ChartQA question string.
            chart_type: Type of chart (default: 'bar').

        Returns:
            ClassificationResult containing prediction label, confidence, and feature dictionary.
        """
        if self.model is None:
            # Auto-attempt loading default model if present
            if self.model_path.exists():
                self.load_model()
            else:
                raise ModelNotFoundError(
                    "Classifier model is not loaded. Train and save a model first."
                )

        # 1. Feature extraction
        df_feat = self.feature_engineer.extract_features_single(question, chart_type)

        # 2. Column alignment with trained feature_names
        if self.feature_names:
            for col in self.feature_names:
                if col not in df_feat.columns:
                    df_feat[col] = 0
            df_feat = df_feat[self.feature_names]

        # 3. Model inference
        pred_class = int(self.model.predict(df_feat)[0])
        probabilities = self.model.predict_proba(df_feat)[0]
        confidence = float(probabilities[pred_class])

        complexity_str = "COMPLEX" if pred_class == 1 else "SIMPLE"
        is_complex = pred_class == 1

        return ClassificationResult(
            question=question,
            complexity=complexity_str,
            is_complex=is_complex,
            confidence=confidence,
            features=df_feat.to_dict(orient="records")[0],
        )
