from __future__ import annotations

import streamlit as st

from backend.ui_api import ask, clear_index, has_index, ingest_pdf_bytes, ingest_url


st.set_page_config(page_title="RAG QA Engine", layout="wide")

st.title("RAG QA Engine")
st.caption("Ingest PDFs/URLs, then ask questions with citations.")

with st.sidebar:
    st.header("Knowledge Base")

    index_ready = has_index()
    st.write(f"Vector index: {'ready' if index_ready else 'not found'}")

    if st.button("Clear vector data", type="secondary"):
        clear_index()
        st.success("Vector data cleared.")
        st.rerun()

    st.divider()
    st.subheader("Ingest PDF")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"], accept_multiple_files=False)
    if st.button("Ingest uploaded PDF", disabled=uploaded is None):
        if uploaded is not None:
            res = ingest_pdf_bytes(uploaded.name, uploaded.getvalue())
            if res.ok:
                st.success(f"{res.message} (chunks: {res.chunks_added})")
                st.rerun()
            else:
                st.error(res.message)

    st.divider()
    st.subheader("Ingest URL")
    url = st.text_input("Web page URL")
    if st.button("Ingest URL"):
        res = ingest_url(url)
        if res.ok:
            st.success(f"{res.message} (chunks: {res.chunks_added})")
            st.rerun()
        else:
            st.error(res.message)

st.subheader("Ask")

col1, col2 = st.columns([3, 1], gap="large")

with col1:
    question = st.text_area("Your question", placeholder="Ask something about the ingested documents…")

with col2:
    top_k = st.slider("Top-K", min_value=1, max_value=10, value=5, step=1)
    ask_clicked = st.button("Get answer", type="primary", use_container_width=True)

if ask_clicked:
    if not has_index():
        st.error("No vector index found. Ingest a PDF or URL first.")
    elif not question.strip():
        st.warning("Type a question first.")
    else:
        with st.spinner("Retrieving and generating answer…"):
            result = ask(question, top_k=top_k)

        st.markdown("### Answer")
        st.write(result.get("answer", ""))

        st.markdown("### Confidence")
        st.write(float(result.get("confidence", 0.0)))

        sources = result.get("sources") or []
        st.markdown("### Citations")
        if not sources:
            st.write("No citations available.")
        else:
            for s in sources:
                st.write(f"- {s}")
