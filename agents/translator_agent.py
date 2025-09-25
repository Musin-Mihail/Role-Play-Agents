# translator_agent.py
from openai import OpenAI


class TranslatorAgent:
    """
    Агент, отвечающий за перевод текста с английского на русский.
    """

    SYSTEM_PROMPT = """
You are an expert English-to-Russian translator. Your task is to translate the user's text.
*** CRITICAL RULES ***
1.  Your primary function is to translate English text to Russian.
2.  If the provided text is already in Russian, you MUST return it unchanged.
3.  Preserve the original meaning, tone, and formatting (like newlines) as much as possible.
4.  Your output MUST be ONLY the translated text. Do not add any extra comments, greetings, or explanations like "Вот перевод:" or "Этот текст уже на русском:".
"""

    def __init__(self, client: OpenAI, log_func):
        self.client = client
        self.log_func = log_func

    def translate(self, text_to_translate: str):
        """
        Переводит предоставленный текст с английского на русский.
        Если текст уже на русском, возвращает его без изменений.
        """
        if not isinstance(text_to_translate, str) or not text_to_translate.strip():
            return text_to_translate

        # We don't log translation prompts to avoid cluttering the main log.txt
        # If needed for debugging, the following line can be uncommented:
        # self.log_func("AGENT_PROMPT", text_to_translate, "TRANSLATOR AGENT")

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
            # self.log_func("AGENT_RESPONSE", translated_text, "TRANSLATOR AGENT")
            return translated_text
        except Exception as e:
            self.log_func("SYSTEM", f"Error during translation: {e}")
            return text_to_translate
