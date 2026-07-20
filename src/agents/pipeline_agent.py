"""Master PipelineAgent orchestrating the end-to-end multimodal ChartQA reasoning pipeline."""

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
    """Master Orchestrator linking ClassifierAgent, RetrievalAgent, ReasoningAgent, and SafeCalculator."""

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
            PipelineResult containing final answer, extracted data, expression, reasoning, and metadata.

        Raises:
            PipelineError: If any step in the pipeline fails unrecoverably.
        """
        if not question or not question.strip():
            raise PipelineError("Question string cannot be empty.")

        # 1. Resolve ChartImage and validate file presence
        if isinstance(image, ChartImage):
            chart_img = image
        else:
            img_p = Path(image)
            chart_img = ChartImage(id=img_p.stem, file_path=img_p)

        chart_img.validate_exists(must_exist=False)

        try:
            # 2. Step 1: ClassifierAgent -> Predict Question Complexity and Chart Type
            logger.info("Running ClassifierAgent...")
            classification_res = self.classifier.predict(
                question=question,
                chart_type="bar",
            )

            # 3. Step 2: RetrievalAgent -> Top-3 RAG Few-shot Examples
            logger.info("Running RetrievalAgent...")
            retrieved_examples = self.retriever.retrieve(
                query=question,
                top_k=3,
            )

            # 4. Step 3: ReasoningAgent (Gemini Flash Vision) -> VLM Reasoning & Formula
            logger.info("Running ReasoningAgent (Gemini Flash Vision)...")
            reasoning_out = self.reasoner.analyze(
                image=chart_img,
                question=question,
                retrieved_examples=retrieved_examples,
                chart_type=classification_res.features.get("chart_type", "bar"),
                complexity=classification_res.complexity,
            )

            # 5. Step 4: SafeCalculator (AST Only) -> Safe Arithmetic Computation
            logger.info("Evaluating expression with SafeCalculator...")
            calc_expr = reasoning_out.calculation_expression
            final_answer = self.calculator.evaluate(calc_expr)

            # 6. Assemble complete PipelineResult
            return PipelineResult(
                final_answer=final_answer,
                extracted_data=reasoning_out.extracted_data,
                calculation_expression=calc_expr,
                reasoning=reasoning_out.reasoning,
                complexity=classification_res,
                retrieved_examples=retrieved_examples,
            )

        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            raise PipelineError(f"Pipeline execution failed: {e}") from e
