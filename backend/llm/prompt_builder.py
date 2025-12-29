from __future__ import annotations


def format_context(chunks: list[str]) -> str:
	context_parts: list[str] = []

	for i, chunk in enumerate(chunks, start=1):
		context_parts.append(f"[Context Chunk {i}]\n{chunk}\n")

	return "\n".join(context_parts)


def build_prompt(context: str, question: str) -> str:
	return f"""
SYSTEM:
You are a question-answering assistant.
Answer ONLY using the provided context.
If the answer is not present, say: "I don't know based on the provided context."

CONTEXT:
<<<
{context}
>>>

QUESTION:
{question}

INSTRUCTIONS:
- Be concise
- Do not use external knowledge
- Base your answer strictly on the context above
"""


__all__ = ["build_prompt", "format_context"]
