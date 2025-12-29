from __future__ import annotations

# Allow running as `python backend/app.py` as well as `python -m backend.app`.
if __package__ is None or __package__ == "":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import shutil
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

def run_query(query):
    # -------- Step 8: Retrieval --------
    retrieved_chunks, similarity_scores = retrieve_chunks(query)

    if not retrieved_chunks:
        return {
            "answer": "No relevant information found in the knowledge base.",
            "confidence": 0.0,
            "sources": []
        }

    context_text = format_context([c["text"] for c in retrieved_chunks])
    prompt = build_prompt(context_text, query)

    try:
        raw_answer = generate_answer(prompt)
    except RuntimeError as e:
        # LLM not configured (e.g., GROQ_API_KEY missing)
        return {
            "answer": f"LLM not configured.\n{e}",
            "confidence": 0.0,
            "sources": extract_sources(retrieved_chunks),
        }

    final_answer = guard_answer(raw_answer, context_present=True)

    confidence = evaluate_answer(
        answer=final_answer,
        context=context_text,
        similarity_scores=similarity_scores
    )

    sources = extract_sources(retrieved_chunks)

    return {
        "answer": final_answer,
        "confidence": confidence,
        "sources": sources
    }


def _prompt_choice() -> str:
    while True:
        choice = input("\nSelect ingestion source: [1] PDF  [2] URL  (or 'exit'): ").strip()
        if choice.lower() in {"exit", "quit", "q"}:
            return "exit"
        if choice in {"1", "2"}:
            return choice
        print("Invalid choice. Enter 1, 2, or 'exit'.")


def _ensure_pdf_in_raw_pdfs(user_input: str) -> Path:
    """Return path to a PDF stored under data/raw/raw_pdfs.

    Accepts either a filename (already in raw_pdfs) or a full path to a PDF,
    which will be copied into raw_pdfs.
    """
    raw_pdfs_dir().mkdir(parents=True, exist_ok=True)

    candidate = Path(user_input).expanduser()
    if candidate.exists() and candidate.is_file():
        dest = raw_pdfs_dir() / candidate.name
        if candidate.resolve() != dest.resolve():
            shutil.copy2(candidate, dest)
        return dest

    dest = raw_pdfs_dir() / user_input
    if dest.exists() and dest.is_file():
        return dest

    raise FileNotFoundError(
        f"PDF not found. Provide a valid path, or place the file in: {raw_pdfs_dir()}"
    )


def ingest_pdf() -> None:
    while True:
        user_input = input(
            f"\nEnter PDF filename (in {raw_pdfs_dir()}) or full path: "
        ).strip().strip('"')
        if user_input.lower() in {"exit", "quit", "q"}:
            return

        try:
            pdf_path = _ensure_pdf_in_raw_pdfs(user_input)
            break
        except Exception as e:
            print(str(e))

    pages = load_pdf_pages(str(pdf_path))
    if not pages:
        print("No extractable text found in the PDF.")
        return

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
    print(f"Ingested PDF: {pdf_path.name} (chunks: {len(records)})")


def ingest_url() -> None:
    while True:
        url = input("\nEnter URL (or 'exit'): ").strip()
        if url.lower() in {"exit", "quit", "q"}:
            return
        if url.startswith("http://") or url.startswith("https://"):
            break
        print("Please enter a valid http(s) URL.")

    text = get_web_text(url)
    text = normalize_text(text)
    if not text:
        print("No extractable text found on the page.")
        return

    records = [
        {"text": chunk, "type": "web", "url": url, "source": url}
        for chunk in make_chunks(text)
    ]

    add_records(records)
    print(f"Ingested URL: {url} (chunks: {len(records)})")


def main() -> None:
    print("RAG QA Engine")
    print("Step 1: Ingest a PDF or a URL (cached)")
    print("Step 2: Build/update vectors (FAISS)")
    print("Step 3: Ask questions with citations")

    choice = _prompt_choice()
    if choice == "exit":
        return
    if choice == "1":
        ingest_pdf()
    elif choice == "2":
        ingest_url()

    if not has_index():
        print("\nVector index not found. Ingestion is required before Q&A.")
        return

    try:
        while True:
            user_query = input("\nAsk a question (or type 'exit'): ").strip()
            if user_query.lower() == "exit":
                break
            if not user_query:
                continue

            result = run_query(user_query)

            print("\nAnswer:")
            print(result["answer"])

            print(f"\nConfidence: {result['confidence']}")

            if result["sources"]:
                print("\nCitations:")
                for src in result["sources"]:
                    print(f"- {src}")
    finally:
        # Optional privacy-by-default: clear vectors on exit so next user
        # doesn't see previous ingested data.
        ans = input("\nClear vector data on exit? [y/N]: ").strip().lower()
        if ans in {"y", "yes"}:
            clear_index()
            print("Vector data cleared.")


if __name__ == "__main__":
    main()
