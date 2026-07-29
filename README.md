# Playwright Testing Chatbot (RAG)

Local RAG chatbot for Playwright testing.

**Flow:** Vector DB (Chroma) → LangChain + Ollama `qwen2.5-coder:1.5b` → ask if satisfied → Internet only if not → Save to KB when marked correct

## Requirements

- Python 3.12+
- [Ollama](https://ollama.com) running locally with:
  - `qwen2.5-coder:1.5b` (chat / coding)
  - `nomic-embed-text` (embeddings)

## Setup

```bash
py -3 -m pip install -r requirements.txt
py -3 index_knowledge.py
py -3 -m streamlit run app.py
```

Or double-click `run_chatbot.bat`.

Open http://localhost:8501

## Optional: Google Custom Search

Set env vars for real Google results when HTML scraping is blocked:

- `GOOGLE_API_KEY`
- `GOOGLE_CSE_ID`

## Project layout

```
app.py                 # Streamlit UI
ask.py                 # CLI ask
ingest_sources.py      # Pull docs into knowledge/
index_knowledge.py     # Rebuild Chroma index
rag/
  pipeline.py          # Vector DB → LLM → internet cascade
  retriever.py         # ChromaDB
  embeddings.py        # Ollama embeddings
  llm.py               # Ollama chat
  web_search.py        # Internet fallback
  history.py           # Q&A history
  knowledge/           # Markdown knowledge base
docs/workflow.md       # Workflow diagram
```

## Repo

https://github.com/Avinash258/RagBaseSolution
