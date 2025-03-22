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
        if para.paragraph_format.first_line_indent is None:
            issues.append("Paragraph missing first-line indent (0.2\").")
        if para.paragraph_format.alignment != 3:  # 3 = justified
            issues.append("Paragraph not justified.")
    return list(set(issues))

def check_headings(text):
    issues = []
    lines = text.split("\n")

    for line in lines:
        clean = line.strip()
        if clean.isupper() and len(clean.split()) < 6 and len(clean) > 3:
            if not clean.isalpha():
                issues.append(f"Main heading may include symbols: '{clean}'")
        elif re.match(r"^\d+\.\s+[A-Z ]+$", clean):
            if not clean.isupper():
                issues.append(f"Subsection not in ALL CAPS: '{clean}'")
        elif re.match(r"^\d+\.\d+\s+.*", clean):
            if not re.search(r"[A-Z][a-z]", clean):
                issues.append(f"Sub-subsection not in Title Case: '{clean}'")
    return issues

def check_tables_figures(text):
    issues = []

    # Check if "Table X." and "Figure X." labels follow rules
    table_labels = re.findall(r"(Table\s+\d+\. .+)", text)
    figure_labels = re.findall(r"(FIGURE\s+\d+\. .+)", text)

    for label in table_labels:
        if not re.match(r"Table\s+\d+\.\s+[A-Z]", label):
            issues.append(f"Incorrect Table caption format: {label}")

    for label in figure_labels:
        if not re.match(r"FIGURE\s+\d+\.\s+[A-Z]", label):
            issues.append(f"Incorrect FIGURE caption format: {label}")

    # Check if tables/figures are referenced
    if not re.search(r"see Table \d+", text):
        issues.append("Tables not referenced in text (e.g., 'see Table 2').")
    if not re.search(r"see Figure \d+", text):
        issues.append("Figures not referenced in text (e.g., 'see Figure 3').")

    return issues
