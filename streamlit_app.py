import streamlit as st
from file_parser import extract_text_from_pdf, extract_text_from_docx
from ref_checker import check_references
from citation_formatter import correct_references
from report_generator import generate_pdf_report
import re

st.set_page_config(page_title="Research Paper Checker", layout="wide")
st.title("🧠 Research Paper Checker (Free AI Tool)")

st.markdown("""
This tool checks:
- 🔁 Duplicated References
- 🔍 Self-Citations
- 🚫 Qubahan Journal Citations
- 📚 APA 7th Edition Formatting (Bold Year, No DOI)
- 👥 Authors Cited ≥ 4 Times
- 📄 Generate PDF Report
""")

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
    with st.spinner("Extracting text from document..."):
        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX.")
            st.stop()

    author_name = extract_author_name(text)
    if author_name:
        st.markdown(f"**Detected author name:** `{author_name}`")
    else:
        st.warning("Could not detect author name from the paper. Self-citation check may be skipped.")

    st.subheader("📑 Reference Analysis")
    ref_report = check_references(text, author_name)
    st.write(ref_report)

    references = ref_report.get("Extracted References", [])

    if "Highly Cited Authors (≥4)" in ref_report:
        cited = ref_report["Highly Cited Authors (≥4)"]
        if cited:
            st.subheader("👥 Authors Cited 4+ Times")
            for author, refs in cited.items():
                st.markdown(f"**{author.title()}** — {len(refs)} times")
                shown = set()
                for ref in refs:
                    if ref not in shown:
                        index_list = [i + 1 for i, r in enumerate(references) if r == ref]
                        for idx in index_list:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{idx}. {ref}")
                        shown.add(ref)
        else:
            st.info("No authors cited 4 or more times.")

    if st.checkbox("✨ Show corrected references in APA 7 style"):
        corrected_refs = correct_references(references)
        for i, ref in enumerate(corrected_refs, start=1):
            st.markdown(f"{i}. {ref}")

    if st.button("📄 Download Full Report as PDF"):
        corrected_refs = correct_references(references)
        pdf = generate_pdf_report(ref_report, corrected_refs, "")
        st.download_button("Download PDF", pdf, file_name="article_review_report.pdf")

    st.success("Done ✅")

else:
    st.info("Please upload a PDF or DOCX file to begin.")
