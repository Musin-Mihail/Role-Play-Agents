import sys
import os
import logging

# Настройка логирования для теста
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TestStep3")

# Добавляем backend в путь
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.core.config import settings
    from app.services.state_service import GameStateService
    from app.services.translator_service import TranslatorService
    from app.core.deps import get_openai_client
except ImportError as e:
    print(f"❌ ImportError: {e}")
    print("Run this script from the root directory.")
    sys.exit(1)


def test_infrastructure():
    print("\n--- Testing Infrastructure Services ---\n")

    # 1. Test GameStateService (Reading)
    print("1. Testing GameStateService (Load)...")
    state_service = GameStateService()

    try:
        game_state = state_service.load_state()
        print(f"✅ State Loaded Successfully.")
        print(f"   - Scene: {game_state.scene.description[:50]}...")
        char_count = len(game_state.characters)
        print(f"   - Characters count: {char_count}")
    except Exception as e:
        print(f"❌ State Load Failed: {e}")
        sys.exit(1)

    # 2. Test GameStateService (Saving)
    print("\n2. Testing GameStateService (Save - Mock Modification)...")
    try:
        # Изменим время, чтобы проверить запись
        original_time = game_state.scene.time
        game_state.scene.time = "midnight_test"

        state_service.save_state(game_state)
        print("✅ State Saved.")

        # Проверим, что записалось
        reloaded_state = state_service.load_state()
        if reloaded_state.scene.time == "midnight_test":
            print("✅ Verification: Change persisted correctly.")
        else:
            print("❌ Verification Failed: Persistence error.")

        # Вернем как было
        game_state.scene.time = original_time
        state_service.save_state(game_state)
        print("   (State restored to original)")

    except Exception as e:
        print(f"❌ State Save Failed: {e}")

    # 3. Test TranslatorService
    print("\n3. Testing TranslatorService...")

    # Получаем клиента через генератор (симуляция DI)
    client_gen = get_openai_client()
    client = next(client_gen)

    translator = TranslatorService(client=client)

    test_phrase = "Hello, world! This is a test."
    print(f"   - Input: {test_phrase}")

    try:
        translated = translator.translate(test_phrase)
        print(f"   - Output: {translated}")

        if translated == test_phrase:
            print("⚠️ Warning: Output equals input. Is the LLM running/configured?")
        else:
            print("✅ Translation received.")

    except Exception as e:
        print(f"❌ Translation Failed: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    test_infrastructure()
