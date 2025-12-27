import sys
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestStep5")

# Добавляем backend в путь
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.core.deps import (
        get_game_engine_service,
        get_openai_client,
        get_state_service,
    )
    from app.services.chronicle_service import ChronicleService
    from app.services.agent_services import (
        ActionSelectorService,
        MotivationGeneratorService,
        ActionConsequenceService,
        StoryWriterService,
        StoryVerifierService,
    )
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)


def test_game_engine():
    print("\n--- Testing Game Engine Service (Full Turn Integration) ---\n")

    # 1. Manually assemble dependencies (simulating DI container)
    client_gen = get_openai_client()
    client = next(client_gen)

    state_service = get_state_service()
    chronicle_service = ChronicleService(client)

    # Logic Services
    action_selector = ActionSelectorService(client)
    motivation_gen = MotivationGeneratorService(client)
    action_consequence = ActionConsequenceService(client)
    story_writer = StoryWriterService(client)
    story_verifier = StoryVerifierService(client)

    # Engine
    engine = get_game_engine_service(
        state_service=state_service,
        chronicle_service=chronicle_service,
        action_selector=action_selector,
        motivation_generator=motivation_gen,
        action_consequence=action_consequence,
        story_writer=story_writer,
        story_verifier=story_verifier,
    )

    # 2. Define Test Inputs
    user_char = "Sveta"
    user_input = "I sit on the sofa and look at Misha."

    print(f"User Character: {user_char}")
    print(f"User Input: {user_input}")
    print("Processing turn... (This may take 10-20 seconds with local LLM)\n")

    try:
        # 3. Execute Turn
        response = engine.process_turn(user_char, user_input)

        # 4. Verify Output
        print("\n✅ Turn Processed Successfully!")
        print(f"   - AI Character: {response.ai_character_name}")
        print(f"   - Completed Actions: {response.completed_actions}")
        print(f"   - Motivation: {response.motivation[:100]}...")
        print(f"   - Story Part: {response.story_part[:100]}...")

        if response.is_success:
            print("   - Status: SUCCESS")
        else:
            print("   - Status: FAILED (Soft)")

    except Exception as e:
        print(f"\n❌ Engine Failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    test_game_engine()
