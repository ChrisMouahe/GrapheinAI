"""Domain exceptions for the ChartQA Multimodal Assistant."""


class ChartQAError(Exception):
    """Base exception for all ChartQA domain errors."""

    pass


class SafeCalculatorError(ChartQAError):
    """Base exception for SafeCalculator errors."""

    pass


class InvalidExpressionError(SafeCalculatorError):
    """Raised when an expression has invalid syntax or cannot be parsed."""

    pass


class ForbiddenASTNodeError(SafeCalculatorError):
    """Raised when an AST node is prohibited for security reasons."""

    def __init__(self, node_name: str, message: str | None = None) -> None:
        self.node_name = node_name
        msg = message or f"Forbidden AST node type detected: '{node_name}'"
        super().__init__(msg)


class DivisionByZeroCalcError(SafeCalculatorError):
    """Raised when division by zero is attempted in SafeCalculator."""

    pass


class DataEngineeringError(ChartQAError):
    """Base exception for data engineering errors."""

    pass


class DataFileNotFoundError(DataEngineeringError):
    """Raised when the specified ChartQA data file cannot be found."""

    pass


class DataPreprocessingError(DataEngineeringError):
    """Raised when data preprocessing or cleaning fails."""

    pass


class ChartValidationError(ChartQAError):
    """Raised when chart data validation fails."""

    pass


class FeatureEngineeringError(ChartQAError):
    """Raised when feature extraction fails."""

    pass


class MLModelError(ChartQAError):
    """Base exception for ML classifier errors."""

    pass


class ModelNotFoundError(MLModelError):
    """Raised when a trained model artifact is not found."""

    pass


class EmbeddingGenerationError(ChartQAError):
    """Raised when embedding generation fails."""

    pass


class RAGPipelineError(ChartQAError):
    """Base exception for RAG pipeline errors."""

    pass


class VectorSearchError(RAGPipelineError):
    """Raised when FAISS vector search fails."""

    pass


class VLMReasoningError(ChartQAError):
    """Base exception for VLM Reasoning Agent errors."""

    pass


class InvalidVLMOutputError(VLMReasoningError):
    """Raised when VLM output fails JSON validation or Pydantic parsing."""

    pass


class PipelineError(ChartQAError):
    """Raised when the master orchestration pipeline encounters an unrecoverable error."""

    pass
