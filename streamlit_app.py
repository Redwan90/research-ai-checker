import streamlit as st
import tempfile
import re
from io import StringIO
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
    check_subheadings,
    check_bullet_points,
    check_reference_formatting
)

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
    return report.getvalue()

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name[-5:]) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(open(file_path, "rb"))
        font_issues = paragraph_issues = margin_issues = subheading_issues = bullet_issues = ref_format_issues = []
    else:
        text = extract_text_from_docx(open(file_path, "rb"))
        font_issues = check_font_and_spacing(file_path)
        paragraph_issues = check_paragraph_format(file_path)
        margin_issues = check_margins(file_path)
        subheading_issues = check_subheadings(file_path)
        bullet_issues = check_bullet_points(file_path)
        ref_format_issues = check_reference_formatting(file_path)

    author_name = extract_author_name(text)
    if author_name:
        st.markdown(f"**🧑‍💼 Detected Author Name:** `{author_name}`")

    ref_report = check_references(text, author_name)
    references = ref_report.get("Extracted References", [])

    heading_issues = check_headings(text)
    table_issues = check_tables_figures(text)

    st.subheader("📑 Reference Analysis Summary")
    st.json(ref_report)

    if "Missing In-Text Citations" in ref_report:
        if ref_report["Missing In-Text Citations"]:
            st.error("❌ Some references are listed but never cited in the text.")
            st.markdown("**Missing In-Text Citations:**")
            st.markdown(", ".join([f"[{num}]" for num in ref_report["Missing In-Text Citations"]]))
        else:
            st.success("✅ All references in the list are cited in the body.")

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

    if st.checkbox("✨ Show corrected references in APA 7 style"):
        corrected_refs = correct_references(references)
        for i, ref in enumerate(corrected_refs, start=1):
            st.markdown(f"{i}. {ref}")

    st.subheader("🧾 Formatting & Style Check")

    with st.expander("🔍 Formatting Validation Results", expanded=True):
        def show_checklist(icon_title, issues):
            st.markdown(f"**{icon_title}**")
            if issues:
                for issue in issues:
                    st.markdown(f"❌ {issue}")
            else:
                st.markdown("✅ All OK")

        show_checklist("🔤 Font Checks", font_issues)
        show_checklist("📐 Paragraph Format", paragraph_issues)
        show_checklist("🧱 Margin Checks", margin_issues)
        show_checklist("📘 Heading Structure", heading_issues)
        show_checklist("📊 Table and Figure Captions", table_issues)
        show_checklist("🔢 Subheading & Sub-subheading Checks", subheading_issues)
        show_checklist("• Bullet Point Style Checks", bullet_issues)
        show_checklist("📚 References Style Checks", ref_format_issues)

        formatting_txt = generate_formatting_txt_report([
            ("Font Checks", font_issues),
            ("Paragraph Format", paragraph_issues),
            ("Margin Checks", margin_issues),
            ("Heading Structure", heading_issues),
            ("Table and Figure Captions", table_issues),
            ("Subheading Checks", subheading_issues),
            ("Bullet Point Checks", bullet_issues),
            ("References Style Checks", ref_format_issues)
        ])
        st.download_button(
            label="📥 Download Formatting Report (.txt)",
            data=formatting_txt,
            file_name="formatting_report.txt",
            mime="text/plain"
        )

    if st.button("📄 Download Full Report as PDF"):
        corrected_refs = correct_references(references)
        formatting_results = {
            "Font Checks": font_issues,
            "Paragraph Format": paragraph_issues,
            "Margin Checks": margin_issues,
            "Heading Structure": heading_issues,
            "Table and Figure Captions": table_issues,
            "Subheading Checks": subheading_issues,
            "Bullet Point Checks": bullet_issues,
            "References Style Checks": ref_format_issues
        }
        pdf_buffer = generate_pdf_report(ref_report, corrected_refs, "", formatting_results)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer.getvalue(),
            file_name="QAJ_AI_Report.pdf",
            mime="application/pdf"
        )

else:
    st.info("Upload a PDF or DOCX research article to begin analysis.")
