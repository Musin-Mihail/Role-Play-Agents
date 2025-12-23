import json
import traceback


def read_state(log_func):
    """Читает состояние из state.json."""
    try:
        with open("state.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_func(f"[SYSTEM: Error! 'state.json' is missing or corrupted. Error: {e}]")
        return None


def save_state(new_state_dict, log_func):
    """Сохраняет новое состояние в state.json."""
    try:
        log_func("[SYSTEM: Saving new state to state.json...]")
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(new_state_dict, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log_func(f"\n[SYSTEM: Error! Failed to save new state. Error: {e}]")
        traceback.print_exc()
        return False
