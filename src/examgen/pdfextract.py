import pypdf

def extract_text(pdf_path:str) -> str:
    text = ""
    for page in pypdf.PdfReader(pdf_path).pages:
        text += page.extract_text() or ""
    return text