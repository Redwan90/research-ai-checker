import streamlit as st
from file_parser import extract_text_from_pdf, extract_text_from_docx
from ref_checker import check_references
from citation_formatter import correct_references
from report_generator import generate_pdf_report
from format_checker import (
    check_font_and_spacing,
    check_paragraph_format,
    check_headings,
    check_tables_figures,
)
import re
import tempfile

st.set_page_config(page_title="Research Paper Checker", layout="wide")
st.title("🧠 Research Paper Checker (Free AI Tool)")

uploaded_file = st.file_uploader("Upload your Research Article (PDF or DOCX)", type=["pdf", "docx"])

def extract_author_name(text):
    match = re.search(r"\n(.*?)\n.*?\n", text)
    if match:
        raw_line = match.group(1)
        clean_line = re.sub(r"[\d\*]+", "", raw_line)
        clean_line = re.sub(r"\s{2,}", " ", clean_line)
        clean_line = clean_line.strip(",; \n")
        return clean_line
    return ""

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name[-5:]) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(open(file_path, "rb"))
        font_issues = []
        paragraph_issues = []
    else:
        text = extract_text_from_docx(open(file_path, "rb"))
        font_issues = check_font_and_spacing(file_path)
        paragraph_issues = check_paragraph_format(file_path)

    author_name = extract_author_name(text)
    if author_name:
        st.markdown(f"**Detected author name:** `{author_name}`")

    ref_report = check_references(text, author_name)
    references = ref_report.get("Extracted References", [])

    heading_issues = check_headings(text)
    table_issues = check_tables_figures(text)

    st.subheader("📑 Reference Analysis")
    st.write(ref_report)

    if "Highly Cited Authors (≥4)" in ref_report:
        st.subheader("👥 Authors Cited 4+ Times")
        cited = ref_report["Highly Cited Authors (≥4)"]
        for author, refs in cited.items():
            st.markdown(f"**{author.title()}** — {len(refs)} times")
            seen = set()
            for ref in refs:
                if ref not in seen:
                    positions = [i + 1 for i, r in enumerate(references) if r == ref]
                    for pos in positions:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{pos}. {ref}")
                    seen.add(ref)

    if st.checkbox("✨ Show corrected references in APA 7 style"):
        corrected_refs = correct_references(references)
        for i, ref in enumerate(corrected_refs, start=1):
            st.markdown(f"{i}. {ref}")

    st.subheader("🧾 Formatting & Style Check")
    if font_issues or paragraph_issues or heading_issues or table_issues:
        if font_issues:
            st.write("🔤 Font Issues:")
            for i in font_issues:
                st.markdown(f"- {i}")
        if paragraph_issues:
            st.write("📐 Paragraph Issues:")
            for i in paragraph_issues:
                st.markdown(f"- {i}")
        if heading_issues:
            st.write("📘 Heading Format Issues:")
            for i in heading_issues:
                st.markdown(f"- {i}")
        if table_issues:
            st.write("📊 Table/Figure Caption Issues:")
            for i in table_issues:
                st.markdown(f"- {i}")
    else:
        st.success("✅ No formatting/style issues found.")

    if st.button("📄 Download Full Report as PDF"):
        corrected_refs = correct_references(references)
        pdf = generate_pdf_report(ref_report, corrected_refs, "")
        st.download_button("Download PDF", pdf, file_name="article_review_report.pdf")

else:
    st.info("Please upload a PDF or DOCX file to begin.")
