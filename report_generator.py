from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf_report(analysis: dict, corrected_refs: list, reviews: str):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "🧠 Research Paper Analysis Report")
    y -= 30

    c.setFont("Helvetica", 11)
    for key, value in analysis.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                c.drawString(50, y, f"- {sub_key}: {len(sub_val)} issue(s)")
                y -= 18
        elif isinstance(value, list):
            c.drawString(50, y, f"- {key}: {len(value)} item(s)")
            y -= 18
        else:
            c.drawString(50, y, f"- {key}: {value}")
            y -= 18

    c.showPage()
    c.setFont("Helvetica", 10)
    for line in reviews.split("\n"):
        c.drawString(50, y, line[:90])
        y -= 14
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer
