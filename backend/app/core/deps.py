from typing import Generator
from openai import OpenAI
from app.core.config import settings


def get_openai_client() -> Generator[OpenAI, None, None]:
    """
    Создает и предоставляет клиент OpenAI.
    Конфигурация берется из settings (переменные окружения).
    """
    client = OpenAI(
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_API_KEY,
    )
    try:
        yield client
    finally:
        client.close()
