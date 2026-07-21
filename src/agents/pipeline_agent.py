"""Master PipelineAgent orchestrating multi-stage research-grade multimodal reasoning."""

import logging
from pathlib import Path
from typing import Any

from src.agents.classifier_agent import ClassifierAgent
from src.agents.graph_interpreter import GraphInterpreter
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.agents.validation_agent import ValidationAgent
from src.models.chart import ChartImage, PipelineResult
from src.models.exceptions import PipelineError
from src.utils.chart_detector import ChartTypeDetector
from src.utils.ocr_engine import OCREngine

logger = logging.getLogger("PipelineAgent")


class PipelineAgent:
    """Master Orchestrator linking Classifier, FAISS Retrieval, OCR Region Engine, Computer Vision Geometry, Guided ReasoningAgent, ValidationAgent, GraphInterpreter, and SafeCalculator."""

    def __init__(
        self,
        classifier_agent: ClassifierAgent | None = None,
        retrieval_agent: RetrievalAgent | None = None,
        reasoning_agent: ReasoningAgent | None = None,
        validation_agent: ValidationAgent | None = None,
        graph_interpreter: GraphInterpreter | None = None,
        safe_calculator: SafeCalculator | None = None,
    ) -> None:
        self.classifier = classifier_agent or ClassifierAgent()
        self.retriever = retrieval_agent or RetrievalAgent()
        self.reasoner = reasoning_agent or ReasoningAgent()
        self.validator = validation_agent or ValidationAgent()
        self.graph_interpreter = graph_interpreter or GraphInterpreter()
        self.calculator = safe_calculator or SafeCalculator()

        self.ocr_engine = OCREngine()
        self.chart_detector = ChartTypeDetector()

    def answer(
        self,
        image: ChartImage | Path | str,
        question: str,
    ) -> PipelineResult:
        """Executes full end-to-end research-grade multimodal reasoning pipeline over a chart image and question.

        Args:
            image: ChartImage model, Path, or filepath string.
            question: User target question string.

        Returns:
            PipelineResult containing final answer, extracted data, expression, reasoning, initial interpretation, validation metrics, and metadata.

        Raises:
            PipelineError: If any step in the pipeline fails unrecoverably.
        """
        if not question or not question.strip():
            raise PipelineError("Question string cannot be empty.")

        if isinstance(image, ChartImage):
            chart_img = image
        else:
            img_p = Path(image)
            chart_img = ChartImage(id=img_p.stem, file_path=img_p)

        chart_img.validate_exists(must_exist=False)
        logger.info(f"Pipeline processing image: '{chart_img.file_path.resolve()}' | Question: '{question}'")

        try:
            # 1. Computer Vision Preprocessing: Detect OCR Text Bounding Boxes & Geometric Chart Structure
            ocr_boxes = self.ocr_engine.detect_ocr_text_boxes(chart_img.file_path)
            structure_info = self.chart_detector.detect_chart_structure(chart_img.file_path)

            # 2. Step 1: ClassifierAgent -> Predict Question Complexity
            classification_res = self.classifier.predict(
                question=question,
                chart_type=structure_info.detected_type,
            )

            # 3. Step 2: RetrievalAgent -> Top-3 RAG Few-shot Examples
            retrieved_examples = self.retriever.retrieve(
                query=question,
                top_k=3,
            )

            # 4. Step 3: ReasoningAgent -> VLM Vision Extraction & Reasoning
            reasoning_out = self.reasoner.analyze(
                image=chart_img,
                question=question,
                retrieved_examples=retrieved_examples,
                chart_type=structure_info.detected_type,
                complexity=classification_res.complexity,
            )

            # 5. Step 4: ValidationAgent -> Cross-Validate OCR, Geometry & VLM Data
            validation_res = self.validator.validate_extraction(
                extraction=reasoning_out.extracted_data,
                structure_info=structure_info,
                ocr_boxes=ocr_boxes,
            )

            # 6. Step 5: Independent GraphInterpreter Agent -> Generate Scientific Report (Accepts ChartExtraction ONLY)
            initial_interp = self.graph_interpreter.interpret_chart(reasoning_out.extracted_data)

            # 7. Step 6: SafeCalculator -> Evaluate Arithmetic AST Expression
            calc_expr = reasoning_out.calculation_expression
            if calc_expr == "UNANSWERABLE" or reasoning_out.is_out_of_domain:
                final_answer = "This question cannot be answered from the provided chart data."
            else:
                final_answer = self.calculator.evaluate(calc_expr)

            return PipelineResult(
                final_answer=final_answer,
                extracted_data=reasoning_out.extracted_data,
                calculation_expression=calc_expr,
                reasoning=reasoning_out.reasoning,
                initial_interpretation=initial_interp,
                complexity=classification_res,
                retrieved_examples=retrieved_examples,
                validation_result=validation_res,
                chart_structure=structure_info,
                is_out_of_domain=reasoning_out.is_out_of_domain,
            )

        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            raise PipelineError(f"Pipeline execution failed: {e}") from e
