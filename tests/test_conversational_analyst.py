"""Comprehensive test suite for Conversational AI Chart Analyst feature."""

from pathlib import Path
import pytest

from src.agents.conversation_manager import ConversationManager
from src.agents.insight_agent import InsightAgent
from src.agents.intent_classifier import QuestionIntentClassifier
from src.agents.pipeline_agent import PipelineAgent
from src.models.chart import (
    ChartExtraction,
    ConfidenceLevel,
    ExtractedDataPoint,
    QuestionIntent,
)
from src.utils.anomaly_detector import AnomalyDetector
from src.utils.stat_calculator import StatisticalEngine


@pytest.fixture
def sample_chart_extraction() -> ChartExtraction:
    """Fixture providing a standard test chart extraction (Sousse, Tunis, Nabeul, Bizerte, Sfax)."""
    return ChartExtraction(
        chart_type="bar",
        title="Chiffre d'affaires estimé par ville",
        x_label="Ville",
        y_label="Chiffre d'affaires (milliers TND)",
        data_points=[
            ExtractedDataPoint(label="Sousse", value=53.0, confidence=0.99),
            ExtractedDataPoint(label="Tunis", value=46.0, confidence=0.99),
            ExtractedDataPoint(label="Nabeul", value=38.0, confidence=0.99),
            ExtractedDataPoint(label="Bizerte", value=32.0, confidence=0.99),
            ExtractedDataPoint(label="Sfax", value=29.0, confidence=0.99),
        ],
        extraction_source="Test Fixture",
    )


@pytest.fixture
def anomalous_chart_extraction() -> ChartExtraction:
    """Fixture providing a dataset with a spike anomaly and drop."""
    return ChartExtraction(
        chart_type="line",
        title="Ventes mensuelles 2026",
        data_points=[
            ExtractedDataPoint(label="Janvier", value=100.0, confidence=0.95),
            ExtractedDataPoint(label="Février", value=110.0, confidence=0.95),
            ExtractedDataPoint(label="Mars", value=105.0, confidence=0.95),
            ExtractedDataPoint(label="Avril", value=450.0, confidence=0.95),  # Spike
            ExtractedDataPoint(label="Mai", value=40.0, confidence=0.95),    # Drop / Trend Shift
        ],
        extraction_source="Test Fixture Anomaly",
    )


class TestQuestionIntentClassifier:
    """Tests for QuestionIntentClassifier."""

    def setup_method(self) -> None:
        self.classifier = QuestionIntentClassifier()

    def test_classify_calculation(self) -> None:
        intent, conf = self.classifier.classify("Quelle est la somme des ventes ?")
        assert intent == QuestionIntent.CALCULATION
        assert conf >= 0.70

    def test_classify_comparison(self) -> None:
        intent, _ = self.classifier.classify("Quel est le meilleur produit et lequel performe le moins ?")
        assert intent == QuestionIntent.COMPARISON

    def test_classify_trend(self) -> None:
        intent, _ = self.classifier.classify("Quelle tendance observe-t-on sur cette courbe ?")
        assert intent == QuestionIntent.TREND

    def test_classify_summary(self) -> None:
        intent, _ = self.classifier.classify("Décris et résume ce graphique en détail.")
        assert intent == QuestionIntent.SUMMARY

    def test_classify_statistics(self) -> None:
        intent, _ = self.classifier.classify("Quel est l'écart-type et la variance des données ?")
        assert intent == QuestionIntent.STATISTICS

    def test_classify_anomaly(self) -> None:
        intent, _ = self.classifier.classify("Observe-t-on un pic ou une anomalie sur le graphique ?")
        assert intent == QuestionIntent.ANOMALY

    def test_classify_explanation(self) -> None:
        intent, _ = self.classifier.classify("Pourquoi la valeur augmente-t-elle subitement ?")
        assert intent == QuestionIntent.EXPLANATION


class TestStatisticalEngine:
    """Tests for StatisticalEngine."""

    def test_compute_summary(self, sample_chart_extraction: ChartExtraction) -> None:
        summary = StatisticalEngine.compute_summary(sample_chart_extraction)
        assert summary.count == 5
        assert summary.minimum == 29.0
        assert summary.maximum == 53.0
        assert summary.mean == 39.6
        assert summary.median == 38.0
        assert summary.range_amplitude == 24.0
        assert summary.std_dev > 0.0

    def test_format_summary_text(self, sample_chart_extraction: ChartExtraction) -> None:
        summary = StatisticalEngine.compute_summary(sample_chart_extraction)
        text = StatisticalEngine.format_summary_text(summary)
        assert "Minimum : 29.0" in text
        assert "Maximum : 53.0" in text
        assert "Moyenne : 39.6" in text


class TestAnomalyDetector:
    """Tests for AnomalyDetector."""

    def test_detect_anomalies(self, anomalous_chart_extraction: ChartExtraction) -> None:
        anomalies = AnomalyDetector.detect_anomalies(anomalous_chart_extraction)
        assert len(anomalies) >= 1
        anomaly_types = [a.anomaly_type for a in anomalies]
        assert "spike" in anomaly_types or "trend_shift" in anomaly_types


class TestInsightAgent:
    """Tests for InsightAgent."""

    def test_generate_insights(self, sample_chart_extraction: ChartExtraction) -> None:
        agent = InsightAgent()
        insights = agent.generate_insights(sample_chart_extraction)
        assert len(insights) >= 1
        categories = [item.category for item in insights]
        assert "dominance" in categories or "ratio" in categories


class TestConversationManager:
    """Tests for ConversationManager multi-turn tracking."""

    def test_multi_turn_history(self) -> None:
        mgr = ConversationManager(max_history_turns=5)
        sid = "session_test_123"

        mgr.add_user_turn(sid, "Quel est le meilleur produit?", intent=QuestionIntent.COMPARISON)
        mgr.add_assistant_turn(sid, "Le meilleur produit est Sousse avec 53k TND.")

        mgr.add_user_turn(sid, "Et le deuxième?", intent=QuestionIntent.COMPARISON)
        mgr.add_assistant_turn(sid, "Le deuxième produit est Tunis avec 46k TND.")

        history = mgr.get_history(sid)
        assert len(history) == 4
        assert history[0].content == "Quel est le meilleur produit?"
        assert history[2].content == "Et le deuxième?"

        prompt_str = mgr.format_history_prompt(sid)
        assert "Sousse avec 53k TND" in prompt_str
        assert "Et le deuxième?" in prompt_str


class TestConversationalPipelineAgent:
    """Integration test for Conversational PipelineAgent."""

    def test_end_to_end_conversational_answer(self, sample_chart_extraction: ChartExtraction) -> None:
        pipeline = PipelineAgent()
        sample_img = Path("data/raw/sample_chart.png")
        if not sample_img.exists():
            sample_img.parent.mkdir(parents=True, exist_ok=True)
            # Create dummy file
            sample_img.write_bytes(b"\x89PNG\r\n\x1a\n")

        res = pipeline.answer(
            image=sample_img,
            question="Quels sont les principaux enseignements de ce graphique ?",
            session_id="test_session_e2e",
            hitl_extraction=sample_chart_extraction,
        )

        assert res.intent in [QuestionIntent.INSIGHT, QuestionIntent.SUMMARY, QuestionIntent.LOOKUP, QuestionIntent.COMPARISON]
        assert res.confidence_level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        assert res.statistics.count == 5
        assert len(res.insights) >= 1
        assert len(res.conversation_history) >= 2
