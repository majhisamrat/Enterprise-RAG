from typing import Any


def truncate_context(
    documents: list[dict[str, Any]],
    max_characters: int = 12000,
) -> list[dict[str, Any]]:
    """
    Limit the total context size.
    """

    result = []
    total = 0

    for doc in documents:

        length = len(doc["text"])

        if total + length > max_characters:
            break

        result.append(doc)
        total += length

    return result