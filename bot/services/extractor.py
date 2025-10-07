import pdfplumber
import docx
from trafilatura import extract as extract_html
import os

def extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            return extract_pdf(path)
        elif ext == ".docx":
            return extract_docx(path)
        else:
            return ""
    except Exception as e:
        print(f"[extract_text_from_file] Error: {e}")
        return ""

def extract_pdf(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
