import json
import logging
import os
from app.core.config import settings
from app.models.game_state import GameState

logger = logging.getLogger(__name__)


class GameStateService:
    """
    Сервис для управления персистентностью состояния игры.
    Отвечает за чтение и запись state.json, используя Pydantic модели.
    """

    def __init__(self):
        self.file_path = settings.STATE_FILE_PATH

    def load_state(self) -> GameState:
        """
        Читает state.json и возвращает валидированный объект GameState.
        """
        if not os.path.exists(self.file_path):
            error_msg = f"State file not found at: {self.file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Валидация через Pydantic
            game_state = GameState(**data)
            logger.info("GameState successfully loaded and validated.")
            return game_state

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from {self.file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading state: {e}")
            raise

    def save_state(self, state: GameState) -> None:
        """
        Сохраняет объект GameState обратно в state.json.
        """
        try:
            # Преобразуем модель обратно в словарь/json
            # mode='json' обеспечивает сериализацию в формат, совместимый с JSON
            json_str = state.model_dump_json(indent=2, exclude_none=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            logger.info(f"GameState successfully saved to {self.file_path}")

        except Exception as e:
            logger.error(f"Failed to save state to {self.file_path}: {e}")
            raise
