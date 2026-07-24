"""Multi-stage confidence calculator evaluating Extraction, OCR, Classification, and Final Answer scores."""

from pydantic import BaseModel, Field
from src.models.chart import PipelineResult


class ConfidenceBreakdown(BaseModel):
    """Multi-stage confidence score breakdown payload."""

    extraction_pct: int = Field(..., ge=0, le=100, description="Extraction confidence score percentage")
    ocr_pct: int = Field(..., ge=0, le=100, description="OCR text recognition confidence percentage")
    classification_pct: int = Field(..., ge=0, le=100, description="Question intent classification confidence percentage")
    final_answer_pct: int = Field(..., ge=0, le=100, description="Final model answer overall confidence percentage")


class ConfidenceCalculator:
    """Computes granular multi-stage confidence percentages across pipeline phases."""

    def __init__(self) -> None:
        pass

    def calculate_confidence(self, pipeline_result: PipelineResult) -> ConfidenceBreakdown:
        """Calculates multi-stage confidence breakdown.

        Args:
            pipeline_result: PipelineResult object.

        Returns:
            ConfidenceBreakdown model.
        """
        # 1. Classification confidence
        classif_conf = pipeline_result.complexity.confidence if pipeline_result.complexity else 0.92
        classif_pct = int(classif_conf * 100) if classif_conf <= 1.0 else int(classif_conf)

        # 2. OCR confidence
        dps = pipeline_result.extracted_data.data_points or []
        unreadable = sum(1 for dp in dps if not dp.label or dp.label == "[Illisible]")
        ocr_ratio = 1.0 - (unreadable / max(1, len(dps)))
        ocr_pct = max(70, int(ocr_ratio * 96))

        # 3. Extraction confidence
        ext_ratio = getattr(pipeline_result.validation_result, "confidence_score", 0.97)
        ext_pct = int(ext_ratio * 100) if ext_ratio <= 1.0 else int(ext_ratio)

        # 4. Final Answer overall confidence
        final_pct = int((classif_pct * 0.2) + (ocr_pct * 0.3) + (ext_pct * 0.5))

        return ConfidenceBreakdown(
            extraction_pct=min(100, max(0, ext_pct)),
            ocr_pct=min(100, max(0, ocr_pct)),
            classification_pct=min(100, max(0, classif_pct)),
            final_answer_pct=min(100, max(0, final_pct)),
        )
