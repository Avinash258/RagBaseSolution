# Playwright Testing Chatbot — Architecture

NEW VISION / SoftServe local RAG assistant for Playwright testing.

## System architecture

```mermaid
flowchart TB
  subgraph clientLayer ["Client"]
    browser["Browser UI"]
  end

  subgraph appLayer ["Application"]
    streamlit["Streamlit app.py"]
    sidebar["Sidebar status rebuild feedback"]
    chatUi["Chat streaming satisfaction feedback"]
  end

  subgraph pipelineLayer ["LangChain cascade"]
    bot["PlaywrightRAGBot"]
    retrieve["ChromaRetriever"]
    synth["ChatOllama synthesize"]
    bareLlm["ChatOllama bare answer"]
    webTool["Web fallback tool"]
    train["Correct save to KB"]
  end

  subgraph localAi ["Local AI - Ollama"]
    embedModel["nomic-embed-text"]
    chatModel["qwen2.5-coder:1.5b"]
  end

  subgraph dataLayer ["Local data"]
    chroma["ChromaDB vector index"]
    knowledge["rag/knowledge curated markdown"]
    history["qa_history.jsonl"]
    learned["web_learned files gitignored"]
  end

  subgraph externalLayer ["External optional"]
    pwDocs["playwright.dev docs"]
    google["Google CSE / HTML search"]
    jina["Jina reader fallback"]
  end

  browser --> streamlit
  streamlit --> sidebar
  streamlit --> chatUi
  chatUi -->|"ask / ask_stream"| bot
  chatUi -->|"No search internet"| webTool
  chatUi -->|"Correct"| train
  chatUi -->|"feedback"| history

  bot --> retrieve
  retrieve --> embedModel
  retrieve --> chroma
  chroma --> knowledge

  bot -->|"score >= 0.68"| synth
  bot -->|"weak RAG"| bareLlm
  synth --> chatModel
  bareLlm --> chatModel

  webTool -.-> pwDocs
  webTool -.-> google
  webTool -.-> jina
  webTool --> synth

  train --> learned
  train --> knowledge
  train --> chroma
  bot --> history

  classDef ui fill:#E8F4FA,stroke:#005587,color:#3d3f42
  classDef svc fill:#FFF8E8,stroke:#F8971D,color:#3d3f42
  classDef ai fill:#E6F7FC,stroke:#00A3E0,color:#3d3f42
  classDef data fill:#F3F4F5,stroke:#53565A,color:#3d3f42
  classDef ext fill:#FFF0E8,stroke:#C69214,color:#3d3f42

  browser:::ui
  streamlit:::ui
  sidebar:::ui
  chatUi:::ui
  bot:::svc
  retrieve:::svc
  synth:::svc
  bareLlm:::svc
  webTool:::svc
  train:::svc
  embedModel:::ai
  chatModel:::ai
  chroma:::data
  knowledge:::data
  history:::data
  learned:::data
  pwDocs:::ext
  google:::ext
  jina:::ext
```

## Request path (simplified)

```mermaid
flowchart LR
  q["User question"] --> emb["Embed query"]
  emb --> vec["Search Chroma"]
  vec -->|"high score"| rag["RAG answer"]
  vec -->|"weak / miss"| llm["Qwen LLM"]
  rag --> sat{"Satisfied?"}
  llm --> sat
  sat -->|"Yes"| done["Done"]
  sat -->|"No"| net["Internet + synthesize"]
  net --> save{"Correct?"}
  save -->|"Yes"| kb["Train vector DB"]
  save -->|"No"| done
  kb --> done
```

## Component map

| Layer | Component | Role |
|-------|-----------|------|
| UI | `app.py` Streamlit | Chat, streaming, satisfaction, feedback, NEW VISION branding |
| Cascade | `rag/lc_pipeline.py` | Vector DB → Qwen → optional internet → KB train |
| LLM | LangChain `ChatOllama` | Local coding model `qwen2.5-coder:1.5b` |
| Embeddings | `nomic-embed-text` via Ollama | Query + document vectors |
| Vector DB | Chroma persistent | Playwright knowledge chunks |
| Knowledge | `rag/knowledge/*.md` | Curated docs (learned files gitignored) |
| History | `rag/history/qa_history.jsonl` | Q&A, feedback, Correct flags |
| Web | `rag/web_search.py` | Docs catalog / Google / Jina when user opts in |

## Modes returned by the bot

| Mode | Meaning |
|------|---------|
| `rag` | Strong vector-DB hit |
| `llm` / `llm_grounded` | Local Qwen answer |
| `internet` | User chose Not satisfied → web |
| `none` | No solid local answer yet |

## Related

- Runtime decision flow: [workflow.md](./workflow.md)
- Setup and privacy notes: [../README.md](../README.md)
