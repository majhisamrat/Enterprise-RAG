def validate_embedding( embedding: list[float], expected_dimension: int = 384 ) -> bool:

    return len(embedding) == expected_dimension