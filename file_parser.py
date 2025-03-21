import fitz  # PyMuPDF
import tempfile
import docx

def extract_text_from_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    doc = fitz.open(tmp_path)
    text = ""
    for page in doc:
        text += page.get_text()

    doc.close()
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
