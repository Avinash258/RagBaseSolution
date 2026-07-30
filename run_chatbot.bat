@echo off
REM Multi-mode Testing Hub (specialist agents + AI Reconcile)
REM Ensure: ollama pull qwen2.5-coder:1.5b
REM         ollama pull nomic-embed-text
REM Optional: GEMINI_API_KEY / NVIDIA_API_KEY in .env
cd /d "%~dp0"
py -3 -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
