from app.prompt_builder.builder import PromptBuilder


class LLMPrompt:
    """
    Wrapper around the PromptBuilder.
    """

    def __init__(self):
        self.builder = PromptBuilder()

    def build(
        self,
        query: str,
        documents: list[dict],
    ) -> str:
        """
        Build the final prompt for the LLM.
        """
        return self.builder.build(
            query=query,
            documents=documents,
        )