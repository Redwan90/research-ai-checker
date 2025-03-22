from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
import os
from io import BytesIO

def draw_section_title(c, y, title):
    c.setFillColor(HexColor("#003366"))
    c.rect(0, y - 5, 600, 25, fill=True, stroke=False)
    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, title)
    c.setFillColor("black")
    return y - 30

def add_footer(c, width, height, page_number):
    c.setFont("Helvetica", 8)
    c.setFillColor("gray")
    c.drawCentredString(width / 2, 30, "Qubahan Academic Journal | ISSN: 2709-8206 | DOI: 10.48161")
    c.drawCentredString(width / 2, 18, f"Page {page_number}")
    c.setFillColor("black")

def generate_pdf_report(analysis: dict, corrected_refs: list, reviews: str, formatting_results: dict):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    page_number = 1

    logo_path = "image.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, (width - 200) / 2, height - 80, width=200, height=40, mask='auto')
        y = height - 120
    else:
        y = height - 50

    y = draw_section_title(c, y, "📑 Article Quality & Reference Report")

    c.setFont("Helvetica", 10)
    for key, value in analysis.items():
        if isinstance(value, dict):
            c.drawString(50, y, f"{key}:")
            y -= 20
            for subkey, subvalue in value.items():
                c.drawString(60, y, f"- {subkey}: {len(subvalue)} issues")
                y -= 15
        elif isinstance(value, list):
            c.drawString(50, y, f"{key}: {len(value)} issues")
            y -= 20
        else:
            c.drawString(50, y, f"{key}: {value}")
            y -= 15
        if y < 100:
            add_footer(c, width, height, page_number)
            page_number += 1
            c.showPage()
            y = height - 50

    if corrected_refs:
        y = draw_section_title(c, y, "📚 Corrected References (APA 7)")
        for i, ref in enumerate(corrected_refs, start=1):
            c.drawString(50, y, f"{i}. {ref[:150]}")
            y -= 15
            if y < 100:
                add_footer(c, width, height, page_number)
                page_number += 1
                c.showPage()
                y = height - 50

    if formatting_results:
        y = draw_section_title(c, y, "📄 Formatting Check Summary")
        for section, issues in formatting_results.items():
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, section)
            y -= 18
            c.setFont("Helvetica", 10)
            if issues:
                for issue in issues:
                    c.drawString(60, y, f"❌ {issue[:100]}")
                    y -= 14
                    if y < 100:
                        add_footer(c, width, height, page_number)
                        page_number += 1
                        c.showPage()
                        y = height - 50
            else:
                c.drawString(60, y, "✅ All OK")
                y -= 14

    add_footer(c, width, height, page_number)
    c.save()
    buffer.seek(0)
    return buffer
