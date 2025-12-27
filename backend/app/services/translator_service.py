import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class TranslatorService:
    """
    Сервис для перевода текста с английского на русский.
    Использует внедренный OpenAI клиент.
    """

    SYSTEM_PROMPT = """
You are an expert English-to-Russian translator. Your task is to translate the user's text.
*** CRITICAL RULES ***
1.  Your primary function is to translate English text to Russian.
2.  If the provided text is already in Russian, you MUST return it unchanged.
3.  Preserve the original meaning, tone, and formatting (like newlines) as much as possible.
4.  Your output MUST be ONLY the translated text.
Do not add any extra comments, greetings, or explanations like "Вот перевод:" or "Этот текст уже на русском:".
"""

    def __init__(self, client: OpenAI):
        self.client = client

    def translate(self, text_to_translate: str) -> str:
        """
        Переводит предоставленный текст с английского на русский.
        Если текст пустой или возникла ошибка, возвращает оригинал.
        """
        if not isinstance(text_to_translate, str) or not text_to_translate.strip():
            return text_to_translate

        try:
            response = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {"role": "user", "content": text_to_translate},
                ],
                temperature=0.1,
            )

            translated_text = response.choices[0].message.content.strip()
            return translated_text

        except Exception as e:
            logger.error(f"Error during translation: {e}")
            # Fallback: вернуть оригинальный текст в случае сбоя AI
            return text_to_translate
