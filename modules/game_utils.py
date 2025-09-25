# modules/game_utils.py
import json
import copy


def log_event(event_type, content, title=""):
    """
    Logs various types of events to the console and log.txt.
    - event_type: 'SYSTEM', 'USER_INPUT', 'AGENT_PROMPT', 'AGENT_RESPONSE', 'FINAL_OUTPUT', 'CHRONICLER_SUMMARY'
    - content: The text content to log.
    - title: An optional title, useful for agent prompts.
    """
    log_message = ""
    console_message = ""

    if event_type == "SYSTEM":
        log_message = f"[SYSTEM] {content}"
        console_message = log_message
    elif event_type == "USER_INPUT":
        log_message = f"\n[USER INPUT] {content}"
        # User input is printed by the input() function itself, so no console_message here.
    elif event_type == "AGENT_PROMPT":
        log_message = (
            f"\n--- PROMPT FOR: {title} ---\n\n{content.strip()}\n\n{'='*80}\n"
        )
        # Prompts are not printed to the console to reduce clutter.
    elif event_type == "AGENT_RESPONSE":
        log_message = f"\n--- RESPONSE FROM: {title} ---\n\n{content}\n\n{'='*80}\n"
    else:
        log_message = f"\n[{event_type.upper()}] {content}"
        console_message = content  # For FINAL_OUTPUT etc.

    if console_message:
        print(console_message)

    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(log_message + "\n")


def save_changes_for_review(title, content, translator_agent):
    """Переводит и сохраняет данные для анализа."""
    translated_title = translator_agent.translate(title)
    if isinstance(content, list):
        content = "\n".join(content)
    if not isinstance(content, str):
        content = str(content)
    translated_content = translator_agent.translate(content)

    with open("review_changes.txt", "a", encoding="utf-8") as f:
        f.write(f"--- {translated_title} ---\n{translated_content.strip()}\n\n")


def get_scene_context(state_dict):
    """Создает текстовое описание сцены."""
    scene_info = state_dict.get("scene", {})
    objects_list = [
        f"{obj['name']} ({obj['location']})"
        for obj in scene_info.get("interactive_objects", [])
    ]
    objects = ", ".join(objects_list) if objects_list else "none"
    return f"Location: {scene_info.get('location', 'N/A')} ({scene_info.get('time', 'N/A')}). {scene_info.get('description', 'N/A')}. Interactive objects: {objects}."


def get_characters_snapshot(state_dict):
    """Создает текстовое описание персонажей."""
    character_texts = []
    for name, char_data in state_dict.get("characters", {}).items():
        holding = (
            ", ".join(char_data.get("holding", []))
            if char_data.get("holding")
            else "nothing"
        )
        character_texts.append(
            f"Character {name} is currently: {char_data.get('current_action', 'N/A')}; "
            f"emotion: {char_data.get('current_emotion', 'N/A')}; holding: {holding}."
        )
    return "\n".join(character_texts)


def clear_session_files():
    """Очищает файлы логов и результатов перед новым запуском."""
    open("log.txt", "w").close()
    open("review_changes.txt", "w").close()
    open("chronology.txt", "w").close()


def deep_merge_dicts(source, destination):
    """
    Рекурсивно сливает словарь `source` в `destination`.
    Если ключ в `source` имеет значение, оно перезаписывает значение в `destination`.
    Это идеально подходит для обновления состояния по частичному JSON.
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
