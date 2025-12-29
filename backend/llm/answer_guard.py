

from __future__ import annotations


def guard_answer(answer: str | None, context_present: bool = True) -> str:

	if not context_present:
		return "No relevant information found in the knowledge base."

	if not answer or len(answer.strip()) == 0:
		return "I don't know based on the provided context."

	lower_answer = answer.lower()

	hallucination_markers = [
		"generally",
		"in most cases",
		"it is widely known",
		"commonly",
		"usually",
		"often",
		"as we know",
	]

	for marker in hallucination_markers:
		if marker in lower_answer:
			return "I don't know based on the provided context."

	lines = answer.strip().split("\n")
	if len(lines) > 8:
		answer = "\n".join(lines[:8])

	return answer.strip()


__all__ = ["guard_answer"]
