import pytest

from app.llm.base import LLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider

import app.llm.router as router


def test_router_devuelve_llm_provider():
    provider = router.get_llm_provider()

    assert isinstance(provider, LLMProvider)


def test_router_devuelve_ollama(monkeypatch):
    monkeypatch.setattr(router, "LLM_PROVIDER", "ollama")

    provider = router.get_llm_provider()

    assert isinstance(provider, OllamaProvider)


def test_router_devuelve_openai(monkeypatch):
    monkeypatch.setattr(router, "LLM_PROVIDER", "openai")

    provider = router.get_llm_provider()

    assert isinstance(provider, OpenAIProvider)


def test_router_proveedor_invalido(monkeypatch):
    monkeypatch.setattr(router, "LLM_PROVIDER", "proveedor_inexistente")

    with pytest.raises(ValueError):
        router.get_llm_provider()