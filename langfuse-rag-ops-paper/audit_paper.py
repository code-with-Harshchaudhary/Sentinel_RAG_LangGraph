"""Structural and PDF audit for the Langfuse RAG Ops research paper."""
from pathlib import Path
import json
import re
import zipfile

import pdfplumber
from lxml import etree
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "langfuse-rag-ops-paper/deliverables/Langfuse_RAG_Ops_Research_Paper.docx"
PDF = ROOT / "langfuse-rag-ops-paper/deliverables/Langfuse_RAG_Ops_Research_Paper.pdf"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

with zipfile.ZipFile(DOCX) as archive:
    document = etree.fromstring(archive.read("word/document.xml"))
    headings = document.xpath('//w:p[w:pPr/w:pStyle[@w:val="Heading1"]]', namespaces=NS)
    tables = document.xpath("//w:tbl", namespaces=NS)
    for table in tables:
        widths = table.xpath("./w:tblGrid/w:gridCol/@w:w", namespaces=NS)
        assert sum(map(int, widths)) == 9360, widths
        indent = table.xpath("./w:tblPr/w:tblInd/@w:w", namespaces=NS)
        assert indent == ["120"], indent
    assert len(headings) == 11, len(headings)

reader = PdfReader(PDF)
assert len(reader.pages) == 12, len(reader.pages)
page_text = [page.extract_text() or "" for page in reader.pages]
assert all(len(text.split()) > 80 for text in page_text), [len(text.split()) for text in page_text]
combined = " ".join(("\n".join(page_text)).split())
for required in [
    "Proposed Langfuse", "benchmark gains", "rag.query", "Recall@k", "client-side masking",
    "not a peer-reviewed", "Langfuse", "LightRAG", "Harsh Chaudhary",
]:
    assert required.lower() in combined.lower(), required
assert not re.search(r"AIza[0-9A-Za-z_-]{20,}|AQ\.[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,}", combined)
assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", combined)

links = 0
for page in reader.pages:
    for annotation in page.get("/Annots", []):
        if annotation.get_object().get("/A", {}).get("/URI"):
            links += 1
assert links >= 9, links

with pdfplumber.open(PDF) as pdf:
    for number, page in enumerate(pdf.pages, 1):
        for char in page.chars:
            assert char["x0"] >= 35 and char["x1"] <= page.width - 35, (number, "horizontal overflow")
            assert char["top"] >= 25 and char["bottom"] <= page.height - 25, (number, "vertical overflow")

summary = {
    "status": "passed",
    "pages": len(reader.pages),
    "section_headings": len(headings),
    "fixed_width_tables": len(tables),
    "pdf_hyperlinks": links,
    "page_word_counts": [len(text.split()) for text in page_text],
    "claim_boundary_checks": "passed",
    "page_boundary_checks": "passed",
    "credential_pattern_and_email_checks": "passed",
    "rendering": "ReportLab PDF generation; Poppler rasterization and full-page visual review",
}
(ROOT / "langfuse-rag-ops-paper/qa/audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
