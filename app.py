"""Root Application Entrypoint for GrapheinAI.

Supports:
1. Streamlit Community Cloud & Hugging Face Spaces (via Streamlit execution)
2. FastAPI ASGI Server Deployment (via Uvicorn / Gunicorn)
"""

import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Expose FastAPI app for ASGI runners
from src.app.api import app as app

if __name__ == "__main__":
    # Streamlit execution fallback
    try:
        import streamlit as st
        if st._is_running_with_streamlit:
            from src.app.streamlit_app import main
            main()
        else:
            import uvicorn
            uvicorn.run("app:app", host="0.0.0.0", port=8088, reload=False)
    except Exception:
        import uvicorn
        uvicorn.run("app:app", host="0.0.0.0", port=8088, reload=False)
