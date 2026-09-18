from abc import ABC, abstractmethod

#Clase base para los proveedores de LLM

class LLMProvider(ABC):
    @abstractmethod

    def responder(self, messages: list[dict]) -> str:
        pass