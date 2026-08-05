from qdrant_client.models import Distance
from qdrant_client.models import VectorParams


COLLECTION_NAME = "enterprise_documents"

def create_collection(client):

    collections = client.get_collections().collections

    names = [c.name for c in collections]

    if COLLECTION_NAME in names:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )