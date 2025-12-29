from __future__ import annotations

import pdfplumber


def load_pdf_pages(pdf_path: str) -> list[dict]:
    """Return a list of {page: int, text: str}."""
    pages: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append({"page": i, "text": text})

    return pages


def load_pdf_as_text(pdf_path: str) -> str:
    pages = load_pdf_pages(pdf_path)
    return "\n".join(p["text"] for p in pages)
