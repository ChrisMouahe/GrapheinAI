"""Master PipelineAgent orchestrating multi-stage research-grade conversational multimodal reasoning."""

import logging, time
from pathlib import Path
from typing import Any

from src.agents.classifier_agent import ClassifierAgent
from src.agents.conversation_manager import ConversationManager
from src.agents.graph_interpreter import GraphInterpreter
from src.agents.insight_agent import InsightAgent
from src.agents.intent_classifier import QuestionIntentClassifier
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.agents.validation_agent import ValidationAgent
from src.models.chart import (
    ChartExtraction,
    ChartImage,
    ConfidenceLevel,
    ConversationalAnalystResult,
    PipelineResult,
    QuestionIntent,
)
from src.models.exceptions import PipelineError
from src.utils.anomaly_detector import AnomalyDetector
from src.utils.chart_detector import ChartTypeDetector
from src.utils.ocr_engine import OCREngine
from src.utils.stat_calculator import StatisticalEngine

logger = logging.getLogger("PipelineAgent")


class PipelineAgent:
    """Master Orchestrator linking Intent Classifier, Statistical Engine, Anomaly Detector, Insight Agent, Conversation Manager, FAISS Retrieval, Gemini Vision, and SafeCalculator."""

    def __init__(
        self,
        classifier_agent: ClassifierAgent | None = None,
        retrieval_agent: RetrievalAgent | None = None,
        reasoning_agent: ReasoningAgent | None = None,
        validation_agent: ValidationAgent | None = None,
        graph_interpreter: GraphInterpreter | None = None,
        safe_calculator: SafeCalculator | None = None,
        intent_classifier: QuestionIntentClassifier | None = None,
        insight_agent: InsightAgent | None = None,
        conversation_manager: ConversationManager | None = None,
    ) -> None:
        self.classifier = classifier_agent or ClassifierAgent()
        self.retriever = retrieval_agent or RetrievalAgent()
        self.reasoner = reasoning_agent or ReasoningAgent()
        self.validator = validation_agent or ValidationAgent()
        self.graph_interpreter = graph_interpreter or GraphInterpreter()
        self.calculator = safe_calculator or SafeCalculator()

        self.intent_classifier = intent_classifier or QuestionIntentClassifier()
        self.insight_agent = insight_agent or InsightAgent()
        self.conversation_manager = conversation_manager or ConversationManager()

        self.ocr_engine = OCREngine()
        self.chart_detector = ChartTypeDetector()

    def answer(
        self,
        image: ChartImage | Path | str,
        question: str,
        session_id: str | None = None,
        hitl_extraction: ChartExtraction | None = None,
    ) -> ConversationalAnalystResult:
        """Executes full end-to-end research-grade conversational reasoning pipeline."""
        if not question or not question.strip():
            raise PipelineError("Question string cannot be empty.")

        if isinstance(image, ChartImage):
            chart_img = image
        else:
            img_p = Path(image)
            chart_img = ChartImage(id=img_p.stem, file_path=img_p)

        sid = session_id or chart_img.id
        logger.info(f"Pipeline processing image: '{chart_img.file_path.resolve()}' | Session: '{sid}' | Question: '{question}'")

        try:
            # 1. Classify Intent & Preprocess Image Structure
            intent, intent_conf = self.intent_classifier.classify(question)
            ocr_boxes = self.ocr_engine.detect_ocr_text_boxes(chart_img.file_path)
            structure_info = self.chart_detector.detect_chart_structure(chart_img.file_path)

            # 2. Extract or reuse HITL chart data
            if hitl_extraction and hitl_extraction.data_points:
                extraction = hitl_extraction
            else:
                extraction = self.reasoner.extract_chart_data(chart_img.file_path)

            # 3. Compute Analytics: Statistics, Anomalies, Insights
            stats = StatisticalEngine.compute_summary(extraction)
            stats_text = StatisticalEngine.format_summary_text(stats)
            anomalies = AnomalyDetector.detect_anomalies(extraction)
            anomalies_text = AnomalyDetector.format_anomalies_text(anomalies)
            insights = self.insight_agent.generate_insights(extraction)
            insights_text = InsightAgent.format_insights_text(insights)

            # 4. Format Conversation History Context
            history_text = self.conversation_manager.format_history_prompt(sid)

            # 5. RAG Retrieval & Question Complexity
            classification_res = self.classifier.predict(
                question=question,
                chart_type=structure_info.detected_type,
            )
            retrieved_examples = self.retriever.retrieve(query=question, top_k=3)

            # 6. Intelligent Intent-Based Routing & Execution
            if intent == QuestionIntent.CALCULATION:
                reasoning_out = self.reasoner.analyze(
                    image=chart_img,
                    question=question,
                    retrieved_examples=retrieved_examples,
                    chart_type=structure_info.detected_type,
                    complexity=classification_res.complexity,
                    statistics_text=stats_text,
                    anomalies_text=anomalies_text,
                    insights_text=insights_text,
                    history_text=history_text,
                    intent=intent.value,
                )
                calc_expr = reasoning_out.calculation_expression
                if calc_expr == "UNANSWERABLE" or reasoning_out.is_out_of_domain:
                    final_answer = "Cette question ne peut pas être calculée à partir des données du graphique."
                else:
                    final_answer = self.calculator.evaluate(calc_expr)

                short_ans = f"Résultat du calcul : {final_answer}"
                explanation = f"Calcul basé sur la formule : {calc_expr}."
                data_just = f"Formule évaluée de manière déterministe via SafeCalculator AST sur les données du graphique ({len(extraction.data_points)} points)."

            elif intent == QuestionIntent.STATISTICS:
                calc_expr = f"mean={stats.mean}, min={stats.minimum}, max={stats.maximum}, std={stats.std_dev}"
                final_answer = f"Moyenne: {stats.mean}, Min: {stats.minimum}, Max: {stats.maximum}, Écart-type: {stats.std_dev}"
                short_ans = f"Moyenne de {stats.mean} (Min: {stats.minimum}, Max: {stats.maximum})."
                explanation = f"Distribution statistique calculée sur {stats.count} observations. Écart-type de {stats.std_dev} et amplitude de {stats.range_amplitude}."
                data_just = f"Calculs statistiques exacts effectués en Python : {stats_text}."
                reasoning_out = self.reasoner.analyze(
                    image=chart_img,
                    question=question,
                    retrieved_examples=retrieved_examples,
                    chart_type=structure_info.detected_type,
                    complexity=classification_res.complexity,
                    statistics_text=stats_text,
                    anomalies_text=anomalies_text,
                    insights_text=insights_text,
                    history_text=history_text,
                    intent=intent.value,
                )

            else:
                reasoning_out = self.reasoner.analyze(
                    image=chart_img,
                    question=question,
                    retrieved_examples=retrieved_examples,
                    chart_type=structure_info.detected_type,
                    complexity=classification_res.complexity,
                    statistics_text=stats_text,
                    anomalies_text=anomalies_text,
                    insights_text=insights_text,
                    history_text=history_text,
                    intent=intent.value,
                )
                calc_expr = reasoning_out.calculation_expression
                if calc_expr and calc_expr != "UNANSWERABLE":
                    try:
                        final_answer = self.calculator.evaluate(calc_expr)
                    except Exception:
                        final_answer = reasoning_out.reasoning
                else:
                    final_answer = reasoning_out.reasoning

                short_ans = str(final_answer).split(".")[0] + "." if isinstance(final_answer, str) and final_answer else f"Résultat: {final_answer}"
                explanation = reasoning_out.reasoning
                data_just = f"Analyse guidée par vision Gemini et appuyée par les données extraites ({len(extraction.data_points)} catégories)."

            # 7. ValidationAgent & Scientific Interpretation
            validation_res = self.validator.validate_extraction(
                extraction=extraction,
                structure_info=structure_info,
                ocr_boxes=ocr_boxes,
            )
            initial_interp = self.graph_interpreter.interpret_chart(extraction)

            # Determine Confidence Rating
            if validation_res.overall_confidence >= 0.85:
                conf_level = ConfidenceLevel.VERY_HIGH
            elif validation_res.overall_confidence >= 0.70:
                conf_level = ConfidenceLevel.HIGH
            elif validation_res.overall_confidence >= 0.50:
                conf_level = ConfidenceLevel.MEDIUM
            else:
                conf_level = ConfidenceLevel.LOW

            # 8. Record Multi-Turn Conversation History
            self.conversation_manager.add_user_turn(sid, question, intent=intent)
            self.conversation_manager.add_assistant_turn(sid, str(final_answer))
            history_turns = self.conversation_manager.get_history(sid)

            return ConversationalAnalystResult(
                final_answer=final_answer,
                extracted_data=extraction,
                calculation_expression=calc_expr,
                reasoning=reasoning_out.reasoning,
                initial_interpretation=initial_interp,
                complexity=classification_res,
                retrieved_examples=retrieved_examples,
                validation_result=validation_res,
                chart_structure=structure_info,
                is_out_of_domain=reasoning_out.is_out_of_domain,
                intent=intent,
                intent_confidence=intent_conf,
                statistics=stats,
                anomalies=anomalies,
                insights=insights,
                confidence_level=conf_level,
                short_answer=short_ans,
                explanation=explanation,
                data_justification=data_just,
                conversation_history=history_turns,
            )

        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            raise PipelineError(f"Pipeline execution failed: {e}") from e
