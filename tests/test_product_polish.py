"""Unit and integration test suite for Product Polish, Design System, Onboarding, Skeleton Loading, Tooltips, and Responsiveness."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.app.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_design_system_css_tokens_and_skeleton_loading():
    """Verifies that design_system.css contains skeleton loading, tooltips, responsive rules, and theme variables."""
    css_path = Path("src/app/static/css/design_system.css")
    assert css_path.exists()
    content = css_path.read_text(encoding="utf-8")

    # Light & Dark theme variable tokens
    assert "--bg-canvas:" in content
    assert "--bg-surface:" in content
    assert "--primary:" in content
    assert ".dark {" in content

    # Product Polish UX Tokens
    assert "skeleton-box" in content
    assert "skeletonPulse" in content
    assert "[data-tooltip]" in content
    assert "empty-state-card" in content

    # Responsive breakpoints
    assert "@media (max-width: 1024px)" in content
    assert "@media (max-width: 768px)" in content


def test_index_html_onboarding_tooltips_and_components():
    """Verifies that index.html includes onboarding tour modal, data-tooltip attributes, empty states, and script functions."""
    html_path = Path("src/app/static/index.html")
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")

    # Onboarding Tour Modal
    assert 'id="onboarding-modal-backdrop"' in content
    assert 'id="tour-step-title"' in content
    assert 'id="tour-step-desc"' in content

    # Tooltips
    assert 'data-tooltip=' in content

    # Script controllers
    assert "startOnboardingTour" in content
    assert "nextTourStep" in content
    assert "closeTourModal" in content

    # Performance Dashboard tab
    assert 'id="tab-performance-content"' in content
    assert 'id="nav-performance"' in content


def test_frontend_static_routes_served(client):
    """Verifies that index.html and design_system.css are served with 200 OK by FastAPI."""
    res_html = client.get("/")
    assert res_html.status_code == 200
    assert "Graphein" in res_html.text

    res_css = client.get("/static/css/design_system.css")
    assert res_css.status_code == 200
    assert "skeleton-box" in res_css.text
