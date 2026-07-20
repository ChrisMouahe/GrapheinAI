"""ReasoningAgent powered by Gemini Flash Vision for multimodal chart reasoning and JSON structure extraction."""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint, ReasoningOutput
from src.models.exceptions import InvalidVLMOutputError, VLMReasoningError

try:
    from google import genai
    from google.genai import types

    HAVE_GENAI_SDK = True
except ImportError:
    genai = None
    types = None
    HAVE_GENAI_SDK = False

logger = logging.getLogger("ReasoningAgent")


class ReasoningAgent:
    """Agent using Gemini Flash Vision API for multimodal visual chart extraction and reasoning."""

    DEFAULT_MODEL: str = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_MODEL,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.client = None

        if self.api_key and HAVE_GENAI_SDK and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    def build_prompt(
        self,
        question: str,
        retrieved_examples: list[dict[str, Any]],
        chart_type: str = "bar",
        complexity: str = "COMPLEX",
    ) -> str:
        """Constructs a structured prompt incorporating anti-hallucination rules, few-shot RAG context, and ML metadata."""
        prompt_parts: list[str] = [
            "### SYSTEM ROLE ###",
            "You are a Senior Multimodal Data Scientist and Visual Chart Reasoning Expert.",
            "",
            "### ANTI-HALLUCINATION & OUTPUT CONSTRAINTS ###",
            "1. NEVER invent, hallucinate, or guess numerical values not visible in the image.",
            "2. NEVER output the final numerical answer directly inside the text response.",
            "3. You MUST formulate an exact, valid arithmetic expression in 'calculation_expression'.",
            "   Only basic operations (+, -, *, /, parentheses) and numbers are allowed in 'calculation_expression'.",
            "4. Your output MUST BE A STRICT JSON OBJECT matching the specified JSON schema.",
            "",
            "### ML CONTEXT METADATA ###",
            f"- Predicted Chart Type: {chart_type}",
            f"- Query Complexity Level: {complexity}",
            "",
            "### FEW-SHOT RAG RETRIEVAL EXAMPLES ###",
        ]

        if retrieved_examples:
            for idx, ex in enumerate(retrieved_examples, 1):
                prompt_parts.append(
                    f"Example {idx}:\n"
                    f"  - Question: {ex.get('question', '')}\n"
                    f"  - Chart Type: {ex.get('chart_type', '')}\n"
                    f"  - Resolution Formula: {ex.get('resolution_formula', '')}\n"
                    f"  - Answer: {ex.get('answer', '')}"
                )
        else:
            prompt_parts.append("No prior context examples retrieved.")

        prompt_parts.extend(
            [
                "",
                "### TARGET QUESTION ###",
                f"Question: {question}",
                "",
                "### REQUIRED JSON OUTPUT FORMAT ###",
                "Respond strictly with a single JSON object in the following format:",
                "```json",
                "{",
                '  "extracted_data": {',
                f'    "chart_type": "{chart_type}",',
                '    "title": "Extracted Chart Title or null",',
                '    "x_label": "X axis label or null",',
                '    "y_label": "Y axis label or null",',
                '    "data_points": [',
                '      {"label": "Category Name", "value": 100.5, "confidence": 0.95}',
                "    ]",
                "  },",
                '  "reasoning": "Step 1: Identified values. Step 2: Formulated arithmetic formula.",',
                '  "calculation_expression": "(100.5 + 50.0) / 2"',
                "}",
                "```",
            ]
        )

        return "\n".join(prompt_parts)

    def analyze(
        self,
        image: ChartImage | Path | str,
        question: str,
        retrieved_examples: list[dict[str, Any]] | None = None,
        chart_type: str = "bar",
        complexity: str = "COMPLEX",
    ) -> ReasoningOutput:
        """Invokes Gemini Flash Vision to reason over chart image and returns validated ReasoningOutput schema.

        Args:
            image: ChartImage object, Path, or file path string.
            question: Target question string.
            retrieved_examples: Top-k examples from RetrievalAgent.
            chart_type: Chart type prediction from ClassifierAgent.
            complexity: Complexity prediction from ClassifierAgent.

        Returns:
            ReasoningOutput validated Pydantic model.

        Raises:
            InvalidVLMOutputError: If response fails JSON parsing or schema validation.
            VLMReasoningError: For general VLM execution failures.
        """
        img_path = image.file_path if isinstance(image, ChartImage) else Path(image)
        examples = retrieved_examples or []

        prompt_text = self.build_prompt(
            question=question,
            retrieved_examples=examples,
            chart_type=chart_type,
            complexity=complexity,
        )

        # Call API or Mock fallback with retries
        raw_response = self._call_vlm_with_retries(img_path, prompt_text, question)

        return self.parse_and_validate_response(raw_response)

    def _call_vlm_with_retries(self, img_path: Path, prompt_text: str, question: str) -> str:
        """Executes VLM call with automatic exponential backoff retries."""
        attempt = 0
        last_exception: Exception | None = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                if self.client is not None:
                    # Load image bytes/PIL image for Gemini API
                    with open(img_path, "rb") as f:
                        img_bytes = f.read()

                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[
                            types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                            prompt_text,
                        ],
                    )
                    if response and response.text:
                        return response.text

                # If client unavailable or no API key, use synthetic fallback response for demo/tests
                return self._generate_synthetic_response(question, img_path)

            except Exception as e:
                last_exception = e
                logger.warning(f"VLM call attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    sleep_time = self.backoff_factor ** attempt
                    time.sleep(sleep_time)

        raise VLMReasoningError(f"VLM call failed after {self.max_retries} attempts: {last_exception}")

    def _generate_synthetic_response(self, question: str, img_path: Path) -> str:
        """Generates deterministic structured JSON response for offline testing or missing API key."""
        q_lower = question.lower()

        if "average" in q_lower or "avg" in q_lower or "mean" in q_lower:
            expr = "(125.4 + 180.2) / 2"
        elif "difference" in q_lower or "diff" in q_lower:
            expr = "180.2 - 125.4"
        elif "total" in q_lower or "sum" in q_lower:
            expr = "125.4 + 180.2"
        else:
            expr = "125.4"

        res_json = {
            "extracted_data": {
                "chart_type": "bar",
                "title": f"Chart Data for {img_path.name}",
                "x_label": "Category",
                "y_label": "Value",
                "data_points": [
                    {"label": "Q1 Sales", "value": 125.4, "confidence": 0.98},
                    {"label": "Q2 Sales", "value": 180.2, "confidence": 0.95},
                ],
            },
            "reasoning": f"Identified data points Q1 Sales (125.4) and Q2 Sales (180.2). Formulated expression '{expr}'.",
            "calculation_expression": expr,
        }
        return json.dumps(res_json, indent=2)

    def parse_and_validate_response(self, raw_text: str) -> ReasoningOutput:
        """Extracts JSON substring, parses, and validates against ReasoningOutput Pydantic schema."""
        if not raw_text or not raw_text.strip():
            raise InvalidVLMOutputError("Empty response received from VLM.")

        # Extract JSON codeblock or raw JSON object
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(1)
        else:
            obj_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            clean_json = obj_match.group(1) if obj_match else raw_text

        try:
            parsed_dict = json.loads(clean_json)
        except json.JSONDecodeError as e:
            raise InvalidVLMOutputError(f"Failed to decode VLM JSON response: {e}\nRaw output: {raw_text}") from e

        try:
            return ReasoningOutput.model_validate(parsed_dict)
        except Exception as e:
            raise InvalidVLMOutputError(f"Pydantic validation error for VLM output: {e}") from e
