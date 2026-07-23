"""Production FastAPI REST Backend for ChartQA Commercial SaaS AI Web Application."""

import json
import io
import time
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from src.agents.classifier_agent import ClassifierAgent
from src.agents.explainability_engine import ExplainabilityEngine
from src.agents.graph_interpreter import GraphInterpreter
from src.agents.multi_chart_pipeline import MultiChartPipelineAgent
from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.recommendation_engine import RecommendationEngine
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.agents.validation_agent import ValidationAgent
from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint, PipelineResult
from src.models.session import AnalysisSession, SessionStatus
from src.models.user import (
    AuthCredentials,
    AuthResponse,
    ForgotPasswordRequest,
    PasswordResetRequest,
    ResetPasswordRequest,
    SignupRequest,
    UpdateProfileRequest,
    UserProfile,
)
from src.models.workspace import (
    ActivityLog,
    AnalysisComment,
    ShareAnalysisRequest,
    ShareLinkRequest,
    Workspace,
)
from src.services.cache_manager import CacheManager
from src.services.collaboration_service import CollaborationService
from src.services.email_service import EmailService
from src.services.observability_service import ObservabilityService
from src.services.session_manager import AnalysisSessionManager
from src.services.supabase_service import SupabaseService
from src.services.task_queue import TaskQueueManager
from src.utils.chart_detector import ChartTypeDetector
from src.utils.confidence_calculator import ConfidenceCalculator
from src.utils.data_validator import DataAnomalyDetector
from src.utils.error_handler import EnterpriseErrorHandler
from src.utils.multi_chart_detector import MultiChartDetector
from src.utils.ocr_engine import OCREngine
from src.utils.anomaly_detector import AnomalyDetector
from src.utils.chart_intelligence_engine import ChartIntelligenceEngine
from src.utils.pdf_generator import PDFReportGenerator
from src.utils.security_guard import PromptInjectionGuard
from src.utils.stat_calculator import StatisticalEngine
from src.utils.structured_logger import StructuredLogger

app = FastAPI(
    title="GrapheinAI SaaS Enterprise API",
    description="REST API backend for GrapheinAI Multimodal Visual Analytics SaaS Platform.",
    version="5.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
STATIC_DIR = Path(__file__).resolve().parent / "static"
I18N_DIR = BASE_DIR / "src" / "i18n" / "translations"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Instantiate Core AI Services & Enterprise Hardening Infrastructure
security_guard = PromptInjectionGuard()
error_handler = EnterpriseErrorHandler()
structured_logger = StructuredLogger()
observability_service = ObservabilityService()
task_queue_manager = TaskQueueManager()
explainability_engine = ExplainabilityEngine()
confidence_calculator = ConfidenceCalculator()
data_anomaly_detector = DataAnomalyDetector()

ocr_engine = OCREngine()
chart_detector = ChartTypeDetector()
multi_chart_detector = MultiChartDetector()
chart_intelligence = ChartIntelligenceEngine()
pdf_generator = PDFReportGenerator()
cache_manager = CacheManager()
session_manager = AnalysisSessionManager(cache_manager=cache_manager)
supabase_service = SupabaseService()
recommendation_engine = RecommendationEngine()
email_service = EmailService()
collaboration_service = CollaborationService(email_service=email_service)

# Global Agent Instances
pipeline_agent = PipelineAgent(chart_intelligence=chart_intelligence)
reasoning_agent = ReasoningAgent()
graph_interpreter = GraphInterpreter()
multi_chart_pipeline = MultiChartPipelineAgent(pipeline_agent=pipeline_agent)
classifier_agent = ClassifierAgent()
validation_agent = ValidationAgent()

@app.exception_handler(Exception)
def global_enterprise_exception_handler(request: Request, exc: Exception):
    err_res = error_handler.handle_exception(exc, category="API")
    structured_logger.error("API", err_res.technical_message, path=request.url.path)
    return JSONResponse(status_code=500, content=err_res.model_dump())

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
I18N_DIR = Path(__file__).parent.parent / "i18n" / "translations"
if I18N_DIR.exists():
    app.mount("/i18n", StaticFiles(directory=str(I18N_DIR)), name="i18n")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class HITLDataOverride(BaseModel):
    label: str | None = None
    value: float | int | str
    confidence: float = 1.0


# --------------------------------------------------------------------
# FASTAPI ROUTE GUARDS & DEPENDENCIES
# --------------------------------------------------------------------

def get_current_user(authorization: str | None = Header(None)) -> UserProfile:
    """FastAPI Header Dependency enforcing authentication for protected routes."""
    token = None
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1].strip()
        else:
            token = authorization.strip()

    user = supabase_service.verify_token(token) if token else None
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Accès non autorisé. Veuillez vous connecter à votre compte GrapheinAI.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    """FastAPI Dependency enforcing admin role privileges."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès refusé. Privilèges Administrateur requis.",
        )
    return current_user


# --------------------------------------------------------------------
# SYSTEM HEALTH ENDPOINT (Public)
# --------------------------------------------------------------------

@app.get("/api/health")
def health_check() -> dict[str, Any]:
    """Health check endpoint indicating pipeline component status."""
    reasoning_agent._ensure_client()
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


# --------------------------------------------------------------------
# ENTERPRISE AUTHENTICATION & IDENTITY ENDPOINTS (Public & User)
# --------------------------------------------------------------------

@app.post("/api/auth/signup")
def auth_signup(req: SignupRequest) -> AuthResponse:
    """Registers a new user account with enterprise profile parameters."""
    try:
        return supabase_service.signup(req)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/auth/login")
def auth_login(creds: AuthCredentials) -> AuthResponse:
    """Authenticates user credentials."""
    try:
        return supabase_service.login(email=creds.email, password=creds.password)
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/auth/logout")
def auth_logout(authorization: str | None = Header(None)) -> dict[str, str]:
    """Terminates user session, invalidates token, and flushes active caches & Gemini context."""
    token = None
    if authorization:
        token = authorization.split(" ")[1].strip() if authorization.startswith("Bearer ") else authorization.strip()
        supabase_service.logout(token)

    cache_manager.clear_all()
    session_manager.clear_active_session()
    return {"status": "logged_out", "message": "Session déconnectée et contexte nettoyé avec succès."}


@app.post("/api/auth/forgot-password")
def auth_forgot_password(req: ForgotPasswordRequest) -> dict[str, Any]:
    """Triggers password reset flow for specified user email."""
    reset_token = supabase_service.forgot_password(req.email)
    return {
        "status": "sent",
        "message": f"Un e-mail de réinitialisation a été envoyé à {req.email}.",
        "reset_token": reset_token,
    }


@app.post("/api/auth/reset-password")
def auth_reset_password(req: ResetPasswordRequest) -> dict[str, str]:
    """Resets user password."""
    target_email = req.email or "demo@graphein.ai"
    supabase_service.reset_password(target_email, req.new_password)
    return {"status": "success", "message": "Mot de passe réinitialisé avec succès."}


@app.get("/api/auth/me")
def get_me(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    """Retrieves authenticated user profile and SaaS metrics."""
    return current_user


@app.put("/api/user/profile")
def update_user_profile(
    req: UpdateProfileRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """Updates user profile information."""
    return supabase_service.update_profile(user_id=current_user.id, updates=req.model_dump(exclude_unset=True))


@app.get("/api/admin/users")
def admin_get_users(admin_user: UserProfile = Depends(require_admin)) -> dict[str, Any]:
    """Admin-only endpoint retrieving system user monitoring metrics."""
    return {
        "admin": admin_user.name,
        "role": admin_user.role,
        "status": "System operational",
        "user_count": len(supabase_service._mock_users),
    }


# --------------------------------------------------------------------
# PROTECTED SAAS ANALYSIS ENDPOINTS
# --------------------------------------------------------------------

@app.post("/api/extract")
async def extract_chart(
    file: UploadFile | None = File(None),
    image_filename: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
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
    session_id: str | None = Form(None),
    target_language: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Executes full multi-stage multimodal reasoning pipeline with AI personalization context."""
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

    # Process HITL overrides if supplied from UI data grid
    hitl_extraction = None
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

                hitl_extraction = ChartExtraction(
                    chart_type="bar",
                    data_points=updated_dps,
                    extraction_source="HITL User Grid Override",
                    metadata={"is_hitl_modified": True},
                )
        except Exception:
            pass

    start_t = time.time()
    result = pipeline_agent.answer(
        image=img_path,
        question=question,
        session_id=session_id or img_path.stem,
        hitl_extraction=hitl_extraction,
        target_language=target_language,
        user_profile=current_user,
    )

    latency = round(time.time() - start_t, 3)

    recs = recommendation_engine.generate_recommendations(
        extraction=result.extracted_data,
        user_profile=current_user,
        target_language=target_language or "fr",
    )

    xai = explainability_engine.generate_xai_report(result, target_language=target_language or "fr")
    confidence = confidence_calculator.calculate_confidence(result)
    anomalies = data_anomaly_detector.inspect_extraction(result.extracted_data)

    observability_service.record_metric("ANALYSIS", latency)
    structured_logger.info("API", f"Analysis completed for {img_path.name}", latency=latency)

    res_dict = result.model_dump()
    res_dict["execution_latency"] = latency
    res_dict["image_filename"] = img_path.name
    res_dict["recommendations"] = recs.model_dump()
    res_dict["xai_breakdown"] = xai.model_dump()
    res_dict["confidence_breakdown"] = confidence.model_dump()
    res_dict["data_validation_report"] = anomalies.model_dump()
    return res_dict


@app.get("/api/chat/history")
def get_chat_history(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieves conversation history turns for a chart session."""
    history = pipeline_agent.conversation_manager.get_history(session_id)
    return {
        "session_id": session_id,
        "turns": [turn.model_dump() for turn in history],
    }


@app.delete("/api/chat/history")
def clear_chat_history(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Clears conversation history turns for a chart session."""
    pipeline_agent.conversation_manager.clear_session(session_id)
    return {
        "session_id": session_id,
        "status": "cleared",
    }


@app.post("/api/report/pdf")
async def download_pdf_report(
    question: str = Form(...),
    image_filename: str = Form("sample_chart.png"),
    hitl_data_json: str | None = Form(None),
    target_language: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> Response:
    """Generates and returns downloadable official PDF report."""
    img_path = RAW_DATA_DIR / image_filename
    if not img_path.exists():
        img_path = RAW_DATA_DIR / "sample_chart.png"

    start_t = time.time()
    result = pipeline_agent.answer(
        image=img_path,
        question=question,
        target_language=target_language,
        user_profile=current_user,
    )

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
        target_language=target_language or "fr",
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ChartQA_Report_{img_path.stem}.pdf"},
    )


# --------------------------------------------------------------------
# SESSION MANAGEMENT REST ENDPOINTS (Protected)
# --------------------------------------------------------------------

@app.post("/api/session/new")
async def create_new_session(
    file: UploadFile | None = File(None),
    image_filename: str | None = Form(None),
    target_language: str | None = Form("fr"),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Creates a brand new isolated AnalysisSession and flushes previous context/caches."""
    lang = target_language if target_language in ["fr", "en"] else "fr"

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

    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Target chart image not found.")

    # Reset FAISS retrieval index
    pipeline_agent.retriever.reset_index()

    start_t = time.time()
    session = session_manager.create_session(
        image_path=img_path,
        file_name=img_path.name,
        target_language=lang,
        flush_cache=True,
    )
    session.user_id = current_user.id

    # Perform fresh vision extraction & structural analysis with ChartIntelligenceEngine
    ocr_boxes = ocr_engine.detect_ocr_text_boxes(img_path)
    chart_metadata = chart_intelligence.analyze_image(img_path, ocr_boxes)
    extraction = reasoning_agent.extract_chart_data(img_path, metadata=chart_metadata)
    chart_metadata = chart_intelligence.reconcile_with_vlm(chart_metadata, extraction.chart_type, vlm_confidence=0.92)

    stats = StatisticalEngine.compute_summary(extraction)
    anomalies = AnomalyDetector.detect_anomalies(extraction)
    insights = pipeline_agent.insight_agent.generate_insights(extraction)

    latency = round(time.time() - start_t, 3)

    session.chart_type = chart_metadata.chart_type.value
    session.chart_metadata = chart_metadata.model_dump()
    session.extraction = extraction
    session.statistics = stats
    session.anomalies = anomalies
    session.insights = insights
    session.execution_latency = latency
    session.status = SessionStatus.ANALYZED
    session_manager.save_active_session()

    # Persist to Supabase Database (RLS bound)
    supabase_service.save_analysis(user_id=current_user.id, session=session)

    return session.model_dump()


@app.get("/api/session/active")
def get_active_session(
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any] | None:
    """Retrieves current active analysis session."""
    session = session_manager.get_active_session()
    return session.model_dump() if session else None


@app.post("/api/session/reextract")
def reextract_session(
    target_language: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Completely flushes old extractions & caches, re-runs vision OCR & Gemini, updates stats & FAISS."""
    session = session_manager.get_active_session()
    if not session:
        raise HTTPException(status_code=400, detail="No active analysis session found.")

    lang = target_language or session.target_language
    img_path = Path(session.image_path)
    if not img_path.exists():
        img_path = RAW_DATA_DIR / session.file_name

    # Flush caches and reset FAISS
    cache_manager.clear_extraction_cache(img_path.stem)
    pipeline_agent.retriever.reset_index()

    start_t = time.time()
    extraction = reasoning_agent.extract_chart_data(img_path)
    structure = chart_detector.detect_chart_structure(img_path)
    stats = StatisticalEngine.compute_summary(extraction)
    anomalies = AnomalyDetector.detect_anomalies(extraction)
    insights = pipeline_agent.insight_agent.generate_insights(extraction)

    latency = round(time.time() - start_t, 3)

    session.user_id = current_user.id
    session.extraction = extraction
    session.chart_type = structure.detected_type
    session.statistics = stats
    session.anomalies = anomalies
    session.insights = insights
    session.execution_latency = latency
    session.target_language = lang
    session.interpretation = None  # Reset interpretation so user can re-generate explicitly
    session.status = SessionStatus.ANALYZED
    session_manager.save_active_session()

    supabase_service.save_analysis(user_id=current_user.id, session=session)

    res = session.model_dump()
    res["message"] = "Re-extraction completed successfully." if lang == "en" else "Ré-extraction effectuée avec succès."
    return res


@app.post("/api/session/interpret")
def generate_session_interpretation(
    target_language: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Explicitly triggers scientific narrative report generation (GraphInterpreter) for active session."""
    session = session_manager.get_active_session()
    if not session or not session.extraction:
        raise HTTPException(status_code=400, detail="No active session with extracted data available.")

    lang = target_language or session.target_language
    recs = recommendation_engine.generate_recommendations(
        extraction=session.extraction,
        user_profile=current_user,
        target_language=lang,
    )
    report = graph_interpreter.interpret_chart(
        extraction=session.extraction,
        target_language=lang,
        user_profile=current_user,
        recommendations=recs,
    )

    session.interpretation = report
    session.status = SessionStatus.INTERPRETED
    session_manager.save_active_session()

    supabase_service.save_analysis(user_id=current_user.id, session=session)

    return {
        "session_id": session.session_id,
        "interpretation": report,
        "recommendations": recs.model_dump(),
        "status": session.status.value,
    }


@app.get("/api/session/history")
def get_session_history(
    current_user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Returns sorted list of private saved analysis sessions for authenticated user."""
    return supabase_service.get_user_analyses(current_user.id)


@app.post("/api/session/reopen/{session_id}")
def reopen_session(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Reopens a historical session into the active workspace."""
    try:
        session = session_manager.reopen_session(session_id)
        return session.model_dump()
    except KeyError:
        user_analyses = supabase_service.get_user_analyses(current_user.id)
        for a in user_analyses:
            if a.get("session_id") == session_id:
                return a
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")


# ====================================================================
# ENTERPRISE WORKSPACES & REAL-TIME COLLABORATION ENDPOINTS
# ====================================================================

@app.get("/api/workspaces")
def list_user_workspaces(
    current_user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Returns list of accessible workspaces for authenticated user."""
    # Ensure default workspace exists
    collaboration_service.get_or_create_default_workspace(current_user)
    workspaces = collaboration_service.get_user_workspaces(current_user.id)
    return [w.model_dump() for w in workspaces]


@app.post("/api/workspaces")
def create_user_workspace(
    name: str = Form(...),
    description: str = Form(""),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Creates a new enterprise workspace."""
    ws = collaboration_service.create_workspace(name=name, owner=current_user, description=description)
    return ws.model_dump()


@app.get("/api/workspaces/{workspace_id}/members")
def list_workspace_members(
    workspace_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Returns active team members in workspace."""
    members = [m for m in collaboration_service._workspace_members if m.workspace_id == workspace_id]
    return [m.model_dump() for m in members]


@app.post("/api/workspaces/{workspace_id}/members")
def add_workspace_member_endpoint(
    workspace_id: str,
    email: str = Form(...),
    role: str = Form("viewer"),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Invites / adds a collaborator member to workspace."""
    # Check if target user account exists
    target_profile = supabase_service.get_profile_by_email(email)
    if not target_profile:
        # User account does not exist -> Create invitation and send email via MailDev
        signed_link = collaboration_service.create_signed_share_link(
            actor=current_user,
            workspace_id=workspace_id,
            role=role,
        )
        collaboration_service.email_service.send_invitation_email(
            recipient_email=email,
            inviter_name=current_user.name,
            resource_name="Workspace",
            share_url=signed_link.share_url,
            expires_at=signed_link.expires_at,
            role=role,
        )
        return {
            "status": "invited",
            "message": f"Invitation envoyée par e-mail à {email}.",
            "share_url": signed_link.share_url,
        }

    member = collaboration_service.add_workspace_member(
        workspace_id=workspace_id,
        member_user=target_profile,
        role=role,
        actor=current_user,
    )
    return {
        "status": "added",
        "member": member.model_dump(),
    }


@app.delete("/api/workspaces/{workspace_id}/members/{user_id}")
def remove_workspace_member_endpoint(
    workspace_id: str,
    user_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Removes a collaborator from workspace."""
    success = collaboration_service.remove_workspace_member(
        workspace_id=workspace_id,
        target_user_id=user_id,
        actor=current_user,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Member not found in workspace.")
    return {"status": "removed"}


@app.post("/api/session/{session_id}/share")
def share_analysis_endpoint(
    session_id: str,
    email: str = Form(...),
    role: str = Form("editor"),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Shares an analysis session with an email address."""
    target_profile = supabase_service.get_profile_by_email(email)
    if not target_profile:
        signed_link = collaboration_service.create_signed_share_link(
            actor=current_user,
            analysis_id=session_id,
            role=role,
        )
        collaboration_service.email_service.send_invitation_email(
            recipient_email=email,
            inviter_name=current_user.name,
            resource_name=f"Analyse {session_id}",
            share_url=signed_link.share_url,
            expires_at=signed_link.expires_at,
            role=role,
        )
        return {
            "status": "invited",
            "message": f"Invitation envoyée par e-mail à {email}.",
            "share_url": signed_link.share_url,
        }

    perm = collaboration_service.grant_analysis_permission(
        analysis_id=session_id,
        target_user=target_profile,
        role=role,
        actor=current_user,
    )
    return {
        "status": "shared",
        "permission": perm.model_dump(),
    }


@app.get("/api/session/{session_id}/comments")
def get_analysis_comments_endpoint(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Returns sorted comments for an analysis session."""
    comments = collaboration_service.get_comments(session_id)
    return [c.model_dump() for c in comments]


@app.post("/api/session/{session_id}/comments")
def add_analysis_comment_endpoint(
    session_id: str,
    text: str = Form(...),
    parent_id: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Adds a new threaded comment or reply."""
    comment = collaboration_service.add_comment(
        analysis_id=session_id,
        author=current_user,
        text=text,
        parent_id=parent_id,
    )
    return comment.model_dump()


@app.get("/api/session/{session_id}/activity")
def get_analysis_activity_endpoint(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Returns audit trail activity logs for session."""
    logs = collaboration_service.get_activity_logs(analysis_id=session_id)
    return [l.model_dump() for l in logs]


@app.post("/api/share/link/create")
def create_share_link_endpoint(
    analysis_id: str | None = Form(None),
    workspace_id: str | None = Form(None),
    role: str = Form("editor"),
    expires_in_hours: int = Form(168),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Generates a cryptographically signed expiring share URL token."""
    res = collaboration_service.create_signed_share_link(
        actor=current_user,
        analysis_id=analysis_id,
        workspace_id=workspace_id,
        role=role,
        expires_in_hours=expires_in_hours,
    )
    return res.model_dump()


@app.get("/api/share/link/{token}")
def verify_share_link_endpoint(token: str) -> dict[str, Any]:
    """Verifies signed share link token signature and expiration timestamp."""
    invitation = collaboration_service.verify_signed_share_link(token)
    if not invitation:
        raise HTTPException(status_code=400, detail="Ce lien de partage est invalide ou a expiré.")

    return {
        "status": "valid",
        "invitation": invitation.model_dump(),
        "redirect_url": f"/#analysis?session_id={invitation.analysis_id}" if invitation.analysis_id else "/#workspaces",
    }


@app.get("/api/notifications")
def list_user_notifications_endpoint(
    current_user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Returns user in-app notifications."""
    notis = collaboration_service.get_user_notifications(current_user.id)
    return [n.model_dump() for n in notis]


@app.put("/api/notifications/{notification_id}/read")
def mark_notification_read_endpoint(
    notification_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Marks notification as read."""
    success = collaboration_service.mark_notification_read(notification_id, current_user.id)
    return {"success": success}


# ====================================================================
# MULTI-CHART INTELLIGENCE & DOCUMENT AI ENDPOINTS
# ====================================================================

@app.get("/api/charts")
def get_session_detected_charts(
    session_id: str | None = None,
    image_filename: str | None = None,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Detects and returns all sub-chart regions in the target image document."""
    fname = image_filename or "sample_chart.png"
    img_path = RAW_DATA_DIR / fname
    if not img_path.exists():
        img_path = RAW_DATA_DIR / "sample_chart.png"

    detection = multi_chart_detector.detect_charts(img_path)
    return detection.model_dump()


@app.get("/api/charts/{chart_id}")
def get_detected_chart_details(
    chart_id: str,
    image_filename: str | None = None,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Returns details for a specific detected sub-chart."""
    fname = image_filename or "sample_chart.png"
    img_path = RAW_DATA_DIR / fname
    detection = multi_chart_detector.detect_charts(img_path)

    for c in detection.detected_charts:
        if c.chart_id == chart_id:
            return c.model_dump()

    raise HTTPException(status_code=404, detail=f"Chart '{chart_id}' not found.")


@app.post("/api/charts/{chart_id}/analyze")
def analyze_specific_sub_chart(
    chart_id: str,
    question: str = Form("Analyser ce graphique spécifique"),
    image_filename: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Executes independent analysis on a single selected sub-chart."""
    fname = image_filename or "sample_chart.png"
    img_path = RAW_DATA_DIR / fname
    detection = multi_chart_detector.detect_charts(img_path)

    target_chart = next((c for c in detection.detected_charts if c.chart_id == chart_id), None)
    crop_path = Path(target_chart.cropped_image_path) if (target_chart and target_chart.cropped_image_path) else img_path

    start_t = time.time()
    result = pipeline_agent.answer(
        image=crop_path,
        question=question,
        session_id=f"single_{chart_id}",
        user_profile=current_user,
    )
    latency = round(time.time() - start_t, 3)

    res_dict = result.model_dump()
    res_dict["execution_latency"] = latency
    res_dict["chart_id"] = chart_id
    return res_dict


@app.post("/api/charts/compare")
def compare_sub_charts_endpoint(
    question: str = Form("Comparer les graphiques détectés"),
    image_filename: str | None = Form(None),
    selected_chart_ids: str | None = Form(None),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Executes multi-chart parallel pipeline and cross-chart comparative fusion."""
    fname = image_filename or "sample_chart.png"
    img_path = RAW_DATA_DIR / fname

    start_t = time.time()
    multi_res = multi_chart_pipeline.process_multi_chart_document(
        image_path=img_path,
        question=question,
        session_id="multi_compare",
        user_profile=current_user,
    )
    latency = round(time.time() - start_t, 3)

    res_dict = multi_res.model_dump()
    res_dict["execution_latency"] = latency
    return res_dict


# ====================================================================
# ENTERPRISE HARDENING: ASYNC QUEUE & ADMIN OBSERVABILITY ENDPOINTS
# ====================================================================

@app.post("/api/tasks/submit")
def submit_async_task(
    task_type: str = Form("EXTRACTION"),
    image_filename: str = Form("sample_chart.png"),
    question: str = Form("Analyser ce graphique"),
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Submits a heavy processing task to the async TaskQueueManager."""
    img_path = RAW_DATA_DIR / image_filename

    def _run_analysis():
        return pipeline_agent.answer(image=img_path, question=question, user_profile=current_user).model_dump()

    task_item = task_queue_manager.submit_task(task_type, _run_analysis)
    structured_logger.info("TASK_QUEUE", f"Submitted async task '{task_item.task_id}' ({task_type})")
    return task_item.model_dump()


@app.get("/api/tasks/{task_id}/status")
def get_async_task_status(
    task_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Returns current status and progress percentage for a queued async task."""
    task = task_queue_manager.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return task.model_dump()


@app.get("/api/admin/metrics")
def get_admin_observability_metrics(
    admin_user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Returns real-time system latencies, CPU/Memory stats for Admin SRE dashboard."""
    report = observability_service.get_system_report(active_users=1)
    return report.model_dump()


@app.get("/api/admin/logs")
def get_admin_system_logs(
    level: str | None = None,
    limit: int = 100,
    admin_user: UserProfile = Depends(require_admin),
) -> list[dict[str, Any]]:
    """Returns in-memory structured logs for Admin SRE log viewer."""
    return structured_logger.get_admin_logs(limit=limit, level_filter=level)


# Serve static single-page web app at root
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
