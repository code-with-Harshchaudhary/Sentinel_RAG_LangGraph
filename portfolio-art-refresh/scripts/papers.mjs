import { readFile, mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

export const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[character]));

// The upstream page is a precompiled artifact. Keep its runtime untouched in
// source and customize both HTML and hydrated card data during the existing build.
export function customizeResearchCard(source, filename) {
  let result = source
    .replaceAll("aDrive 阿里云盘", "Research & Papers")
    .replaceAll("/work/ali01.png", "/work/research-papers-card-v2.png")
    .replaceAll("/work/ali02.png", "/work/research-papers-hover-v2.png")
    .replaceAll('href="/adrive"', 'href="/papers/"')
    .replaceAll('href:"/adrive"', 'href:"/papers/"')
    .replaceAll('href:"/papers/",year:"2020-2022"', 'href:"/papers/",year:"2026–"');
  if (filename === "index.html") {
    result = result.replace(/<a\b[^>]*href="\/papers\/"[\s\S]*?<\/a>/g,
      (card) => card.replaceAll("2020-2022", "2026–").replaceAll("Research & Papers", "Research &amp; Papers"));
    result = result.replace("</head>", '<script src="/papers/card-link.js" defer></script></head>');
  }
  return result;
}

export async function validatePapers(papers, publicRoot) {
  if (!Array.isArray(papers)) throw new Error("papers.json must contain an array");
  const slugs = new Set();
  for (const paper of papers) {
    if (!paper || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(paper.slug) || slugs.has(paper.slug)) {
      throw new Error("Each paper needs a unique lowercase slug");
    }
    slugs.add(paper.slug);
    for (const key of ["title", "subtitle", "type", "description"]) {
      if (typeof paper[key] !== "string" || !paper[key].trim()) throw new Error(`Missing paper ${key}`);
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(paper.date) || Number.isNaN(Date.parse(paper.date)) ||
      new Date(paper.date).toISOString().slice(0, 10) !== paper.date) throw new Error("Invalid paper date");
    if (!Number.isInteger(paper.pages) || paper.pages < 1) throw new Error("Invalid page count");
    for (const key of ["topics", "highlights"]) {
      if (!Array.isArray(paper[key]) || !paper[key].length || paper[key].some((x) => typeof x !== "string" || !x.trim())) {
        throw new Error(`Invalid paper ${key}`);
      }
    }
    for (const [key, extension] of [["pdf", "pdf"], ["editable", "docx"]]) {
      if (key === "editable" && !paper[key]) continue;
      const pattern = new RegExp(`^/papers/files/[a-z0-9][a-z0-9._-]*\\.${extension}$`);
      if (typeof paper[key] !== "string" || !pattern.test(paper[key])) throw new Error(`Invalid ${key} asset path`);
      const bytes = await readFile(join(publicRoot, paper[key].slice(1)));
      const valid = extension === "pdf" ? bytes.subarray(0, 5).toString() === "%PDF-" : bytes.subarray(0, 2).toString() === "PK";
      if (!valid) throw new Error(`Invalid ${key} file contents`);
    }
  }
  return [...papers].sort((left, right) => right.date.localeCompare(left.date));
}

const renderPaper = (paper, index) => {
  const e = escapeHtml;
  const date = new Date(`${paper.date}T00:00:00Z`).toLocaleDateString("en-GB", { month: "short", year: "numeric", timeZone: "UTC" });
  return `<article class="paper" id="${e(paper.slug)}" data-paper data-search="${e([paper.title, paper.subtitle, paper.description, paper.type, ...paper.topics].join(" ").toLowerCase())}">
    <div class="paper-meta"><span class="index">${String(index + 1).padStart(2, "0")}</span><span>${e(paper.type)}</span><time datetime="${e(paper.date)}">${e(date)}</time></div>
    <h2>${e(paper.title)}</h2><p class="subtitle">${e(paper.subtitle)}</p>
    <p class="description">${e(paper.description)}</p>
    <ul class="tags" aria-label="Topics">${paper.topics.map((topic) => `<li>${e(topic)}</li>`).join("")}</ul>
    <details><summary>Inside this paper <span aria-hidden="true">+</span></summary><ul>${paper.highlights.map((item) => `<li>${e(item)}</li>`).join("")}</ul></details>
    <div class="paper-actions"><a class="primary" href="${e(paper.pdf)}" target="_blank" rel="noopener" aria-label="Read ${e(paper.title)} PDF (opens in a new tab)">Read paper <span aria-hidden="true">↗</span></a><a href="${e(paper.pdf)}" download>Download PDF <span aria-hidden="true">↓</span></a></div>
    <div class="paper-foot"><span>${paper.pages} pages · PDF</span>${paper.editable ? `<a href="${e(paper.editable)}" download>Editable Word copy ↗</a>` : ""}</div>
  </article>`;
};

export function renderPapersPage(papers) {
  const count = papers.length;
  return `<!doctype html>
<html lang="en" data-theme="dark"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Research &amp; Papers — Harsh Chaudhary</title>
<meta name="description" content="Technical case studies, engineering notes, and research explorations by Harsh Chaudhary. Read the Sentinel RAG Ops report.">
<meta property="og:title" content="Research &amp; Papers — Harsh Chaudhary">
<meta property="og:description" content="A growing collection of AI engineering case studies and research explorations. Start with Sentinel RAG Ops.">
<meta property="og:type" content="website">
<meta property="og:image" content="https://harsh-haoqi-portfolio.harshch310702.chatgpt.site/work/research-papers-card-v2.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Research &amp; Papers — Harsh Chaudhary">
<meta name="twitter:description" content="AI engineering case studies and research explorations.">
<meta name="twitter:image" content="https://harsh-haoqi-portfolio.harshch310702.chatgpt.site/work/research-papers-card-v2.png">
<link rel="icon" href="/assets/icon.svg"><link rel="stylesheet" href="/papers/papers.css">
<script src="/papers/theme.js"></script><script src="/papers/papers.js" defer></script>
</head><body>
<a class="skip-link" href="#papers">Skip to papers</a>
<header class="site-header"><a class="brand" href="/">HARSH.DESIGN</a><nav aria-label="Main navigation"><a href="/#selected-work">Work</a><a href="/macos">Mac OS</a><button type="button" id="theme-toggle" aria-label="Switch color theme">Theme[D]</button></nav></header>
<main class="shell"><div class="breadcrumbs"><a href="/#selected-work">← All work</a><span>Collection / 001</span></div>
<section class="intro" aria-labelledby="collection-title"><div><p class="eyebrow">Notes from the build</p><h1 id="collection-title">Research<br><span>&amp; Papers.</span></h1></div><div class="intro-note"><p>A closer look at what I build,<br>how it works, and what I learn.</p><span class="count-label">${String(count).padStart(2, "0")} ${count === 1 ? "paper" : "papers"} · Ongoing collection</span></div></section>
<div class="collection-layout"><aside class="collection-cover"><div class="cover-art"><img class="cover-default" src="/work/research-papers-card-v2.png" width="1024" height="1365" alt="Research and Papers monograph with a knowledge graph cover" fetchpriority="high"><img class="cover-hover" src="/work/research-papers-hover-v2.png" width="1024" height="1365" alt="" aria-hidden="true" loading="lazy"></div><p class="cover-caption"><span>Independent explorations</span><span>2026–</span></p><p class="cover-note">Practical ideas, documented decisions, and honest results. A collection that grows with the work.</p></aside>
<section id="papers" aria-label="Paper collection"><div class="collection-toolbar"><p>Reading room <span id="result-count" aria-live="polite" aria-atomic="true">(${String(count).padStart(2, "0")})</span></p><label for="paper-search"><span class="visually-hidden">Search papers by title or topic</span><input id="paper-search" type="search" placeholder="Search papers / topics" autocomplete="off"></label></div>
<div class="paper-list">${papers.map(renderPaper).join("\n")}</div>
<p id="no-results" class="empty-state"${count ? " hidden" : ""}>${count ? "No matching papers. Try another title or topic." : "The first paper is on its way."}</p>
<p class="publication-note">A note on the work: each entry is labelled by format. Technical case studies document engineering work; they are not presented as peer-reviewed publications.</p>
</section></div><section class="next-note"><span aria-hidden="true">+</span><div><h2>More questions. More papers.</h2><p>New explorations will join this collection over time.</p></div><a href="/#selected-work">Explore other work ↗</a></section></main>
<footer class="site-footer"><span>Harsh Chaudhary</span><span>Research / Build / Document</span><a href="#collection-title">Back to top ↑</a></footer>
</body></html>`;
}

export async function writePapersPage({ root, client }) {
  const papers = await validatePapers(JSON.parse(await readFile(join(root, "frontend/interface/papers.json"), "utf8")), client);
  await mkdir(join(client, "papers"), { recursive: true });
  await writeFile(join(client, "papers/index.html"), renderPapersPage(papers));
  return papers;
}
