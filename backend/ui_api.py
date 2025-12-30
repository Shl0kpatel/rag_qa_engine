from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.embeddings.vector_store import add_records, clear_index, has_index
from backend.evaluation.answer_evaluator import evaluate_answer
from backend.evaluation.source_attribution import extract_sources
from backend.ingestion.pdf_loader import load_pdf_pages
from backend.ingestion.text_cleaner import normalize_text
from backend.ingestion.web_cache_loader import get_web_text
from backend.llm.answer_guard import guard_answer
from backend.llm.llm_client import generate_answer
from backend.llm.prompt_builder import build_prompt, format_context
from backend.processing.chunker import make_chunks
from backend.retrieval.retriever import retrieve_chunks
from backend.utils.paths import raw_pdfs_dir, raw_text_dir


@dataclass(frozen=True)
class IngestResult:
    ok: bool
    message: str
    chunks_added: int = 0
    stored_as: str | None = None


def ingest_pdf_bytes(filename: str, data: bytes) -> IngestResult:
    raw_pdfs_dir().mkdir(parents=True, exist_ok=True)

    safe_name = Path(filename).name
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"

    dest = raw_pdfs_dir() / safe_name
    dest.write_bytes(data)

    return ingest_pdf_path(dest)


def ingest_pdf_path(pdf_path: str | Path) -> IngestResult:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists() or not pdf_path.is_file():
        return IngestResult(ok=False, message=f"PDF not found: {pdf_path}")

    pages = load_pdf_pages(str(pdf_path))
    if not pages:
        return IngestResult(ok=False, message="No extractable text found in the PDF.")

    raw_text_dir().mkdir(parents=True, exist_ok=True)

    combined_text = "\n\n".join(p["text"] for p in pages)
    combined_text = normalize_text(combined_text)
    (raw_text_dir() / f"{pdf_path.stem}.txt").write_text(combined_text, encoding="utf-8")

    records: list[dict] = []
    for p in pages:
        page_num = int(p["page"])
        page_text = normalize_text(p["text"])
        if not page_text:
            continue

        for chunk in make_chunks(page_text):
            records.append(
                {
                    "text": chunk,
                    "type": "pdf",
                    "file": pdf_path.name,
                    "page": page_num,
                    "source": f"{pdf_path.name} (page {page_num})",
                }
            )

    add_records(records)
    return IngestResult(
        ok=True,
        message=f"Ingested PDF: {pdf_path.name}",
        chunks_added=len(records),
        stored_as=pdf_path.name,
    )


def ingest_url(url: str) -> IngestResult:
    url = (url or "").strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return IngestResult(ok=False, message="Please enter a valid http(s) URL.")

    text = get_web_text(url)
    text = normalize_text(text)
    if not text:
        return IngestResult(ok=False, message="No extractable text found on the page.")

    records = [
        {"text": chunk, "type": "web", "url": url, "source": url}
        for chunk in make_chunks(text)
    ]

    add_records(records)
    return IngestResult(ok=True, message=f"Ingested URL: {url}", chunks_added=len(records))


def ask(query: str, top_k: int = 5) -> dict:
    query = (query or "").strip()
    if not query:
        return {"answer": "", "confidence": 0.0, "sources": []}

    retrieved_chunks, similarity_scores = retrieve_chunks(query, top_k=top_k)

    if not retrieved_chunks:
        return {
            "answer": "No relevant information found in the knowledge base.",
            "confidence": 0.0,
            "sources": [],
        }

    context_text = format_context([c["text"] for c in retrieved_chunks])
    prompt = build_prompt(context_text, query)

    try:
        raw_answer = generate_answer(prompt)
    except RuntimeError as e:
        return {
            "answer": f"LLM not configured.\n{e}",
            "confidence": 0.0,
            "sources": extract_sources(retrieved_chunks),
        }

    final_answer = guard_answer(raw_answer, context_present=True)

    confidence = evaluate_answer(
        answer=final_answer, context=context_text, similarity_scores=similarity_scores
    )

    sources = extract_sources(retrieved_chunks)

    return {"answer": final_answer, "confidence": confidence, "sources": sources}


__all__ = [
    "IngestResult",
    "ask",
    "clear_index",
    "has_index",
    "ingest_pdf_bytes",
    "ingest_pdf_path",
    "ingest_url",
]
