# Harsh Unified Portfolio

This repository delivers two independent frontend experiences under one portfolio deployment.

## Frontend

### HARSH Portfolio

- **Route:** `/`
- **Source:** `frontend/interface/public/`
- **Purpose:** Main animated HARSH portfolio.
- **Runtime assets:** bundled Next static files in `_next/`, plus `fonts/`, `images/`, `models/`, `stickers/`, `work/`, `audio/`, and `assets/`.

### macOS Portfolio

- **Route:** `/macos`
- **Wrapper:** `frontend/macos/index.html`
- **Desktop app:** `frontend/macos/public/desktop.html`
- **Purpose:** Interactive macOS desktop-style portfolio.
- **Assets:** `frontend/macos/public/assets/__l5e/assets-v1/` preserves the legacy UUID asset library because the desktop references those paths directly. Icons and analytics support files are separated into `icons/` and `scripts/`.

#### Photos media library

The Photos window is generated from `C:\my phone\project`. To add or remove media:

1. Add or remove files in `C:\my phone\project`.
2. Run `npm run sync:media`.
3. Run `npm run build`.

Supported inputs are JPG, JPEG, PNG, WebP, HEIC, HEIF, MP4, MOV, and M4V. The sync command creates optimized WebP photos, H.264/AAC MP4 videos, poster thumbnails, and `frontend/macos/public/media/library/manifest.json`. Source files are never modified.

The two applications remain separate. They share a deployment bundle, not a frontend implementation.

## Backend / Worker

- **Source:** `backend/worker/index.js`
- The worker serves assets, resolves `/macos` to its wrapper page, and preserves the existing dotless GET fallback to the HARSH root page.

## Build System

- **Source:** `scripts/build.mjs`
- **Development:** `npm run dev`
- **Production build:** `npm run build`
- **Validation:** `npm test`

The build creates `dist/` from scratch:

- `frontend/interface/public/` → `dist/client/`
- `frontend/macos/public/` → `dist/client/macos/`
- `frontend/macos/index.html` → `dist/client/macos/index.html`
- `backend/worker/index.js` → `dist/server/index.js`

## Generated Output

`dist/` is generated deployment output only. Do not edit it manually; rebuild it with `npm run build`.

## Research & Papers

The left research card opens `/papers/`, a static, searchable reading collection.
Its default/hover artwork is in `frontend/interface/public/work/research-papers-*.png`.
The collection currently includes the Sentinel RAG Ops technical case study and a Langfuse RAG Ops research design paper. Neither is presented as a peer-reviewed publication.

To add another paper:

1. Put the PDF in `frontend/interface/public/papers/files/` with a lowercase, hyphenated filename.
2. Add an entry to `frontend/interface/papers.json`, following the existing record. Use a unique `slug`, real ISO date (`YYYY-MM-DD`), accurate `pages` and `type`, and `/papers/files/your-file.pdf` for `pdf`.
3. An `editable` DOCX download is optional. Keep private data and credentials out of all public downloads.
4. Run `npm test`, then publish through the existing Sites workflow. The build sorts newest first and updates the collection count automatically. Missing/invalid downloads fail the build.

The readable collection template is in `scripts/papers.mjs`; styling and search/theme behavior are in `frontend/interface/public/papers/`. The original compiled Next source is preserved: the established build applies the card replacement to both HTML and hydrated data. A native-navigation handler sends this one card to the independent static route.

The two conceptual paper artworks were generated using the built-in image tool. The exact prompts are recorded in `docs/research-papers-artwork-prompts.md`.

## Hosting

`.openai/hosting.json` remains at the repository root and is copied into the generated deployment bundle.
