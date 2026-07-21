"""Domain models for ChartQA Multimodal Assistant using Pydantic v2."""

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, field_validator

from src.models.exceptions import ChartValidationError


class ExtractedDataPoint(BaseModel):
    """Represents a single data point extracted from a chart image."""

    label: str = Field(..., description="Label or category of the data point")
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

    chart_type: str = Field(
        ..., description="Type of the chart (e.g., bar, line, pie, scatter)"
    )
    title: str | None = Field(default=None, description="Title of the chart")
    x_label: str | None = Field(default=None, description="Label for the X-axis")
    y_label: str | None = Field(default=None, description="Label for the Y-axis")
    data_points: list[ExtractedDataPoint] = Field(
        default_factory=list, description="Extracted key-value data points"
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
    format: str | None = Field(
        default=None, description="Image format (e.g., png, jpg, webp)"
    )

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

    model_config = {"extra": "ignore"}
