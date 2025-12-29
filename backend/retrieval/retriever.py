from __future__ import annotations

from backend.embeddings.vector_store import search


def _distance_to_similarity(distance: float) -> float:
	# FAISS IndexFlatL2 returns squared L2 distances (smaller is better).
	# Map to (0, 1] for downstream confidence heuristics.
	return 1.0 / (1.0 + max(0.0, float(distance)))


def retrieve_chunks(query: str, top_k: int = 5):
	"""Return (records, similarity_scores)."""
	records, distances = search(query, top_k=top_k)
	similarity_scores = [_distance_to_similarity(d) for d in distances]
	return records, similarity_scores


__all__ = ["retrieve_chunks"]
