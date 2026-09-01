# Research & Papers artwork v2

Mode: Built-in image_gen, one generation call for the default asset and one edit call for the hover asset. No CLI/API fallback.

## Default

Output: research-papers-default-v2.png

Intent: generate (stylized-concept).

Exact prompt:

```text
Use case: stylized-concept
Asset type: Portrait 3:4 editorial hero artwork, default state for an AI-engineering Research & Papers collection website.
Primary request: Create a striking, art-directed industrial 3D campaign image of a research monograph. The result must feel like premium contemporary print-design sculpture, not a generic stationery photograph.
Scene/backdrop: A clean luminous pale lavender-gray seamless studio backdrop and low architectural plinth, with elegant tonal separation and generous uncluttered negative space.
Subject: ONE impeccably crafted charcoal hard-cover research monograph, closed, poised diagonally across the plinth. Crisp layered pale ivory paper edges are exposed along its lower and right edges. A single sculptural sweep of ivory sheets curls upward behind the book like a controlled page fan, forming a beautiful architectural arc rather than a random stack.
Cover design: Oversized beautifully kerned warm-white editorial grotesk typography, two lines exactly "RESEARCH" then "PAPERS", strong hierarchy and legible at thumbnail size. A sparse, precise silver-foil node-link technical diagram sits in the lower cover region: fine straight lines, small circles, and balanced geometry. A restrained acid-lime elastic or narrow tab provides one sharp accent near the fore-edge.
Style/medium: Exceptionally polished photorealistic industrial 3D rendering, tactile fine materials, sophisticated contemporary editorial art direction.
Composition/framing: PORTRAIT 3:4. Close three-quarter elevated hero view, diagonal book orientation, the sculptural book and paper ensemble occupies about 75 percent of the canvas. All main book edges remain in frame. Crisp dimensional silhouette with enough room for a future partly-open cover in the same camera setup. This is standalone artwork, not a website screenshot.
Lighting/mood: Beautiful raking directional studio light from upper left, velvety deep charcoal contrasted with luminous ivory, silver foil glints, long soft lavender shadows, clean atmospheric depth, restrained and confident.
Color palette: Velvety charcoal, warm-white paper, pale lavender-gray, silver, one controlled acid-lime accent.
Text (verbatim): "RESEARCH" and "PAPERS", each exactly once on the cover. No other words anywhere.
Constraints: Physically plausible fine bookbinding, precise page edges and paper geometry. No scattered props, no extra books, no beige stationery stack, no fake metrics or labels, no journal logos, no glass, no neon science-fiction clutter, no UI frame, no watermark. Render one finished artwork.
```

## Hover

Output: research-papers-hover-v2.png

Intent: edit (precise-object-edit).

Edit target: C:/Users/Chaudhary/Desktop/Sentinel-RAG-Ops/output/imagegen/research-papers-default-v2.png

Exact prompt:

```text
Use case: precise-object-edit
Asset type: Matching hover-state editorial hero artwork for an AI-engineering Research & Papers collection website.
Input images: Image 1 is the edit target and exact visual anchor, the newly rendered charcoal monograph with ivory paper sculpture.
Primary request: Create the coherent next moment of this exact scene: the charcoal front cover has lifted partly open toward the left, hinging plausibly at the spine, and a few ivory interior pages form a graceful shallow arc revealing a precise fine graphite node-link graph printed on the main ivory interior page. The front cover remains visible with its oversized warm-white "RESEARCH" then "PAPERS" typography and silver technical diagram intact. Open the cover only enough to reveal the interior, keeping the dimensional silhouette controlled and premium. Let the same acid-lime bookmark/tab be slightly more exposed, providing a subtly stronger accent.
Invariants: Keep the exact PORTRAIT 3:4 canvas dimensions, same camera viewpoint, lens, framing, plinth geometry, luminous pale lavender-gray background, raking upper-left light, material finish, paper sculpture behind the book, and original book base position and diagonal orientation. Preserve the same palette and overall ensemble scale. Do not move the camera, zoom, or redesign the setting; this must crossfade smoothly with the default image as a website hover pair.
Materials: Velvety charcoal hard-cover with beautiful large warm-white editorial typography, tactile pale ivory page stock with crisp layered edges, restrained silver-foil cover lines, fine graphite interior graph, acid-lime tab.
Constraints: Physically plausible book binding, stiff cover, natural page curvature and thin page edges. The only words are "RESEARCH" and "PAPERS", each exactly once, both on the original front cover. Interior graph has no labels or numbers. No additional books, no scattered props, no fake metrics, no logos, no glass, no neon science-fiction effects, no UI frame, no watermark. Change only the cover opening, interior page arc/graph visibility, matching local shadows and exposed lime tab; preserve everything else.
```

