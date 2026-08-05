from sentence_transformers import SentenceTransformer

class EmbeddingModel():

    __model = None

    @classmethod
    def load(cls, model_name: str = "BAAI/bge-small-en-v1.5" ):

        if cls.__model is None:
            cls.__model = SentenceTransformer(model_name)

        return cls.__model