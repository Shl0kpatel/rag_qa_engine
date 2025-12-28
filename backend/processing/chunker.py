MAX_WORDS = 400
OVERLAP_WORDS = 80


def count_words(a):
    return len(a.split())


def make_paragraphs(a):
    b = []
    temp = []

    parts = a.split("\n\n")
    for p in parts:
        if p.strip():
            b.append(p.strip())

    if len(b) > 1:
        return b

    lines = a.split("\n")
    b = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        temp.append(line)

        if line.endswith(".") or line.endswith(":"):
            b.append(" ".join(temp))
            temp = []

    if temp:
        b.append(" ".join(temp))

    return b


def get_overlap(a):
    words = a.split()
    if len(words) <= OVERLAP_WORDS:
        return a
    return " ".join(words[len(words) - OVERLAP_WORDS:])


def make_chunks(a):
    paras = make_paragraphs(a)

    res = []
    curr = []
    size = 0

    for p in paras:
        p_size = count_words(p)

        if p_size > MAX_WORDS:
            if curr:
                res.append("\n\n".join(curr))
                curr = []
                size = 0

            w = p.split()
            i = 0
            while i < len(w):
                part = " ".join(w[i:i + MAX_WORDS])
                res.append(part)
                i += MAX_WORDS - OVERLAP_WORDS
            continue

        if size + p_size <= MAX_WORDS:
            curr.append(p)
            size += p_size
        else:
            done = "\n\n".join(curr)
            res.append(done)

            ov = get_overlap(done)
            curr = [ov, p]
            size = count_words(ov) + p_size

    if curr:
        res.append("\n\n".join(curr))

    return res


if __name__ == "__main__":
    with open("data/raw/raw_text/google_sre.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = make_chunks(text)
    print(len(chunks))

    sizes = [len(x.split()) for x in chunks]
    print(min(sizes), max(sizes))
