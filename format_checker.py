from docx import Document
import re

def check_font_and_spacing(docx_path):
    doc = Document(docx_path)
    issues = []
    for para in doc.paragraphs:
        for run in para.runs:
            font = run.font
            name = font.name
            size = font.size.pt if font.size else None
            if name and name != "Palatino Linotype":
                issues.append(f"Font is '{name}' instead of Palatino Linotype.")
            if size and size != 12:
                issues.append(f"Font size is {size} pt instead of 12 pt.")
    return list(set(issues))

def check_paragraph_format(docx_path):
    doc = Document(docx_path)
    issues = []
    for para in doc.paragraphs:
        fmt = para.paragraph_format
        if fmt.first_line_indent is None:
            issues.append("Paragraph missing first-line indent (should be 0.2\").")
        if fmt.alignment != 3:
            issues.append("Paragraph not justified.")
    return list(set(issues))

def check_margins(docx_path):
    doc = Document(docx_path)
    section = doc.sections[0]
    issues = []
    if abs(section.top_margin.inches - 1.0) > 0.05:
        issues.append("Top margin is not 1 inch.")
    if abs(section.bottom_margin.inches - 1.0) > 0.05:
        issues.append("Bottom margin is not 1 inch.")
    if abs(section.left_margin.inches - 0.7) > 0.05:
        issues.append("Left margin is not 0.7 inches.")
    if abs(section.right_margin.inches - 0.7) > 0.05:
        issues.append("Right margin is not 0.7 inches.")
    return issues

def check_headings(text):
    issues = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) > 100:
            continue
        if line.isupper() and not re.match(r"^\d", line) and len(line.split()) <= 6:
            if not line.replace(" ", "").isalpha():
                issues.append(f"Main heading '{line}' contains symbols or numbers — should be ALL CAPS only.")
        elif re.match(r"^\d+\.\s+[A-Z ]+$", line):
            if not line.isupper():
                issues.append(f"Subheading '{line}' should be ALL CAPS.")
        elif re.match(r"^\d+\.\d+\s+.*", line):
            title_part = line.split(" ", 1)[1] if " " in line else ""
            words = title_part.split()
            title_case = all(w.istitle() or w.lower() in ['of', 'and', 'to', 'in', 'on'] for w in words)
            if not title_case:
                issues.append(f"Sub-subheading '{line}' should be in Title Case.")
    return issues

def check_tables_figures(text):
    issues = []
    table_labels = re.findall(r"(Table\s+\d+\. .+)", text)
    figure_labels = re.findall(r"(FIGURE\s+\d+\. .+)", text)
    for label in table_labels:
        if not re.match(r"Table\s+\d+\.\s+[A-Z]", label):
            issues.append(f"Incorrect Table caption format: {label}")
    for label in figure_labels:
        if not re.match(r"FIGURE\s+\d+\.\s+[A-Z]", label):
            issues.append(f"Incorrect FIGURE caption format: {label}")
    if not re.search(r"see Table \d+", text):
        issues.append("❌ Tables not referenced in text (e.g., 'see Table 2').")
    if not re.search(r"see Figure \d+", text):
        issues.append("❌ Figures not referenced in text (e.g., 'see Figure 3').")
    return issues
