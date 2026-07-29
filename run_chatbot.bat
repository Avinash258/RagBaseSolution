@echo off
REM Run Playwright RAG chatbot UI (uses local Ollama)
cd /d "%~dp0"
py -3 -m streamlit run app.py
