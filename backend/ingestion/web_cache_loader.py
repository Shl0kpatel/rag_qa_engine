import os
import re
from web_loader import load_webpage_as_text

RAW_WEB_DIR = "data/raw/raw_web"


def url_to_filename(url: str) -> str:
    filename = re.sub(r"https?://", "", url)
    filename = re.sub(r"[^\w]+", "_", filename)
    return filename.strip("_") + ".txt"


def get_web_text(url: str) -> str:
    os.makedirs(RAW_WEB_DIR, exist_ok=True)

    filename = url_to_filename(url)
    cache_path = os.path.join(RAW_WEB_DIR, filename)

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    text = load_webpage_as_text(url)

    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text


if __name__ == "__main__":
    url = "https://kubernetes.io/docs/concepts/overview/"
    text = get_web_text(url)
    print(text[:1000])
