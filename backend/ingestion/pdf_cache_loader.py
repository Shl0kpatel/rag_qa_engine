from __future__ import annotations

from pathlib import Path

from backend.ingestion.pdf_loader import load_pdf_as_text
from backend.utils.paths import raw_pdfs_dir, raw_text_dir


def get_raw_text(pdf_filename: str) -> str:
    """Load a PDF from data/raw/raw_pdfs and cache extracted text in data/raw/raw_text."""
    pdf_path = raw_pdfs_dir() / pdf_filename
    cache_path = raw_text_dir() / (Path(pdf_filename).stem + ".txt")

    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    text = load_pdf_as_text(str(pdf_path))
    raw_text_dir().mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text
