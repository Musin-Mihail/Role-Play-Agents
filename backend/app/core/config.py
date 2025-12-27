import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Configuration using Pydantic Settings.
    Reads values from environment variables or .env file.
    """

    # Base paths
    # backend/app/core/config.py -> backend/app/core -> backend/app -> backend
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Role-Play Engine API"

    # OpenAI / Local LLM Configuration
    OPENAI_API_KEY: str = "not-needed"
    OPENAI_BASE_URL: str = "http://localhost:1234/v1"

    # Game Settings
    # Files are now expected to be inside the backend directory (or configured via env)
    STATE_FILE_PATH: Path = BASE_DIR / "state.json"
    CHRONOLOGY_FILE_PATH: Path = BASE_DIR / "chronology.txt"

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"), case_sensitive=True, extra="ignore"
    )


settings = Settings()
