"""Comprehensive pytest suite for ReasoningAgent, Prompt Engineering, Pydantic validation, and PipelineAgent orchestration."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.agents.classifier_agent import ClassifierAgent
from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.models.chart import ChartImage, PipelineResult, ReasoningOutput
from src.models.exceptions import (
    InvalidVLMOutputError,
    PipelineError,
    VLMReasoningError,
)


@pytest.fixture
def sample_img_path(tmp_path: Path) -> Path:
    img_file = tmp_path / "chart_sample.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01")
    return img_file


@pytest.fixture
def valid_vlm_json() -> str:
    return json.dumps(
        {
            "extracted_data": {
                "chart_type": "bar",
                "title": "Quarterly Performance",
                "x_label": "Quarter",
                "y_label": "Sales",
                "data_points": [
                    {"label": "Q1", "value": 100.0, "confidence": 0.95},
                    {"label": "Q2", "value": 200.0, "confidence": 0.98},
                ],
            },
            "reasoning": "Summing Q1 and Q2 values.",
            "calculation_expression": "100.0 + 200.0",
        }
    )


class TestReasoningAgent:
    def test_build_prompt(self) -> None:
        agent = ReasoningAgent()
        examples = [
            {
                "question": "What is the avg growth?",
                "chart_type": "line",
                "resolution_formula": "(v1+v2)/2",
                "answer": "15",
            }
        ]
        prompt = agent.build_prompt("What is the average sales?", retrieved_examples=examples)

        assert "ANTI-HALLUCINATION" in prompt
        assert "What is the avg growth?" in prompt
        assert "What is the average sales?" in prompt
        assert "calculation_expression" in prompt

    def test_parse_and_validate_response_success(self, valid_vlm_json: str) -> None:
        agent = ReasoningAgent()
        output = agent.parse_and_validate_response(valid_vlm_json)

        assert isinstance(output, ReasoningOutput)
        assert output.extracted_data.chart_type == "bar"
        assert output.calculation_expression == "100.0 + 200.0"
        assert len(output.extracted_data.data_points) == 2

    def test_parse_and_validate_markdown_codeblock(self, valid_vlm_json: str) -> None:
        agent = ReasoningAgent()
        wrapped_json = f"```json\n{valid_vlm_json}\n```"
        output = agent.parse_and_validate_response(wrapped_json)

        assert isinstance(output, ReasoningOutput)
        assert output.calculation_expression == "100.0 + 200.0"

    def test_invalid_json_raises_exception(self) -> None:
        agent = ReasoningAgent()
        with pytest.raises(InvalidVLMOutputError):
            agent.parse_and_validate_response("Invalid non-json response text")

    def test_invalid_schema_raises_exception(self) -> None:
        agent = ReasoningAgent()
        bad_json = '{"invalid_field": "val"}'
        with pytest.raises(InvalidVLMOutputError):
            agent.parse_and_validate_response(bad_json)

    def test_analyze_with_mock_gemini_client(self, sample_img_path: Path, valid_vlm_json: str) -> None:
        agent = ReasoningAgent(api_key="mock_key")
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = valid_vlm_json
        mock_client.models.generate_content.return_value = mock_response
        agent.client = mock_client

        output = agent.analyze(
            image=sample_img_path,
            question="What is the total sales?",
        )

        assert isinstance(output, ReasoningOutput)
        assert output.calculation_expression == "100.0 + 200.0"

    def test_analyze_synthetic_fallback(self, sample_img_path: Path) -> None:
        agent = ReasoningAgent(api_key=None)  # No API key triggers synthetic fallback
        output = agent.analyze(
            image=sample_img_path,
            question="What is the average growth rate?",
        )

        assert isinstance(output, ReasoningOutput)
        assert output.calculation_expression == "(125.4 + 180.2) / 2"


class TestPipelineAgentOrchestration:
    def test_full_pipeline_execution(self, sample_img_path: Path) -> None:
        pipeline = PipelineAgent()
        res = pipeline.answer(
            image=sample_img_path,
            question="What is the average growth rate?",
        )

        assert isinstance(res, PipelineResult)
        assert res.final_answer == 152.8
        assert res.calculation_expression == "(125.4 + 180.2) / 2"
        assert res.complexity.complexity in ("SIMPLE", "COMPLEX")
        assert len(res.extracted_data.data_points) >= 2

    def test_pipeline_empty_question_raises(self, sample_img_path: Path) -> None:
        pipeline = PipelineAgent()
        with pytest.raises(PipelineError):
            pipeline.answer(image=sample_img_path, question="")

    def test_pipeline_with_mocked_reasoner(self, sample_img_path: Path) -> None:
        mock_reasoner = MagicMock(spec=ReasoningAgent)
        mock_reasoning_out = ReasoningOutput.model_validate(
            {
                "extracted_data": {
                    "chart_type": "bar",
                    "title": "Mock Title",
                    "data_points": [{"label": "A", "value": 50}],
                },
                "reasoning": "Multiplying 50 by 2.",
                "calculation_expression": "50 * 2",
            }
        )
        mock_reasoner.analyze.return_value = mock_reasoning_out

        pipeline = PipelineAgent(reasoning_agent=mock_reasoner)
        res = pipeline.answer(image=sample_img_path, question="Calculate value")

        assert res.final_answer == 100
        assert res.calculation_expression == "50 * 2"
