import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""
    OPENAI_MODEL: str = "llama-3.3-70b-versatile"
    ENVIRONMENT: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    TECTONIC_PATH: str = r"C:\Users\tajin\.local\bin\tectonic.exe"

    # Base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    PROMPTS_DIR: Path = BASE_DIR / "prompts"
    STORAGE_DIR: Path = BASE_DIR / "storage"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

# Ensure storage directory exists
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "resumes").mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "pdfs").mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "tex").mkdir(parents=True, exist_ok=True)
