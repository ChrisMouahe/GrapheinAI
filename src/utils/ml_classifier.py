"""Machine Learning training and evaluation pipeline for ChartQA question complexity classification.

Trains XGBoost and RandomForest models, compares performance metrics (Accuracy, Precision, Recall, F1, Confusion Matrix),
and automatically saves the best performing model artifact using joblib.
"""

import json
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from src.models.exceptions import MLModelError
from src.utils.feature_engineering import ChartQAFeatureEngineer


class ChartQAClassifierTrainer:
    """Trainer pipeline for training and evaluating XGBoost and RandomForest classifiers."""

    def __init__(
        self,
        output_dir: Path | str = "models",
        random_state: int = 42,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.random_state = random_state
        self.feature_engineer = ChartQAFeatureEngineer()
        self.best_model: Any | None = None
        self.best_model_name: str | None = None
        self.evaluation_results: dict[str, Any] = {}

    def train_and_evaluate(
        self,
        df: pd.DataFrame,
        test_size: float = 0.25,
    ) -> dict[str, Any]:
        """Runs end-to-end feature extraction, model training, evaluation, comparison, and saving.

        Args:
            df: ChartQA DataFrame containing 'question' and optional 'chart_type' columns.
            test_size: Proportion of test split.

        Returns:
            Dictionary containing metrics for both models and winning model details.
        """
        if df.empty or "question" not in df.columns:
            raise MLModelError("Invalid input DataFrame for training.")

        X, y = self.feature_engineer.fit_transform(df)

        # Ensure balanced or sufficient samples for train/test split
        if len(df) < 4:
            # For small synthetic test sets, duplicate rows for training demonstration
            X = pd.concat([X] * 4, ignore_index=True)
            y = pd.concat([y] * 4, ignore_index=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y if len(np.unique(y)) > 1 else None
        )

        # 1. Train RandomForest (Baseline)
        rf_model = RandomForestClassifier(n_estimators=100, random_state=self.random_state)
        rf_model.fit(X_train, y_train)
        rf_preds = rf_model.predict(X_test)
        rf_metrics = self._calculate_metrics(y_test, rf_preds)

        # 2. Train XGBoost (Primary Model)
        xgb_model = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=self.random_state,
            eval_metric="logloss",
        )
        xgb_model.fit(X_train, y_train)
        xgb_preds = xgb_model.predict(X_test)
        xgb_metrics = self._calculate_metrics(y_test, xgb_preds)

        results = {
            "RandomForest": rf_metrics,
            "XGBoost": xgb_metrics,
            "feature_names": list(X.columns),
        }

        # Select winner based on F1-score then Accuracy
        if xgb_metrics["f1_score"] >= rf_metrics["f1_score"]:
            self.best_model = xgb_model
            self.best_model_name = "XGBoost"
        else:
            self.best_model = rf_model
            self.best_model_name = "RandomForest"

        results["winner"] = self.best_model_name
        self.evaluation_results = results

        # Automatically save best model and metadata
        self.save_model()

        return results

    def _calculate_metrics(self, y_true: np.ndarray | pd.Series, y_pred: np.ndarray) -> dict[str, Any]:
        """Calculates evaluation metrics dictionary."""
        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        cm = confusion_matrix(y_true, y_pred).tolist()

        return {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "confusion_matrix": cm,
        }

    def save_model(self, filename: str = "best_classifier.joblib") -> Path:
        """Saves the best trained model artifact and its metadata JSON file."""
        if self.best_model is None:
            raise MLModelError("No trained model available to save. Run train_and_evaluate() first.")

        model_path = self.output_dir / filename
        joblib.dump(self.best_model, model_path)

        metadata_path = self.output_dir / "classifier_metadata.json"
        metadata = {
            "model_type": self.best_model_name,
            "feature_names": self.evaluation_results.get("feature_names", []),
            "metrics": self.evaluation_results.get(self.best_model_name, {}),
            "all_results": {
                k: v for k, v in self.evaluation_results.items() if k != "feature_names"
            },
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return model_path
