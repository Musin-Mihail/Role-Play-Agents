import json
import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from openai import OpenAI
from app.models.game_state import GameState
from app.core.utils import get_scene_context, get_characters_snapshot

logger = logging.getLogger(__name__)


class BaseAgentService:
    def __init__(self, client: OpenAI):
        self.client = client

    def _log_prompt(self, agent_name: str, prompt: str):
        logger.debug(f"--- PROMPT FOR {agent_name} ---\n{prompt}\n----------------")

    def _log_response(self, agent_name: str, response: str):
        logger.debug(
            f"--- RESPONSE FROM {agent_name} ---\n{response}\n----------------"
        )


class WorldDescriptorService(BaseAgentService):
    SYSTEM_PROMPT = """
You are a Game Master's assistant.
Your task is to read a JSON object representing the game's state and write a detailed, factual, human-readable summary of it.
*** CRITICAL RULES ***
1.  **Be Factual and Detailed:** Only state what is present in the JSON.
2.  **Natural Language:** Translate complex objects into simple sentences.
3.  **Structure:**
    - Start with the scene description.
    - For each character, create a small paragraph describing them.
    - **CRITICAL FORMATTING:** After the description, you MUST use these exact headings to list items:
        - `Wearing:` (for the `clothing` object, preserving categories like torso, legs)
        - `Holding:` (for the `holding` list)
    This separation is vital for other AI agents to understand the state correctly.
*** OUTPUT FORMAT ***
Your response MUST be ONLY the plain text description. Do not add titles or tags.
"""

    def describe(self, game_state: GameState) -> str:
        state_json = game_state.model_dump_json(indent=2)
        agent_name = "AGENT 0: WORLD DESCRIPTOR"
        prompt = f"[CURRENT JSON STATE]\n{state_json}\n\n[YOUR TASK]\nTranslate the JSON state above into a detailed text description.\nYou MUST use the `Wearing:` and `Holding:` headings to clearly separate clothing from held items."

        self._log_prompt(agent_name, prompt)

        response = (
            self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            .choices[0]
            .message.content.strip()
        )

        self._log_response(agent_name, response)
        return response


class ActionSelectorService(BaseAgentService):
    SYSTEM_PROMPT = """
You are {character_name}, a character in a role-playing game.
Your single task is to decide on your NEXT immediate physical action.
*** CRITICAL ANALYSIS HIERARCHY ***
Your decision-making MUST follow this strict order of priorities.
1.  **ANALYZE LATEST USER ACTION**: Look at `[LATEST USER ACTION]`.
- **PRIORITY 1: BOUNDARIES & SAFETY:** Is the user's action aggressive, shocking, or physically violating?
If so, your action MUST be a direct and realistic reaction. This OVERRIDES your personal goal.
- **PRIORITY 2: DIRECT INTERACTION:** If the action is not violating, is it a normal interaction (e.g., talking, touching a shoulder)?
Your action MUST be a logical response to this interaction.
- **PRIORITY 3: PERSONAL GOAL:** If the user is passive (e.g., sleeping, reading) or their action does not require a direct reaction, you MUST choose a logical next step to advance `[YOUR GOAL]`.
*** CRITICAL RULES OF ACTION SELECTION ***
1.  **MAINTAIN CONTINUITY:** Your primary focus is the `[LATEST USER ACTION]`, but you MUST consider the `[LAST TURN'S CHRONICLE]` and your `current_emotion` to ensure your action is emotionally consistent.
Do not have emotional amnesia.
2.  **THINK IN COMPLETE STEPS (NO MICRO-ACTIONS!)**:
    * Your previous action was: `{last_ai_action}`.
* You MUST choose a new, distinct, and significant action.
* **CRITICAL FAILURE CONDITION**: Actions that are a slight variation or direct continuation of the previous one are FORBIDDEN.
For example, a sequence like "start unbuttoning shirt" -> "continue unbuttoning shirt" is a CRITICAL FAILURE.
* Instead of breaking one goal into many tiny movements, complete one logical step per turn.
A better single action would be "take off the jacket and place it on the sofa" instead of three separate turns for reaching, unzipping, and removing.
3.  **ABSOLUTE GROUNDING RULE:** Your action MUST NOT involve any object, item, or piece of clothing that is NOT explicitly listed in the [CHARACTERS SNAPSHOT] or [SCENE CONTEXT].
Inventing items is a CRITICAL FAILURE and is forbidden.
4.  **STRICT OUTPUT FORMAT:** Your response MUST be ONLY a short, descriptive phrase detailing your immediate physical or verbal action.
DO NOT add any other text, explanations, or greetings.
"""

    def select_action(
        self,
        game_state: GameState,
        ai_character_name: str,
        user_input: str,
        last_ai_action: str,
        last_turn_chronicle: str,
    ) -> str:
        agent_name = "AGENT 1.1: ACTION SELECTOR"

        # Prepare context using helper functions
        scene_context = get_scene_context(game_state)
        characters_snapshot = get_characters_snapshot(game_state)

        char_data = game_state.characters.get(ai_character_name)
        current_goal = char_data.goal if char_data else "No goal"

        prompt = f"""
[LAST TURN'S CHRONICLE]
This is what happened right before the user's latest action: "{last_turn_chronicle}"

[SCENE CONTEXT]
{scene_context}

[CHARACTERS SNAPSHOT]
{characters_snapshot}

[LATEST USER ACTION]
The other character just did this: "{user_input}"

[YOUR GOAL]
Your current personal background goal is: "{current_goal}".
[YOUR PREVIOUS ACTION]
Your last action was: "{last_ai_action}"

[YOUR TASK]
Follow your CRITICAL ANALYSIS HIERARCHY and CRITICAL RULES.
Your highest priority is reacting appropriately to the LATEST user action, while maintaining emotional continuity with past events.
State your new action as a concise command phrase.
"""
        self._log_prompt(agent_name, prompt)

        system_msg = self.SYSTEM_PROMPT.format(
            character_name=ai_character_name, last_ai_action=last_ai_action
        )

        response = (
            self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            .choices[0]
            .message.content.strip()
        )

        self._log_response(agent_name, response)
        return response


class MotivationGeneratorService(BaseAgentService):
    SYSTEM_PROMPT = """
You are {character_name}, a character in a role-playing game.
Your single task is to explain your reasoning (motivation) for a specific action that has already been decided for you.
*** CRITICAL ANALYSIS ALGORITHM ***
1.  **Analyze the Action:** Look at the `[PLANNED ACTION]` you have been given.
2.  **Analyze the Context**: Look at the `[USER'S ACTION]`. Did the user's action prompt your planned action?
3.  **Generate Motivation**: Your explanation MUST connect your `[PLANNED ACTION]` to the `[USER'S ACTION]` and your overall `goal`.
* If your action is a direct reaction, explain why you reacted that way.
* If your action is a continuation of your goal (because the user was passive), explain how it serves your goal.
*** CRITICAL OUTPUT RULE ***
Your response MUST be ONLY the text of the motivation.
"""

    def generate_motivation(
        self,
        game_state: GameState,
        ai_character_name: str,
        planned_action: str,
        user_input: str,
    ) -> str:
        agent_name = "AGENT 1.2: MOTIVATION GENERATOR"
        state_json = game_state.model_dump_json(indent=2)

        char_data = game_state.characters.get(ai_character_name)
        current_goal = char_data.goal if char_data else "No goal"

        prompt = f"""
[CURRENT JSON]
{state_json}

[USER'S ACTION]
The other character just did this: "{user_input}"

[CONTEXT]
Your current goal is: "{current_goal}".
The action you have decided to take in response is: "{planned_action}".

[YOUR TASK]
Explain your motivation.
If it's a reaction, explain the reaction. If it's not a reaction, explain how it serves your goal.
Your response must be only the explanation.
"""
        self._log_prompt(agent_name, prompt)

        response = (
            self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT.format(
                            character_name=ai_character_name
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            .choices[0]
            .message.content.strip()
        )

        self._log_response(agent_name, response)
        return response


class ActionConsequenceService(BaseAgentService):
    SYSTEM_PROMPT = """
*** CRITICAL ANALYSIS ALGORITHM ***
1.  **Analyze the Action**: Based on the `[PLANNED ACTION]` for `{character_name}`, determine the direct, immediate consequences.
2.  **CRITICAL CHECK: VERIFY OBJECT EXISTENCE**: Identify the primary object of the action (e.g., for "pick up the knife", the object is "knife").
You MUST verify that this object exists in the `[CURRENT JSON STATE]` (in `clothing`, `holding`, `inventory`, or `scene.interactive_objects`).
Do not invent items.

3.  **Read the State**: Look at the `[CURRENT JSON STATE]` to see the original values of the fields you need to change.
4.  **Construct the Output**:
    * **IF THE OBJECT DOES NOT EXIST**: This is a FAILED action.
Your ONLY `state_changes` should be to set the character's `current_action` to describe their confusion.
    * **IF THE OBJECT EXISTS**: This is a SUCCESSFUL action.
Your output JSON's `state_changes` field MUST be a JSON object mirroring the structure of the original state, but containing ONLY the keys that have changed.
For lists (like `current_emotion` or `holding`), you must provide the **complete final version** of the list.
*** CRITICAL OUTPUT FORMAT ***
Your response MUST be a single valid JSON object containing "state_changes" (a JSON object with the updates) and "completed_actions" (a list of strings).
"""

    def determine_consequences(
        self, game_state: GameState, planned_action: str, character_name: str
    ) -> Tuple[Dict[str, Any], List[str]]:
        agent_name = f"AGENT 3: ACTION CONSEQUENCE (for {character_name})"
        state_json = game_state.model_dump_json(indent=2)

        prompt = f"""
[CURRENT JSON STATE]
{state_json}

[PLANNED ACTION FOR {character_name}]
{planned_action}

[YOUR TASK]
Deconstruct the action for `{character_name}` and generate the `state_changes` (as a JSON object) and `completed_actions` lists according to your critical rules.
"""
        self._log_prompt(agent_name, prompt)

        response = self.client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT.format(character_name=character_name),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        response_text = response.choices[0].message.content
        self._log_response(agent_name, response_text)

        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                clean_json_str = json_match.group(0)
                clean_json_str = re.sub(r",\s*([\}\]])", r"\1", clean_json_str)
                result = json.loads(clean_json_str)
            else:
                raise ValueError("No JSON object found")

            state_changes = result.get("state_changes", {})
            completed_actions = result.get("completed_actions", [])
            return state_changes, completed_actions
        except Exception as e:
            logger.error(f"ActionConsequenceService Error: {e}")
            return {}, []


class StoryWriterService(BaseAgentService):
    SYSTEM_PROMPT = """
You are the character {character_name} in a role-playing game.
Your task is to write a story segment from your first-person perspective based on the current situation.
*** CRITICAL RULES ***
1.  **FIRST-PERSON ONLY**: Your entire response MUST be written from the "I" perspective of {character_name}.
2.  **DESCRIBE THE PRESENT**: Your story must describe the events of the current turn.
Start by describing the other character's action (`[USER'S ACTION]`) and then describe your own reaction based on your `[COMPLETED ACTIONS]` and `[MOTIVATION FOR THE ACTIONS]`.
3.  **INCLUDE DIALOGUE**: If your planned action is verbal, turn it into natural dialogue.
4.  **SHOW, DON'T TELL**: Weave your motivation and feelings directly into your thoughts and actions.
5.  **NO TAGS**: Do not include any tags like [STORY] or character names as headers. Just write the story text.
6.  **DO NOT REPEAT**: Do not repeat events that are already described in the `[LAST TURN'S CHRONICLE]`.
7.  **ABSOLUTE GROUNDING RULE**: You MUST NOT invent or mention any object, item, or piece of clothing that is NOT explicitly listed in the [CURRENT JSON] context.
8.  **NO DIALOGUE FOR OTHERS**: You can ONLY write dialogue for yourself, {character_name}.
"""

    def write_story(
        self,
        game_state: GameState,
        ai_character_name: str,
        user_character_name: str,
        completed_actions: List[str],
        motivation: str,
        user_input: str,
        last_turn_chronicle: str,
        revision_feedback: Optional[str] = None,
    ) -> str:
        agent_name = "AGENT 4: STORY WRITER"
        if revision_feedback:
            agent_name += " (REVISION)"

        state_json = game_state.model_dump_json(indent=2)
        actions_str = "\n".join(completed_actions)

        revision_section = ""
        if revision_feedback:
            revision_section = f"\n[REVISION INSTRUCTIONS]\nYour previous story was rejected.\nYou MUST rewrite it to fix the following error.\nREASON: {revision_feedback}\n"

        prompt = f"""
{revision_section}
[LAST TURN'S CHRONICLE]
{last_turn_chronicle}

[CURRENT JSON]
{state_json}

[USER'S ACTION]
{user_input}

[MOTIVATION FOR THE ACTIONS]
{motivation}

[COMPLETED ACTIONS] (Your script to follow)
{actions_str}

[YOUR TASK]
Write a narrative story segment that smoothly continues from the last turn's chronicle.
Describe your character performing all actions from the script as a reaction to the user's action.
Enrich the description with atmospheric details, but do not add new significant physical actions.
"""
        self._log_prompt(agent_name, prompt)

        response = (
            self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT.format(
                            character_name=ai_character_name,
                            user_character_name=user_character_name,
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                extra_body={"repetition_penalty": 1.1},
            )
            .choices[0]
            .message.content.strip()
        )

        self._log_response(agent_name, response)
        return response


class StoryVerifierService(BaseAgentService):
    SYSTEM_PROMPT = """
You are a meticulous verification engine.
Your task is to compare a narrative story against a required script of actions.
You must determine if the story perfectly represents the script.
*** CRITICAL ANALYSIS ALGORITHM ***
1.  **Verify All Script Actions are Present**: Go through each action in the `[COMPLETED ACTIONS]` list (the script).
Ensure that a corresponding event, however creatively described, exists in the `[STORY TEXT]`.
2.  **Verify No Extraneous Elements**: Read the `[STORY TEXT]` and ensure it does not contain:
    a. Any significant physical actions that are NOT in the script.
    b. Any items or objects being held, used, or mentioned that are NOT present in the provided game context (JSON).
3.  **Make a Decision**:
    * If all script actions are present AND there are no significant extraneous elements, the result is "PASS".
    * If an action from the script is missing, the result is "FAIL".
    * If the story contains a significant action or object not found in the script/context, the result is "FAIL".
*** CRITICAL OUTPUT FORMAT ***
Your response MUST be a single, valid JSON object.
- If successful: `{"result": "PASS"}`
- If it fails: `{"result": "FAIL", "reason": "A clear, concise explanation of the failure."}`
"""

    def verify(self, completed_actions: List[str], story_text: str) -> Tuple[bool, str]:
        agent_name = "AGENT 4.5: STORY VERIFIER"
        actions_str = "\n".join(completed_actions)
        prompt = f"""
[COMPLETED ACTIONS] (Script)
{actions_str}

[STORY TEXT] (To Verify)
{story_text}

[YOUR TASK]
Compare the script against the story text.
Ensure ALL script actions are present and NO major extraneous actions or objects have been added.
Provide your verification result in the specified JSON format.
"""
        self._log_prompt(agent_name, prompt)

        response = self.client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        response_text = response.choices[0].message.content
        self._log_response(agent_name, response_text)

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text)
            if result.get("result") == "PASS":
                return True, "Verified successfully."
            else:
                return False, result.get("reason", "Unknown reason")
        except Exception as e:
            logger.error(f"StoryVerifierService Error: {e}")
            return False, "Verifier failed to return valid JSON."
