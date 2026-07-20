"""Tests for domain models and exceptions."""

from pathlib import Path
import pytest
from pydantic import ValidationError

from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint
from src.models.exceptions import (
    ChartQAError,
    ChartValidationError,
    ForbiddenASTNodeError,
    SafeCalculatorError,
)


class TestExtractedDataPoint:
    def test_valid_datapoint(self) -> None:
        dp = ExtractedDataPoint(label="Category A", value=100.5, confidence=0.95)
        assert dp.label == "Category A"
        assert dp.value == 100.5
        assert dp.confidence == 0.95

    def test_invalid_confidence_raises(self) -> None:
        with pytest.raises(ValidationError):
            ExtractedDataPoint(label="A", value=10, confidence=1.5)

        with pytest.raises(ValidationError):
            ExtractedDataPoint(label="A", value=10, confidence=-0.1)


class TestChartExtraction:
    def test_valid_chart_extraction(self) -> None:
        dp1 = ExtractedDataPoint(label="A", value=10)
        dp2 = ExtractedDataPoint(label="B", value="20.5")
        dp3 = ExtractedDataPoint(label="C", value="NonNumeric")

        extraction = ChartExtraction(
            chart_type="  BAR  ",
            title="Sample Chart",
            data_points=[dp1, dp2, dp3],
        )

        assert extraction.chart_type == "bar"
        assert extraction.title == "Sample Chart"
        assert extraction.get_numerical_values() == [10.0, 20.5]

    def test_empty_chart_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChartExtraction(chart_type="   ")


class TestChartImage:
    def test_chart_image_conversion_and_validation(self, tmp_path: Path) -> None:
        img_file = tmp_path / "test.png"
        img_file.touch()

        chart_img = ChartImage(id="img_1", file_path=str(img_file), width=800, height=600)
        assert chart_img.file_path == img_file
        assert chart_img.validate_exists(must_exist=True) is True

    def test_nonexistent_image_raises(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "missing.png"
        chart_img = ChartImage(id="img_2", file_path=missing_file)
        assert chart_img.validate_exists(must_exist=False) is False
        with pytest.raises(ChartValidationError):
            chart_img.validate_exists(must_exist=True)


class TestExceptions:
    def test_forbidden_ast_node_error_message(self) -> None:
        err = ForbiddenASTNodeError(node_name="Call")
        assert "Call" in str(err)
        assert issubclass(ForbiddenASTNodeError, SafeCalculatorError)
        assert issubclass(SafeCalculatorError, ChartQAError)
