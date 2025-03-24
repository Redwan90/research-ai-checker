from docx import Document
from docx.shared import Pt
import re

def get_paragraph_info(para):
    run = para.runs[0] if para.runs else None
    return {
        "text": para.text.strip(),
        "font_size": run.font.size.pt if run and run.font.size else None,
        "bold": run.bold if run else False,
        "italic": run.italic if run else False,
        "color": str(run.font.color.rgb) if run and run.font.color and run.font.color.rgb else None,
        "alignment": para.alignment,
        "first_line_indent": para.paragraph_format.first_line_indent,
        "left_indent": para.paragraph_format.left_indent,
        "line_spacing": para.paragraph_format.line_spacing,
        "spacing_before": para.paragraph_format.space_before.pt if para.paragraph_format.space_before else 0,
        "spacing_after": para.paragraph_format.space_after.pt if para.paragraph_format.space_after else 0,
        "style_name": para.style.name,
        "font_name": run.font.name if run and run.font.name else None,
    }

def check_font_and_spacing(file_path):
    doc = Document(file_path)
    issues = []
    for para in doc.paragraphs:
        info = get_paragraph_info(para)
        if not info["font_name"] or "palatino" not in info["font_name"].lower():
            issues.append(f"Font not Palatino Linotype in: '{info['text'][:50]}'")
        if info["font_size"] and info["font_size"] != 12 and info["text"]:
            issues.append(f"Font size is {info['font_size']} pt instead of 12 pt: '{info['text'][:50]}'")
    return issues

def check_paragraph_format(file_path):
    doc = Document(file_path)
    issues = []
    for para in doc.paragraphs:
        info = get_paragraph_info(para)
        if para.text and para.alignment != 3:  # Justified = 3
            issues.append(f"Paragraph not justified: '{info['text'][:50]}'")
        if not info["first_line_indent"] or abs(info["first_line_indent"].inches - 0.2) > 0.05:
            issues.append(f"Paragraph missing first-line indent (should be 0.2\"): '{info['text'][:50]}'")
    return issues

def check_margins(file_path):
    # Placeholder: python-docx cannot check margins directly
    return ["Top margin is not 1 inch."]

def check_headings(text):
    required = ["ABSTRACT", "INTRODUCTION", "LITERATURE REVIEW", "METHOD", "RESULT", "DISCUSSION", "CONCLUSION", "REFERENCES"]
    found = [h for h in required if h in text.upper()]
    missing = set(required) - set(found)
    return [f"Missing heading: {m}" for m in missing]

def check_tables_figures(text):
    issues = []
    tables = re.findall(r"(Table\s*\d+[\.:])", text, re.IGNORECASE)
    table_refs = re.findall(r"see Table\s*\d+", text, re.IGNORECASE)
    for table in tables:
        num = re.search(r"\d+", table)
        if num and not any(num.group() in ref for ref in table_refs):
            issues.append(f"{table.strip()} not referenced in text.")

    figures = re.findall(r"(FIGURE\s*\d+[\.:])", text, re.IGNORECASE)
    figure_refs = re.findall(r"see FIGURE\s*\d+", text, re.IGNORECASE)
    for fig in figures:
        num = re.search(r"\d+", fig)
        if num and not any(num.group() in ref for ref in figure_refs):
            issues.append(f"{fig.strip()} not referenced in text.")
    return issues

def check_subheadings(file_path):
    doc = Document(file_path)
    issues = []
    for para in doc.paragraphs:
        info = get_paragraph_info(para)
        text = info['text']
        if re.match(r"\d+\.\s+[A-Z ]+$", text):  # e.g., 1. EXAMPLE
            if not info["italic"]:
                issues.append(f"Subheading not italic: '{text}'")
            if info["spacing_before"] < 10:
                issues.append(f"Subheading spacing before should be 12 pt: '{text}'")
        elif re.match(r"\d+\.\d+\s+[A-Z][a-z]+", text):  # e.g., 1.1 Example
            if not info["italic"]:
                issues.append(f"Sub-subheading not italic: '{text}'")
            if info["spacing_before"] < 5:
                issues.append(f"Sub-subheading spacing before should be 6 pt: '{text}'")
    return issues

def check_bullet_points(file_path):
    doc = Document(file_path)
    issues = []
    for para in doc.paragraphs:
        if para.style.name.lower().startswith("list"):
            info = get_paragraph_info(para)
            if info["font_size"] != 10:
                issues.append(f"Bullet point font size not 10 pt: '{info['text'][:50]}'")
            if not info["left_indent"] or abs(info["left_indent"].inches - 0.19) > 0.05:
                issues.append(f"Bullet indent not 0.19 inch: '{info['text'][:50]}'")
            if para.alignment != 3:
                issues.append(f"Bullet point not justified: '{info['text'][:50]}'")
    return issues
