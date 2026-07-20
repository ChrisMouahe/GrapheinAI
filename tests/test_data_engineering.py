"""Tests for ChartQADataEngineer pipeline."""

from pathlib import Path
import pytest
import pandas as pd

from src.models.exceptions import DataEngineeringError, DataFileNotFoundError
from src.utils.data_engineering import ChartQADataEngineer


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    csv_file = tmp_path / "test_chartqa.csv"
    data = """chart_id,question,answer,chart_type,num_data_points
img_01.png,Q1?,10,bar,4
img_02.png,Q2?,20,line,
img_03.png,Q3?,,bar,6
"""
    csv_file.write_text(data, encoding="utf-8")
    return csv_file


class TestChartQADataEngineer:
    def test_load_data_success(self, sample_csv_path: Path) -> None:
        engineer = ChartQADataEngineer(sample_csv_path)
        df = engineer.load_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["chart_id", "question", "answer", "chart_type", "num_data_points"]

    def test_load_data_file_not_found(self, tmp_path: Path) -> None:
        engineer = ChartQADataEngineer(tmp_path / "missing.csv")
        with pytest.raises(DataFileNotFoundError):
            engineer.load_data()

    def test_load_data_no_path_provided(self) -> None:
        engineer = ChartQADataEngineer()
        with pytest.raises(DataEngineeringError):
            engineer.load_data()

    def test_clean_missing_values(self, sample_csv_path: Path) -> None:
        engineer = ChartQADataEngineer(sample_csv_path)
        engineer.load_data()
        cleaned = engineer.clean_missing_values()

        assert cleaned["num_data_points"].isnull().sum() == 0
        assert cleaned["answer"].isnull().sum() == 0

    def test_convert_types(self, sample_csv_path: Path) -> None:
        engineer = ChartQADataEngineer(sample_csv_path)
        engineer.load_data()
        engineer.clean_missing_values()
        converted = engineer.convert_types()

        assert pd.api.types.is_numeric_dtype(converted["answer"])
        assert pd.api.types.is_numeric_dtype(converted["num_data_points"])

    def test_get_descriptive_stats(self, sample_csv_path: Path) -> None:
        engineer = ChartQADataEngineer(sample_csv_path)
        engineer.load_data()
        engineer.clean_missing_values()
        engineer.convert_types()

        stats = engineer.get_descriptive_stats()
        assert stats["num_rows"] == 3
        assert stats["num_columns"] == 5
        assert "chart_type" in stats["categorical_summary"]

    def test_generate_exploratory_plots(self, sample_csv_path: Path, tmp_path: Path) -> None:
        engineer = ChartQADataEngineer(sample_csv_path)
        engineer.load_data()
        engineer.clean_missing_values()
        engineer.convert_types()

        output_dir = tmp_path / "plots"
        plots = engineer.generate_exploratory_plots(output_dir=output_dir)

        assert len(plots) >= 1
        for plot in plots:
            assert plot.exists()

    def test_operations_without_loading_raise(self) -> None:
        engineer = ChartQADataEngineer()
        with pytest.raises(DataEngineeringError):
            engineer.clean_missing_values()

        with pytest.raises(DataEngineeringError):
            engineer.convert_types()

        with pytest.raises(DataEngineeringError):
            engineer.get_descriptive_stats()

        with pytest.raises(DataEngineeringError):
            engineer.generate_exploratory_plots()
