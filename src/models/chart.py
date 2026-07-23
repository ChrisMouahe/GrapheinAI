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
    chart_metadata: Any | None = Field(
        default=None, description="Rich metadata from ChartIntelligenceEngine"
    )
    is_out_of_domain: bool = Field(
        default=False, description="True if target question cannot be answered from chart data"
    )

    model_config = {"extra": "ignore"}


from enum import Enum


class QuestionIntent(str, Enum):
    """Categorized question intent classes."""

    LOOKUP = "LOOKUP"
    CALCULATION = "CALCULATION"
    COMPARISON = "COMPARISON"
    TREND = "TREND"
    SUMMARY = "SUMMARY"
    STATISTICS = "STATISTICS"
    INSIGHT = "INSIGHT"
    ANOMALY = "ANOMALY"
    EXPLANATION = "EXPLANATION"
    FORECAST_REQUEST = "FORECAST_REQUEST"
    OTHER = "OTHER"


class ConfidenceLevel(str, Enum):
    """Qualitative user-facing confidence rating."""

    VERY_HIGH = "Très élevée"
    HIGH = "Élevée"
    MEDIUM = "Moyenne"
    LOW = "Faible"


class StatisticalSummary(BaseModel):
    """Descriptive statistical metrics computed over extracted chart data."""

    minimum: float | None = Field(default=None, description="Minimum numeric value")
    maximum: float | None = Field(default=None, description="Maximum numeric value")
    mean: float | None = Field(default=None, description="Arithmetic average mean")
    median: float | None = Field(default=None, description="Median middle value")
    std_dev: float | None = Field(default=None, description="Standard deviation")
    variance: float | None = Field(default=None, description="Statistical variance")
    range_amplitude: float | None = Field(default=None, description="Range (max - min)")
    count: int = Field(default=0, description="Total number of observations")

    model_config = {"extra": "ignore"}


class AnomalyItem(BaseModel):
    """Statistical anomaly detected in chart dataset."""

    anomaly_type: str = Field(..., description="Anomaly classification (spike, drop, outlier, trend_shift)")
    label: str | None = Field(default=None, description="Category or data point label associated")
    value: float | int | None = Field(default=None, description="Observed anomalous value")
    description: str = Field(..., description="Detailed description of the detected anomaly")
    severity: str = Field(default="MEDIUM", description="Severity level (HIGH, MEDIUM, LOW)")
    z_score: float | None = Field(default=None, description="Statistical Z-score if applicable")

    model_config = {"extra": "ignore"}


class InsightItem(BaseModel):
    """Business insight observation grounded strictly in extracted data."""

    category: str = Field(..., description="Insight category (dominance, trend, stability, variance, ratio)")
    statement: str = Field(..., description="Business insight statement")
    evidence: str = Field(..., description="Data-backed evidence supporting the insight")

    model_config = {"extra": "ignore"}


class ConversationTurn(BaseModel):
    """Single turn in a chat session for a loaded chart image."""

    role: str = Field(..., description="Role ('user' or 'assistant')")
    content: str = Field(..., description="Message text content")
    timestamp: float = Field(..., description="Unix timestamp of message")
    intent: QuestionIntent | None = Field(default=None, description="Detected intent if user message")

    model_config = {"extra": "ignore"}


class ConversationalAnalystResult(PipelineResult):
    """Enriched output produced by Conversational AI Chart Analyst assistant."""

    intent: QuestionIntent = Field(default=QuestionIntent.OTHER, description="Detected question intent")
    intent_confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Intent classification confidence score")
    statistics: StatisticalSummary = Field(default_factory=StatisticalSummary, description="Descriptive statistical metrics")
    anomalies: list[AnomalyItem] = Field(default_factory=list, description="Detected statistical anomalies")
    insights: list[InsightItem] = Field(default_factory=list, description="Generated business insights")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH, description="Qualitative confidence rating")
    short_answer: str = Field(default="", description="Concise direct response")
    explanation: str = Field(default="", description="Detailed contextual explanation")
    data_justification: str = Field(default="", description="Data-backed justification")
    conversation_history: list[ConversationTurn] = Field(default_factory=list, description="Chat turn history for session")

