import re

def evaluate_answer(answer, context, similarity_scores):


    if not answer or "i don't know" in answer.lower():
        return 0.0

    # -------- Signal 1: Retrieval strength --------
    if similarity_scores:
        retrieval_score = sum(similarity_scores) / len(similarity_scores)
        retrieval_score = min(retrieval_score, 1.0)
    else:
        retrieval_score = 0.0

    # -------- Signal 2: Context coverage --------
    answer_tokens = set(re.findall(r"\w+", answer.lower()))
    context_tokens = set(re.findall(r"\w+", context.lower()))

    if len(answer_tokens) == 0:
        coverage_score = 0.0
    else:
        overlap = answer_tokens.intersection(context_tokens)
        coverage_score = len(overlap) / len(answer_tokens)

    coverage_score = min(coverage_score, 1.0)

    # -------- Signal 3: Behavior penalty --------
    penalty = 0.0

    if len(answer.split()) > 120:
        penalty += 0.2

    vague_markers = [
        "generally",
        "usually",
        "commonly",
        "often",
        "in most cases"
    ]

    for marker in vague_markers:
        if marker in answer.lower():
            penalty += 0.2
            break

    confidence = (
        0.4 * retrieval_score +
        0.4 * coverage_score +
        0.2 * (1 - penalty)
    )

    return round(max(0.0, min(confidence, 1.0)), 2)
