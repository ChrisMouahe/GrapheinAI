"""Feature engineering pipeline for ChartQA dataset.

Extracts text-based, semantic, and structural features from questions and chart metadata,
and generates binary targets (SIMPLE vs COMPLEX) for machine learning classification.
"""

import re
from typing import Any
import pandas as pd

from src.models.exceptions import FeatureEngineeringError


class ChartQAFeatureEngineer:
    """Reusable feature engineering and target generation pipeline for ChartQA."""

    MATH_KEYWORDS: list[str] = [
        "difference",
        "diff",
        "average",
        "avg",
        "mean",
        "sum",
        "total",
        "ratio",
        "percentage",
        "percent",
        "%",
        "growth",
        "highest",
        "lowest",
        "max",
        "maximum",
        "min",
        "minimum",
        "compare",
        "compared",
        "increase",
        "decrease",
        "change",
        "rate",
        "more",
        "less",
        "multiplied",
        "divided",
    ]

    KNOWN_CHART_TYPES: list[str] = ["bar", "line", "pie", "scatter"]

    def __init__(self) -> None:
        self.feature_names: list[str] = []

    def extract_question_features(self, question: str) -> dict[str, Any]:
        """Extracts textual, mathematical, and structural features from a single question string."""
        if not isinstance(question, str):
            question = str(question) if question is not None else ""

        q_clean = question.strip().lower()
        words = q_clean.split()
        num_tokens = len(words)
        question_len = len(q_clean)

        # Keyword matching
        keyword_hits = 0
        feature_dict: dict[str, Any] = {}
        for kw in self.MATH_KEYWORDS:
            kw_clean = kw.strip().lower()
            present = 1 if re.search(r"\b" + re.escape(kw_clean) + r"\b", q_clean) or kw_clean in q_clean else 0
            feature_dict[f"has_kw_{kw_clean.replace('%', 'pct')}"] = present
            if present:
                keyword_hits += 1

        feature_dict["question_len"] = question_len
        feature_dict["num_tokens"] = num_tokens
        feature_dict["has_math_keyword"] = 1 if keyword_hits > 0 else 0
        feature_dict["keyword_count"] = keyword_hits
        feature_dict["num_digits"] = len(re.findall(r"\d", q_clean))
        feature_dict["is_question_mark"] = 1 if q_clean.endswith("?") else 0
        feature_dict["avg_word_len"] = (
            sum(len(w) for w in words) / num_tokens if num_tokens > 0 else 0.0
        )

        return feature_dict

    def extract_features_single(self, question: str, chart_type: str = "bar") -> pd.DataFrame:
        """Extracts feature row DataFrame for a single input question and chart type."""
        q_features = self.extract_question_features(question)

        c_type = chart_type.strip().lower() if isinstance(chart_type, str) else "bar"
        for known_type in self.KNOWN_CHART_TYPES:
            q_features[f"chart_type_{known_type}"] = 1 if known_type in c_type else 0

        df_feat = pd.DataFrame([q_features])
        return df_feat

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms a DataFrame containing 'question' and 'chart_type' columns into feature matrix X.

        Args:
            df: DataFrame containing at minimum a 'question' column.

        Returns:
            pd.DataFrame of engineered numerical features.
        """
        if "question" not in df.columns:
            raise FeatureEngineeringError("Input DataFrame missing required column 'question'.")

        records: list[dict[str, Any]] = []
        for idx, row in df.iterrows():
            q_str = str(row["question"])
            c_type = str(row.get("chart_type", "bar"))
            feat = self.extract_question_features(q_str)

            # Chart type encoding
            c_type_clean = c_type.strip().lower()
            for known_type in self.KNOWN_CHART_TYPES:
                feat[f"chart_type_{known_type}"] = 1 if known_type in c_type_clean else 0

            records.append(feat)

        feature_df = pd.DataFrame(records)
        self.feature_names = list(feature_df.columns)
        return feature_df

    def create_binary_target(self, df: pd.DataFrame) -> pd.Series:
        """Generates binary target column (0: SIMPLE, 1: COMPLEX) based on text and dataset rules.

        Rules for COMPLEX (1):
        - Contains arithmetic / comparative keywords OR
        - Question length > 60 chars OR
        - Contains numerical operations or multiple numbers.
        """
        if "question" not in df.columns:
            raise FeatureEngineeringError("Input DataFrame missing required column 'question'.")

        targets: list[int] = []
        for idx, row in df.iterrows():
            q_text = str(row["question"]).lower()
            q_feats = self.extract_question_features(q_text)

            is_complex = (
                q_feats["has_math_keyword"] == 1
                or q_feats["question_len"] > 55
                or q_feats["num_digits"] >= 2
                or "vs" in q_text
                or "difference" in q_text
            )
            targets.append(1 if is_complex else 0)

        return pd.Series(targets, name="target", index=df.index)

    def fit_transform(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """Runs both feature extraction and binary target creation on a dataset."""
        X = self.transform(df)
        y = self.create_binary_target(df)
        return X, y
