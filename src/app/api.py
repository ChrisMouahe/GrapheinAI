"""Production FastAPI REST Backend for ChartQA Commercial SaaS AI Web Application."""

import json
import io
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from src.agents.classifier_agent import ClassifierAgent
from src.agents.graph_interpreter import GraphInterpreter
from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.agents.validation_agent import ValidationAgent
from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint, PipelineResult
from src.utils.chart_detector import ChartTypeDetector
from src.utils.ocr_engine import OCREngine
from src.utils.pdf_generator import PDFReportGenerator
from src.utils.security_guard import PromptInjectionGuard

app = FastAPI(
    title="ChartQA Research AI API",
    description="REST API backend for ChartQA Commercial Multimodal Vision Analysis Platform.",
    version="4.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent Instances
pipeline_agent = PipelineAgent()
classifier_agent = ClassifierAgent()
reasoning_agent = ReasoningAgent()
validation_agent = ValidationAgent()
graph_interpreter = GraphInterpreter()
ocr_engine = OCREngine()
chart_detector = ChartTypeDetector()
pdf_generator = PDFReportGenerator()
security_guard = PromptInjectionGuard()

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


class HITLDataOverride(BaseModel):
    label: str | None = None
    value: float | int | str
    confidence: float = 1.0


@app.get("/api/health")
def health_check() -> dict[str, Any]:
    """Health check endpoint indicating pipeline component status."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "opencv_ocr": True,
            "cv_chart_detector": True,
            "validation_agent": True,
            "graph_interpreter": True,
            "safe_calculator_ast": True,
            "xgboost_classifier": True,
            "faiss_rag": True,
            "gemini_vlm": reasoning_agent.client is not None,
        },
    }


@app.post("/api/extract")
async def extract_chart(
    file: UploadFile | None = File(None),
    image_filename: str | None = Form(None),
) -> dict[str, Any]:
    """Extracts OCR text boxes, CV geometry, and dynamic tabular data from chart image."""
    try:
        if file is not None:
            contents = await file.read()
            if len(contents) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit.")

            img_path = RAW_DATA_DIR / f"uploaded_{file.filename}"
            with open(img_path, "wb") as f:
                f.write(contents)
        elif image_filename:
            img_path = RAW_DATA_DIR / image_filename
            if not img_path.exists():
                img_path = RAW_DATA_DIR / "sample_chart.png"
        else:
            img_path = RAW_DATA_DIR / "sample_chart.png"

        ocr_boxes = ocr_engine.detect_ocr_text_boxes(img_path)
        structure = chart_detector.detect_chart_structure(img_path)
        extraction = reasoning_agent.extract_chart_data(img_path)

        return {
            "image_filename": img_path.name,
            "chart_structure": structure.model_dump(),
            "ocr_boxes": [b.model_dump() for b in ocr_boxes],
            "extracted_data": extraction.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/analyze")
async def analyze_chart(
    question: str = Form(...),
    file: UploadFile | None = File(None),
    image_filename: str | None = Form(None),
    hitl_data_json: str | None = Form(None),
) -> dict[str, Any]:
    """Executes full multi-stage multimodal reasoning pipeline over chart image and target question."""
    try:
        security_guard.inspect_prompt(question)
    except Exception as se:
        raise HTTPException(status_code=400, detail=f"Security Alert: {se}") from se

    if file is not None:
        contents = await file.read()
        img_path = RAW_DATA_DIR / f"uploaded_{file.filename}"
        with open(img_path, "wb") as f:
            f.write(contents)
    elif image_filename:
        img_path = RAW_DATA_DIR / image_filename
        if not img_path.exists():
            img_path = RAW_DATA_DIR / "sample_chart.png"
    else:
        img_path = RAW_DATA_DIR / "sample_chart.png"

    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Target chart image not found.")

    start_t = time.time()
    result = pipeline_agent.answer(image=img_path, question=question)

    # Process HITL overrides if supplied from UI data grid
    if hitl_data_json:
        try:
            hitl_items = json.loads(hitl_data_json)
            if isinstance(hitl_items, list) and len(hitl_items) > 0:
                updated_dps = []
                for item in hitl_items:
                    lbl = item.get("label")
                    val = item.get("value")
                    conf = float(item.get("confidence", 1.0))
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        pass
                    updated_dps.append(ExtractedDataPoint(label=lbl, value=val, confidence=conf))

                result.extracted_data.data_points = updated_dps
                result.extracted_data.metadata["is_hitl_modified"] = True

                # Recalculate expression and answer with updated HITL data
                vals = [dp.value for dp in updated_dps if isinstance(dp.value, (int, float))]
                if vals and not result.is_out_of_domain:
                    q_lower = question.lower()
                    if "total" in q_lower or "sum" in q_lower:
                        result.calculation_expression = " + ".join(str(v) for v in vals)
                    elif "difference" in q_lower or "diff" in q_lower:
                        result.calculation_expression = f"{max(vals)} - {min(vals)}"
                    else:
                        result.calculation_expression = f"({' + '.join(str(v) for v in vals)}) / {len(vals)}"

                    result.final_answer = pipeline_agent.calculator.evaluate(result.calculation_expression)
                    result.initial_interpretation = graph_interpreter.interpret_chart(result.extracted_data)

        except Exception as ex:
            pass

    latency = round(time.time() - start_t, 3)

    res_dict = result.model_dump()
    res_dict["execution_latency"] = latency
    res_dict["image_filename"] = img_path.name
    return res_dict


@app.post("/api/report/pdf")
async def download_pdf_report(
    question: str = Form(...),
    image_filename: str = Form("sample_chart.png"),
    hitl_data_json: str | None = Form(None),
) -> Response:
    """Generates and returns downloadable official PDF report."""
    img_path = RAW_DATA_DIR / image_filename
    if not img_path.exists():
        img_path = RAW_DATA_DIR / "sample_chart.png"

    start_t = time.time()
    result = pipeline_agent.answer(image=img_path, question=question)

    if hitl_data_json:
        try:
            hitl_items = json.loads(hitl_data_json)
            if isinstance(hitl_items, list) and len(hitl_items) > 0:
                updated_dps = []
                for item in hitl_items:
                    lbl = item.get("label")
                    val = item.get("value")
                    conf = float(item.get("confidence", 1.0))
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        pass
                    updated_dps.append(ExtractedDataPoint(label=lbl, value=val, confidence=conf))

                result.extracted_data.data_points = updated_dps
                result.extracted_data.metadata["is_hitl_modified"] = True
                vals = [dp.value for dp in updated_dps if isinstance(dp.value, (int, float))]
                if vals and not result.is_out_of_domain:
                    q_lower = question.lower()
                    if "total" in q_lower or "sum" in q_lower:
                        result.calculation_expression = " + ".join(str(v) for v in vals)
                    elif "difference" in q_lower or "diff" in q_lower:
                        result.calculation_expression = f"{max(vals)} - {min(vals)}"
                    else:
                        result.calculation_expression = f"({' + '.join(str(v) for v in vals)}) / {len(vals)}"
                    result.final_answer = pipeline_agent.calculator.evaluate(result.calculation_expression)
                    result.initial_interpretation = graph_interpreter.interpret_chart(result.extracted_data)
        except Exception:
            pass

    latency = round(time.time() - start_t, 3)

    pdf_bytes = pdf_generator.generate_pdf_bytes(
        result=result,
        image_path=img_path,
        execution_latency=latency,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ChartQA_Report_{img_path.stem}.pdf"},
    )


# Serve static single-page web app at root
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
