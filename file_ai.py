import os
import PyPDF2
from docx import Document


# ----------------------------------------------------
# Read PDF and DOCX files safely
# ----------------------------------------------------
def extract_text_from_file(path):
    text = ""

    # PDF
    if path.endswith(".pdf"):
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
        except Exception:
            return ""

    # DOCX
    elif path.endswith(".docx"):
        try:
            doc = Document(path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception:
            return ""

    return text.strip()


# ----------------------------------------------------
# Trim content for Telegram
# ----------------------------------------------------
def trim_for_telegram(text):
    if not text:
        return "No readable text found in the file."

    # Telegram messages max around 4000 chars
    if len(text) > 2000:
        return text[:2000] + "\n\n...(trimmed)"
    
    return text
