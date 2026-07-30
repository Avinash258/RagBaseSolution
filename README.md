# Multi-mode Testing Hub (RAG)

NEW VISION / SoftServe **Streamlit** hub with **eight specialist agents**, **AI Reconcile**, and providers **Local (Ollama) / Gemini / NVIDIA**.

**Playwright path:** Vector DB → Qwen → satisfied? → Internet if not → Correct saves to KB

## Requirements

- Python 3.12+
- [Ollama](https://ollama.com) with:
  - `qwen2.5-coder:1.5b` (chat)
  - `nomic-embed-text` (embeddings)
- Optional: `GEMINI_API_KEY`, `NVIDIA_API_KEY` for cloud providers
- NVIDIA uses the OpenAI-compatible client (`openai` package) against `https://integrate.api.nvidia.com/v1` with model `z-ai/glm-5.2` by default

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

Copy `.env.example` to `.env` for models, Ollama URL, and API keys.

## Modes (specialist agents)

| Mode | Agent focus |
|------|-------------|
| Playwright KB | Existing RAG cascade + web gate |
| Synthetic data | Fixtures / personas |
| Manual cases | Structured manual test cases |
| Test strategy | Strategy / plan templates |
| Estimation | Effort ranges |
| Agile | Scrum/Kanban QA |
| Defect lifecycle | Triage / severity |
| Workflow diagram | Requirements → Mermaid flowchart |

## AI Reconcile

| Strategy | Behavior |
|----------|----------|
| Off | Single specialist answer |
| Two providers | Same mode on primary + secondary → merge |
| RAG + LLM | RAG draft + bare LLM → merge |
| Multi-mode | Up to 3 agents → merge |
| On demand | After any answer, **Reconcile with secondary provider** |

Reconcile always produces **one final answer** (drafts in an expander). No Arena vote UI.

## Privacy

Saved answers are local and may appear in future replies. Do not save secrets, credentials, private URLs, or customer data.

## Rebuild index

**Tech Data → Rebuild indexes**, or:

```bash
python index_knowledge.py
```

## Smoke / unit tests

```bash
python smoke_test.py
pytest -q
```

## Project layout

```
app.py                 # Streamlit UI (mode cards, Tech Data, reconcile)
rag/
  agents/              # BaseModeAgent, specialists, ReconcileAgent, AgentHub
  modes.py             # Mode registry
  providers.py         # Ollama / Gemini / NVIDIA
  diagram.py           # Mermaid extract/validate
  lc_pipeline.py       # Playwright cascade
  knowledge/modes/     # Per-mode seed knowledge
docs/
  architecture.md
  workflow.md
```

## Diagrams

- [Architecture](docs/architecture.md)
- [Workflow](docs/workflow.md)

## Repo

https://github.com/Avinash258/RagBaseSolution
