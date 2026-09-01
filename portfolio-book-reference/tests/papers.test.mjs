import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { runInNewContext } from "node:vm";
import { customizeResearchCard, renderPapersPage, validatePapers } from "../scripts/papers.mjs";
import worker from "../backend/worker/index.js";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const publicRoot = join(root, "frontend/interface/public");
const entries = JSON.parse(await readFile(join(root, "frontend/interface/papers.json"), "utf8"));

test("the collection validates its real document downloads", async () => {
  assert.equal((await validatePapers(entries, publicRoot)).length, entries.length);
  for (const image of ["rag-connected-knowledge-closed.png", "rag-connected-knowledge-open.png"]) {
    const data = await readFile(join(publicRoot, "work", image));
    assert.equal(data.subarray(1, 4).toString(), "PNG");
  }
});

test("invalid file paths, missing downloads, duplicates, and metadata fail closed", async () => {
  const sample = entries[0];
  await assert.rejects(validatePapers([{ ...sample, pdf: "/papers/files/../../.env" }], publicRoot), /Invalid pdf/);
  await assert.rejects(validatePapers([{ ...sample, pdf: "/papers/files/missing.pdf" }], publicRoot), /ENOENT/);
  await assert.rejects(validatePapers([sample, sample], publicRoot), /unique/);
  await assert.rejects(validatePapers([{ ...sample, date: "2026-02-31" }], publicRoot), /Invalid paper date/);
  await assert.rejects(validatePapers([{ ...sample, pages: -1 }], publicRoot), /Invalid page count/);
  await assert.rejects(validatePapers([{ ...sample, topics: [42] }], publicRoot), /Invalid paper topics/);
});

test("additional entries sort newest first and optional Word downloads stay optional", async () => {
  const extra = { ...entries[0], slug: "second-study", date: "2026-09-01", editable: undefined };
  const sorted = await validatePapers([...entries, extra], publicRoot);
  assert.equal(sorted[0].slug, "second-study");
  const html = renderPapersPage(sorted);
  assert.match(html, /02 papers/);
  assert.equal((html.match(/data-paper /g) || []).length, sorted.length);
  assert.equal((html.match(/Editable Word copy/g) || []).length, entries.filter((paper) => paper.editable).length);
});

test("content is escaped, real links exist without JavaScript, and empty collection is supported", () => {
  const html = renderPapersPage([{ ...entries[0], title: '<script>alert("x")</script>' }]);
  assert.match(html, /&lt;script&gt;/);
  assert.doesNotMatch(html, /<script>alert/);
  assert.match(html, /href="\/papers\/files\/sentinel-rag-ops.pdf" target="_blank" rel="noopener"/);
  assert.match(html, /Technical case study/);
  assert.match(renderPapersPage([]), /The first paper is on its way/);
});

test("the exact left card changes in HTML and hydrated data, preserving adjacent cards", async () => {
  const html = customizeResearchCard(await readFile(join(publicRoot, "index.html"), "utf8"), "index.html");
  const source = await readFile(join(publicRoot, "_next/static/chunks/d59f7a97fb1c563f.js"), "utf8");
  const js = customizeResearchCard(source, "d59f7a97fb1c563f.js");
  assert.match(html, /aria-label="Research &amp; Papers - 2026–" href="\/papers\/"/);
  assert.match(html, /src="\/papers\/card-link.js" defer/);
  assert.match(js, /name:"Research & Papers",imageUrl:"\/work\/rag-connected-knowledge-closed.png",hoverImageUrl:"\/work\/rag-connected-knowledge-open.png",href:"\/papers\/",year:"2026–"/);
  assert.match(js, /name:"Shore Icon",imageUrl:"\/work\/si.png"/);
  assert.match(js, /name:"Teambition",imageUrl:"\/work\/c4.png"/);
  assert.doesNotMatch(js, /href:"\/adrive"/);
});

test("search filters entries and reports no results, with persistent theme switching", async () => {
  const elements = new Map();
  const element = (id) => { const item = { textContent: "", dataset: {}, listeners: {}, attrs: {}, addEventListener(name, fn) { this.listeners[name] = fn; }, setAttribute(name, value) { this.attrs[name] = value; } }; elements.set(id, item); return item; };
  const button = element("theme-toggle");
  const search = element("paper-search");
  const counter = element("result-count");
  const empty = element("no-results");
  const records = [{ dataset: { search: "sentinel rag knowledge graphs" } }, { dataset: { search: "agent evaluation" } }];
  const html = { dataset: { theme: "dark" } };
  const storage = new Map();
  runInNewContext(await readFile(join(publicRoot, "papers/papers.js"), "utf8"), {
    document: { documentElement: html, getElementById: (id) => elements.get(id), querySelectorAll: () => records },
    localStorage: { setItem: (key, value) => storage.set(key, value) },
  });
  search.value = "RAG graphs"; search.listeners.input();
  assert.equal(records[0].hidden, false); assert.equal(records[1].hidden, true); assert.equal(counter.textContent, "(01)");
  search.value = "no match"; search.listeners.input(); assert.equal(empty.hidden, false);
  search.value = ""; search.listeners.input(); assert.equal(counter.textContent, "(02)"); assert.equal(empty.hidden, true);
  button.listeners.click(); assert.equal(html.dataset.theme, "light"); assert.equal(storage.get("theme"), "light");
});

test("card clicks and keyboard activation use native navigation without hijacking modifier clicks", async () => {
  let listener; let destination;
  class Element { closest() { return { href: "https://example.test/papers/" }; } }
  runInNewContext(await readFile(join(publicRoot, "papers/card-link.js"), "utf8"), {
    document: { addEventListener(name, fn, capture) { assert.equal(name, "click"); assert.equal(capture, true); listener = fn; } },
    Element, window: { location: { assign(url) { destination = url; } } },
  });
  const event = { target: new Element(), button: 0, preventDefault() { this.prevented = true; }, stopImmediatePropagation() { this.stopped = true; } };
  listener(event); assert.equal(destination, "https://example.test/papers/"); assert.ok(event.prevented && event.stopped);
  destination = undefined; listener({ ...event, ctrlKey: true }); assert.equal(destination, undefined);
});

test("worker resolves both collection URLs and HEAD without changing macOS or asset behavior", async () => {
  for (const method of ["GET", "HEAD"]) for (const path of ["/papers", "/papers/"]) {
    let requested;
    await worker.fetch(new Request(`https://example.test${path}`, { method }), { ASSETS: { fetch(request) { requested = request; return new Response(null, { status: 200 }); } } });
    assert.equal(new URL(requested.url).pathname, "/papers/index.html"); assert.equal(requested.method, method);
  }
  let requested;
  const env = { ASSETS: { fetch(request) { requested = request; return new Response(null, { status: 200 }); } } };
  await worker.fetch(new Request("https://example.test/macos"), env);
  assert.equal(new URL(requested.url).pathname, "/macos/index.html");
  await worker.fetch(new Request("https://example.test/papers/files/sentinel-rag-ops.pdf"), env);
  assert.equal(new URL(requested.url).pathname, "/papers/files/sentinel-rag-ops.pdf");
});
