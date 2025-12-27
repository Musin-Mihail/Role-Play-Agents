import sys
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Добавляем backend в путь
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.services.state_service import GameStateService
    from app.services.agent_services import (
        ActionSelectorService,
        ActionConsequenceService,
    )
    from app.core.deps import get_openai_client
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)


def test_logic_agents():
    print("\n--- Testing Logic Agents (Stateless) ---\n")

    # 1. Setup Deps
    client_gen = get_openai_client()
    client = next(client_gen)

    state_service = GameStateService()
    try:
        game_state = state_service.load_state()
    except Exception as e:
        print(f"❌ Failed to load state: {e}")
        return

    # 2. Test Action Selector
    print("1. Testing ActionSelectorService...")
    selector = ActionSelectorService(client)

    # Mock data
    ai_char = "Sveta"
    user_input = "I wave my hand hello."
    last_action = "sat on the sofa"
    last_chronicle = "The room was quiet."

    try:
        action = selector.select_action(
            game_state, ai_char, user_input, last_action, last_chronicle
        )
        print(f"✅ Selected Action: {action}")
    except Exception as e:
        print(f"❌ ActionSelector Failed: {e}")
        sys.exit(1)

    # 3. Test Action Consequence
    print("\n2. Testing ActionConsequenceService...")
    consequence_service = ActionConsequenceService(client)

    try:
        changes, events = consequence_service.determine_consequences(
            game_state, action, ai_char
        )
        print(f"✅ Consequences Determined:")
        print(f"   - Changes keys: {list(changes.keys())}")
        print(f"   - Events: {events}")
    except Exception as e:
        print(f"❌ ActionConsequence Failed: {e}")

    client.close()


if __name__ == "__main__":
    test_logic_agents()
