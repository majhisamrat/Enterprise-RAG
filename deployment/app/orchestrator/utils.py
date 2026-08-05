import time
from typing import Any


def execution_time(start: float) -> float:
    """
    Calculate execution time in seconds.
    """

    return round(time.perf_counter() - start, 3)


def build_metadata(
    query: str,
    documents: list[dict[str, Any]],
    execution_time_seconds: float,
) -> dict[str, Any]:
    """
    Build metadata for the final response.
    """

    return {
        "query": query,
        "documents_retrieved": len(documents),
        "execution_time": execution_time_seconds,
    }