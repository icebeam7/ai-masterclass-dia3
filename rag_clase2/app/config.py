"""Lectura y validación de variables locales."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    project_endpoint: str
    chat_model: str
    embedding_model: str
    embedding_dimensions: int
    search_endpoint: str
    search_index: str
    search_admin_key: str
    top_k: int
    storage_account_url: str
    storage_container: str
    storage_prefix: str

    @classmethod
    def from_env(cls) -> "Settings":
        keys = ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_MODEL_DEPLOYMENT_NAME",
                "AZURE_AI_EMBEDDING_DEPLOYMENT_NAME", "AZURE_SEARCH_ENDPOINT",
                "AZURE_SEARCH_INDEX", "AZURE_SEARCH_ADMIN_KEY",
                "AZURE_STORAGE_ACCOUNT_URL", "AZURE_STORAGE_CONTAINER"]
        missing = [key for key in keys if not os.getenv(key) or os.getenv(key, '').startswith(('REEMPLAZAR_', 'https://TU-'))]
        if missing:
            raise ValueError("Faltan variables de .env: " + ", ".join(missing))
        dims = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
        top_k = int(os.getenv("TOP_K", "4"))
        if dims < 1 or not 1 <= top_k <= 10:
            raise ValueError("EMBEDDING_DIMENSIONS debe ser positivo y TOP_K entre 1 y 10")
        endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"].rstrip("/")
        if "/api/projects/" not in endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT debe ser el endpoint del proyecto Foundry")
        return cls(endpoint, os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                   os.environ["AZURE_AI_EMBEDDING_DEPLOYMENT_NAME"], dims,
                   os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/"),
                   os.environ["AZURE_SEARCH_INDEX"], os.environ["AZURE_SEARCH_ADMIN_KEY"],
                   top_k, os.environ["AZURE_STORAGE_ACCOUNT_URL"].rstrip("/"),
                   os.environ["AZURE_STORAGE_CONTAINER"], os.getenv("AZURE_STORAGE_PREFIX", ""))
