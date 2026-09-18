from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider

from app.config import LLM_PROVIDER

def get_llm_provider():
    provider = LLM_PROVIDER.lower()

    if provider == "openai":
        return OpenAIProvider()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"proveedor LLM no válido: {LLM_PROVIDER}"
    )

