"""Chart Taxonomy types and ChartMetadata Pydantic v2 models for ChartIntelligenceEngine."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChartTaxonomyType(str, Enum):
    """Supported 23 chart taxonomy classification types."""

    VERTICAL_BAR = "vertical_bar"
    HORIZONTAL_BAR = "horizontal_bar"
    GROUPED_BAR = "grouped_bar"
    STACKED_BAR = "stacked_bar"
    STACKED_100_BAR = "100_stacked_bar"
    LINE = "line"
    MULTI_LINE = "multi_line"
    AREA = "area"
    STACKED_AREA = "stacked_area"
    SCATTER_PLOT = "scatter_plot"
    BUBBLE_CHART = "bubble_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    RADAR_CHART = "radar_chart"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    BOX_PLOT = "box_plot"
    WATERFALL = "waterfall"
    CANDLESTICK = "candlestick"
    TIMELINE = "timeline"
    MIXED_CHART = "mixed_chart"
    OTHER = "other"


class ChartMetadata(BaseModel):
    """Rich metadata extracted by Computer Vision ChartIntelligenceEngine."""

    chart_type: ChartTaxonomyType = Field(default=ChartTaxonomyType.VERTICAL_BAR, description="Fine-grained chart taxonomy classification")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Overall classification confidence rating")
    orientation: str = Field(default="vertical", description="Chart orientation ('vertical', 'horizontal', 'radial', 'matrix', 'none')")
    number_of_series: int = Field(default=1, ge=1, description="Detected number of data series / categories")
    legend_detected: bool = Field(default=False, description="True if a color legend box is present")
    grid_detected: bool = Field(default=True, description="True if horizontal/vertical grid lines were detected")
    x_axis: dict[str, Any] = Field(default_factory=dict, description="X-axis metadata (label, tick density, numeric status)")
    y_axis: dict[str, Any] = Field(default_factory=dict, description="Y-axis metadata (label, scale range)")
    colors: list[str] = Field(default_factory=list, description="Dominant dominant HEX color palette")
    title: str | None = Field(default=None, description="Extracted chart main title")
    subtitle: str | None = Field(default=None, description="Extracted chart subtitle")
    language_detected: str = Field(default="fr", description="Primary language of text labels ('fr' or 'en')")
    decision_rationale: str = Field(default="", description="Computer Vision rationale supporting classification decision")
    cv_confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Computer Vision heuristic confidence")
    vlm_confidence: float | None = Field(default=None, description="Gemini Vision confidence rating if cross-validated")
    final_decision_source: str = Field(default="Computer Vision Engine", description="Engine producing final decision ('Computer Vision Engine' or 'Gemini Vision VLM')")

    model_config = {"extra": "ignore"}
