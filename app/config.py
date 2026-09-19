from pathlib import Path
import os

from dotenv import load_dotenv

MAX_CONTEXT_TURNS = 5
MAX_CONTEXT_CHARS = 12000

#Directorio raiz

BASE_DIR = Path(__file__).resolve().parent.parent

#Carpetas principales

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DOCS_DIR = BASE_DIR / "docs"

#Base de datos

DATABASE_PATH = DATA_DIR / "memoria.db"

#Variables de entorno
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

#CONFIG PROVEEDOR
LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER", 
    "ollama"
    )

#CONFIG OPENAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-nano"
)

#CONFIG OLLAMA
OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:4b"
)

#Config asistente

ASSISTANT_NAME = os.getenv(
    "ASSISTANT_NAME",
    "Asistente"
)

#Inicializacion de directorios

def crear_directorios() -> None:
    DATA_DIR.mkdir(parents = True, exist_ok = True)
    LOGS_DIR.mkdir(parents = True, exist_ok = True)
    DOCS_DIR.mkdir(parents = True, exist_ok = True)