import os
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChronicleService:
    """
    Сервис для управления хронологией событий.
    Отвечает за чтение истории, добавление новых записей и сжатие (суммаризацию).
    """

    SYSTEM_PROMPT_CHRONICLER = """
You are a historian and archivist.
Your task is to write a brief, factual, third-person narrative summary of a single game turn based on the actions of two characters.
*** CRITICAL RULES ***
1.  **INPUT**: You will receive the action of the user's character and the resulting action of the AI's character.
2.  **OUTPUT**: Your response MUST be a single, concise paragraph.
3.  **PERSPECTIVE**: The summary MUST be in the third-person.
4.  **NO TAGS**: Do not include any tags like [STORY], [MOTIVATION], or character names as headers.
5.  **COMBINE ACTIONS**: Do not just list the actions. Weave them into a single, coherent narrative describing what just happened.
6.  **BE OBJECTIVE**: Only record what happened. Do not include internal thoughts, motivations, or intentions unless they were explicitly stated as dialogue or action.
"""

    SYSTEM_PROMPT_SUMMARIZER = """
You are a scriptwriter and editor. Your task is to take a raw game log, which includes character thoughts, actions, and dialogues, and rewrite it into a concise, third-person narrative story.
*** CRITICAL RULES ***
1.  **PRESERVE THE STORY**: The core events, actions, and the order in which they happen MUST be preserved.
2.  **REMOVE ALL TAGS**: You MUST remove all special tags.
3.  **CREATE A NARRATIVE**: Convert the log into a flowing, readable story.
4.  **THIRD-PERSON PERSPECTIVE**: The entire story must be told from a third-person point of view.
5.  **BE CONCISE**: The final text must be significantly shorter than the original.
"""

    def __init__(self, client: OpenAI):
        self.client = client
        self.file_path = settings.CHRONOLOGY_FILE_PATH

    def _read_file(self) -> str:
        if not os.path.exists(self.file_path):
            return ""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading chronology file: {e}")
            return ""

    def _append_to_file(self, text: str):
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception as e:
            logger.error(f"Error appending to chronology file: {e}")

    def _overwrite_file(self, text: str):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(text.strip() + "\n")
        except Exception as e:
            logger.error(f"Error overwriting chronology file: {e}")

    def get_full_chronology(self) -> str:
        return self._read_file()

    def get_last_turn_chronicle(self) -> str:
        """Возвращает последнюю запись (абзац) из хронологии."""
        content = self._read_file().strip()
        if not content:
            return "This is the first turn of the story."
        # Предполагаем, что записи разделены переводами строк. Берем последний непустой блок.
        lines = [line for line in content.split("\n") if line.strip()]
        return lines[-1] if lines else "This is the first turn of the story."

    def create_turn_summary(
        self,
        user_char_name: str,
        user_action: str,
        ai_char_name: str,
        ai_story_part: str,
        ai_motivation: str,
    ) -> str:
        """Генерирует саммари хода через LLM."""
        cleaned_ai_story = ai_story_part.replace("[STORY]", "").strip()
        prompt = f"""
Here are the actions and motivations for the turn.
Create a concise, third-person narrative summary.

- User Character ({user_char_name}) Action: "{user_action}"
- AI Character ({ai_char_name}) Motivation: "{ai_motivation}"
- AI Character ({ai_char_name}) Resulting Story: "{cleaned_ai_story}"
"""
        try:
            completion = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT_CHRONICLER},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            summary = completion.choices[0].message.content.strip()
            self._append_to_file(summary)
            return summary
        except Exception as e:
            logger.error(f"Failed to create turn summary: {e}")
            fallback = f"{user_char_name} did {user_action}. {ai_char_name} reacted."
            self._append_to_file(fallback)
            return fallback

    def summarize_if_needed(self, word_limit=6000):
        """Проверяет размер хронологии и сжимает ее при необходимости."""
        text = self._read_file()
        word_count = len(text.split())

        if word_count > word_limit:
            logger.info(f"Chronology size ({word_count}) exceeds limit. Summarizing...")
            try:
                completion = self.client.chat.completions.create(
                    model="local-model",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT_SUMMARIZER},
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3,
                )
                summary_text = completion.choices[0].message.content.strip()
                self._overwrite_file(summary_text)
                logger.info("Chronology summarized successfully.")
            except Exception as e:
                logger.error(f"Chronology summarization failed: {e}")
