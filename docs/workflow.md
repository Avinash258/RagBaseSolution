# Playwright Testing Chatbot — Workflow

```mermaid
flowchart TD
    startNode(["User asks a question"]) --> embedQuery["Embed query with nomic-embed-text"]
    embedQuery --> searchChroma["Search Chroma vector DB"]
    searchChroma --> scoreCheck{"Best score >= 0.68?"}

    scoreCheck -->|"Yes"| highConf{"Score >= 0.85?"}
    highConf -->|"Yes"| fastExtract["Fast extract from top chunks"]
    highConf -->|"No"| synthRag["Synthesize with gemma4:e2b using retrieved sources"]
    fastExtract --> showRag["Return cited answer mode: rag"]
    synthRag --> showRag
    showRag --> saveHist1["Save to history"]
    saveHist1 --> doneNode(["Done"])

    scoreCheck -->|"No"| llmCall["Ask local gemma4:e2b"]
    llmCall --> llmOk{"Proper LLM answer?"}
    llmOk -->|"Yes"| showLlm["Return answer mode: llm"]
    showLlm --> saveHist2["Save to history"]
    saveHist2 --> correctBtn{"User marks Correct?"}
    correctBtn -->|"Yes"| trainKb["Write knowledge file and embed into Chroma"]
    correctBtn -->|"No"| doneNode
    trainKb --> doneNode

    llmOk -->|"No"| webSearch["Search internet / Playwright docs"]
    webSearch --> fetchPages["Fetch page text"]
    fetchPages --> synthWeb["Synthesize with gemma4:e2b"]
    synthWeb --> showWeb["Return answer mode: internet"]
    showWeb --> saveHist3["Save to history"]
    saveHist3 --> correctBtn

    classDef store fill:#C2E5FF,stroke:#3DADFF
    classDef decision fill:#FFECBD,stroke:#FFC943
    classDef ok fill:#CDF4D3,stroke:#66D575
    classDef warn fill:#FFCDC2,stroke:#FF7556

    searchChroma:::store
    trainKb:::store
    scoreCheck:::decision
    highConf:::decision
    llmOk:::decision
    correctBtn:::decision
    showRag:::ok
    showLlm:::ok
    showWeb:::ok
    webSearch:::warn
```

## Cascade summary

1. **Vector DB (Chroma)** — retrieve Playwright knowledge  
2. **Ollama `gemma4:e2b`** — rewrite/synthesize from sources (skipped on very high similarity for speed)  
3. **Local LLM alone** — if RAG is weak  
4. **Internet** — if LLM has no proper answer  
5. **History → Correct** — only then train the knowledge base / vector DB  
