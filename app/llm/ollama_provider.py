from ollama import chat

from app.config import OLLAMA_MODEL
from app.llm.base import LLMProvider

class OllamaProvider(LLMProvider):

    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model

    def responder(self, messages: list[dict]) -> str:
        response = chat(
            model = self.model,
            messages = messages
        )

        return response.message.content