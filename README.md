# Sentinel RAG Ops

Sentinel RAG Ops is Harsh Singh's document intelligence and retrieval operations platform. It uploads and parses documents, builds vector and knowledge graph indexes, and exposes search, graph exploration, and operational controls through a FastAPI backend and React console.

## Features

- Gemini generation and embeddings with one `GEMINI_API_KEY`
- Document upload, scan, status, retry, and deletion workflows
- PDF, DOCX, PPTX, XLSX, Markdown, text, and other common formats
- Vector retrieval plus graph-based local, global, hybrid, naive, and mix modes
- API-key protection for public deployments
- Local file storage for development
- Supabase PostgreSQL for RAG state and private Supabase Storage for source documents
- Vercel frontend and Render Docker backend configuration

The internal `lightrag` Python namespace and `LIGHTRAG_*` environment variables remain for compatibility with the underlying engine. Required upstream copyright and dependency notices are retained in [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Architecture

```text
Browser
  |-- local: React dev server (5173) -> FastAPI (9621)
  `-- cloud: Vercel -> Render FastAPI -> Gemini
                                    |-> Supabase PostgreSQL
                                    `-> private Supabase Storage
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the detailed request and storage flow.

## Run locally

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/), [Bun](https://bun.sh/), and a Gemini API key.

In PowerShell from the repository root:

```powershell
Copy-Item .env.example .env
notepad .env
uv sync --extra api --extra postgres --extra pytest
Set-Location lightrag_webui
bun install --frozen-lockfile
bun run dev
```

Put your real key in `.env` as `GEMINI_API_KEY=...`. Keep the frontend terminal open. In a second terminal, run:

```powershell
Set-Location C:\Project_main\Sentinel-RAG-Ops
uv run sentinel-rag-server --host 127.0.0.1 --port 9621
```

Open [http://localhost:5173](http://localhost:5173). When prompted, enter the `LIGHTRAG_API_KEY` value from your local `.env`.

### One-command Docker run

After creating `.env`:

```powershell
docker compose up --build -d
docker compose logs -f sentinel-rag-ops
```

Open [http://localhost:9621/webui/](http://localhost:9621/webui/). Stop it with `docker compose down`.

## Deploy free portfolio hosting

The supported split deployment is:

- **Vercel:** static React console
- **Render:** Dockerized FastAPI API and processing worker
- **Supabase:** PostgreSQL with pgvector plus private source-document storage

Follow [docs/VERCEL_SUPABASE_DEPLOYMENT.md](docs/VERCEL_SUPABASE_DEPLOYMENT.md). All required templates are already included:

- `render.yaml`
- `lightrag_webui/vercel.json`
- `.env.supabase.example`
- `deploy/supabase/bootstrap.sql`

Free Render services sleep when idle and have limited memory, so cold starts and large documents can be slow. This setup is suitable for a portfolio or small demonstration; production traffic should use a paid instance.

## Quality checks

```powershell
uv run ruff check lightrag tests
uv run pytest tests/api tests/llm/gemini_impl tests/kg/postgres_impl tests/workspace -m offline --tb=short `
  --ignore=tests/api/config/test_api_config_lollms_host.py `
  --ignore=tests/api/config/test_embedding_dimension_guard.py `
  --ignore=tests/api/config/test_ollama_embedding_dimension.py `
  --ignore=tests/api/config/test_ollama_think_startup_validation.py
Set-Location lightrag_webui
bun run lint
bun run test
bun run build:vercel
```

## Configuration and secrets

- `.env.example` is the safe local template.
- `.env.supabase.example` documents cloud-only values.
- `.env` is ignored by Git and must never be committed.
- `SUPABASE_SERVICE_ROLE_KEY`, database credentials, and `GEMINI_API_KEY` belong only on the backend.
- Only `VITE_BACKEND_URL` belongs in Vercel. Every `VITE_*` value is visible to browsers.

## Repository layout

| Path | Purpose |
| --- | --- |
| `lightrag/` | FastAPI service, RAG engine, parsers, providers, and storage adapters |
| `lightrag_webui/` | React/Vite operations console |
| `tests/` | Backend and frontend regression coverage |
| `deploy/supabase/` | Supabase database and bucket bootstrap SQL |
| `docs/` | Architecture and deployment guides |
| `Dockerfile`, `render.yaml` | Production backend image and Render blueprint |

## Maintainer

- **Harsh Singh** — AI Engineer / Software Developer
- GitHub: [code-with-Harshchaudhary](https://github.com/code-with-Harshchaudhary)
- LinkedIn: **[MY LINKEDIN URL]**
- Email: **[MY EMAIL]**

The LinkedIn and email values remain explicit placeholders because they were not provided.

## License

MIT. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
