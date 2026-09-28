# RagBaseSolution â€” Playwright Testing Chatbot (RAG)

Local **RAG** chatbot for Playwright testing knowledge â€” ChromaDB + Ollama with a self-improving knowledge base.

> Pairs with [AI-Shadow-Product-Owner](https://github.com/Avinash258/AI-Shadow-Product-Owner) Â· [Portfolio](https://avinash258.github.io/Protfolio/)

## Overview

Ask questions about Playwright testing and get answers grounded in a local vector store. When the model needs broader context it can fall back to the web; answers marked correct can be saved back into the knowledge base so the system improves over time.

**Flow:** Vector DB (Chroma) â†’ Ollama LLM â†’ optional web lookup â†’ save to KB when validated

## Features

- Local-first RAG over Playwright / QA knowledge
- Indexing and ingest pipelines for custom docs
- Threshold calibration for retrieval quality
- Smoke tests for chat and web-learn paths
- Batch helpers for Windows (`run_chatbot.bat`)

## Stack

- Python Â· ChromaDB Â· Ollama
- Knowledge corpus under `knowledge/`
- RAG pipeline under `rag/`

## Getting started

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Index knowledge, then chat
python index_knowledge.py
python app.py
# or
python ask.py "How do I use Playwright fixtures?"
```

Optional: `ingest_sources.py`, `calibrate_threshold.py`, and `smoke_*.py` for ops and validation.

## Project layout

```
knowledge/   source documents for the KB
rag/         retrieval and generation helpers
docs/        design / usage notes
app.py       chatbot entry
ask.py       one-shot Q&A CLI
```

## Author

**Avinash Sharma** â€” QA Automation Architect / Lead SDET  
[GitHub](https://github.com/Avinash258) Â· [LinkedIn](https://www.linkedin.com/in/p-avinash-sharma-8b0203b9/) Â· [Portfolio](https://avinash258.github.io/Protfolio/)
