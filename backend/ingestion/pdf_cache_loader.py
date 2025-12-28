import os
from pdf_loader import load_pdf_as_text

RAW_PDF_PATH = "data/raw_pdfs/google_sre.pdf"
CACHE_TEXT_PATH = "data/raw_text/google_sre.txt"

def get_raw_text() -> str:
    if os.path.exists(CACHE_TEXT_PATH):
        with open(CACHE_TEXT_PATH, "r", encoding="utf-8") as f:
            return f.read()

    text = load_pdf_as_text(RAW_PDF_PATH)

    os.makedirs(os.path.dirname(CACHE_TEXT_PATH), exist_ok=True)
    with open(CACHE_TEXT_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    return text


if __name__ == "__main__":
    text = get_raw_text()
    print(text[:1000])
