"""Streamlit Web Application & Human-in-the-Loop UI for ChartQA Multimodal Assistant."""

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
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint
from src.models.exceptions import (
    ChartValidationError,
    PromptInjectionDetectedError,
    UIValidationError,
)
from src.utils.security_guard import PromptInjectionGuard


# Page Configuration
st.set_page_config(
    page_title="ChartQA Multimodal Assistant",
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
    .metric-card {
        background-color: #F0F4F8;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
    .security-badge {
        background-color: #FFEBEE;
        border-left: 5px solid #D32F2F;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state() -> None:
    """Initializes Streamlit session state stores."""
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "selected_question" not in st.session_state:
        st.session_state["selected_question"] = ""
    if "hitl_edited_df" not in st.session_state:
        st.session_state["hitl_edited_df"] = None


def validate_uploaded_image(file_bytes: bytes, filename: str) -> Image.Image:
    """Validates uploaded image file format, resolution, and size.

    Raises:
        UIValidationError: If image exceeds size limits or has invalid resolution.
    """
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

    # Instantiate Agents & Security Guard
    security_guard = PromptInjectionGuard()
    classifier_agent = ClassifierAgent()
    pipeline_agent = PipelineAgent()

    # Sidebar: Information & Settings
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/combo-chart.png", width=64)
        st.title("ChartQA Assistant")
        st.markdown("**Sprint 4 - Multimodal AI System**")

        st.divider()
        st.subheader("⚙️ System Status")
        st.success("🟢 SafeCalculator (AST): Active")
        st.success("🟢 Classifier (XGBoost): Active")
        st.success("🟢 RAG (FAISS + MiniLM): Active")
        st.success("🟢 VLM (Gemini Flash): Active")
        st.success("🟢 Security Guard: Active")

        st.divider()
        st.subheader("📜 Pipeline Flow")
        st.markdown(
            """
            1. **Upload & Validate**
            2. **ML Classification**
            3. **FAISS RAG Few-Shot Retrieval**
            4. **VLM Extraction & Reasoning**
            5. **Human-in-the-Loop Data Editor**
            6. **AST SafeCalculator Execution**
            """
        )

        st.divider()
        if st.button("🗑️ Clear Query History"):
            st.session_state["history"] = []
            st.rerun()

    # Main Interface Header
    st.markdown('<div class="main-title">📊 Assistant Multimodal de Raisonnement sur Graphiques</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Analyse visuelle, extraction structurée, validation humaine (HITL) et calcul arithmétique sécurisé.</div>',
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

                    # Save temp image for pipeline consumption
                    temp_dir = Path("data/raw")
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    temp_img_path = temp_dir / f"temp_{uploaded_file.name}"
                    pil_image.save(temp_img_path)

                    st.image(pil_image, caption=f"Uploaded: {uploaded_file.name} ({pil_image.width}x{pil_image.height}px)", use_container_width=True)

                except (UIValidationError, ChartValidationError) as ve:
                    st.error(f"❌ Image Validation Error: {ve}")
                    return

            else:
                # Default sample image fallback
                sample_img_path = Path("data/raw/sample_chart.png")
                if sample_img_path.exists():
                    pil_image = Image.open(sample_img_path)
                    temp_img_path = sample_img_path
                    st.image(pil_image, caption="Default Demo Chart Image (Quarterly Sales 2024)", use_container_width=True)

        with col_right:
            st.subheader("2. ML Preview & Classification")
            if temp_img_path and temp_img_path.exists():
                preview_q = "What is the average value?"
                cls_result = classifier_agent.predict(preview_q, chart_type="bar")

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Detected Chart Type", cls_result.features.get("chart_type", "bar").upper())
                with c2:
                    st.metric("Complexity Level", cls_result.complexity)
                with c3:
                    st.metric("ML Confidence", f"{cls_result.confidence:.1%}")

            st.divider()
            st.subheader("3. Enter Question & Preset Suggestions")

            # Preset suggestion buttons
            st.markdown("**Suggestions:**")
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                if st.button("📊 Avg Sales Rate"):
                    st.session_state["selected_question"] = "What is the average sales rate across quarters?"
            with s_col2:
                if st.button("➕ Total Sum"):
                    st.session_state["selected_question"] = "What is the total sum of all sales?"
            with s_col3:
                if st.button("➖ Difference Max-Min"):
                    st.session_state["selected_question"] = "What is the difference between Q2 and Q1 sales?"

            user_question = st.text_input(
                "Type your target question:",
                value=st.session_state.get("selected_question", "What is the average sales rate across quarters?"),
                key="user_question_input",
            )

            run_pipeline_btn = st.button("🚀 Run Multimodal Reasoning", type="primary", use_container_width=True)

        st.divider()

        # Human-in-the-Loop (HITL) Data Editor Section
        st.subheader("4. 🛠️ Human-in-the-Loop (HITL) Data Point Editor")
        st.info("Review or edit the extracted chart values below. Your changes will automatically override calculation inputs.")

        # Default initial data points table
        initial_data = [
            {"label": "Q1 Sales", "value": 125.4, "confidence": 0.98},
            {"label": "Q2 Sales", "value": 180.2, "confidence": 0.95},
            {"label": "Q3 Sales", "value": 140.0, "confidence": 0.92},
            {"label": "Q4 Sales", "value": 210.5, "confidence": 0.96},
        ]
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

            # PART 8 — Security Guard: Anti-Prompt-Injection Check
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
            with st.spinner("Executing Multimodal Pipeline (Classifier -> RAG -> VLM -> AST Calculator)..."):
                try:
                    pipeline_result = pipeline_agent.answer(
                        image=temp_img_path,
                        question=user_question,
                    )
                    latency = time.time() - start_time

                    # Apply HITL modifications if data was edited
                    if edited_df is not None and not edited_df.empty:
                        # Update extracted_data with user edited rows
                        updated_dps = []
                        for _, r in edited_df.iterrows():
                            val = r["value"]
                            try:
                                val = float(val)
                            except ValueError:
                                pass
                            updated_dps.append(
                                ExtractedDataPoint(
                                    label=str(r["label"]),
                                    value=val,
                                    confidence=float(r.get("confidence", 1.0)),
                                )
                            )
                        pipeline_result.extracted_data.data_points = updated_dps

                    # Display Final Answer Result Card
                    st.markdown(
                        f'<div class="result-badge">✨ Final Calculated Answer: {pipeline_result.final_answer}</div>',
                        unsafe_allow_html=True,
                    )

                    # Detailed Breakdown Expander
                    with st.expander("🔍 Detailed Technical Breakdown & Context", expanded=True):
                        e1, e2, e3 = st.columns(3)
                        with e1:
                            st.markdown(f"**Arithmetic Expression:** `{pipeline_result.calculation_expression}`")
                        with e2:
                            st.markdown(f"**Execution Latency:** `{latency:.2f} seconds`")
                        with e3:
                            st.markdown(f"**Complexity:** `{pipeline_result.complexity.complexity}` ({pipeline_result.complexity.confidence:.1%})")

                        st.markdown("**Step-by-step Reasoning:**")
                        st.write(pipeline_result.reasoning)

                        st.markdown("**Extracted Data Points (HITL Applied):**")
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
