import re

def normalize_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


if __name__ == "__main__":
    with open("data/raw_text/google_sre.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = normalize_text(raw_text)
    print(cleaned_text[:1000])
