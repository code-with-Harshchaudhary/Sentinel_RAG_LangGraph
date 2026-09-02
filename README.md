# Sentinel RAG Ops

Sentinel RAG Ops is a document knowledge platform for graph and vector retrieval. It combines a FastAPI service with a React console for document ingestion, processing status, knowledge graph exploration, and evidence-backed queries.

The application is built on the LightRAG engine. The compatible `lightrag` Python namespace and required upstream legal notices are retained.

## Technology

- Python 3.10+ and FastAPI
- React 19, TypeScript, Vite, and Bun
- Graph and vector retrieval with pluggable storage backends
- OpenAI, Gemini, Ollama, and other supported model providers
- Docker Compose for local or server deployment

## Repository layout

- [Application](LightRAG-main/) — backend, WebUI, tests, Docker configuration, and technical documentation
- [Technical case study](portfolio-report/Sentinel_RAG_Ops_Portfolio_Report.md) — verified architecture and engineering report
- [Observability research](langfuse-rag-ops-paper/Langfuse_RAG_Ops_Research_Paper.md) — proposed Langfuse tracing and evaluation design
- [Third-party notices](LightRAG-main/THIRD_PARTY_NOTICES.md) — preserved licenses and attribution

## Run with Docker

Install Docker Desktop, then run these commands from the repository root:

```powershell
Set-Location .\LightRAG-main
Copy-Item .env.example .env
```

Edit `LightRAG-main/.env` and replace the provider and security placeholders. At minimum, configure an LLM provider, an embedding provider, and either `LIGHTRAG_API_KEY` or account authentication.

Start the application:

```powershell
docker compose up --build -d
docker compose ps
```

Open <http://127.0.0.1:9621/webui/>. Follow logs with `docker compose logs -f sentinel-rag-ops`, and stop the stack with `docker compose down`.

## Run for development

Install [uv](https://docs.astral.sh/uv/) and [Bun](https://bun.sh/), then:

```powershell
Set-Location .\LightRAG-main
Copy-Item .env.example .env
uv sync --extra api --extra offline-storage --extra offline-llm --extra pytest
Set-Location .\lightrag_webui
bun install --frozen-lockfile
bun run build
Set-Location ..
uv run sentinel-rag-server
```

The WebUI is served at <http://127.0.0.1:9621/webui/>. Development and provider-specific details are in the [application guide](LightRAG-main/README.md).

## Validation

From `LightRAG-main`:

```powershell
uv run ruff check lightrag tests
Set-Location .\lightrag_webui
bun run lint
bun run test
bun run build
```

Some integration tests require external databases or model-provider credentials. Never commit `.env`, API keys, uploaded documents, or local index data.

## License

The project is distributed under the MIT License. See [LICENSE](LightRAG-main/LICENSE) and [THIRD_PARTY_NOTICES.md](LightRAG-main/THIRD_PARTY_NOTICES.md).
