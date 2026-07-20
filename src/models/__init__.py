"""Domain models and exceptions for ChartQA Multimodal Assistant."""

from src.models.chart import (
    ChartExtraction,
    ChartImage,
    ClassificationResult,
    ExtractedDataPoint,
    RAGRetrievalResult,
)
from src.models.exceptions import (
    ChartQAError,
    ChartValidationError,
    DataEngineeringError,
    DataFileNotFoundError,
    DataPreprocessingError,
    DivisionByZeroCalcError,
    EmbeddingGenerationError,
    FeatureEngineeringError,
    ForbiddenASTNodeError,
    InvalidExpressionError,
    MLModelError,
    ModelNotFoundError,
    RAGPipelineError,
    SafeCalculatorError,
    VectorSearchError,
)

__all__ = [
    "ChartImage",
    "ChartExtraction",
    "ExtractedDataPoint",
    "ClassificationResult",
    "RAGRetrievalResult",
    "ChartQAError",
    "SafeCalculatorError",
    "InvalidExpressionError",
    "ForbiddenASTNodeError",
    "DivisionByZeroCalcError",
    "DataEngineeringError",
    "DataFileNotFoundError",
    "DataPreprocessingError",
    "ChartValidationError",
    "FeatureEngineeringError",
    "MLModelError",
    "ModelNotFoundError",
    "EmbeddingGenerationError",
    "RAGPipelineError",
    "VectorSearchError",
]
