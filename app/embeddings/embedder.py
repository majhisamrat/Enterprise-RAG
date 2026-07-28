from typing import List
from app.utils.logger import logger

from app.config import settings
from app.embeddings.base import BaseEmbedder
from app.embeddings.batch import batch_iterator
from app.embeddings.embedding_model import EmbeddingModel
from app.ingestion.schemas import ChunkedDocument


class Embedder(BaseEmbedder):

    def __init__(
        self,
        model_name: str = settings.MODEL_NAME,
        batch_size: int = 32,
    ):
        self.model_name = model_name
        self.model = EmbeddingModel.load(model_name)
        self.batch_size = batch_size

    def embed(
        self,
        document: ChunkedDocument,
    ) -> ChunkedDocument:

        logger.info(
            f"Generating embeddings for {len(document.chunks)} chunks..."
        )

        for batch in batch_iterator(
            document.chunks,
            self.batch_size,
        ):
            texts = [chunk.text for chunk in batch]

            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding.tolist()

        logger.success(
            f"Generated embeddings for {len(document.chunks)} chunks."
        )

        return document

    def embed_query(self, query: str) -> List[float]:
        """Embed a single search query."""
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.tolist()