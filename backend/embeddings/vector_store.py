import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.processing.chunker import make_chunks

INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "chunks.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_index(chunks):
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(chunks, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)

    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print("FAISS index saved.")


def search(query, top_k=5):
    model = SentenceTransformer(MODEL_NAME)

    index = faiss.read_index(INDEX_FILE)
    with open(CHUNKS_FILE, "rb") as f:
        chunks = pickle.load(f)

    q_emb = model.encode([query])
    distances, indices = index.search(q_emb, top_k)

    return [chunks[i] for i in indices[0]]


if __name__ == "__main__":
    with open("data/raw/raw_text/google_sre.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = make_chunks(text)

    # RUN ONCE
    build_index(chunks)

    print("\n--- TEST SEARCH ---\n")
    for r in search("What is Site Reliability Engineering?"):
        print("\n", r[:400])
