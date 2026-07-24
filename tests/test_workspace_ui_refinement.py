"""Integration and UI test suite for Workspace UI Refinement, Stepper, Settings Modal, Drag & Drop Upload, and QuestionRouter."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.app.api import app
from src.services.gemini.router import QuestionRouter, RouteTarget


@pytest.fixture
def client():
    return TestClient(app)


def test_question_router_conversational_natural_language():
    """Verifies that QuestionRouter routes conversational queries (bonjour, explique, comment) to GEMINI_VLM."""
    router = QuestionRouter()
    
    # Conversational natural language queries
    assert router.route_question("Bonjour, peux-tu m'expliquer ce graphique ?") == RouteTarget.GEMINI_VLM
    assert router.route_question("Comment interpréter les tendances observées ?") == RouteTarget.GEMINI_VLM
    assert router.route_question("Pourquoi cette catégorie est en baisse ?") == RouteTarget.GEMINI_VLM

    # Math queries still route to AST_CALCULATOR
    assert router.route_question("Quelle est la somme des ventes ?") == RouteTarget.AST_CALCULATOR
    assert router.route_question("Quel est le total de la distribution ?") == RouteTarget.AST_CALCULATOR


def test_ui_index_html_stepper_and_settings_modal_structure():
    """Verifies index.html contains the 5-step Stepper, Drag & Drop Hero Zone, and 6-tab Settings Modal."""
    html_path = Path("src/app/static/index.html")
    assert html_path.exists()

    content = html_path.read_text(encoding="utf-8")

    # 1. 5-step SaaS Stepper
    assert 'id="workflow-stepper"' in content
    assert 'step-1-item' in content
    assert 'step-5-item' in content

    # 2. Hero Drag & Drop Zone
    assert 'id="upload-hero-container"' in content
    assert 'handleDragOver' in content
    assert 'handleDrop' in content

    # 3. Dynamic Progress Bar
    assert 'id="analysis-progress-container"' in content
    assert 'saas-progress-fill' in content

    # 4. Settings Control Center Modal
    assert 'id="settings-control-modal"' in content
    assert 'openSettingsControlModal' in content
    assert 'switchSettingsTab' in content

    # 5. Header Settings gear button & user context text badge
    assert 'openSettingsControlModal' in content
    assert 'id="user-context-text"' in content


def test_design_system_css_saas_classes():
    """Verifies design_system.css contains Hero Upload, Stepper, and Settings Modal classes."""
    css_path = Path("src/app/static/css/design_system.css")
    assert css_path.exists()

    content = css_path.read_text(encoding="utf-8")

    assert ".upload-hero-zone" in content
    assert ".saas-stepper" in content
    assert ".saas-progress-bar" in content
    assert ".settings-modal-dialog" in content
