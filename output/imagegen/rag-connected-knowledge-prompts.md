# RAG Connected Knowledge artwork

Mode: Built-in image_gen. One edit call per asset; no CLI/API fallback.

## Closed book

Output: rag-connected-knowledge-closed.png

Intent: edit (text-localization).

Edit target: C:/Users/CHAUDH~1/AppData/Local/Temp/codex-clipboard-afabe946-1576-4370-ae4c-2fcf407aaeec.png

Exact prompt:

```text
Use case: text-localization
Asset type: Closed-book website research card image.
Input images: Image 1 is the edit target. This supplied white-book photograph is the exact visual reference, not general inspiration.
Primary request: Edit ONLY the printed words on the white book cover to create a RAG research monograph. Remove every original economics, virus, COVID and original author word. Replace the main title with these two exact centered lines: "RAG" then "CONNECTED KNOWLEDGE". Replace the subtitle with two exact centered lines: "GRAPH-BASED RETRIEVAL" then "AN ENGINEERING CASE STUDY". Replace the original author inside the thin rectangular author box with "HARSH CHAUDHARY".
Typography: Keep the clean black uppercase sans-serif typography and hierarchy of the reference. Main title bold, subtitle smaller and letterspaced, author uppercase inside the same thin black rectangle. Fit the longer second title line neatly across the same title area with balanced margins; every word must be crisp and spelled exactly.
Invariants: Keep the identical overhead camera, centered upright white book, portrait canvas ratio and crop, same book dimensions and spine position, pale-grey background, white paper/cover texture, realistic binding and edges, directional soft light and original cast shadows. Preserve the red scatter dots, diagonal rising black line across the cover, graphic positions and overall graphic layout. Preserve the horizontal black divider and author-box geometry. Do not recompose, rotate, recolor, zoom or add props.
Constraints: Only the five specified title/subtitle/author lines should be visible as text. No original title/author remnants, extra words, gibberish, logos or watermark. No charcoal book, lavender plinth, lime tab or sculptural paper props. High fidelity to the supplied photo takes priority over new art direction. Produce one edited closed-book image.
```

## Open book

Output: rag-connected-knowledge-open.png

Intent: edit (precise-object-edit).

Edit target: C:/Users/Chaudhary/Desktop/Sentinel-RAG-Ops/output/imagegen/rag-connected-knowledge-closed.png

Exact prompt:

```text
Use case: precise-object-edit
Asset type: Matching partly-open hover-state website research card image.
Input images: Image 1 is the edit target and exact visual anchor: the already retitled upright white RAG book.
Primary request: Show this SAME white book partly open. Lift only its front cover approximately 50 degrees above the page block, rotating on its LEFT spine hinge; do not open it completely flat. Keep the front cover's printed face visible to the overhead camera, with its existing red scatter dots, diagonal black line, title, subtitle and author box preserved in correct perspective. Reveal the right portion of a white interior page beneath the lifted cover, with a restrained elegant red-and-black connected-node diagram and one small black uppercase heading "CONNECTED KNOWLEDGE". A small natural curl of one interior page is allowed; avoid large curls or loose sheets.
Invariants: Preserve the exact image dimensions and upright portrait framing, identical overhead camera, original spine position, book base footprint, scale, orientation, white cover materials, pale-grey background, soft directional light and overall photographic style. The book base must not rotate or shift, and the backdrop must not change. Keep the entire partly opened book within the original canvas. This pair will be crossfaded as a website hover, so preserve scene alignment.
Cover text: Keep the existing main title "RAG" / "CONNECTED KNOWLEDGE"; subtitle "GRAPH-BASED RETRIEVAL" / "AN ENGINEERING CASE STUDY"; author "HARSH CHAUDHARY", with exact spelling. Preserve their typography and original cover placement as the cover tilts. Interior heading is exactly "CONNECTED KNOWLEDGE".
Geometry and shadows: Physically plausible left-side bound spine and rigid cover, precise page thickness, grounded page block, natural local cover shadow over interior, original outside lighting direction. The open cover should remain projected over part of the book rather than becoming a broad flat two-page spread.
Constraints: Change only the cover opening, necessary page reveal, interior diagram and physically matching local shadows. No paragraphs, filler text, gibberish, labels or numbers in the diagram. No new props, no extra books, no charcoal book, lavender plinth, lime tab, paper sculpture, logos, watermarks or UI. High fidelity to the reference is more important than new art direction. Produce one partly-open-book image.
```

