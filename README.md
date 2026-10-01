# Sentinel RAG Ops

**A full-stack document intelligence platform for uploading, indexing, searching, and exploring your documents with AI.**

## 🌐 Live Website

### [https://sentry-rag.vercel.app/]

> **Try the live application:** upload documents, ask questions, explore knowledge graphs, and manage document-processing workflows from one interface.

> [!IMPORTANT]
> Replace `https://your-rag-website-url.com` above with your deployed RAG website URL before publishing this README.

---

## Overview

Sentinel RAG Ops is a document intelligence and retrieval operations platform created by **Harsh Singh**. It parses uploaded documents, builds vector and knowledge-graph indexes, and provides powerful search, graph exploration, and operational controls through a FastAPI backend and React console.

## Key Features

- Gemini-powered text generation and embeddings using one `GEMINI_API_KEY`
- Document upload, scanning, status tracking, retry, and deletion workflows
- Support for PDF, DOCX, PPTX, XLSX, Markdown, text, and other common formats
- Vector retrieval and graph-based retrieval
- Local, global, hybrid, naive, and mix query modes
- Interactive knowledge-graph exploration
- API-key protection for public deployments
- Local file storage for development
- Supabase PostgreSQL for RAG state and private Supabase Storage for source documents
- Deployment configuration for a Vercel frontend and Render backend

## Architecture

```text
Browser
  |-- Local: React development server (5173) -> FastAPI (9621)
  `-- Cloud: Vercel -> Render FastAPI -> Gemini
                                      |-> Supabase PostgreSQL
                                      `-> Private Supabase Storage
```

For a detailed explanation of the request and storage flow, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Run Locally

### Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Node.js LTS
- A Gemini API key

### Quick Start on Windows

From the repository root, run:

```powershell
.\start-sentinel.cmd
```

The launcher verifies the required tools, prepares the React interface, creates the runtime folders, and starts the API and bundled WebUI.

Open **[http://127.0.0.1:9621/webui/](http://127.0.0.1:9621/webui/)** in your browser. Press `Ctrl+C` in the terminal to stop the application.

### Manual Development Mode

In PowerShell, from the repository root:

```powershell
Copy-Item .env.example .env
notepad .env
uv sync --extra api --extra postgres --extra pytest
Set-Location lightrag_webui
npx --yes bun@1 install --frozen-lockfile
npx --yes bun@1 run dev
```

Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Keep the frontend terminal open. In a second terminal, run:

```powershell
Set-Location C:\Project_main\Sentinel-RAG-Ops
uv run sentinel-rag-server --host 127.0.0.1 --port 9621
```

Open **[http://localhost:5173](http://localhost:5173)**.

Local development enters guest mode automatically when `AUTH_ACCOUNTS` is not configured. A deployed API-key-protected backend uses the `LIGHTRAG_API_KEY` configured on Render.

## Run with Docker

After creating your `.env` file, run:

```powershell
docker compose up --build -d
docker compose logs -f sentinel-rag-ops
```

Open **[http://localhost:9621/webui/](http://localhost:9621/webui/)**. To stop the application, run:

```powershell
docker compose down
```

## Deployment

The recommended portfolio deployment uses:

| Service | Purpose |
| --- | --- |
| **Vercel** | Hosts the static React console |
| **Render** | Runs the Dockerized FastAPI API and processing worker |
| **Supabase** | Provides PostgreSQL with pgvector and private document storage |

Follow [docs/VERCEL_SUPABASE_DEPLOYMENT.md](docs/VERCEL_SUPABASE_DEPLOYMENT.md) for the complete deployment guide.

The repository includes the required deployment templates:

- `render.yaml`
- `lightrag_webui/vercel.json`
- `.env.supabase.example`
- `deploy/supabase/bootstrap.sql`

> [!NOTE]
> Free Render services sleep when idle and have limited memory. Cold starts and large-document processing may be slow. The free setup is suitable for a portfolio or small demonstration; production traffic should use a paid service.

## Configuration and Security

- `.env.example` is the safe local configuration template.
- `.env.supabase.example` documents cloud-only values.
- `.env` is ignored by Git and must never be committed.
- Keep `SUPABASE_SERVICE_ROLE_KEY`, database credentials, and `GEMINI_API_KEY` on the backend only.
- Only `VITE_BACKEND_URL` belongs in Vercel.
- Every `VITE_*` value is visible to users in the browser.

The internal `lightrag` Python namespace and `LIGHTRAG_*` environment variables are retained for compatibility with the underlying engine. Required upstream copyright and dependency notices are available in [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Quality Checks

Run the backend checks from the repository root:

```powershell
uv run ruff check lightrag tests
uv run pytest tests/api tests/llm/gemini_impl tests/kg/postgres_impl tests/workspace -m offline --tb=short `
  --ignore=tests/api/config/test_api_config_lollms_host.py `
  --ignore=tests/api/config/test_embedding_dimension_guard.py `
  --ignore=tests/api/config/test_ollama_embedding_dimension.py `
  --ignore=tests/api/config/test_ollama_think_startup_validation.py
```

Run the frontend checks:

```powershell
Set-Location lightrag_webui
bun run lint
bun run test
bun run build:vercel
```

## Repository Structure

| Path | Purpose |
| --- | --- |
| `lightrag/` | FastAPI service, RAG engine, parsers, providers, and storage adapters |
| `lightrag_webui/` | React/Vite operations console |
| `tests/` | Backend and frontend regression coverage |
| `deploy/supabase/` | Supabase database and bucket bootstrap SQL |
| `docs/` | Architecture and deployment guides |
| `Dockerfile`, `render.yaml` | Production backend image and Render blueprint |

## Maintainer

**Harsh Singh** — AI Engineer / Software Developer

- GitHub: [code-with-Harshchaudhary](https://github.com/code-with-Harshchaudhary)
- LinkedIn: **[Add your LinkedIn URL]**
- Email: **[Add your email address]**

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

