import ftfy


def fix_encoding(text: str) -> str:
    """
    Fix mojibake and broken unicode.
    """

    return ftfy.fix_text(text)