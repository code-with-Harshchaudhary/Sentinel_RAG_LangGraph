# Sentinel RAG Ops architecture

## System map

```text
Browser / API client
        |
        v
FastAPI service (`lightrag/api`)
        |
        +--> ingestion pipeline (`lightrag/pipeline.py`)
        |      +--> parser routing (`lightrag/parser`)
        |      +--> chunkers (`lightrag/chunker`)
        |      +--> entity/relation extraction (`lightrag/operate.py`)
        |
        +--> query pipeline (`lightrag/operate.py`)
        |      +--> vector retrieval
        |      +--> graph traversal
        |      +--> context assembly and generation
        |
        +--> storage adapters (`lightrag/kg`)
               +--> key/value documents and cache
               +--> document status
               +--> vector indexes
               +--> graph database
```

The React application in `lightrag_webui` calls the FastAPI routes. Its production build is written to `lightrag/api/webui` and served by the same process.

## Ingestion lifecycle

1. A client uploads a file or places it in `INPUT_DIR` and requests a scan.
2. The document manager normalizes the source identity and validates size, type, and parser rules.
3. A parser converts the source to normalized text plus structured sidecar data for headings, tables, equations, and images.
4. A chunker splits normalized content according to the requested strategy.
5. The extraction LLM identifies entities and relationships.
6. The pipeline writes full documents, chunks, graph records, vector embeddings, and status records.
7. Shared-storage coordination publishes update flags so workers refresh their view.

Document states include pending, processing, processed, failed, and deleted/recovery transitions. API routes expose status and pipeline history so operators can diagnose failures without reading raw storage files.

## Query lifecycle

1. The request is validated and assigned a query mode.
2. The query is embedded.
3. Vector and/or graph stores select relevant chunks, entities, and relationships.
4. Optional reranking improves the candidate order.
5. Context is bounded by configured token limits.
6. The query LLM produces a normal or streamed response.

Modes trade latency for context breadth: `naive` uses chunks, `local` emphasizes nearby entities, `global` emphasizes relationships and community-level context, `hybrid` combines local/global retrieval, `mix` combines graph and vector context, and `bypass` sends the request directly to the generation provider.

## Storage model

Four adapter categories are configured independently:

- `LIGHTRAG_KV_STORAGE`: source documents, chunks, and cache records
- `LIGHTRAG_DOC_STATUS_STORAGE`: ingestion state and metadata
- `LIGHTRAG_GRAPH_STORAGE`: entities and relationships
- `LIGHTRAG_VECTOR_STORAGE`: embeddings for chunks, entities, and relationships

The local defaults use JSON, NetworkX, and NanoVectorDB under `WORKING_DIR`. Production deployments can select PostgreSQL, Neo4j, Redis, Qdrant, Milvus, MongoDB, OpenSearch, and other installed adapters. All instances that share a workspace must agree on embedding model/dimension and storage configuration.

## Provider roles

Generation is role-aware. Extraction, keyword discovery, query generation, and optional vision processing can share the default LLM or use role-specific models. Embedding and reranking are separate providers with their own concurrency limits.

Provider modules live in `lightrag/llm`; option validation lives in `lightrag/llm/binding_options`. Provider packages that are intentionally optional may be installed lazily, so an import-only dependency scan is not sufficient grounds for deletion.

## API and security

The server assembles routers for documents, graphs, queries, Ollama-compatible access, authentication, and health. Middleware enforces request/body limits, admission capacity, CORS, and authentication.

Public deployments must configure either `LIGHTRAG_API_KEY` or `AUTH_ACCOUNTS` with `TOKEN_SECRET`. TLS can terminate at a reverse proxy. `LIGHTRAG_API_PREFIX` supports path-based multi-site routing; the server injects runtime prefix configuration into the WebUI response.

## Extension points

- Add LLM/embedding providers under `lightrag/llm` and register their binding options.
- Add storage implementations under `lightrag/kg` and register required environment variables.
- Add parser engines through `lightrag/parser/plugins.py`.
- Add chunking strategies under `lightrag/chunker`.
- Customize entity types and prompts under `PROMPT_DIR`.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `lightrag/` | Core engine, API, providers, parsers, storage, tools |
| `lightrag_webui/` | React/Vite operations console |
| `tests/` | Backend and frontend regression coverage |
| `docs/` | Detailed design and deployment references |
| `prompts/` | User-customizable prompt samples |
| `data/` | Ignored runtime inputs, indexes, and prompt overrides |
| `Dockerfile` | Multi-stage frontend/backend production image |
| `docker-compose.yml` | Single-service durable local deployment |

## Operational lifecycle

For a release: install from the lockfiles, build the WebUI, run lint and tests, build the container, perform an authenticated health check, upload a small document, wait for `processed`, run a retrieval query, and verify persistence after restart. Back up the external databases or `data/rag_storage` before migrations.

The internal `lightrag` namespace and `LIGHTRAG_` environment variables are compatibility identifiers. They are not the public product identity and should only be renamed as a separately planned breaking migration.
