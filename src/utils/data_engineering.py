"""Data engineering module for loading, cleaning, transforming, and visualizing ChartQA benchmark data."""

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.models.exceptions import (
    DataEngineeringError,
    DataFileNotFoundError,
    DataPreprocessingError,
)


class ChartQADataEngineer:
    """Pipeline for loading, cleaning, processing, and analyzing ChartQA datasets."""

    def __init__(self, data_path: Path | str | None = None) -> None:
        self.data_path: Path | None = Path(data_path) if data_path else None
        self.df: pd.DataFrame | None = None

    def load_data(self, file_path: Path | str | None = None) -> pd.DataFrame:
        """Loads a ChartQA CSV file into a pandas DataFrame.

        Args:
            file_path: Optional explicit path to the CSV file.

        Returns:
            Loaded pandas DataFrame.

        Raises:
            DataFileNotFoundError: If the CSV file does not exist.
            DataPreprocessingError: If reading the CSV fails.
        """
        path = Path(file_path) if file_path else self.data_path
        if not path:
            raise DataEngineeringError("No data file path provided.")

        if not path.exists():
            raise DataFileNotFoundError(f"Data file not found at: {path}")

        try:
            self.df = pd.read_csv(path)
            self.data_path = path
            return self.df
        except Exception as e:
            raise DataPreprocessingError(f"Failed to read CSV file: {e}") from e

    def clean_missing_values(
        self,
        df: pd.DataFrame | None = None,
        drop_threshold: float = 0.5,
    ) -> pd.DataFrame:
        """Cleans missing values by filling numerical NAs with median, categorical NAs with mode, or dropping columns.

        Args:
            df: Optional DataFrame to process.
            drop_threshold: Threshold ratio of missing values above which a column is dropped.

        Returns:
            Cleaned pandas DataFrame.
        """
        target_df = df if df is not None else self.df
        if target_df is None:
            raise DataEngineeringError("No DataFrame available to clean. Call load_data() first.")

        cleaned_df = target_df.copy()

        try:
            # Drop columns exceeding drop_threshold
            missing_ratios = cleaned_df.isnull().mean()
            cols_to_drop = missing_ratios[missing_ratios > drop_threshold].index.tolist()
            if cols_to_drop:
                cleaned_df = cleaned_df.drop(columns=cols_to_drop)

            # Fill missing values column by column
            for col in cleaned_df.columns:
                if cleaned_df[col].isnull().sum() > 0:
                    if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                        median_val = cleaned_df[col].median()
                        cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    else:
                        mode_series = cleaned_df[col].mode()
                        fill_val = mode_series[0] if not mode_series.empty else "Unknown"
                        cleaned_df[col] = cleaned_df[col].fillna(fill_val)

            if df is None:
                self.df = cleaned_df

            return cleaned_df
        except Exception as e:
            raise DataPreprocessingError(f"Error during missing value cleaning: {e}") from e

    def convert_types(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        """Converts DataFrame columns to appropriate data types.

        Args:
            df: Optional DataFrame to process.

        Returns:
            DataFrame with coerced types.
        """
        target_df = df if df is not None else self.df
        if target_df is None:
            raise DataEngineeringError("No DataFrame available to convert types.")

        converted_df = target_df.copy()

        try:
            # Coerce numeric columns if possible
            for col in converted_df.columns:
                if "count" in col.lower() or "num" in col.lower() or "val" in col.lower() or "answer" in col.lower():
                    converted_df[col] = pd.to_numeric(converted_df[col], errors="coerce")

                # String columns cleanup
                if pd.api.types.is_object_dtype(converted_df[col]):
                    converted_df[col] = converted_df[col].astype(str).str.strip()

            if df is None:
                self.df = converted_df

            return converted_df
        except Exception as e:
            raise DataPreprocessingError(f"Error converting types: {e}") from e

    def get_descriptive_stats(self, df: pd.DataFrame | None = None) -> dict[str, Any]:
        """Produces comprehensive descriptive statistics for the dataset.

        Returns:
            Dictionary containing row count, column statistics, data types, missing value counts, etc.
        """
        target_df = df if df is not None else self.df
        if target_df is None:
            raise DataEngineeringError("No DataFrame available to calculate statistics.")

        numeric_df = target_df.select_dtypes(include=["number"])
        categorical_df = target_df.select_dtypes(include=["object", "string"])

        stats: dict[str, Any] = {
            "num_rows": len(target_df),
            "num_columns": len(target_df.columns),
            "columns": list(target_df.columns),
            "data_types": {col: str(dtype) for col, dtype in target_df.dtypes.items()},
            "missing_values": target_df.isnull().sum().to_dict(),
            "numeric_summary": numeric_df.describe().to_dict() if not numeric_df.empty else {},
            "categorical_summary": {
                col: {
                    "unique_values": categorical_df[col].nunique(),
                    "top_value": categorical_df[col].mode()[0] if not categorical_df[col].empty else None,
                }
                for col in categorical_df.columns
            },
        }

        return stats

    def generate_exploratory_plots(
        self,
        df: pd.DataFrame | None = None,
        output_dir: Path | str = "data/processed/plots",
    ) -> list[Path]:
        """Generates exploratory visualizations from the dataset and saves them to disk.

        Args:
            df: Optional DataFrame to visualize.
            output_dir: Directory where plot PNG images will be saved.

        Returns:
            List of file Paths to generated plot images.
        """
        target_df = df if df is not None else self.df
        if target_df is None:
            raise DataEngineeringError("No DataFrame available to generate plots.")

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        generated_plots: list[Path] = []

        # Setting styling
        sns.set_theme(style="whitegrid", palette="muted")

        # 1. Chart Type distribution plot (if 'chart_type' column exists)
        if "chart_type" in target_df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            type_counts = target_df["chart_type"].value_counts()
            sns.barplot(x=type_counts.index, y=type_counts.values, ax=ax, hue=type_counts.index, legend=False)
            ax.set_title("Distribution of Chart Types in ChartQA Benchmark", fontsize=14, fontweight="bold")
            ax.set_xlabel("Chart Type", fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            plt.tight_layout()
            
            plot_file = out_path / "chart_type_distribution.png"
            plt.savefig(plot_file, dpi=150)
            plt.close(fig)
            generated_plots.append(plot_file)

        # 2. Numerical distributions (if any numeric column exists)
        numeric_cols = target_df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.histplot(target_df[col].dropna(), kde=True, ax=ax, color="#4C72B0")
            ax.set_title(f"Distribution of {col}", fontsize=14, fontweight="bold")
            ax.set_xlabel(col, fontsize=12)
            ax.set_ylabel("Frequency", fontsize=12)
            plt.tight_layout()

            plot_file = out_path / f"dist_{col}.png"
            plt.savefig(plot_file, dpi=150)
            plt.close(fig)
            generated_plots.append(plot_file)

        return generated_plots
