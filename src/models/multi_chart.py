"""Pydantic v2 data models for Multi-Chart Intelligence, Bounding Box Segmentation, and Cross-Chart Fusion."""

from typing import Any
from pydantic import BaseModel, Field

from src.models.chart import ChartExtraction, PipelineResult


class ChartRegion(BaseModel):
    """Bounding box coordinates of a detected chart sub-region."""

    x: int = Field(..., description="Top-left corner X coordinate")
    y: int = Field(..., description="Top-left corner Y coordinate")
    w: int = Field(..., description="Bounding box width")
    h: int = Field(..., description="Bounding box height")


class DetectedChart(BaseModel):
    """Structured metadata and status of a single detected sub-chart in a multi-chart document."""

    chart_id: str = Field(..., description="Unique sub-chart identifier (ex: chart_1, chart_2)")
    chart_index: int = Field(..., description="1-indexed sequence number")
    title: str = Field(default="Graphique Détecté", description="Title or header of the sub-chart")
    chart_type: str = Field(default="bar", description="Detected architecture (ex: bar, line, pie, scatter, radar, heatmap)")
    confidence: float = Field(default=0.95, description="Detection confidence score")
    bbox: ChartRegion = Field(..., description="Bounding box region in original image")
    cropped_image_path: str = Field(default="", description="Path to cropped sub-image artifact")
    data_point_count: int = Field(default=0, description="Count of extracted numerical data points")
    extraction: ChartExtraction | None = Field(default=None, description="Independent ChartExtraction model")


class MultiChartDetectionResult(BaseModel):
    """Complete detection output payload containing all segmented sub-charts."""

    total_charts_detected: int = Field(..., description="Total count of detected charts in the image")
    detected_charts: list[DetectedChart] = Field(default_factory=list, description="List of detected sub-charts")
    image_width: int = Field(default=1920, description="Original image width")
    image_height: int = Field(default=1080, description="Original image height")


class CrossChartComparison(BaseModel):
    """Comparative correlation analysis between two sub-charts."""

    source_chart_id: str = Field(..., description="First chart ID (ex: chart_1)")
    target_chart_id: str = Field(..., description="Second chart ID (ex: chart_2)")
    source_title: str = Field(default="", description="First chart title")
    target_title: str = Field(default="", description="Second chart title")
    comparison_summary: str = Field(..., description="Comparative narrative (ex: Ventes vs Profits)")
    correlation_type: str = Field(default="positive", description="'positive', 'negative', 'divergence', 'neutre'")
    correlation_score: float = Field(default=0.0, description="Statistical correlation score (-1.0 to +1.0)")


class MultiChartPipelineResult(BaseModel):
    """Complete multi-chart processing result containing individual analyses and holistic fusion."""

    session_id: str = Field(..., description="Session identifier")
    detection_result: MultiChartDetectionResult = Field(..., description="Sub-charts detection result")
    individual_results: dict[str, PipelineResult] = Field(default_factory=dict, description="PipelineResult per chart_id")
    cross_chart_comparisons: list[CrossChartComparison] = Field(default_factory=list, description="Cross-chart comparative findings")
    global_summary: str = Field(..., description="Holistic executive briefing fusing all detected charts")
    global_recommendations: list[str] = Field(default_factory=list, description="Consolidated strategic action items")
