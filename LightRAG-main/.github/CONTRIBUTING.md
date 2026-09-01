# Contributing to Sentinel RAG Ops

Use an issue to describe a bug or proposed behavior before a large change. Replace the repository placeholder below after creating your GitHub repository:

`https://github.com/YOUR_GITHUB_USERNAME/sentinel-rag-ops/issues`

## Development setup

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/sentinel-rag-ops.git
cd sentinel-rag-ops
cp .env.example .env
uv sync --extra test
cd lightrag_webui && bun install --frozen-lockfile && bun run build && cd ..
```

Create a focused branch, preserve public API compatibility unless the change explicitly requires a migration, and add tests for changed behavior.

## Checks

```bash
uv run ruff check lightrag tests
uv run pytest -m "not integration"
cd lightrag_webui
bun run lint
bun test
bun run build
```

Integration tests are opt-in with `--run-integration` or `LIGHTRAG_RUN_INTEGRATION=true` and require the external services named by their markers.

Never include provider keys, database passwords, `.env`, production exports, or user documents in a pull request.
