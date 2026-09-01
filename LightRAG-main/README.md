# Sentinel RAG Ops

Sentinel RAG Ops is a production-oriented knowledge operations platform. It ingests documents, extracts and chunks their content, builds a graph plus vector indexes, and exposes retrieval through a FastAPI service and React console.

## What it includes

- Document upload, scanning, status tracking, and recovery
- Native parsing for text, Markdown, PDF, DOCX, PPTX, XLSX, and other text formats
- Knowledge-graph exploration and editing
- Local, global, hybrid, naive, mix, and bypass query modes
- Pluggable LLM, embedding, reranking, graph, vector, and key-value providers
- API-key or account-based authentication
- Docker deployment and reverse-proxy path support

The stable internal Python namespace is `lightrag` for source compatibility. Product branding, package metadata, commands, UI, runtime output, and deployment identity belong to Sentinel RAG Ops. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for retained legal attribution.

## Supported uploads

Common supported formats include `.txt`, `.md`, `.mdx`, `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.csv`, `.json`, `.xml`, `.yaml`, `.yml`, `.html`, `.rtf`, `.odt`, `.tex`, `.epub`, source-code files, and log/config files. The server's `GET /documents/supported-file-types` endpoint is the authoritative list for the active parser configuration.

## Prerequisites

- Python 3.10-3.14 (3.12 recommended)
- [uv](https://docs.astral.sh/uv/) for Python dependency management
- [Bun](https://bun.sh/) for the WebUI and frontend tests
- An LLM and embedding provider, such as OpenAI, Gemini, or Ollama

## Fresh-clone setup

```bash
cp .env.example .env
uv sync --extra api --extra offline-storage --extra offline-llm --extra pytest
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..
uv run sentinel-rag-server
```

On PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

Open `http://127.0.0.1:9621/webui/`. API documentation is available at `http://127.0.0.1:9621/docs` when `ENABLE_API_DOCS=true`.

Before the first run, edit `.env` and provide at least the LLM and embedding credentials. Never commit `.env`.

## Environment variables

The complete starter configuration is in `.env.example`. The values most deployments need are:

| Variable | Purpose |
| --- | --- |
| `HOST`, `PORT` | API bind address and port |
| `LLM_BINDING`, `LLM_MODEL` | Generation provider and model |
| `LLM_BINDING_API_KEY` | Generation provider credential |
| `EMBEDDING_BINDING`, `EMBEDDING_MODEL`, `EMBEDDING_DIM` | Embedding configuration |
| `EMBEDDING_BINDING_API_KEY` | Embedding provider credential |
| `LIGHTRAG_API_KEY` | Protects the API with an `X-API-Key` header |
| `AUTH_ACCOUNTS`, `TOKEN_SECRET` | Optional username/password authentication |
| `LIGHTRAG_*_STORAGE` | Storage backend classes |
| `WORKING_DIR`, `INPUT_DIR`, `PROMPT_DIR` | Persistent application paths |

The `LIGHTRAG_` prefix is retained as a compatibility contract with the core engine.

## Development

Run the backend:

```bash
uv run sentinel-rag-server --host 127.0.0.1 --port 9621
```

Run the frontend dev server in another terminal:

```bash
cd lightrag_webui
bun run dev
```

The frontend proxies API requests to `http://localhost:9621` by default.

## Build, lint, and test

```bash
make build
make lint
make test
```

Equivalent direct commands:

```bash
cd lightrag_webui && bun run build && cd ..
uv run ruff check lightrag tests
cd lightrag_webui && bun run lint && bun run test && cd ..
uv run --no-sync pytest tests/ -m offline --tb=short
```

The complete offline suite targets Linux in CI. On Windows, a small set of
filesystem-hardening tests requires POSIX permissions, symlinks, or filenames
that NTFS rejects. Integration tests require the external services or provider
credentials named by their markers.

## Docker deployment

1. Replace `YOUR_GITHUB_USERNAME` in `docker-compose.yml` if you intend to push an image.
2. Copy `.env.example` to `.env` and add production credentials.
3. Set `LIGHTRAG_API_KEY` or `AUTH_ACCOUNTS` plus `TOKEN_SECRET` before exposing the service.
4. Start the stack:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f sentinel-rag-ops
```

Persistent inputs, indexes, and prompts are stored under `data/` and are ignored by Git.

## Production checklist

- Use a strong API key or account credentials and token secret.
- Keep `.env` in the deployment secret store, not the repository.
- Put TLS at a reverse proxy or configure the server's certificate options.
- Pin and back up external databases when replacing the default local stores.
- Mount `data/` on durable storage.
- Run tests and build the WebUI before creating the image.
- Restrict API documentation in public environments with `ENABLE_API_DOCS=false`.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the request flow, storage model, component map, extension points, and operational lifecycle.

## License

MIT. The retained upstream copyright notice is in [LICENSE](LICENSE).
