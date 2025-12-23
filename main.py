import traceback
from openai import OpenAI

from agents import (
    ActionSelectorAgent,
    MotivationGeneratorAgent,
    ActionConsequenceAgent,
    StoryWriterAgent,
    StoryVerifierAgent,
    TranslatorAgent,
)

from modules.state_manager import read_state, save_state
from modules.chronology_manager import add_to_chronology
from modules.turn_processors import create_turn_summary, summarize_chronology_if_needed
from modules.game_utils import (
    log_event,
    save_changes_for_review,
    get_scene_context,
    get_characters_snapshot,
    clear_session_files,
    deep_merge_dicts,
)


def setup_game():
    """Подготовка к началу игры: выбор персонажа и инициализация агентов."""
    state_dict = read_state(lambda msg: log_event("SYSTEM", msg))
    if not state_dict:
        return None, None, None, None

    character_names = list(state_dict.get("characters", {}).keys())
    log_event("SYSTEM", "Choose your character:")
    for i, name in enumerate(character_names):
        print(f"  {i + 1}: {name}")

    while True:
        try:
            choice = input(
                f"Enter the number of your character (1-{len(character_names)}) > "
            )
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(character_names):
                user_character_name = character_names[selected_index]
                break
            else:
                log_event("SYSTEM", "Error! Please enter a valid number from the list.")
        except ValueError:
            log_event("SYSTEM", "Error! Please enter a number.")

    ai_character_name = [
        name for name in character_names if name != user_character_name
    ][0]
    log_event("SYSTEM", f"\nYou are {user_character_name}. AI is {ai_character_name}.")

    client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

    agents = {
        "translator": TranslatorAgent(client=client, log_func=log_event),
        "action_selector": ActionSelectorAgent(
            client=client, ai_character_name=ai_character_name, log_func=log_event
        ),
        "motivation_generator": MotivationGeneratorAgent(
            client=client, ai_character_name=ai_character_name, log_func=log_event
        ),
        "action_consequence": ActionConsequenceAgent(client=client, log_func=log_event),
        "story_writer": StoryWriterAgent(
            client=client,
            ai_character_name=ai_character_name,
            user_character_name=user_character_name,
            log_func=log_event,
        ),
        "story_verifier": StoryVerifierAgent(client=client, log_func=log_event),
    }
    return client, agents, user_character_name, ai_character_name


def main():
    log_event("SYSTEM", "--- Interactive Role-Play Started ---")
    clear_session_files()

    client, agents, user_character_name, ai_character_name = setup_game()
    if not agents:
        log_event("SYSTEM", "Game setup failed. Exiting.")
        return

    last_planned_action = "has not acted yet"
    last_turn_chronicle = "This is the first turn of the story."
    current_state_dict = read_state(lambda msg: log_event("SYSTEM", msg))

    while True:
        try:
            summarize_chronology_if_needed(client)
            print(f"\nYour turn ({user_character_name}) > ")
            user_input = input().strip()
            log_event("USER_INPUT", user_input)
            if user_input.lower() == "exit":
                break
            if not user_input:
                log_event("SYSTEM", "Empty message.")
                continue

            save_changes_for_review("USER INPUT", user_input, agents["translator"])

            log_event("SYSTEM", "1/7 Determining consequences of your action...")
            user_state_changes, _ = agents["action_consequence"].determine_consequences(
                current_state_dict, user_input, user_character_name
            )

            intermediate_state = deep_merge_dicts(
                user_state_changes, current_state_dict
            )

            if not intermediate_state:
                log_event(
                    "SYSTEM",
                    "Critical Error! Failed to create intermediate state. Skipping turn.",
                )
                continue

            log_event("SYSTEM", "2/7 Selecting AI action...")
            scene_context = get_scene_context(intermediate_state)
            characters_snapshot = get_characters_snapshot(intermediate_state)

            ai_char_goal = (
                intermediate_state.get("characters", {})
                .get(ai_character_name, {})
                .get("goal", "No goal")
            )

            planned_action = agents["action_selector"].select_action(
                ai_char_goal,
                scene_context,
                characters_snapshot,
                user_input,
                last_planned_action,
                last_turn_chronicle,
            )

            log_event("SYSTEM", "3/7 Generating AI motivation...")
            motivation = agents["motivation_generator"].generate_motivation(
                intermediate_state, planned_action, user_input
            )
            save_changes_for_review("AI MOTIVATION", motivation, agents["translator"])

            log_event("SYSTEM", "4/7 Determining AI action consequences...")
            ai_state_changes, completed_actions = agents[
                "action_consequence"
            ].determine_consequences(
                intermediate_state, planned_action, ai_character_name
            )
            save_changes_for_review(
                "AI COMPLETED ACTIONS", completed_actions, agents["translator"]
            )

            log_event("SYSTEM", "5/7 Writing and verifying story...")
            story_part = ""
            if completed_actions or ai_state_changes:
                for attempt in range(3):
                    current_story_part = agents["story_writer"].write_story(
                        completed_actions,
                        motivation,
                        intermediate_state,
                        user_input,
                        last_turn_chronicle,
                        None,
                    )
                    is_verified, feedback = agents["story_verifier"].verify(
                        completed_actions, current_story_part
                    )
                    if is_verified:
                        story_part = current_story_part
                        log_event("SYSTEM", f"Story verified on attempt {attempt+1}.")
                        break
                    else:
                        log_event(
                            "SYSTEM",
                            f"Verification failed (Attempt {attempt + 1}/3): {feedback}. Retrying...",
                        )
                else:
                    log_event("SYSTEM", "Story generation failed. Discarding turn.")
                    continue
            else:
                story_part = f"{ai_character_name} does nothing in response."

            log_event("SYSTEM", "6/7 Applying AI state changes...")
            new_state = deep_merge_dicts(ai_state_changes, intermediate_state)

            log_event("SYSTEM", "7/7 Saving results...")
            final_motivation_output = (
                f"--- МОТИВАЦИЯ ({ai_character_name}) ---\n{motivation}"
            )
            final_story_output = f"--- {ai_character_name} ---\n{story_part}"
            log_event(
                "FINAL_OUTPUT", f"{final_motivation_output}\n\n{final_story_output}"
            )

            if new_state and save_state(
                new_state, lambda msg: log_event("SYSTEM", msg)
            ):
                current_state_dict = new_state
                turn_summary = create_turn_summary(
                    client,
                    user_character_name,
                    user_input,
                    ai_character_name,
                    story_part,
                    motivation,
                )
                add_to_chronology(turn_summary)
                last_turn_chronicle = turn_summary
                last_planned_action = planned_action
                log_event("CHRONICLER_SUMMARY", turn_summary)
                save_changes_for_review(
                    "CHRONICLER SUMMARY", turn_summary, agents["translator"]
                )
            else:
                log_event("SYSTEM", "Turn failed. State not saved.")

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            log_event("SYSTEM", error_message)
            traceback.print_exc()


if __name__ == "__main__":
    main()
