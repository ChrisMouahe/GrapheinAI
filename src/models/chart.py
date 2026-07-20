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
