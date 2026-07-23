"""Research Benchmark Test Suite measuring Extraction Accuracy, OCR Region Accuracy, Latency, and Validation Metrics."""

import time
from pathlib import Path
import pytest

from src.agents.graph_interpreter import GraphInterpreter
from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.validation_agent import ValidationAgent
from src.models.chart import ChartExtraction, ExtractedDataPoint, PipelineResult, ValidationResult
from src.utils.chart_detector import ChartTypeDetector
from src.utils.ocr_engine import OCREngine


@pytest.fixture
def bar_chart_path() -> Path:
    return Path("data/raw/sample_chart.png")


@pytest.fixture
def line_chart_path() -> Path:
    return Path("data/raw/sample_chart_line.png")


class TestBenchmarkAccuracyAndPerformance:
    """Benchmark test suite measuring accuracy metrics, latency, and absence of invented labels."""

    def test_ocr_region_detection_accuracy(self, bar_chart_path: Path, line_chart_path: Path) -> None:
        ocr_engine = OCREngine()

        boxes_bar = ocr_engine.detect_ocr_text_boxes(bar_chart_path)
        boxes_line = ocr_engine.detect_ocr_text_boxes(line_chart_path)

        assert isinstance(boxes_bar, list)
        assert isinstance(boxes_line, list)
        assert len(boxes_bar) > 0
        assert len(boxes_line) > 0

        # Verify region types are valid
        valid_regions = {"title", "x_axis", "y_axis", "legend", "plot"}
        for b in boxes_bar:
            assert b.region in valid_regions
            assert len(b.box) == 4
            assert b.confidence >= 0.70

    def test_chart_geometry_detector(self, bar_chart_path: Path, line_chart_path: Path) -> None:
        detector = ChartTypeDetector()

        struct_bar = detector.detect_chart_structure(bar_chart_path)
        struct_line = detector.detect_chart_structure(line_chart_path)

        assert struct_bar.detected_type in ["bar", "horizontal_bar", "grouped_bar"]
        assert struct_line.detected_type in ["line", "bar"]
        assert struct_bar.confidence >= 0.75

    def test_validation_agent_confidence_scoring(self, bar_chart_path: Path) -> None:
        validator = ValidationAgent()
        ocr_engine = OCREngine()
        detector = ChartTypeDetector()
        reasoner = ReasoningAgent()

        ext = reasoner.extract_chart_data(bar_chart_path)
        struct = detector.detect_chart_structure(bar_chart_path)
        ocr_boxes = ocr_engine.detect_ocr_text_boxes(bar_chart_path)

        val_res = validator.validate_extraction(ext, struct, ocr_boxes)

        assert isinstance(val_res, ValidationResult)
        assert 0.0 <= val_res.ocr_accuracy <= 1.0
        assert 0.0 <= val_res.extraction_accuracy <= 1.0
        assert 0.0 <= val_res.overall_confidence <= 1.0
        assert isinstance(val_res.validation_notes, list)

    def test_graph_interpreter_independent_analysis(self, bar_chart_path: Path) -> None:
        reasoner = ReasoningAgent()
        ext = reasoner.extract_chart_data(bar_chart_path)

        interpreter = GraphInterpreter()
        report = interpreter.interpret_chart(ext)

        assert isinstance(report, str)
        assert "SCIENTIFIC GRAPHIC INTERPRETATION REPORT" in report
        assert "Peak Maximum" in report
        assert "Minimum Threshold" in report
        assert "Executive Summary" in report

    def test_no_invented_category_labels(self, bar_chart_path: Path) -> None:
        pipeline = PipelineAgent()
        result = pipeline.answer(bar_chart_path, "What is the average growth rate?")

        assert isinstance(result, PipelineResult)
        for dp in result.extracted_data.data_points:
            if dp.label is not None:
                assert dp.label.lower() not in ["category a", "category b", "category c", "series 1"]

    def test_benchmark_latency_and_accuracy_metrics(self, bar_chart_path: Path) -> None:
        pipeline = PipelineAgent()
        questions = [
            "What is the average growth rate?",
            "What is the total sum across categories?",
            "What is the difference between maximum and minimum values?",
        ]

        latencies = []
        for q in questions:
            t0 = time.time()
            res = pipeline.answer(bar_chart_path, q)
            dt = time.time() - t0
            latencies.append(dt)

            assert res.final_answer is not None
            assert res.validation_result.overall_confidence > 0.60

        avg_latency = sum(latencies) / len(latencies)
        print(f"\n[BENCHMARK] Average Pipeline Execution Latency: {avg_latency:.3f} seconds across {len(questions)} queries.")
        assert avg_latency < 5.0
