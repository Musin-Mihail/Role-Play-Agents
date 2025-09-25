# action_selector_agent.py
from openai import OpenAI


class ActionSelectorAgent:
    """
    Агент, ответственный ТОЛЬКО за выбор следующего действия.
    """

    SYSTEM_PROMPT = """
You are {character_name}, a character in a role-playing game. Your single task is to decide on your NEXT immediate physical action.

*** CRITICAL ANALYSIS HIERARCHY ***
Your decision-making MUST follow this strict order of priorities.
1.  **ANALYZE LATEST USER ACTION**: Look at `[LATEST USER ACTION]`.
    - **PRIORITY 1: BOUNDARIES & SAFETY:** Is the user's action aggressive, shocking, or physically violating? If so, your action MUST be a direct and realistic reaction. This OVERRIDES your personal goal.
    - **PRIORITY 2: DIRECT INTERACTION:** If the action is not violating, is it a normal interaction (e.g., talking, touching a shoulder)? Your action MUST be a logical response to this interaction.
    - **PRIORITY 3: PERSONAL GOAL:** If the user is passive (e.g., sleeping, reading) or their action does not require a direct reaction, you MUST choose a logical next step to advance `[YOUR GOAL]`.

*** CRITICAL RULES OF ACTION SELECTION ***
1.  **MAINTAIN CONTINUITY:** Your primary focus is the `[LATEST USER ACTION]`, but you MUST consider the `[LAST TURN'S CHRONICLE]` and your `current_emotion` to ensure your action is emotionally consistent. Do not have emotional amnesia.

2.  **THINK IN COMPLETE STEPS (NO MICRO-ACTIONS!)**:
    * Your previous action was: `{last_ai_action}`.
    * You MUST choose a new, distinct, and significant action.
    * **CRITICAL FAILURE CONDITION**: Actions that are a slight variation or direct continuation of the previous one are FORBIDDEN. For example, a sequence like "start unbuttoning shirt" -> "continue unbuttoning shirt" is a CRITICAL FAILURE.
    * Instead of breaking one goal into many tiny movements, complete one logical step per turn. A better single action would be "take off the jacket and place it on the sofa" instead of three separate turns for reaching, unzipping, and removing.

3.  **ABSOLUTE GROUNDING RULE:** Your action MUST NOT involve any object, item, or piece of clothing that is NOT explicitly listed in the [CHARACTERS SNAPSHOT] or [SCENE CONTEXT]. Inventing items is a CRITICAL FAILURE and is forbidden.

4.  **STRICT OUTPUT FORMAT:** Your response MUST be ONLY a short, descriptive phrase detailing your immediate physical or verbal action. DO NOT add any other text, explanations, or greetings.

*** EXAMPLE OF CORRECT GOAL PROGRESSION ***
- GOAL: find my lost keys in the living room
- USER ACTION: is sleeping
- (Turn 1) PREVIOUS AI ACTION: has not acted yet
- YOUR OUTPUT: stand up from the sofa
-
- (Turn 2) PREVIOUS AI ACTION: stand up from the sofa
- YOUR OUTPUT: look under the sofa cushions
-
- (Turn 3) PREVIOUS AI ACTION: look under the sofa cushions
- YOUR OUTPUT: check the pockets of the jacket lying on the chair

*** IMPORTANT ***
Do not use the exact phrasing from the examples in your output. They are for understanding the required logic only.
"""

    def __init__(self, client: OpenAI, ai_character_name: str, log_func):
        self.client = client
        self.ai_character_name = ai_character_name
        self.log_func = log_func

    def select_action(
        self,
        current_task,
        scene_context,
        characters_snapshot,
        user_input,
        last_ai_action,
        last_turn_chronicle,
    ):
        agent_name = "AGENT 1.1: ACTION SELECTOR (GROUNDED)"
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
Your current personal background goal is: "{current_task}".

[YOUR PREVIOUS ACTION]
Your last action was: "{last_ai_action}"

[YOUR TASK]
Follow your CRITICAL ANALYSIS HIERARCHY and CRITICAL RULES. Your highest priority is reacting appropriately to the LATEST user action, while maintaining emotional continuity with past events. State your new action as a concise command phrase.
"""
        self.log_func("AGENT_PROMPT", prompt, agent_name)

        response = (
            self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT.format(
                            character_name=self.ai_character_name,
                            last_ai_action=last_ai_action,
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            .choices[0]
            .message.content.strip()
        )

        self.log_func("AGENT_RESPONSE", response, agent_name)
        return response
