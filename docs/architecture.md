# Multi-mode Testing Hub — Architecture

NEW VISION / SoftServe hub: specialist agents, AI Reconcile, multi-provider LLM.

## System architecture

```mermaid
flowchart TB
  subgraph clientLayer ["Client"]
    browser["Browser UI"]
  end

  subgraph appLayer ["Application"]
    streamlit["Streamlit app.py"]
    modeCards["Mode cards landing"]
    techData["Tech Data expander"]
    reconcileUi["Reconcile controls"]
  end

  subgraph agentLayer ["Specialist agents"]
    hub["AgentHub"]
    pwAgent["PlaywrightKbAgent"]
    otherAgents["Other mode agents"]
    recon["ReconcileAgent"]
  end

  subgraph providers ["LLM providers"]
    ollama["Ollama local"]
    gemini["Gemini"]
    nvidia["NVIDIA"]
  end

  subgraph dataLayer ["Local data"]
    chroma["ChromaDB"]
    knowledge["rag/knowledge + modes"]
    history["qa_history.jsonl"]
  end

  browser --> streamlit
  streamlit --> modeCards
  streamlit --> techData
  streamlit --> reconcileUi
  streamlit --> hub
  hub --> pwAgent
  hub --> otherAgents
  hub --> recon
  pwAgent --> chroma
  otherAgents --> chroma
  hub --> ollama
  hub --> gemini
  hub --> nvidia
  chroma --> knowledge
  hub --> history
```

## Reconcile strategies

```mermaid
flowchart LR
  q["Question"] --> strat{"Strategy"}
  strat -->|Off| single["One agent"]
  strat -->|TwoProviders| a["Draft A + Draft B"]
  strat -->|RagLlm| b["RAG + LLM drafts"]
  strat -->|MultiMode| c["2-3 mode agents"]
  strat -->|OnDemand| d["Existing + secondary"]
  a --> merge["ReconcileAgent"]
  b --> merge
  c --> merge
  d --> merge
  single --> out["Final answer"]
  merge --> out
```

## Component map

| Layer | Component | Role |
|-------|-----------|------|
| UI | `app.py` | Mode cards, Tech Data, providers, reconcile, Mermaid |
| Hub | `rag/agents/hub.py` | Route modes + reconcile strategies |
| Agents | `rag/agents/specialists.py` | One class per mode |
| Reconcile | `rag/agents/reconcile.py` | Merge drafts into one answer |
| Providers | `rag/providers.py` | Ollama / Gemini / NVIDIA generate+stream |
| Diagram | `rag/diagram.py` | Mermaid extract/validate |
| Playwright | `rag/lc_pipeline.py` | Vector DB → LLM → internet cascade |
| Modes | `rag/modes.py` | Registry + knowledge paths |

## Related

- Runtime Playwright cascade: [workflow.md](./workflow.md)
- Setup: [../README.md](../README.md)
