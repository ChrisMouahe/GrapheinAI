"""Master PipelineAgent orchestrating the end-to-end multimodal ChartQA reasoning pipeline without mocks."""

import logging
from pathlib import Path
from typing import Any

from src.agents.classifier_agent import ClassifierAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.models.chart import ChartImage, PipelineResult
from src.models.exceptions import PipelineError

logger = logging.getLogger("PipelineAgent")


class PipelineAgent:
    """Master Orchestrator linking ClassifierAgent, RetrievalAgent, ReasoningAgent, and SafeCalculator dynamically."""

    def __init__(
        self,
        classifier_agent: ClassifierAgent | None = None,
        retrieval_agent: RetrievalAgent | None = None,
        reasoning_agent: ReasoningAgent | None = None,
        safe_calculator: SafeCalculator | None = None,
    ) -> None:
        self.classifier = classifier_agent or ClassifierAgent()
        self.retriever = retrieval_agent or RetrievalAgent()
        self.reasoner = reasoning_agent or ReasoningAgent()
        self.calculator = safe_calculator or SafeCalculator()

    def answer(
        self,
        image: ChartImage | Path | str,
        question: str,
    ) -> PipelineResult:
        """Executes full end-to-end multimodal reasoning pipeline over a chart image and question.

        Args:
            image: ChartImage model, Path, or filepath string.
            question: User target question string.

        Returns:
            PipelineResult containing final answer, extracted data, expression, reasoning, initial interpretation, and metadata.

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
            # 1. Step 1: ClassifierAgent -> Predict Question Complexity and Chart Type
            classification_res = self.classifier.predict(
                question=question,
                chart_type="bar",
            )

            # 2. Step 2: RetrievalAgent -> Top-3 RAG Few-shot Examples
            retrieved_examples = self.retriever.retrieve(
                query=question,
                top_k=3,
            )

            # 3. Step 3: ReasoningAgent -> VLM Vision Extraction & Out-of-Domain Check
            reasoning_out = self.reasoner.analyze(
                image=chart_img,
                question=question,
                retrieved_examples=retrieved_examples,
                chart_type=classification_res.features.get("chart_type", "bar"),
                complexity=classification_res.complexity,
            )

            # 4. Handle Out-of-Domain Query Cleanly
            calc_expr = reasoning_out.calculation_expression
            if calc_expr == "UNANSWERABLE" or reasoning_out.is_out_of_domain:
                final_answer = "This question cannot be answered from the provided chart data."
            else:
                # Step 4: SafeCalculator (AST Only) -> Safe Arithmetic Computation
                final_answer = self.calculator.evaluate(calc_expr)

            return PipelineResult(
                final_answer=final_answer,
                extracted_data=reasoning_out.extracted_data,
                calculation_expression=calc_expr,
                reasoning=reasoning_out.reasoning,
                initial_interpretation=reasoning_out.initial_interpretation or "",
                complexity=classification_res,
                retrieved_examples=retrieved_examples,
                is_out_of_domain=reasoning_out.is_out_of_domain,
            )

        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            raise PipelineError(f"Pipeline execution failed: {e}") from e
