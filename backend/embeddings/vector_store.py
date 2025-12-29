from __future__ import annotations

from pathlib import Path
import pickle
from typing import Any, Iterable

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.utils.paths import vectors_dir

MODEL_NAME = "all-MiniLM-L6-v2"

_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


def _index_path() -> Path:
    return vectors_dir() / "faiss_index.bin"


def _records_path() -> Path:
    return vectors_dir() / "records.pkl"


def _ensure_vectors_dir() -> None:
    vectors_dir().mkdir(parents=True, exist_ok=True)


def has_index() -> bool:
    return _index_path().exists() and _records_path().exists()


def build_index(records: list[dict[str, Any]]) -> None:
    """Create a fresh FAISS index from records.

    Each record must contain at least: {"text": str, "source": str}.
    """
    _ensure_vectors_dir()

    texts = [r["text"] for r in records]
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True)

    dim = int(embeddings.shape[1])
    index = faiss.IndexFlatL2(dim)
    index.add(np.asarray(embeddings, dtype=np.float32))

    faiss.write_index(index, str(_index_path()))
    with open(_records_path(), "wb") as f:
        pickle.dump(records, f)


def add_records(records: list[dict[str, Any]]) -> None:
    """Append records to existing index; creates index if missing."""
    if not records:
        return

    if not has_index():
        build_index(records)
        return

    index = faiss.read_index(str(_index_path()))
    with open(_records_path(), "rb") as f:
        existing_records: list[dict[str, Any]] = pickle.load(f)

    texts = [r["text"] for r in records]
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    index.add(np.asarray(embeddings, dtype=np.float32))
    existing_records.extend(records)

    faiss.write_index(index, str(_index_path()))
    with open(_records_path(), "wb") as f:
        pickle.dump(existing_records, f)


def search(query: str, top_k: int = 5) -> tuple[list[dict[str, Any]], list[float]]:
    """Return (records, distances)."""
    if not has_index():
        raise FileNotFoundError(
            "FAISS index not found. Ingest data and build vectors first."
        )

    model = _get_model()
    index = faiss.read_index(str(_index_path()))
    with open(_records_path(), "rb") as f:
        records: list[dict[str, Any]] = pickle.load(f)

    q_emb = model.encode([query])
    distances, indices = index.search(np.asarray(q_emb, dtype=np.float32), top_k)

    hits: list[dict[str, Any]] = []
    hit_distances: list[float] = []
    for dist, idx in zip(distances[0].tolist(), indices[0].tolist(), strict=False):
        if idx < 0:
            continue
        hits.append(records[idx])
        hit_distances.append(float(dist))

    return hits, hit_distances
