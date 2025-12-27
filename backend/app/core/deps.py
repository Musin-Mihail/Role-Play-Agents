from typing import Generator
from fastapi import Depends
from openai import OpenAI
from app.core.config import settings

# Import Logic Services
from app.services.state_service import GameStateService
from app.services.chronicle_service import ChronicleService
from app.services.game_engine_service import GameEngineService
from app.services.agent_services import (
    ActionSelectorService,
    MotivationGeneratorService,
    ActionConsequenceService,
    StoryWriterService,
    StoryVerifierService,
    WorldDescriptorService,
)


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


# --- Service Providers ---


def get_state_service() -> GameStateService:
    return GameStateService()


def get_chronicle_service(
    client: OpenAI = Depends(get_openai_client),
) -> ChronicleService:
    return ChronicleService(client)


def get_action_selector_service(
    client: OpenAI = Depends(get_openai_client),
) -> ActionSelectorService:
    return ActionSelectorService(client)


def get_motivation_generator_service(
    client: OpenAI = Depends(get_openai_client),
) -> MotivationGeneratorService:
    return MotivationGeneratorService(client)


def get_action_consequence_service(
    client: OpenAI = Depends(get_openai_client),
) -> ActionConsequenceService:
    return ActionConsequenceService(client)


def get_story_writer_service(
    client: OpenAI = Depends(get_openai_client),
) -> StoryWriterService:
    return StoryWriterService(client)


def get_story_verifier_service(
    client: OpenAI = Depends(get_openai_client),
) -> StoryVerifierService:
    return StoryVerifierService(client)


def get_world_descriptor_service(
    client: OpenAI = Depends(get_openai_client),
) -> WorldDescriptorService:
    return WorldDescriptorService(client)


def get_game_engine_service(
    state_service: GameStateService = Depends(get_state_service),
    chronicle_service: ChronicleService = Depends(get_chronicle_service),
    action_selector: ActionSelectorService = Depends(get_action_selector_service),
    motivation_generator: MotivationGeneratorService = Depends(
        get_motivation_generator_service
    ),
    action_consequence: ActionConsequenceService = Depends(
        get_action_consequence_service
    ),
    story_writer: StoryWriterService = Depends(get_story_writer_service),
    story_verifier: StoryVerifierService = Depends(get_story_verifier_service),
) -> GameEngineService:
    return GameEngineService(
        state_service=state_service,
        chronicle_service=chronicle_service,
        action_selector=action_selector,
        motivation_generator=motivation_generator,
        action_consequence=action_consequence,
        story_writer=story_writer,
        story_verifier=story_verifier,
    )
