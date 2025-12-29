def extract_sources(chunks):
    """
    Extracts unique sources from retrieved chunks.
    Each chunk is assumed to be a dict with a 'source' field.
    """

    sources = []

    for chunk in chunks:
        source = chunk.get("source")

        if not source:
            if chunk.get("type") == "pdf" and chunk.get("file") and chunk.get("page"):
                source = f"{chunk['file']} (page {chunk['page']})"
            elif chunk.get("type") == "web" and chunk.get("url"):
                source = chunk["url"]

        if source and source not in sources:
            sources.append(source)

    return sources
