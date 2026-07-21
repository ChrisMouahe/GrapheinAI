"""Domain models for ChartQA Research-Grade Multimodal Assistant using Pydantic v2."""

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator

from src.models.exceptions import ChartValidationError


class OCRTextBox(BaseModel):
    """Represents a text region detected by OpenCV OCR processing."""

    text: str | None = Field(default=None, description="Extracted text string or None if unreadable")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="OCR confidence score")
    box: list[int] = Field(default_factory=lambda: [0, 0, 0, 0], description="Bounding box coordinates [x, y, w, h]")
    region: str = Field(default="plot", description="Region type: title, x_axis, y_axis, legend, plot")

    model_config = {"extra": "ignore"}


class ChartStructureInfo(BaseModel):
    """Represents geometric visual structure detected by OpenCV computer vision."""

    detected_type: str = Field(..., description="Detected visual type (bar, grouped_bar, line, pie, scatter)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Geometric detection confidence score")
    has_x_axis: bool = Field(default=True, description="True if X axis line detected")
    has_y_axis: bool = Field(default=True, description="True if Y axis line detected")
    has_legend: bool = Field(default=False, description="True if legend box detected")
    geometry_features: dict[str, Any] = Field(default_factory=dict, description="Visual contour and geometry features")

    model_config = {"extra": "ignore"}


class ValidationResult(BaseModel):
    """Represents cross-validation metrics comparing OCR, Computer Vision, and VLM outputs."""

    ocr_accuracy: float = Field(default=1.0, ge=0.0, le=1.0, description="Estimated OCR detection accuracy")
    extraction_accuracy: float = Field(default=1.0, ge=0.0, le=1.0, description="Estimated visual extraction accuracy")
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Combined pipeline confidence score")
    requires_human_confirmation: bool = Field(
        default=False, description="True if overall_confidence < 0.70 requiring HITL confirmation"
    )
    validation_notes: list[str] = Field(default_factory=list, description="Validation audit observations")

    model_config = {"extra": "ignore"}


class ExtractedDataPoint(BaseModel):
    """Represents a single data point extracted from a chart image."""

    label: str | None = Field(default=None, description="Label or category of the data point, or None if unreadable")
    value: float | int | str = Field(..., description="Value associated with the label")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the extraction between 0.0 and 1.0",
    )

    model_config = {"frozen": False, "extra": "forbid"}


class ChartExtraction(BaseModel):
    """Represents structured tabular or numerical data extracted from a chart."""

    chart_type: str = Field(..., description="Type of the chart (e.g., bar, line, pie, scatter)")
    title: str | None = Field(default=None, description="Title of the chart")
    x_label: str | None = Field(default=None, description="Label for the X-axis")
    y_label: str | None = Field(default=None, description="Label for the Y-axis")
    data_points: list[ExtractedDataPoint] = Field(
        default_factory=list, description="Extracted key-value data points"
    )
    extraction_source: str = Field(
        default="OpenCV OCR + Gemini Flash Vision",
        description="Source of visual extraction",
    )
    ocr_boxes: list[OCRTextBox] = Field(
        default_factory=list, description="Pre-extracted OCR text bounding boxes"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional contextual metadata"
    )

    @field_validator("chart_type")
    @classmethod
    def validate_chart_type(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not cleaned:
            raise ValueError("chart_type cannot be empty")
        return cleaned

    def get_numerical_values(self) -> list[float]:
        """Returns all numerical values from extracted data points."""
        values: list[float] = []
        for dp in self.data_points:
            if isinstance(dp.value, (int, float)):
                values.append(float(dp.value))
            elif isinstance(dp.value, str):
                try:
                    values.append(float(dp.value))
                except ValueError:
                    pass
        return values

    model_config = {"extra": "ignore"}


class ChartImage(BaseModel):
    """Represents chart image metadata and file handle."""

    id: str = Field(..., description="Unique identifier for the chart image")
    file_path: Path = Field(..., description="Path to the chart image file")
    width: int | None = Field(default=None, ge=1, description="Width in pixels")
    height: int | None = Field(default=None, ge=1, description="Height in pixels")
    format: str | None = Field(default=None, description="Image format (e.g., png, jpg, webp)")

    @field_validator("file_path")
    @classmethod
    def convert_path(cls, v: Path | str) -> Path:
        return Path(v)

    def validate_exists(self, must_exist: bool = False) -> bool:
        """Verifies if the file path exists on disk."""
        exists = self.file_path.exists()
        if must_exist and not exists:
            raise ChartValidationError(f"Chart image file not found: {self.file_path}")
        return exists

    model_config = {"extra": "ignore"}


class ClassificationResult(BaseModel):
    """Represents the output of the question complexity classifier."""

    question: str = Field(..., description="Target question text")
    complexity: str = Field(..., description="Complexity classification ('SIMPLE' or 'COMPLEX')")
    is_complex: bool = Field(..., description="True if question is COMPLEX, False if SIMPLE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction probability confidence")
    features: dict[str, Any] = Field(default_factory=dict, description="Engineered features used for prediction")

    model_config = {"extra": "ignore"}


class RAGRetrievalResult(BaseModel):
    """Represents top-k vector retrieval output from RAG pipeline."""

    query: str = Field(..., description="User search query")
    top_k: int = Field(..., ge=1, description="Number of results requested")
    results: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved top-k items with scores")

    model_config = {"extra": "ignore"}


class ReasoningOutput(BaseModel):
    """Represents structured JSON output produced by Gemini Flash Vision ReasoningAgent."""

    extracted_data: ChartExtraction = Field(..., description="Extracted chart data points and metadata")
    reasoning: str = Field(..., description="Step-by-step reasoning explaining the logic")
    calculation_expression: str = Field(..., description="Arithmetic expression to be evaluated by SafeCalculator")
    initial_interpretation: str | None = Field(
        default=None, description="Automatic professional scientific narrative interpretation of the chart"
    )
    is_out_of_domain: bool = Field(
        default=False, description="True if target question cannot be answered from the chart data"
    )
    chart_structure: ChartStructureInfo | None = Field(
        default=None, description="Detected geometric chart structure info"
    )

    model_config = {"extra": "ignore"}


class PipelineResult(BaseModel):
    """Represents the final output of the master PipelineAgent multimodal reasoning orchestrator."""

    final_answer: float | int | str = Field(..., description="Final calculated answer")
    extracted_data: ChartExtraction = Field(..., description="Extracted chart data points")
    calculation_expression: str = Field(..., description="Arithmetic expression evaluated by SafeCalculator")
    reasoning: str = Field(..., description="Step-by-step reasoning text")
    initial_interpretation: str = Field(
        default="", description="Automatic scientific narrative interpretation of the graphic"
    )
    complexity: ClassificationResult = Field(..., description="ML complexity classification metadata")
    retrieved_examples: list[dict[str, Any]] = Field(
        default_factory=list, description="Few-shot RAG context examples used"
    )
    validation_result: ValidationResult = Field(
        default_factory=ValidationResult, description="Cross-validation metrics and confidence score"
    )
    chart_structure: ChartStructureInfo | None = Field(
        default=None, description="Geometric computer vision structure info"
    )
    is_out_of_domain: bool = Field(
        default=False, description="True if target question cannot be answered from chart data"
    )

    model_config = {"extra": "ignore"}
