# Playwright Testing Chatbot (RAG)

Local **LangChain** RAG chatbot for Playwright testing (Streamlit + Ollama + Chroma).

**Flow:** Vector DB → Qwen (`qwen2.5-coder`) → ask if satisfied → Internet only if not → Correct saves to KB

## Requirements

- Python 3.12+
- [Ollama](https://ollama.com) with:
  - `qwen2.5-coder:1.5b` (chat)
  - `nomic-embed-text` (embeddings)

## Setup

```bash
python -m pip install -r requirements.txt
python index_knowledge.py
python -m streamlit run app.py
```

Windows:

```bat
py -3 -m pip install -r requirements.txt
py -3 index_knowledge.py
run_chatbot.bat
```

Open http://localhost:8501

Copy `.env.example` to `.env` to override models / Ollama URL.

## How it works

1. **Vector DB** — retrieve curated Playwright docs from `rag/knowledge/`
2. **Qwen (LangChain ChatOllama)** — synthesize or answer when RAG is weak
3. **Satisfied?** — internet search runs only after **No — search internet**
4. **Helpful?** — response feedback stored in history
5. **Correct — save to KB** — writes local markdown + embeds into Chroma

**Privacy:** Saved answers are stored locally and may appear in future replies. Do not save secrets, credentials, private URLs, or customer data.

**Learned files:** Runtime `web_learned_*.md` files are gitignored. Only curated docs should be committed.

## Rebuild index

Use the sidebar **Rebuild index** button, or:

```bash
python index_knowledge.py
```

If knowledge files change, the sidebar warns when the index may be stale.

## Smoke tests

```bash
python smoke_test.py
python smoke_force_web.py
python smoke_web_learn.py
```

Unit tests (no Ollama required):

```bash
pytest -q
```

## Optional: Google Custom Search

- `GOOGLE_API_KEY`
- `GOOGLE_CSE_ID`

## Knowledge directories

| Path | Purpose |
|------|---------|
| `rag/knowledge/` | Active KB used by the app (curated docs) |
| `knowledge/playwright/` | Legacy/sample notes — not the runtime index root |

## Project layout

```
app.py                 # Streamlit UI
ask.py                 # CLI ask
index_knowledge.py     # Rebuild Chroma index
rag/
  lc_pipeline.py       # LangChain cascade
  retriever.py         # ChromaDB
  history.py           # Q&A + feedback
  knowledge/           # Markdown knowledge base
docs/
  architecture.md      # System architecture diagram
  workflow.md          # Runtime decision flow
tests/unit/            # Offline unit tests
```

## Diagrams

- [Architecture](docs/architecture.md) — components and data flow  
- [Workflow](docs/workflow.md) — satisfaction-gated answer cascade  

## Repo

https://github.com/Avinash258/RagBaseSolution
