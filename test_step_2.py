import json
import sys
import os

# Добавляем backend в путь импорта
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.models.game_state import GameState
    from app.models.api_dtos import TurnRequest
except ImportError as e:
    print(f"❌ ImportError: {e}")
    print("Make sure you are running this script from the root directory.")
    sys.exit(1)


def test_data_layer():
    print("--- Testing Data Layer (Pydantic Models) ---")

    # 1. Test parsing state.json
    state_file = "state.json"
    if not os.path.exists(state_file):
        print(f"❌ Error: {state_file} not found.")
        sys.exit(1)

    print(f"Reading {state_file}...")
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Attempt validation
        game_state = GameState(**data)
        print("✅ GameState model validation successful!")

        # Verify specific deeply nested data
        char_name = list(game_state.characters.keys())[0]
        char = game_state.characters[char_name]
        print(f"   - Scene Location: {game_state.scene.location}")
        print(f"   - Character detected: {char_name}")
        print(f"   - Clothing (Torso): {char.clothing.torso}")

    except Exception as e:
        print(f"❌ Validation Failed: {e}")
        sys.exit(1)

    # 2. Test DTO creation
    print("\nTesting DTO creation...")
    try:
        req = TurnRequest(user_character_name="Sveta", user_input="Hello")
        print(f"✅ TurnRequest created: {req.model_dump_json()}")
    except Exception as e:
        print(f"❌ DTO Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_data_layer()
