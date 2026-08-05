from app.ingestion.metadata import MetadataExtractor
from app.ingestion.parsers.parser_factory import ParserFactory


class IngestionPipeline:

    def __init__(self):
        self.parser = ParserFactory()
        self.metadata = MetadataExtractor()

    def process(self, file_path: str):

        document = self.parser.parse(file_path)

        document = self.metadata.process(
            document,
            file_path,
        )

        return document