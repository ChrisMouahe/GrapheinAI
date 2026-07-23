"""Analysis Session data models for managing independent chart analysis lifecycles."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.models.chart import (
    AnomalyItem,
    ChartExtraction,
    ConversationTurn,
    InsightItem,
    StatisticalSummary,
)


class SessionStatus(str, Enum):
    """Enumeration of active analysis session states for UI indicator rendering."""

    IDLE = "IDLE"
    EXTRACTING = "EXTRACTING"
    ANALYZED = "ANALYZED"
    INTERPRETED = "INTERPRETED"
    CONVERSATION_ACTIVE = "CONVERSATION_ACTIVE"


class AnalysisSession(BaseModel):
    """Encapsulates complete isolated context for a single chart analysis session."""

    session_id: str = Field(..., description="Unique identifier for the analysis session")
    user_id: str | None = Field(default=None, description="UUID of owning user profile")
    created_at: str = Field(..., description="Timestamp when the session was initialized")
    file_name: str = Field(..., description="Original filename of the target chart image")
    image_path: str = Field(..., description="Disk filepath to the chart image")
    thumbnail_path: str | None = Field(default=None, description="Disk filepath to chart thumbnail")
    chart_type: str = Field(default="bar", description="Detected or user-specified chart type")
    chart_metadata: Any | None = Field(default=None, description="Rich metadata from ChartIntelligenceEngine")
    extraction: ChartExtraction | None = Field(default=None, description="Extracted structured chart tabular data")
    statistics: StatisticalSummary | None = Field(default=None, description="Calculated statistical summary metrics")
    anomalies: list[AnomalyItem] = Field(default_factory=list, description="Detected statistical anomaly items")
    insights: list[InsightItem] = Field(default_factory=list, description="Generated executive chart insights")
    interpretation: str | None = Field(default=None, description="Generated scientific narrative report text")
    conversation_history: list[ConversationTurn] = Field(default_factory=list, description="Isolated multi-turn chatbot history")
    execution_latency: float = Field(default=0.0, description="Processing latency in seconds")
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall validation confidence rating")
    target_language: str = Field(default="fr", description="Target response language ('fr' or 'en')")
    status: SessionStatus = Field(default=SessionStatus.IDLE, description="Current workflow state indicator")
    question_count: int = Field(default=0, description="Number of analytical questions submitted in this session")
    has_pdf: bool = Field(default=False, description="True if ReportLab PDF report has been generated")

    model_config = {"extra": "ignore"}
