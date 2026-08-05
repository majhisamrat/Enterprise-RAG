from app.keyword_search.index import (
    ElasticsearchIndexer,
)
from app.keyword_search.search import (
    KeywordSearch,
)


class BM25Retriever:

    def __init__(self):

        self.indexer = ElasticsearchIndexer()

        self.searcher = KeywordSearch()

    def index(self, document):

        self.indexer.index(document)

    def search( self, query: str, limit: int = 10):

        return self.searcher.search(
            query,
            limit,
        )