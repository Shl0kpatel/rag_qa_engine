from __future__ import annotations

import re
from pathlib import Path

from backend.ingestion.web_loader import load_webpage_as_text
from backend.utils.paths import raw_web_dir


def url_to_filename(url: str) -> str:
    filename = re.sub(r"https?://", "", url)
    filename = re.sub(r"[^\w]+", "_", filename)
    return filename.strip("_") + ".txt"


def get_web_text(url: str) -> str:
    raw_web_dir().mkdir(parents=True, exist_ok=True)

    filename = url_to_filename(url)
    cache_path = raw_web_dir() / filename

    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    text = load_webpage_as_text(url)

    cache_path.write_text(text, encoding="utf-8")

    return text


if __name__ == "__main__":
    url = "https://kubernetes.io/docs/concepts/overview/"
    text = get_web_text(url)
    print(text[:1000])
