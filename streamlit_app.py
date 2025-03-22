import streamlit as st
import tempfile
import re
from file_parser import extract_text_from_pdf, extract_text_from_docx
from ref_checker import check_references
from citation_formatter import correct_references
from report_generator import generate_pdf_report
from format_checker import (
    check_font_and_spacing,
    check_paragraph_format,
    check_margins,
    check_headings,
    check_tables_figures,
)
from io import StringIO

st.set_page_config(page_title="Research AI Checker", layout="wide")
st.title("🧠 Research Paper Quality & Format Checker")

uploaded_file = st.file_uploader("📤 Upload your research article (PDF or DOCX)", type=["pdf", "docx"])

def extract_author_name(text):
    match = re.search(r"\n(.*?)\n.*?\n", text)
    if match:
        raw_line = match.group(1)
        clean_line = re.sub(r"[\d\*]+", "", raw_line)
        clean_line = re.sub(r"\s{2,}", " ", clean_line)
        clean_line = clean_line.strip(",; \n")
        return clean_line
    return ""

def generate_formatting_txt_report(sections):
    report = StringIO()
    report.write("🔍 Formatting Validation Report\n\n")
    for title, issues in sections:
        report.write(f"=== {title} ===\n")
        if issues:
            for issue in issues:
                report.write(f"❌ {issue}\n")
        else:
            report.write("✅ All OK\n")
        report.write("\n")
    report.seek(0)
    return report

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name[-5:]) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(open(file_path, "rb"))
        font_issues = []
        paragraph_issues = []
        margin_issues = []
    else:
        text = extract_text_from_docx(open(file_path, "rb"))
        font_issues = check_font_and_spacing(file_path)
        paragraph_issues = check_paragraph_format(file_path)
        margin_issues = check_margins(file_path)

    author_name = extract_author_name(text)
    if author_name:
        st.markdown(f"**🧑‍💼 Detected Author Name:** `{author_name}`")

    # Reference analysis
    ref_report = check_references(text, author_name)
    references = ref_report.get("Extracted References", [])

    # Formatting checks
    heading_issues = check_headings(text)
    table_issues = check_tables_figures(text)

    st.subheader("📑 Reference Analysis Summary")
    st.json(ref_report)

    # Highly cited authors
    if "Highly Cited Authors (≥4)" in ref_report:
        cited = ref_report["Highly Cited Authors (≥4)"]
        if cited:
            st.subheader("👥 Authors Cited 4+ Times")
            for author, refs in cited.items():
                st.markdown(f"**{author.title()}** — {len(refs)} times")
                shown = set()
                for ref in refs:
                    if ref not in shown:
                        indices = [i + 1 for i, r in enumerate(references) if r == ref]
                        for idx in indices:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{idx}. {ref}")
                        shown.add(ref)

    # APA Formatter
    if st.checkbox("✨ Show corrected references in APA 7 style"):
        corrected_refs = correct_references(references)
        for i, ref in enumerate(corrected_refs, start=1):
            st.markdown(f"{i}. {ref}")

    # Formatting Checklist
    st.subheader("🧾 Formatting & Style Check")

    def show_checklist(title, issues):
        st.markdown(f"**{title}**")
        if issues:
            for issue in issues:
                st.markdown(f"❌ {issue}")
        else:
            st.markdown("✅ All OK")

    with st.expander("🔍 Formatting Validation Results", expanded=True):
        show_checklist("🔤 Font Checks", font_issues)
        show_checklist("📐 Paragraph Format", paragraph_issues)
        show_checklist("🧱 Margin Checks", margin_issues)
        show_checklist("📘 Heading Structure", heading_issues)
        show_checklist("📊 Table and Figure Captions", table_issues)

        # Download .txt formatting report
        formatting_txt = generate_formatting_txt_report([
            ("Font Checks", font_issues),
            ("Paragraph Format", paragraph_issues),
            ("Margin Checks", margin_issues),
            ("Heading Structure", heading_issues),
            ("Table and Figure Captions", table_issues)
        ])
        st.download_button(
            label="📥 Download Formatting Report (.txt)",
            data=formatting_txt,
            file_name="formatting_report.txt",
            mime="text/plain"
        )

    # Download full PDF report
    if st.button("📄 Download Full Report as PDF"):
        corrected_refs = correct_references(references)
        formatting_results = {
            "Font Checks": font_issues,
            "Paragraph Format": paragraph_issues,
            "Margin Checks": margin_issues,
            "Heading Structure": heading_issues,
            "Table and Figure Captions": table_issues
        }
        pdf = generate_pdf_report(ref_report, corrected_refs, "", formatting_results)
        st.download_button("📥 Download PDF", pdf, file_name="QAJ_AI_Report.pdf")

else:
    st.info("Upload a PDF or DOCX research article to begin analysis.")
