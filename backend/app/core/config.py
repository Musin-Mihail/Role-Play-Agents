from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Configuration using Pydantic Settings.
    Reads values from environment variables or .env file.
    """

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Role-Play Engine API"

    # OpenAI / Local LLM Configuration
    # Defaults set to match the original main.py local setup
    OPENAI_API_KEY: str = "not-needed"
    OPENAI_BASE_URL: str = "http://localhost:1234/v1"

    # Game Settings
    STATE_FILE_PATH: str = "state.json"
    CHRONOLOGY_FILE_PATH: str = "chronology.txt"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
