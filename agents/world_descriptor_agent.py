import json
from openai import OpenAI


class WorldDescriptorAgent:
    """
    Агент, ответственный за преобразование state.json в ПОДРОБНОЕ текстовое описание.
    """

    SYSTEM_PROMPT = """
You are a Game Master's assistant. Your task is to read a JSON object representing the game's state and write a detailed, factual, human-readable summary of it.

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

**Example Output:**
The scene is set in an apartment...

Sveta Musina is a woman with long dark hair. Her son is Misha Musin. She is currently standing by the sofa.
Wearing:
- torso: T-shirt
- legs: pants
Holding:
- smartphone
"""

    def __init__(self, client: OpenAI, log_func):
        self.client = client
        self.log_func = log_func

    def describe(self, current_state_dict):
        """
        Генерирует текстовое описание мира из JSON.
        """
        current_state_str = json.dumps(current_state_dict, indent=2, ensure_ascii=False)
        agent_name = "AGENT 0: WORLD DESCRIPTOR (CLARITY FIX)"
        prompt = f"""
[CURRENT JSON STATE]
{current_state_str}

[YOUR TASK]
Translate the JSON state above into a detailed text description. You MUST use the `Wearing:` and `Holding:` headings to clearly separate clothing from held items.
"""
        self.log_func("AGENT_PROMPT", prompt, agent_name)

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

        self.log_func("AGENT_RESPONSE", response, agent_name)
        return response
