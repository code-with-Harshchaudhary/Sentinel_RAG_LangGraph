"""Create the verified PDF edition with ReportLab from the shared paper content."""
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from build_paper import PAGES, WORK, NAVY, BLUE, TEAL, MUTED, INK, LIGHT


ROOT = Path(__file__).resolve().parents[1]
OUT = WORK / "deliverables" / "Langfuse_RAG_Ops_Research_Paper.pdf"
FONTDIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Calibri", str(FONTDIR / "calibri.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Bold", str(FONTDIR / "calibrib.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Italic", str(FONTDIR / "calibrii.ttf")))
pdfmetrics.registerFont(TTFont("Consolas", str(FONTDIR / "consola.ttf")))


def color(hex_value):
    return colors.HexColor("#" + hex_value)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="PaperBody", fontName="Calibri", fontSize=9.4, leading=11.4, textColor=color(INK), spaceAfter=5.5))
styles.add(ParagraphStyle(name="PaperH1", fontName="Calibri-Bold", fontSize=16, leading=18, textColor=color(BLUE), spaceAfter=7))
styles.add(ParagraphStyle(name="PaperH2", fontName="Calibri-Bold", fontSize=11.5, leading=13.5, textColor=color(BLUE), spaceBefore=6, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="PaperKicker", fontName="Calibri-Bold", fontSize=8.5, leading=10, textColor=color(TEAL), spaceAfter=5))
styles.add(ParagraphStyle(name="PaperSmall", fontName="Calibri", fontSize=8.3, leading=10, textColor=color(MUTED), spaceAfter=4))
styles.add(ParagraphStyle(name="PaperCaption", fontName="Calibri", fontSize=7.8, leading=9.2, textColor=color(MUTED), spaceAfter=5))
styles.add(ParagraphStyle(name="PaperCallout", fontName="Calibri-Bold", fontSize=9.2, leading=11.2, textColor=color(NAVY), backColor=color(LIGHT), borderPadding=4, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="PaperCode", fontName="Consolas", fontSize=7.3, leading=9, textColor=color(INK), backColor=color(LIGHT), borderPadding=7, spaceBefore=4, spaceAfter=5))
styles.add(ParagraphStyle(name="PaperStep", fontName="Calibri", fontSize=9.1, leading=11, leftIndent=15, firstLineIndent=-15, textColor=color(INK), spaceAfter=4))
styles.add(ParagraphStyle(name="PaperRef", fontName="Calibri", fontSize=7.8, leading=9.4, textColor=color(MUTED), spaceAfter=5))
styles.add(ParagraphStyle(name="CoverKicker", fontName="Calibri-Bold", fontSize=10, leading=12, alignment=TA_CENTER, textColor=color(TEAL), spaceAfter=14))
styles.add(ParagraphStyle(name="CoverTitle", fontName="Calibri-Bold", fontSize=29, leading=31, alignment=TA_CENTER, textColor=color(NAVY), spaceAfter=10))
styles.add(ParagraphStyle(name="CoverSubtitle", fontName="Calibri", fontSize=15, leading=18, alignment=TA_CENTER, textColor=color(MUTED), spaceAfter=14))
styles.add(ParagraphStyle(name="CoverBody", fontName="Calibri", fontSize=10, leading=13, alignment=TA_CENTER, textColor=color(INK), spaceAfter=14))


def later_page(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setFont("Calibri", 7.6)
    canvas.setFillColor(color(MUTED))
    canvas.drawString(doc.leftMargin, height - 37, "LANGFUSE RAG OPS  /  RESEARCH DESIGN PAPER")
    canvas.setStrokeColor(colors.HexColor("#D6DEE7"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, height - 43, width - doc.rightMargin, height - 43)
    canvas.drawString(doc.leftMargin, 34, "Harsh Chaudhary  |  Portfolio research")
    canvas.drawRightString(width - doc.rightMargin, 34, str(doc.page))
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setTitle("Langfuse for Graph-RAG Operations: A Traceable Evaluation Blueprint for Sentinel RAG Ops")
    canvas.setAuthor("Harsh Chaudhary")
    canvas.setSubject("Independent portfolio research design paper")
    canvas.restoreState()


def para(text, style="PaperBody"):
    return Paragraph(escape(text).replace("\n", "<br/>"), styles[style])


def rich_para(text, style="PaperBody"):
    return Paragraph(text, styles[style])


def paper_table(headers, rows, widths):
    col_widths = [width / 9360 * 6.5 * inch for width in widths]
    data = [[Paragraph(f"<b>{escape(item)}</b>", styles["PaperSmall"]) for item in headers]]
    for row in rows:
        data.append([Paragraph(escape(item), styles["PaperSmall"]) for item in row])
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F4F7")),
        ("TEXTCOLOR", (0, 0), (-1, -1), color(INK)),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D6DEE7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def add_cover(story):
    story.extend([
        Spacer(1, 0.42 * inch),
        para("PORTFOLIO RESEARCH DESIGN PAPER", "CoverKicker"),
        para("Langfuse for\nGraph-RAG Operations", "CoverTitle"),
        para("A Traceable Evaluation Blueprint\nfor Sentinel RAG Ops", "CoverSubtitle"),
        para("Observability architecture, trace contracts, evaluation methodology,\nand privacy-aware operational evidence", "CoverBody"),
        para("Harsh Chaudhary\n1 September 2026", "PaperSmall"),
        Spacer(1, 0.18 * inch),
        rich_para("<b>Abstract</b>", "PaperH2"),
        para("Graph-and-vector RAG systems can fail at ingestion, retrieval, context assembly, model invocation, or evaluation while still producing plausible outputs. This paper proposes a Langfuse-based observability and evaluation architecture for Sentinel RAG Ops, a LightRAG-derived document knowledge application. It defines trace boundaries, typed observations, safe metadata, an offline-to-online evaluation loop, operational metrics, release gates, and privacy controls. The work is a design study: it contributes a testable protocol and implementation roadmap, but reports no fabricated Langfuse traces or benchmark gains."),
        para("TRACE  /  EVALUATE  /  DIAGNOSE  /  GOVERN", "PaperKicker"),
        para("Paper status: independent portfolio research design; proposed Langfuse integration; not peer-reviewed.", "PaperSmall"),
    ])


def build():
    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=inch, rightMargin=inch, topMargin=0.72 * inch, bottomMargin=0.68 * inch,
        title="Langfuse for Graph-RAG Operations: A Traceable Evaluation Blueprint for Sentinel RAG Ops",
        author="Harsh Chaudhary",
    )
    story = []
    add_cover(story)
    step_number = 0
    for section_index, (title, blocks) in enumerate(PAGES, 1):
        story.append(PageBreak())
        story.append(para(f"{section_index:02d}  /  RESEARCH DESIGN", "PaperKicker"))
        story.append(para(title, "PaperH1"))
        step_number = 0
        for kind, data in blocks:
            if kind == "h2":
                story.append(para(data, "PaperH2"))
            elif kind == "p":
                story.append(para(data))
            elif kind == "small":
                story.append(para(data, "PaperSmall"))
            elif kind == "callout":
                story.append(para(data, "PaperCallout"))
            elif kind == "code":
                story.append(para(data, "PaperCode"))
            elif kind == "step":
                step_number += 1
                story.append(rich_para(f"<b>{step_number}. {escape(data[0])}.</b> {escape(data[1])}", "PaperStep"))
            elif kind == "table":
                story.extend([paper_table(*data), Spacer(1, 5)])
            elif kind == "figure":
                path = WORK / data[0]
                max_height = 2.35 * inch if data[0] == "observability_architecture.png" else 2.18 * inch
                image = Image(str(path), width=6.5 * inch, height=max_height)
                story.append(KeepTogether([image, para(data[1], "PaperCaption")]))
            elif kind == "ref":
                label, url = data
                story.append(rich_para(f"{escape(label)}<br/><link href='{escape(url)}' color='#{TEAL}'>{escape(url)}</link>", "PaperRef"))
    doc.build(story, onFirstPage=first_page, onLaterPages=later_page)
    print(f"Created {OUT}")


if __name__ == "__main__":
    build()
