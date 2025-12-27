import logging
from typing import Optional, List
from app.core.utils import deep_merge_dicts
from app.models.api_dtos import TurnResponse
from app.services.state_service import GameStateService
from app.services.chronicle_service import ChronicleService
from app.services.agent_services import (
    ActionSelectorService,
    MotivationGeneratorService,
    ActionConsequenceService,
    StoryWriterService,
    StoryVerifierService,
)

logger = logging.getLogger(__name__)


class GameEngineService:
    """
    Оркестратор игрового цикла.
    Заменяет собой логику цикла while True из старого main.py.
    """

    def __init__(
        self,
        state_service: GameStateService,
        chronicle_service: ChronicleService,
        action_selector: ActionSelectorService,
        motivation_generator: MotivationGeneratorService,
        action_consequence: ActionConsequenceService,
        story_writer: StoryWriterService,
        story_verifier: StoryVerifierService,
    ):
        self.state_service = state_service
        self.chronicle_service = chronicle_service
        self.action_selector = action_selector
        self.motivation_generator = motivation_generator
        self.action_consequence = action_consequence
        self.story_writer = story_writer
        self.story_verifier = story_verifier

    def process_turn(self, user_character_name: str, user_input: str) -> TurnResponse:
        logger.info(f"--- Processing turn for {user_character_name}: {user_input} ---")

        # 1. Загрузка состояния
        current_state = self.state_service.load_state()

        # Определяем имя AI персонажа (первый, кто не юзер)
        ai_character_name = next(
            (
                name
                for name in current_state.characters.keys()
                if name != user_character_name
            ),
            None,
        )
        if not ai_character_name:
            raise ValueError("AI character not found in state.")

        # 2. Определение последствий действия ПОЛЬЗОВАТЕЛЯ
        logger.info("1/7 Determining user consequences...")
        user_changes, _ = self.action_consequence.determine_consequences(
            current_state, user_input, user_character_name
        )

        # Применяем изменения пользователя к промежуточному состоянию (в памяти)
        # Для deep_merge_dicts нужно преобразовать модели в dict
        current_state_dict = current_state.model_dump()
        intermediate_state_dict = deep_merge_dicts(user_changes, current_state_dict)

        # Преобразуем обратно в объект GameState для работы агентов
        # (Это важно, так как агенты ожидают GameState объект)
        from app.models.game_state import GameState

        intermediate_state = GameState(**intermediate_state_dict)

        # 3. Подготовка контекста для AI
        logger.info("2/7 Selecting AI action...")
        last_turn_chronicle = self.chronicle_service.get_last_turn_chronicle()

        # Получаем последнее действие AI из текущего состояния (как approximation)
        ai_char_data = intermediate_state.characters.get(ai_character_name)
        last_ai_action = ai_char_data.current_action if ai_char_data else "unknown"

        planned_action = self.action_selector.select_action(
            intermediate_state,
            ai_character_name,
            user_input,
            last_ai_action,
            last_turn_chronicle,
        )

        # 4. Генерация мотивации
        logger.info("3/7 Generating motivation...")
        motivation = self.motivation_generator.generate_motivation(
            intermediate_state, ai_character_name, planned_action, user_input
        )

        # 5. Последствия действий AI
        logger.info("4/7 Determining AI consequences...")
        ai_changes, completed_actions = self.action_consequence.determine_consequences(
            intermediate_state, planned_action, ai_character_name
        )

        # 6. Написание истории с верификацией
        logger.info("5/7 Writing story...")
        story_part = ""
        verification_passed = False
        feedback = None

        # Если действий нет, заглушка
        if not completed_actions and not ai_changes:
            story_part = f"{ai_character_name} does nothing."
            verification_passed = True
        else:
            for attempt in range(3):
                story_part = self.story_writer.write_story(
                    intermediate_state,
                    ai_character_name,
                    user_character_name,
                    completed_actions,
                    motivation,
                    user_input,
                    last_turn_chronicle,
                    revision_feedback=feedback,
                )

                is_valid, reason = self.story_verifier.verify(
                    completed_actions, story_part
                )
                if is_valid:
                    verification_passed = True
                    logger.info(f"Story verified on attempt {attempt + 1}")
                    break
                else:
                    logger.warning(
                        f"Verification failed (Attempt {attempt + 1}): {reason}"
                    )
                    feedback = reason

            if not verification_passed:
                logger.error("Story generation failed after 3 attempts.")
                # Fallback: просто перечисляем действия
                story_part = f"(System: Story generation failed) Actions taken: {', '.join(completed_actions)}"

        # 7. Применение изменений AI и сохранение
        logger.info("6/7 Applying AI state changes...")
        final_state_dict = deep_merge_dicts(ai_changes, intermediate_state_dict)
        final_state = GameState(**final_state_dict)

        logger.info("7/7 Saving results...")
        self.state_service.save_state(final_state)

        # 8. Обновление хронологии
        turn_summary = self.chronicle_service.create_turn_summary(
            user_character_name, user_input, ai_character_name, story_part, motivation
        )

        # Асинхронно или просто после ответа можно сжать хронологию
        self.chronicle_service.summarize_if_needed()

        return TurnResponse(
            ai_character_name=ai_character_name,
            motivation=motivation,
            story_part=story_part,
            completed_actions=completed_actions,
            is_success=True,
        )
