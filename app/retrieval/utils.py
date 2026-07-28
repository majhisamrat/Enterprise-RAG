def normalize_scores(
    scores: list[float],
) -> list[float]:
    """
    Min-max normalize scores.
    """

    if not scores:
        return []

    minimum = min(scores)
    maximum = max(scores)

    if minimum == maximum:
        return [1.0] * len(scores)

    return [
        (s - minimum) / (maximum - minimum)
        for s in scores
    ]