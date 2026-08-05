from typing import Any


def validate_documents(
    documents: list[dict[str, Any]],
) -> None:
    """
    Validate retrieved documents before reranking.
    """
    if not isinstance(documents, list):
        raise TypeError("Documents must be a list.")

    required_fields = {
        "chunk_id",
        "text",
    }

    for document in documents:

        missing = required_fields - document.keys()

        if missing:
            raise ValueError(
                f"Missing required fields: {missing}"
            )