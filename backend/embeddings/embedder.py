import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.processing.chunker import make_chunks
from sentence_transformers import SentenceTransformer
MODEL_NAME = "all-MiniLM-L6-v2"

def load_model():
    model = SentenceTransformer(MODEL_NAME)
    return model


def embed_chunks(chunks):
    model = load_model()
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings


if __name__ == "__main__":

    with open("data/raw/raw_text/google_sre.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = make_chunks(text)
    vectors = embed_chunks(chunks)

    print("Chunks:", len(chunks))
    print("Vector shape:", len(vectors), len(vectors[0]))


