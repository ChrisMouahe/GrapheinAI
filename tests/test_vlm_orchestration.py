"""Comprehensive pytest suite for Gemini Flash Vision ReasoningAgent and master PipelineAgent orchestrator."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.models.chart import (
    ChartExtraction,
    ChartImage,
    ExtractedDataPoint,
    PipelineResult,
    ReasoningOutput,
)
from src.models.exceptions import InvalidVLMOutputError


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    img_file = tmp_path / "chart_sample.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\x5c\x72\xa8\x66")
    return img_file


class TestReasoningAgent:
    """Unit tests for ReasoningAgent prompt building, VLM output parsing, and error handling."""

    def test_build_prompt(self) -> None:
        agent = ReasoningAgent()
        examples = [
            {
                "question": "What is the average sales?",
                "chart_type": "bar",
                "resolution_formula": "(10 + 20) / 2",
                "answer": "15.0",
            }
        ]
        prompt = agent.build_prompt(
            question="What is the total sales?",
            retrieved_examples=examples,
            chart_type="bar",
            complexity="COMPLEX",
        )

        assert "### SYSTEM ROLE ###" in prompt
        assert "NEVER invent, hallucinate, or guess numerical values" in prompt
        assert "What is the total sales?" in prompt
        assert "What is the average sales?" in prompt
        assert "(10 + 20) / 2" in prompt

    def test_parse_and_validate_response_success(self) -> None:
        agent = ReasoningAgent()
        valid_json_text = json.dumps(
            {
                "extracted_data": {
                    "chart_type": "bar",
                    "title": "Quarterly Revenue",
                    "data_points": [
                        {"label": "Q1", "value": 100.0, "confidence": 0.98},
                        {"label": "Q2", "value": 150.0, "confidence": 0.95},
                    ],
                },
                "reasoning": "Summing Q1 and Q2 revenue.",
                "calculation_expression": "100.0 + 150.0",
            }
        )

        output = agent.parse_and_validate_response(valid_json_text)
        assert isinstance(output, ReasoningOutput)
        assert output.extracted_data.chart_type == "bar"
        assert len(output.extracted_data.data_points) == 2
        assert output.calculation_expression == "100.0 + 150.0"

    def test_parse_and_validate_markdown_codeblock(self) -> None:
        agent = ReasoningAgent()
        markdown_text = """
        Here is the JSON result:
        ```json
        {
          "extracted_data": {
            "chart_type": "line",
            "data_points": [{"label": "A", "value": 10.0}]
          },
          "reasoning": "Single point extracted.",
          "calculation_expression": "10.0 * 2"
        }
        ```
        """
        output = agent.parse_and_validate_response(markdown_text)
        assert output.extracted_data.chart_type == "line"
        assert output.calculation_expression == "10.0 * 2"

    def test_invalid_json_raises_exception(self) -> None:
        agent = ReasoningAgent()
        invalid_text = "This is not JSON text at all."
        with pytest.raises(InvalidVLMOutputError):
            agent.parse_and_validate_response(invalid_text)

    def test_invalid_schema_raises_exception(self) -> None:
        agent = ReasoningAgent()
        incomplete_json = json.dumps({"reasoning": "Missing extracted_data and calculation_expression"})
        with pytest.raises(InvalidVLMOutputError):
            agent.parse_and_validate_response(incomplete_json)

    def test_analyze_with_mock_gemini_client(self, sample_image_path: Path) -> None:
        agent = ReasoningAgent(api_key="mock_key")
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "extracted_data": {
                    "chart_type": "bar",
                    "data_points": [
                        {"label": "A", "value": 50.0, "confidence": 0.9},
                        {"label": "B", "value": 75.0, "confidence": 0.95},
                    ],
                },
                "reasoning": "Mocked analysis.",
                "calculation_expression": "50.0 + 75.0",
            }
        )
        mock_client.models.generate_content.return_value = mock_response
        agent.client = mock_client

        result = agent.analyze(
            image=sample_image_path,
            question="What is the sum?",
        )

        assert isinstance(result, ReasoningOutput)
        assert result.calculation_expression == "50.0 + 75.0"
        mock_client.models.generate_content.assert_called()

    def test_analyze_dynamic_fallback(self, sample_image_path: Path) -> None:
        agent = ReasoningAgent()  # No client set
        result = agent.analyze(
            image=sample_image_path,
            question="What is the average growth rate?",
        )
        assert isinstance(result, ReasoningOutput)
        assert result.extracted_data.chart_type == "bar"
        assert len(result.extracted_data.data_points) == 3


class TestPipelineAgentOrchestration:
    """Integration tests for master PipelineAgent multimodal reasoning orchestrator."""

    def test_full_pipeline_execution(self, sample_image_path: Path) -> None:
        pipeline = PipelineAgent()
        result = pipeline.answer(
            image=sample_image_path,
            question="What is the average growth rate?",
        )

        assert isinstance(result, PipelineResult)
        assert isinstance(result.final_answer, (int, float))
        assert result.final_answer > 0
        assert "/" in result.calculation_expression or "+" in result.calculation_expression
        assert result.complexity.complexity == "COMPLEX"
        assert len(result.retrieved_examples) > 0

    def test_pipeline_empty_question_raises(self, sample_image_path: Path) -> None:
        pipeline = PipelineAgent()
        with pytest.raises(Exception):
            pipeline.answer(image=sample_image_path, question="")

    def test_pipeline_with_mocked_reasoner(self, sample_image_path: Path) -> None:
        mock_reasoner = MagicMock(spec=ReasoningAgent)
        mock_reasoner.extract_chart_data.return_value = ChartExtraction(
            chart_type="bar",
            data_points=[
                ExtractedDataPoint(label="X", value=10.0),
                ExtractedDataPoint(label="Y", value=20.0),
            ],
        )
        mock_reasoner.is_out_of_domain_query.return_value = False
        mock_reasoner.analyze.return_value = ReasoningOutput(
            extracted_data=ChartExtraction(
                chart_type="bar",
                data_points=[
                    ExtractedDataPoint(label="X", value=10.0),
                    ExtractedDataPoint(label="Y", value=20.0),
                ],
            ),
            reasoning="Mocked reasoning logic.",
            calculation_expression="10.0 * 20.0",
        )

        pipeline = PipelineAgent(reasoning_agent=mock_reasoner)
        result = pipeline.answer(
            image=sample_image_path,
            question="What is X times Y?",
        )

        assert result.final_answer == 200.0
        assert result.calculation_expression == "10.0 * 20.0"
        assert "SCIENTIFIC GRAPHIC INTERPRETATION REPORT" in result.initial_interpretation
