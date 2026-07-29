@echo off
REM Playwright RAG chatbot (LangChain + Ollama)
REM Ensure: ollama pull qwen2.5-coder:1.5b
REM         ollama pull nomic-embed-text
cd /d "%~dp0"
py -3 -m streamlit run app.py
