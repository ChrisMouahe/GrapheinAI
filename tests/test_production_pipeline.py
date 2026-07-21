"""Integration test suite verifying dynamic execution, PDF report generation, and multi-image/multi-query variance."""

from pathlib import Path
import pytest
import pandas as pd

from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.models.chart import ChartExtraction, PipelineResult
from src.utils.pdf_generator import PDFReportGenerator
from src.utils.rag_pipeline import FAISSRAGPipeline


@pytest.fixture
def bar_chart_path() -> Path:
    return Path("data/raw/sample_chart.png")


@pytest.fixture
def line_chart_path() -> Path:
    return Path("data/raw/sample_chart_line.png")


class TestProductionPipelineDynamics:
    """Integration tests verifying dynamic pipeline variance and non-static behavior across different images and questions."""

    def test_multi_image_dynamic_extraction_variance(self, bar_chart_path: Path, line_chart_path: Path) -> None:
        reasoner = ReasoningAgent()

        ext_bar = reasoner.extract_chart_data(bar_chart_path)
        ext_line = reasoner.extract_chart_data(line_chart_path)

        assert isinstance(ext_bar, ChartExtraction)
        assert isinstance(ext_line, ChartExtraction)

        # Dynamic extraction MUST produce different chart types or data values for different images
        assert ext_bar.chart_type != ext_line.chart_type or [dp.value for dp in ext_bar.data_points] != [dp.value for dp in ext_line.data_points]

    def test_initial_scientific_interpretation(self, bar_chart_path: Path) -> None:
        reasoner = ReasoningAgent()
        ext = reasoner.extract_chart_data(bar_chart_path)
        interp = reasoner.generate_initial_interpretation(bar_chart_path, ext)

        assert isinstance(interp, str)
        assert len(interp) > 200
        assert "Executive Summary" in interp or "Observed Variables" in interp or "Trends" in interp

    def test_multi_question_dynamic_rag_and_formula_variance(self, bar_chart_path: Path) -> None:
        pipeline = PipelineAgent()

        res_q1 = pipeline.answer(bar_chart_path, "What is the average growth rate?")
        res_q2 = pipeline.answer(bar_chart_path, "What is the total sum across all quarters?")

        assert isinstance(res_q1, PipelineResult)
        assert isinstance(res_q2, PipelineResult)

        # Different questions MUST produce different formulas or answers
        assert res_q1.calculation_expression != res_q2.calculation_expression or res_q1.final_answer != res_q2.final_answer

    def test_pdf_report_generation(self, bar_chart_path: Path) -> None:
        pipeline = PipelineAgent()
        result = pipeline.answer(bar_chart_path, "Calculate average value.")

        pdf_gen = PDFReportGenerator()
        pdf_bytes = pdf_gen.generate_pdf_bytes(result, bar_chart_path, execution_latency=1.2)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")
