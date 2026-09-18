from openai import OpenAI

from app.llm.base import LLMProvider
from app.config import OPENAI_MODEL

class OpenAIProvider(LLMProvider):

    def __init__(self, model: str = f"{OPENAI_MODEL}"):
        self.client = OpenAI()
        self.model = model

    def responder(self, messages: list[dict]) -> str:
        response = self.client.responses.create(
            model = self.model,
            input = messages
        )

        return response.output_text

    

