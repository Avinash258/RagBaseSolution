# Playwright Testing Chatbot — Workflow

```mermaid
flowchart TD
    startNode(["User asks a question"]) --> embedQuery["Embed query with nomic-embed-text"]
    embedQuery --> searchChroma["Search Chroma vector DB"]
    searchChroma --> scoreCheck{"Best score >= 0.68?"}

    scoreCheck -->|"Yes"| highConf{"Score >= 0.85?"}
    highConf -->|"Yes"| fastExtract["Fast extract from top chunks"]
    highConf -->|"No"| synthRag["Synthesize with qwen2.5-coder:1.5b"]
    fastExtract --> askSat
    synthRag --> askSat

    scoreCheck -->|"No"| llmCall["Ask local qwen2.5-coder:1.5b"]
    llmCall --> llmOk{"Proper LLM answer?"}
    llmOk -->|"Yes"| askSat["Ask user: Are you satisfied?"]
    llmOk -->|"No"| askSat

    askSat -->|"Yes — satisfied"| doneNode(["Done"])
    askSat -->|"No — search internet"| webSearch["Search internet / Playwright docs"]
    webSearch --> synthWeb["Synthesize with qwen2.5-coder:1.5b"]
    synthWeb --> showWeb["Return mode: internet"]
    showWeb --> correctBtn{"User marks Correct?"}
    correctBtn -->|"Yes"| trainKb["Train Chroma knowledge base"]
    correctBtn -->|"No"| doneNode
    trainKb --> doneNode

    classDef store fill:#C2E5FF,stroke:#3DADFF
    classDef decision fill:#FFECBD,stroke:#FFC943
    classDef ok fill:#CDF4D3,stroke:#66D575
    classDef warn fill:#FFCDC2,stroke:#FF7556

    searchChroma:::store
    trainKb:::store
    scoreCheck:::decision
    highConf:::decision
    llmOk:::decision
    askSat:::decision
    correctBtn:::decision
    showWeb:::ok
    webSearch:::warn
```

## Cascade summary

1. **Vector DB (Chroma)** — retrieve Playwright knowledge  
2. **Ollama `qwen2.5-coder:1.5b` (LangChain)** — synthesize or answer if RAG is weak  
3. **Ask user** — Are you satisfied?  
4. **Internet** — only if the user clicks **No — search internet**  
5. **History → Correct** — only then train the knowledge base / vector DB  
