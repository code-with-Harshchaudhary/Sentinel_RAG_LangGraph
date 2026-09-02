# Deploy Sentinel RAG Ops with Vercel, Render, and Supabase

This project uses Vercel only for the React console. Render runs the long-lived FastAPI process and ingestion worker. Supabase stores the RAG tables and private copies of uploaded source documents.

```text
Vercel WebUI -> Render API -> Gemini
                           |-> Supabase PostgreSQL + pgvector
                           `-> private Supabase Storage bucket
```

Do not place the full backend in a Vercel Function. Document parsing and ingestion require a long-running process, background scheduling, and temporary filesystem access.

## 1. Create Supabase resources

1. Create a Supabase project.
2. Open **SQL Editor** and run `deploy/supabase/bootstrap.sql`.
3. Confirm that the `vector` extension and private `sentinel-documents` bucket exist.
4. Open **Connect**, select the shared pooler in **Session mode**, and copy the host, port, user, and password. Use port `5432`; the transaction pooler on `6543` is unsuitable for this adapter.
5. Copy the project URL and service-role key from **Project Settings > API**. The service-role key is backend-only.

The application creates its RAG tables during the first successful backend startup. Run the hardening section in `bootstrap.sql` again afterward so any generated `lightrag_%` tables are protected from the Supabase Data API roles.

## 2. Deploy the backend to Render

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. Render reads the root `render.yaml` and creates `sentinel-rag-ops-api`.
4. Add the requested secret values:

| Render variable | Value source |
| --- | --- |
| `GEMINI_API_KEY` | Google AI Studio |
| `POSTGRES_HOST` | Supabase Session pooler |
| `POSTGRES_USER` | Supabase Session pooler, usually `postgres.PROJECT_REF` |
| `POSTGRES_PASSWORD` | Supabase database password |
| `SUPABASE_URL` | `https://PROJECT_REF.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key |
| `CORS_ORIGINS` | Temporary Vercel URL now; replace with the final URL in step 4 |

Render generates `LIGHTRAG_API_KEY`. Copy its value from the Render environment page after deployment because you will enter it in the web console.

Wait for `https://YOUR-RENDER-SERVICE.onrender.com/health` to return successfully. If startup fails, check the Render logs first for an incorrect database host, password, or Supabase key.

## 3. Deploy the frontend to Vercel

Import the same GitHub repository into Vercel and set:

| Vercel setting | Value |
| --- | --- |
| Framework Preset | Vite |
| Root Directory | `lightrag_webui` |
| Install Command | `bun install --frozen-lockfile` |
| Build Command | `bun run build:vercel` |
| Output Directory | `dist` |

Add one Vercel environment variable for Production and Preview:

```text
VITE_BACKEND_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

Never add Gemini, database, API, or Supabase service-role secrets to Vercel. `VITE_*` variables are compiled into public browser code.

Deploy the site and open it. Enter the generated `LIGHTRAG_API_KEY` at the login screen.

## 4. Lock CORS to the frontend

Copy the final production Vercel origin, such as `https://sentinel-rag-ops.vercel.app`. On Render, set:

```text
CORS_ORIGINS=https://YOUR-FINAL-VERCEL-DOMAIN
```

Redeploy the Render service. Use a stable production/custom domain because Vercel preview domains change.

## 5. How persistence works

- `PGKVStorage`, `PGVectorStorage`, `PGTableGraphStorage`, and `PGDocStatusStorage` keep documents, chunks, embeddings, graph records, cache, and processing status in Supabase PostgreSQL.
- Uploaded source files are first mirrored to `documents/pending/WORKSPACE/` in the private Supabase bucket.
- After successful parsing, the source is moved to `documents/processed/WORKSPACE/`.
- On backend restart, missing pending sources are restored to the temporary input directory so a Scan action can recover work interrupted before ingestion.
- Document deletion and Clear Documents also remove the matching Supabase objects.

The local Render filesystem remains temporary working space. No Supabase credential is sent to the browser.

## 6. Verify the deployment

1. Open the Vercel URL and sign in with `LIGHTRAG_API_KEY`.
2. Upload one small text or PDF document.
3. Wait for its state to become `processed`.
4. Run a retrieval query and open the knowledge graph.
5. In Supabase, confirm RAG tables contain rows and the private bucket contains the processed source.
6. Restart the Render service and confirm the document and query still work.
7. Confirm anonymous and authenticated Supabase roles cannot directly read the generated RAG tables or private bucket.

## Limits of the free setup

Render's free instance sleeps after inactivity and has limited memory. Cold starts can take around a minute, and large PDFs or simultaneous ingestion may exceed available resources. Keep `MAX_PARALLEL_INSERT=1`, start with small files, and upgrade the backend when reliability or traffic matters.
