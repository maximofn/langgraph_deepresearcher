# LangGraph Deep Researcher

Multi-agent deep research system built on [LangGraph](https://github.com/langchain-ai/langgraph). A supervisor agent coordinates parallel research sub-agents that gather, compress and synthesize information into a final report.

## Architecture

Pipeline of four agents:

1. **Scope** — clarifies the request and generates a research brief (GPT-4.1)
2. **Supervisor** — breaks the brief into topics and launches research agents in parallel (Claude Sonnet 4.5)
3. **Research agents** — iterative web search via Tavily (or local filesystem via MCP), up to `max_concurrent_researchers` in parallel (Claude Sonnet 4.5)
4. **Writer** — synthesizes all findings into a final markdown report (GPT-4.1)

Model assignments live in `src/LLM_models/LLM_models.py`.

## Interfaces

Three ways to run the researcher:

### 1. CLI

```bash
uv sync
source .venv/bin/activate
python src/langgraph_deepresearch.py
```

### 2. FastAPI + React web UI (recommended)

Full-featured UI with session history, real-time streaming over WebSockets, clarification flow and persisted reports.

```bash
# Backend (Docker)
docker compose up --build -d         # API on http://localhost:8000

# Frontend (Vite dev server)
cd web
npm install
npm run dev                           # UI on http://localhost:5173
```

- Backend: `api/` (FastAPI, SQLite persistence, WebSocket events, optional Prometheus metrics)
- Frontend: `web/` (React 18, TypeScript, TailwindCSS, zustand, react-router)

### 3. Gradio (legacy)

```bash
python run_gradio.py                  # http://localhost:7860
```

## Environment

Create a `.env` with the keys you need:

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
TAVILY_API_KEY=
LANGSMITH_API_KEY=
GITHUB_API_KEY=
CEREBRAS_API_KEY=
```

## Tests

```bash
python test/test_agent_research.py
python test/test_agent_scope.py
pytest test/api/                      # FastAPI tests
```

See [CLAUDE.md](CLAUDE.md) for the full architecture, state schemas, patterns and development workflow.
