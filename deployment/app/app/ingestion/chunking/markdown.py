from app.ingestion.chunking.base import BaseChunker


class MarkdownChunker(BaseChunker):
    """
    Markdown-aware chunking.

    Phase 7.2

    Splits documents using markdown
    headers instead of character count.

    Example:

    # Heading
    ## Subheading
    ### Topic
    """

    def chunk(self, document):
        raise NotImplementedError(
            "Markdown-aware chunking will be implemented later."
        )