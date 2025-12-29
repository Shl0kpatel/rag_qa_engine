from __future__ import annotations

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_MODEL: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


def embed_chunks(chunks: list[str]):
    model = load_model()
    return model.encode(chunks, show_progress_bar=True)


