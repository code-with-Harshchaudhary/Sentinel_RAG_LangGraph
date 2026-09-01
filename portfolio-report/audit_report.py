"""Validate the report artifacts without opening project data or credentials."""
from pathlib import Path
import json
import re
import zipfile
from lxml import etree
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / 'output/docx/Sentinel_RAG_Ops_Portfolio_Report.docx'
PDF = ROOT / 'output/pdf/Sentinel_RAG_Ops_Portfolio_Report.pdf'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(DOCX) as archive:
    document = etree.fromstring(archive.read('word/document.xml'))
    headings = document.xpath('//w:p[w:pPr/w:pStyle[@w:val="Heading1"]]', namespaces=NS)
    tables = document.xpath('//w:tbl', namespaces=NS)
    for table in tables:
        widths = table.xpath('./w:tblGrid/w:gridCol/@w:w', namespaces=NS)
        assert sum(map(int, widths)) == 9360, widths
    assert len(headings) == 11

reader = PdfReader(PDF)
assert len(reader.pages) == 12
page_text = [page.extract_text() for page in reader.pages]
assert all(len(text.split()) > 100 for text in page_text)
assert '1. Documents.' in page_text[7]
assert '1. Measure retrieval quality.' in page_text[10]
combined = ' '.join(('\n'.join(page_text)).split())
assert not re.search(r'AIza[0-9A-Za-z_-]{20,}|AQ\.[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,}', combined)
assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', combined)
for required in ['16 nodes', '15 edges', '4,556', 'historical observations', 'LightRAG', 'not a peer-reviewed']:
    assert required in combined, required
links = 0
for page in reader.pages:
    for annotation in page.get('/Annots', []):
        if annotation.get_object().get('/A', {}).get('/URI'):
            links += 1
assert links >= 6

with pdfplumber.open(PDF) as pdf:
    for number, page in enumerate(pdf.pages, 1):
        for char in page.chars:
            assert char['x0'] >= 35 and char['x1'] <= page.width - 35, (number, 'horizontal overflow')
            assert char['top'] >= 25 and char['bottom'] <= page.height - 25, (number, 'vertical overflow')

summary = {
    'status': 'passed',
    'pages': len(reader.pages),
    'section_headings': len(headings),
    'fixed_width_tables': len(tables),
    'pdf_hyperlinks': links,
    'page_word_counts': [len(text.split()) for text in page_text],
    'numbering_restart_checks': 'passed',
    'page_boundary_checks': 'passed',
    'credential_pattern_and_email_checks': 'passed',
    'rendering': 'Microsoft Word PDF export; Poppler rasterization',
}
(ROOT / 'portfolio-report/qa/audit_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
