import requests
from bs4 import BeautifulSoup


def load_webpage_as_text(url: str) -> str:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


if __name__ == "__main__":
    url = "https://kubernetes.io/docs/concepts/overview/"
    text = load_webpage_as_text(url)
    print(text[:1000])
