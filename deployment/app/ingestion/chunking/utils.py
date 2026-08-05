import hashlib


def generate_chunk_id(
    document: str,
    page: int | str,
    text: str,
) -> str:
 
    value = f"{document}:{page}:{text}"

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()