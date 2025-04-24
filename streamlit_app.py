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
        raw = match.group(1)
        clean = re.sub(r"[\d\*]+", "", raw)
        return re.sub(r"\s{2,}", " ", clean).strip(",; \n")
    return ""

def generate_formatting_txt_report(sections):
    buf = StringIO()
    buf.write("🔍 Formatting Validation Report\n\n")
    for title, issues in sections:
        buf.write(f"=== {title} ===\n")
        if issues:
            for issue in issues:
                buf.write(f"❌ {issue}\n")
        else:
            buf.write("✅ All OK\n")
        buf.write("\n")
    return buf.getvalue()

def show_checklist(title, issues):
    st.markdown(f"### {title}")
    if issues:
        for issue in issues:
            st.markdown(f"❌ {issue}")
    else:
        st.markdown("✅ All OK")

if uploaded_file:
    # Save uploaded to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name[-5:]) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    # Extract text & formatting issues
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

    # Reference & author extraction
    author = extract_author_name(text)
    if author:
        st.markdown(f"**🧑‍💼 Detected Author Name:** `{author}`")

    ref_report = check_references(text, author)
    refs = ref_report.get("Extracted References", [])

    heading_issues = check_headings(text)
    table_issues = check_tables_figures(text)

    # Display summary JSON
    st.subheader("📑 Reference Analysis Summary")
    st.json(ref_report)

    # Missing in-text citations
    missing = ref_report.get("Missing In-Text Citations", [])
    if missing:
        st.error("❌ Some references are listed but never cited in the text.")
        st.markdown("**Missing In-Text Citations:** " + ", ".join(f"[{i}]" for i in missing))
    else:
        st.success("✅ All listed references are cited in the body.")

    # Authors cited >4
    cited_dict = ref_report.get("Highly Cited Authors (>4)", {})
    if cited_dict:
        st.subheader("👥 Authors Cited More Than 4 Times")
        for auth, rlist in cited_dict.items():
            st.markdown(f"**{auth.title()}** — {len(rlist)} times")
            shown = set()
            for r in rlist:
                if r not in shown:
                    idxs = [i+1 for i,x in enumerate(refs) if x==r]
                    for idx in idxs:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{idx}. {r}")
                    shown.add(r)

    # Qubahan citations
    qaj_list = ref_report.get("Qahanan Citations", ref_report.get("Qubahan Citations", []))
    if qaj_list:
        st.subheader("🔍 Qubahan Academic Journal Citations")
        st.markdown(f"Total QAJ citations: {len(qaj_list)}")
        if len(qaj_list) > 2:
            excess = ref_report.get("Excess Qubahan Citations", [])
            st.markdown(f"❌ Only up to 2 QAJ citations allowed. {len(excess)} overage:")
            for r in excess:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{r}")

    # Corrected APA references
    if st.checkbox("✨ Show corrected references in APA 7 style"):
        corrected = correct_references(refs)
        for i, r in enumerate(corrected, start=1):
            st.markdown(f"{i}. {r}")

    # Formatting & Style Check
    st.subheader("🧾 Formatting & Style Check")
    show_checklist("🔤 Font Checks", font_issues)
    show_checklist("📐 Paragraph Format", paragraph_issues)
    show_checklist("📏 Margin Checks", margin_issues)
    show_checklist("🔠 Heading Structure", heading_issues)
    show_checklist("📊 Table and Figure Captions", table_issues)
    show_checklist("🔢 Subheading & Sub-subheading Checks", subheading_issues)
    show_checklist("• Bullet Point Style Checks", bullet_issues)
    show_checklist("📚 References Style Checks", ref_format_issues)

    # Download formatting report
    fmt_text = generate_formatting_txt_report([
        ("Font Checks", font_issues),
        ("Paragraph Format", paragraph_issues),
        ("Margin Checks", margin_issues),
        ("Heading Structure", heading_issues),
        ("Table and Figure Captions", table_issues),
        ("Subheading Checks", subheading_issues),
        ("Bullet Point Checks", bullet_issues),
        ("References Style Checks", ref_format_issues),
    ])
    st.download_button(
        "📥 Download Formatting Report (.txt)",
        fmt_text,
        "formatting_report.txt",
        "text/plain"
    )

    # Download full PDF report
    if st.button("📄 Download Full Report as PDF"):
        corrected = correct_references(refs)
        fmt_results = {
            "Font Checks": font_issues,
            "Paragraph Format": paragraph_issues,
            "Margin Checks": margin_issues,
            "Heading Structure": heading_issues,
            "Table and Figure Captions": table_issues,
            "Subheading Checks": subheading_issues,
            "Bullet Point Checks": bullet_issues,
            "References Style Checks": ref_format_issues
        }
        pdf_buf = generate_pdf_report(ref_report, corrected, "", fmt_results)
        st.download_button(
            "📥 Download PDF",
            pdf_buf.getvalue(),
            "QAJ_AI_Report.pdf",
            "application/pdf"
        )

else:
    st.info("Upload a PDF or DOCX research article to begin analysis.")
