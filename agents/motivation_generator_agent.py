import json
from openai import OpenAI


class MotivationGeneratorAgent:
    """
    Агент, ответственный ТОЛЬКО за генерацию мотивации для УЖЕ ВЫБРАННОГО действия.
    """

    SYSTEM_PROMPT = """
You are {character_name}, a character in a role-playing game. Your single task is to explain your reasoning (motivation) for a specific action that has already been decided for you.

*** CRITICAL ANALYSIS ALGORITHM ***
1.  **Analyze the Action:** Look at the `[PLANNED ACTION]` you have been given.
2.  **Analyze the Context**: Look at the `[USER'S ACTION]`. Did the user's action prompt your planned action?
3.  **Generate Motivation**: Your explanation MUST connect your `[PLANNED ACTION]` to the `[USER'S ACTION]` and your overall `goal`.
    * If your action is a direct reaction, explain why you reacted that way.
    * If your action is a continuation of your goal (because the user was passive), explain how it serves your goal.

*** CRITICAL OUTPUT RULE ***
Your response MUST be ONLY the text of the motivation.

*** EXAMPLES (FOR STYLE ONLY - DO NOT COPY) ***
- **Example 1 (Reacting to User):**
  - USER'S ACTION: `I ask what you are looking for.`
  - PLANNED ACTION: `tell him I'm looking for my keys`
  - GOAL: `find my lost keys`
  - YOUR OUTPUT: `His question was direct, so I decided it was easier to just tell him the truth instead of being secretive.`

- **Example 2 (Acting on Goal during User Passivity):**
  - USER'S ACTION: `I continue reading my book.`
  - PLANNED ACTION: `look under the sofa`
  - GOAL: `find my lost keys`
  - YOUR OUTPUT: `He seems occupied with his book, so it's a good moment to continue my search. The sofa is the most likely place.`
  
*** IMPORTANT ***
Do not use the exact phrasing from the examples in your output. They are for understanding the required style and logic only.
"""

    def __init__(self, client: OpenAI, ai_character_name: str, log_func):
        self.client = client
        self.ai_character_name = ai_character_name
        self.log_func = log_func

    def generate_motivation(self, current_state_dict, planned_action, user_input):
        """
        Генерирует мотивацию для заданного действия.
        """
        current_state_str = json.dumps(current_state_dict, indent=2, ensure_ascii=False)

        ai_character_details = current_state_dict["characters"].get(
            self.ai_character_name
        )

        current_task = (
            ai_character_details.get("goal", "No current goal.")
            if ai_character_details
            else "No goal found."
        )
        agent_name = "AGENT 1.2: MOTIVATION GENERATOR (DIVERSIFIED)"
        prompt = f"""
[CURRENT JSON]
{current_state_str}

[USER'S ACTION]
The other character just did this: "{user_input}"

[CONTEXT]
Your current goal is: "{current_task}".
The action you have decided to take in response is: "{planned_action}".

[YOUR TASK]
Explain your motivation. If it's a reaction, explain the reaction. If it's not a reaction, explain how it serves your goal.
Your response must be only the explanation.
"""
        self.log_func("AGENT_PROMPT", prompt, agent_name)

        response = (
            self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT.format(
                            character_name=self.ai_character_name
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
