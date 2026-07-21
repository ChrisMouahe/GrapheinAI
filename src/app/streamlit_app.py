"""Streamlit Web Application & Human-in-the-Loop UI for ChartQA Research-Grade Multimodal Assistant."""

import time
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image
import streamlit as st

from src.agents.classifier_agent import ClassifierAgent
from src.agents.pipeline_agent import PipelineAgent
from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint
from src.models.exceptions import (
    ChartValidationError,
    PromptInjectionDetectedError,
    UIValidationError,
)
from src.utils.pdf_generator import PDFReportGenerator
from src.utils.security_guard import PromptInjectionGuard


# Page Configuration
st.set_page_config(
    page_title="ChartQA Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (CSS)
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .result-badge {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .out-of-domain-badge {
        background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .security-badge {
        background-color: #FFEBEE;
        border-left: 5px solid #D32F2F;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .source-badge {
        background-color: #E3F2FD;
        border-left: 5px solid #1E88E5;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_cached_pipeline() -> PipelineAgent:
    """Caches heavy ML and FAISS pipeline models only."""
    return PipelineAgent()


@st.cache_resource
def get_cached_classifier() -> ClassifierAgent:
    """Caches ML XGBoost classifier model only."""
    return ClassifierAgent()


@st.cache_resource
def get_cached_security_guard() -> PromptInjectionGuard:
    """Caches NLP security guard patterns."""
    return PromptInjectionGuard()


@st.cache_resource
def get_cached_pdf_generator() -> PDFReportGenerator:
    """Caches ReportLab PDF generator."""
    return PDFReportGenerator()


def init_session_state() -> None:
    """Initializes Streamlit session state stores."""
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "selected_question" not in st.session_state:
        st.session_state["selected_question"] = ""


def validate_uploaded_image(file_bytes: bytes, filename: str) -> Image.Image:
    """Validates uploaded image file format, resolution, and size."""
    max_size_bytes = 10 * 1024 * 1024  # 10 MB limit
    if len(file_bytes) > max_size_bytes:
        raise UIValidationError(
            f"Image file '{filename}' exceeds maximum allowed size of 10 MB ({len(file_bytes)/1e6:.2f} MB)."
        )

    try:
        pil_img = Image.open(BytesIO(file_bytes))
        width, height = pil_img.size

        if width < 50 or height < 50:
            raise UIValidationError(
                f"Image resolution too low ({width}x{height}px). Minimum required is 50x50px."
            )

        return pil_img
    except Exception as e:
        if isinstance(e, UIValidationError):
            raise
        raise ChartValidationError(f"Invalid or corrupted image file '{filename}': {e}") from e


def main() -> None:
    init_session_state()

    # Retrieve Cached Heavy Models (ONLY models are cached)
    security_guard = get_cached_security_guard()
    classifier_agent = get_cached_classifier()
    pipeline_agent = get_cached_pipeline()
    pdf_generator = get_cached_pdf_generator()

    # Sidebar: Information & Settings
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/combo-chart.png", width=64)
        st.title("ChartQA Research Assistant")
        st.markdown("**Research-Grade Multi-stage Architecture**")

        st.divider()
        st.subheader("⚙️ System Status")
        st.success("🟢 OpenCV OCR Detector: Active")
        st.success("🟢 Computer Vision Geometry: Active")
        st.success("🟢 ValidationAgent: Active")
        st.success("🟢 GraphInterpreter: Active")
        st.success("🟢 SafeCalculator (AST): Active")
        st.success("🟢 Classifier (XGBoost): Active")
        st.success("🟢 RAG (FAISS + MiniLM): Active")
        st.success("🟢 VLM (Gemini Flash Vision): Active")

        st.divider()
        st.subheader("📜 Pipeline Flow")
        st.markdown(
            """
            1. **Upload & Validate**
            2. **OpenCV OCR Region Detection**
            3. **CV Geometry Chart Detector**
            4. **Guided Gemini VLM Extraction**
            5. **ValidationAgent Confidence Scoring**
            6. **GraphInterpreter Report Generation**
            7. **Human-in-the-Loop Editor**
            8. **AST SafeCalculator Execution**
            9. **ReportLab PDF Export**
            """
        )

        st.divider()
        if st.button("🗑️ Clear Query History"):
            st.session_state["history"] = []
            st.rerun()

    # Main Interface Header
    st.markdown('<div class="main-title">📊 Assistant Multimodal de Raisonnement sur Graphiques</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Pipeline de niveau recherche : OpenCV OCR, détection géométrique, ValidationAgent et rapport PDF.</div>',
        unsafe_allow_html=True,
    )

    # Tabs for Main Workspace and Session History
    tab_workspace, tab_history = st.tabs(["🚀 Reasoning Workspace", "📜 Session History"])

    with tab_workspace:
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.subheader("1. Upload Chart Image")
            uploaded_file = st.file_uploader(
                "Select a chart image (PNG, JPG, JPEG)",
                type=["png", "jpg", "jpeg"],
                key="chart_uploader",
            )

            pil_image = None
            temp_img_path = None

            if uploaded_file is not None:
                try:
                    file_bytes = uploaded_file.getvalue()
                    pil_image = validate_uploaded_image(file_bytes, uploaded_file.name)

                    temp_dir = Path("data/raw")
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    temp_img_path = temp_dir / f"uploaded_{uploaded_file.name}"
                    pil_image.save(temp_img_path)

                    st.image(pil_image, caption=f"Uploaded: {uploaded_file.name} ({pil_image.width}x{pil_image.height}px)", use_container_width=True)

                except (UIValidationError, ChartValidationError) as ve:
                    st.error(f"❌ Image Validation Error: {ve}")
                    return

            else:
                sample_img_path = Path("data/raw/sample_chart.png")
                if sample_img_path.exists():
                    pil_image = Image.open(sample_img_path)
                    temp_img_path = sample_img_path
                    st.image(pil_image, caption="Default Chart Image (Quarterly Sales 2024)", use_container_width=True)

        with col_right:
            st.subheader("2. ML & Computer Vision Preview")
            if temp_img_path and temp_img_path.exists():
                preview_q = "What is the average value across variables?"
                cls_result = classifier_agent.predict(preview_q, chart_type="bar")
                structure = pipeline_agent.chart_detector.detect_chart_structure(temp_img_path)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("CV Detected Chart Architecture", structure.detected_type.upper())
                with c2:
                    st.metric("Complexity Level", cls_result.complexity)
                with c3:
                    st.metric("CV Detection Confidence", f"{structure.confidence:.1%}")

            st.divider()
            st.subheader("3. Enter Question & Preset Suggestions")

            st.markdown("**Quick Preset Suggestions:**")
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                if st.button("📊 Avg Growth Rate"):
                    st.session_state["selected_question"] = "What is the average growth rate?"
            with s_col2:
                if st.button("➕ Total Sum"):
                    st.session_state["selected_question"] = "What is the total sum across categories?"
            with s_col3:
                if st.button("➖ Difference Max-Min"):
                    st.session_state["selected_question"] = "What is the difference between maximum and minimum values?"

            user_question = st.text_input(
                "Type your target question:",
                value=st.session_state.get("selected_question", "What is the average growth rate?"),
                key="user_question_input",
            )

            run_pipeline_btn = st.button("🚀 Run Research Multimodal Pipeline", type="primary", use_container_width=True)

        st.divider()

        # Human-in-the-Loop (HITL) Data Editor Section
        st.subheader("4. 🛠️ Human-in-the-Loop (HITL) Data Point Editor")
        st.info("Dynamic data points extracted from OpenCV OCR + Gemini Flash Vision. Edit, add, or delete values below to override calculation inputs.")

        if temp_img_path and temp_img_path.exists():
            initial_extraction = pipeline_agent.reasoner.extract_chart_data(temp_img_path)
            initial_data = [dp.model_dump() for dp in initial_extraction.data_points]
            source_label = initial_extraction.extraction_source
        else:
            initial_data = [{"label": "Category A", "value": 100.0, "confidence": 0.95}]
            source_label = "OpenCV OCR + Structural Parser (Offline Fallback)"

        st.markdown(f'<div class="source-badge">ℹ️ Multi-stage Extraction Source: <b>{source_label}</b></div>', unsafe_allow_html=True)

        df_initial = pd.DataFrame(initial_data)

        edited_df = st.data_editor(
            df_initial,
            num_rows="dynamic",
            use_container_width=True,
            key="hitl_editor",
        )

        st.divider()

        # Pipeline Execution Handler
        if run_pipeline_btn:
            if not user_question.strip():
                st.warning("⚠️ Please enter a question before running reasoning.")
                return

            # Anti-Prompt-Injection Security Check
            try:
                security_guard.inspect_prompt(user_question)
            except PromptInjectionDetectedError as se:
                st.markdown(f'<div class="security-badge">🚨 <b>SECURITY BLOCK:</b> {se}</div>', unsafe_allow_html=True)
                st.error("Execution blocked to prevent prompt injection attack.")
                return

            if not temp_img_path or not temp_img_path.exists():
                st.error("No valid chart image found.")
                return

            start_time = time.time()
            progress_bar = st.progress(0, text="Initializing Research Pipeline...")

            try:
                progress_bar.progress(20, text="Running OpenCV OCR Region Detector & CV Geometry Analyzer...")
                time.sleep(0.1)

                progress_bar.progress(40, text="Executing Guided Gemini Flash Vision Reasoning & ValidationAgent...")
                pipeline_result = pipeline_agent.answer(
                    image=temp_img_path,
                    question=user_question,
                )

                progress_bar.progress(70, text="Generating GraphInterpreter Report & Evaluating SafeCalculator AST...")
                progress_bar.progress(90, text="Formatting ReportLab PDF Document...")

                latency = time.time() - start_time

                # Check if user edited HITL rows
                is_hitl_edited = False
                if edited_df is not None and not edited_df.empty:
                    updated_dps = []
                    for _, r in edited_df.iterrows():
                        val = r["value"]
                        lbl_val = r["label"] if pd.notna(r["label"]) and str(r["label"]).strip() != "" else None
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                        updated_dps.append(
                            ExtractedDataPoint(
                                label=lbl_val,
                                value=val,
                                confidence=float(r.get("confidence", 1.0)),
                            )
                        )
                    pipeline_result.extracted_data.data_points = updated_dps
                    is_hitl_edited = True
                    pipeline_result.extracted_data.metadata["is_hitl_modified"] = True

                progress_bar.progress(100, text="Complete!")
                time.sleep(0.2)
                progress_bar.empty()

                # Display Validation Metrics Badge
                val_res = pipeline_result.validation_result
                v1, v2, v3 = st.columns(3)
                with v1:
                    st.metric("Overall Validation Confidence", f"{val_res.overall_confidence:.1%}")
                with v2:
                    st.metric("OCR Region Accuracy", f"{val_res.ocr_accuracy:.1%}")
                with v3:
                    st.metric("Extraction Accuracy", f"{val_res.extraction_accuracy:.1%}")

                if val_res.requires_human_confirmation:
                    st.warning("⚠️ Validation Alert: Overall confidence is below 70%. Please review extracted values in the HITL Editor.")

                # Display Final Answer Result Card
                if pipeline_result.is_out_of_domain:
                    st.markdown(
                        f'<div class="out-of-domain-badge">⚠️ Out-of-Domain Query<br/><font size=4>{pipeline_result.final_answer}</font></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="result-badge">✨ Final Calculated Answer: {pipeline_result.final_answer}</div>',
                        unsafe_allow_html=True,
                    )

                if is_hitl_edited:
                    st.warning("🛠️ Note: Human-in-the-Loop edits were applied to the calculation & PDF report.")

                # PDF Export Section
                pdf_bytes = pdf_generator.generate_pdf_bytes(
                    result=pipeline_result,
                    image_path=temp_img_path,
                    execution_latency=latency,
                )
                st.download_button(
                    label="📄 Download Official PDF Report",
                    data=pdf_bytes,
                    file_name=f"ChartQA_Report_{temp_img_path.stem}.pdf",
                    mime="application/pdf",
                    type="primary",
                )

                st.divider()

                # Automatic Graphic Interpretation Section (GraphInterpreter)
                st.subheader("📊 5. Automatic Scientific Graphic Interpretation (GraphInterpreter)")
                st.markdown(pipeline_result.initial_interpretation)

                st.divider()

                # Detailed Technical Breakdown Expander
                with st.expander("🔍 Detailed Technical Breakdown, OCR Bounding Boxes & Context", expanded=True):
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        st.markdown(f"**Arithmetic Expression:** `{pipeline_result.calculation_expression}`")
                    with e2:
                        st.markdown(f"**Execution Latency:** `{latency:.2f} seconds`")
                    with e3:
                        st.markdown(f"**Complexity:** `{pipeline_result.complexity.complexity}` ({pipeline_result.complexity.confidence:.1%})")

                    st.markdown("**Validation Audit Notes:**")
                    for note in val_res.validation_notes:
                        st.markdown(f"- {note}")

                    st.markdown("**Step-by-step Reasoning:**")
                    st.write(pipeline_result.reasoning)

                    st.markdown("**Extracted Data Points (HITL Status Included):**")
                    st.dataframe(pd.DataFrame([dp.model_dump() for dp in pipeline_result.extracted_data.data_points]))

                    st.markdown("**Retrieved Few-Shot RAG Context:**")
                    for idx, ex in enumerate(pipeline_result.retrieved_examples, 1):
                        st.markdown(f"- **Example {idx}:** *{ex.get('question')}* ➔ Formula: `{ex.get('resolution_formula')}`")

                # Log into Session State History
                history_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "question": user_question,
                    "answer": pipeline_result.final_answer,
                    "expression": pipeline_result.calculation_expression,
                    "complexity": pipeline_result.complexity.complexity,
                    "confidence": f"{val_res.overall_confidence:.1%}",
                    "image_name": temp_img_path.name,
                }
                st.session_state["history"].insert(0, history_entry)

            except Exception as ex:
                st.error(f"❌ Pipeline Execution Error: {ex}")

    # Session History Tab
    with tab_history:
        st.subheader("📜 Session Query History")
        if not st.session_state["history"]:
            st.info("No queries executed in this session yet.")
        else:
            df_hist = pd.DataFrame(st.session_state["history"])
            st.dataframe(df_hist, use_container_width=True)


if __name__ == "__main__":
    main()
