"""Unit and integration test suite for Enterprise SaaS UI Design System V2, Light/Dark ThemeManager, and static assets."""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from src.app.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index_html_structure_and_sidebar():
    """Verifies index.html contains fixed sidebar, ThemeManager, Google Fonts, and DataGrid."""
    html_path = Path("src/app/static/index.html")
    assert html_path.exists(), "src/app/static/index.html must exist"

    content = html_path.read_text(encoding="utf-8")

    # Plus Jakarta Sans Font & ThemeManager
    assert 'Plus+Jakarta+Sans' in content or 'Plus Jakarta Sans' in content
    assert 'theme_manager.js' in content

    # Fixed Sidebar Navigation Links
    assert 'id="nav-dashboard"' in content
    assert 'id="nav-analysis"' in content
    assert 'id="nav-history"' in content
    assert 'id="nav-reports"' in content
    assert 'id="nav-admin-console"' in content
    assert 'id="nav-monitoring"' in content
    assert 'id="nav-performance"' in content

    # Dashboard & Studio Screen Content Containers
    assert 'id="tab-dashboard-content"' in content
    assert 'id="tab-analysis-content"' in content
    assert 'id="tab-history-content"' in content
    assert 'id="tab-reports-content"' in content

    # DataGrid & Controls
    assert 'id="datagrid-search"' in content
    assert 'id="datagrid-table"' in content
    assert 'exportDataGridCSV' in content
    assert 'filterDataGrid' in content
    assert 'sortDataGrid' in content


def test_design_system_css_tokens():
    """Verifies design_system.css token file contains Light and Dark mode CSS variables."""
    css_path = Path("src/app/static/css/design_system.css")
    assert css_path.exists(), "src/app/static/css/design_system.css must exist"

    content = css_path.read_text(encoding="utf-8")

    # Light Theme Variables
    assert "--bg-canvas: #F8FAFC;" in content
    assert "--bg-surface: #FFFFFF;" in content
    assert "--border: #E2E8F0;" in content
    assert "--primary: #2563EB;" in content

    # Dark Theme Variables
    assert ".dark {" in content
    assert "--bg-canvas: #0F172A;" in content
    assert "--bg-surface: #111827;" in content
    assert "--border: #334155;" in content

    # Components & Utilities
    assert ".pro-card" in content
    assert ".pro-input" in content
    assert ".pro-btn-primary" in content
    assert ".pro-btn-secondary" in content
    assert ".pro-btn-ghost" in content
    assert ".pro-btn-danger" in content
    assert ".datagrid-table" in content
    assert ".badge-status" in content


def test_theme_manager_js_file():
    """Verifies theme_manager.js script exists and contains instant theme toggle logic."""
    js_path = Path("src/app/static/js/theme_manager.js")
    assert js_path.exists(), "src/app/static/js/theme_manager.js must exist"

    content = js_path.read_text(encoding="utf-8")
    assert "initTheme" in content
    assert "toggleTheme" in content
    assert "graphein_theme" in content


def test_i18n_dictionaries_contain_enterprise_keys():
    """Verifies fr.json and en.json dictionaries contain enterprise dashboard and DataGrid keys."""
    import json

    fr_path = Path("src/i18n/translations/fr.json")
    en_path = Path("src/i18n/translations/en.json")
    assert fr_path.exists()
    assert en_path.exists()

    fr_dict = json.loads(fr_path.read_text(encoding="utf-8"))
    en_dict = json.loads(en_path.read_text(encoding="utf-8"))

    for dict_obj in [fr_dict, en_dict]:
        assert "dashboard" in dict_obj
        assert "total_analyses" in dict_obj["dashboard"]
        assert "datagrid" in dict_obj
        assert "export_csv" in dict_obj["datagrid"]
        assert "nav" in dict_obj
        assert "dashboard" in dict_obj["nav"]


def test_api_serves_frontend_css_and_js(client):
    """Verifies FastAPI GET / serves index.html, static css, and static js."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Enterprise Data Analytics" in res_root.text

    res_css = client.get("/static/css/design_system.css")
    assert res_css.status_code == 200
    assert "--bg-canvas" in res_css.text

    res_js = client.get("/static/js/theme_manager.js")
    assert res_js.status_code == 200
    assert "toggleTheme" in res_js.text
