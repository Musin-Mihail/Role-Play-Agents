import copy
from typing import Dict, Any, List
from app.models.game_state import GameState


def deep_merge_dicts(
    source: Dict[str, Any], destination: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Рекурсивно сливает словарь source в destination.
    Используется для обновления GameState частичным JSON от AI.
    """
    dest_copy = copy.deepcopy(destination)
    for key, value in source.items():
        if (
            isinstance(value, dict)
            and key in dest_copy
            and isinstance(dest_copy[key], dict)
        ):
            dest_copy[key] = deep_merge_dicts(value, dest_copy[key])
        else:
            dest_copy[key] = value
    return dest_copy


def get_scene_context(game_state: GameState) -> str:
    """Создает текстовое описание сцены из объекта GameState."""
    scene = game_state.scene

    objects_list = [f"{obj.name} ({obj.location})" for obj in scene.interactive_objects]
    objects_str = ", ".join(objects_list) if objects_list else "none"

    return (
        f"Location: {scene.location} ({scene.time}). "
        f"{scene.description}. Interactive objects: {objects_str}."
    )


def get_characters_snapshot(game_state: GameState) -> str:
    """Создает текстовое описание персонажей из объекта GameState."""
    character_texts = []
    for name, char_data in game_state.characters.items():
        holding = ", ".join(char_data.holding) if char_data.holding else "nothing"
        # Обращаемся к атрибутам Pydantic модели
        text = (
            f"Character {name} is currently: {char_data.current_action}; "
            f"emotion: {char_data.current_emotion}; holding: {holding}."
        )
        character_texts.append(text)

    return "\n".join(character_texts)
