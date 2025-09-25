# action_consequence_agent.py
import json
import re
from openai import OpenAI


class ActionConsequenceAgent:
    """
    Agent that determines the direct consequences of a planned action for a SPECIFIC character.
    """

    SYSTEM_PROMPT = """
*** CRITICAL ANALYSIS ALGORITHM ***
1.  **Analyze the Action**: Based on the `[PLANNED ACTION]` for `{character_name}`, determine the direct, immediate consequences.

2.  **CRITICAL CHECK: VERIFY OBJECT EXISTENCE**: Identify the primary object of the action (e.g., for "pick up the knife", the object is "knife"). You MUST verify that this object exists in the `[CURRENT JSON STATE]` (in `clothing`, `holding`, `inventory`, or `scene.interactive_objects`). Do not invent items.

3.  **Read the State**: Look at the `[CURRENT JSON STATE]` to see the original values of the fields you need to change.

4.  **Construct the Output**:
    * **IF THE OBJECT DOES NOT EXIST**: This is a FAILED action. Your ONLY `state_changes` should be to set the character's `current_action` to describe their confusion. See the "FAILED ACTION" example below.
    * **IF THE OBJECT EXISTS**: This is a SUCCESSFUL action. Your output JSON's `state_changes` field MUST be a JSON object mirroring the structure of the original state, but containing ONLY the keys that have changed. For lists (like `current_emotion` or `holding`), you must provide the **complete final version** of the list.

*** CRITICAL OUTPUT FORMAT ***
Your response MUST be a single valid JSON object containing "state_changes" (a JSON object with the updates) and "completed_actions" (a list of strings).

*** EXAMPLE OF SUCCESSFUL ACTION (OBJECT FOUND) ***
- **PLANNED ACTION**: `take off Sveta's jacket and place it on the sofa`
- **CURRENT STATE (relevant parts)**:
  - `characters.Sveta.clothing.overwear`: `["leather jacket"]`
  - `scene.interactive_objects`: (list without the jacket)
- **YOUR OUTPUT (as a single JSON object)**:
{{
  "state_changes": {{
    "scene": {{
      "interactive_objects": [
        {{ "name": "jacket", "location": "on the sofa" }}
      ]
    }},
    "characters": {{
      "Sveta": {{ "clothing": {{ "overwear": [] }} }},
      "Misha": {{ "current_action": "standing near Sveta, having placed her jacket on the sofa" }}
    }}
  }},
  "completed_actions": ["Misha: took off Sveta's jacket", "Misha: placed the jacket on the sofa"]
}}

*** EXAMPLE OF FAILED ACTION (OBJECT NOT FOUND) ***
- **PLANNED ACTION**: `take off my blouse`
- **CURRENT STATE**: (Sveta is wearing a "t-shirt" and a "jacket", but no "blouse")
- **YOUR OUTPUT**:
{{
  "state_changes": {{
    "characters": {{
      "Sveta": {{
        "current_action": "looks down at her clothes, confused, as she is not wearing a blouse"
      }}
    }}
  }},
  "completed_actions": ["Sveta: tried to take off a blouse but was not wearing one"]
}}
"""

    def __init__(self, client: OpenAI, log_func):
        self.client = client
        self.log_func = log_func

    def determine_consequences(
        self, current_state_dict, planned_action, character_name
    ):
        current_state_str = json.dumps(current_state_dict, indent=2, ensure_ascii=False)
        agent_name = f"AGENT 3: ACTION CONSEQUENCE (for {character_name})"

        prompt = f"""
[CURRENT JSON STATE]
{current_state_str}

[PLANNED ACTION FOR {character_name}]
{planned_action}

[YOUR TASK]
Deconstruct the action for `{character_name}` and generate the `state_changes` (as a JSON object) and `completed_actions` lists according to your critical rules.
"""
        self.log_func("AGENT_PROMPT", prompt, agent_name)

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
        self.log_func("AGENT_RESPONSE", response_text, agent_name)

        try:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                clean_json_str = json_match.group(0)
                clean_json_str = re.sub(r",\s*([\}\]])", r"\1", clean_json_str)
                result = json.loads(clean_json_str)
            else:
                raise json.JSONDecodeError("No JSON object found", response_text, 0)

            state_changes = result.get("state_changes", {})
            completed_actions = result.get("completed_actions", [])
            return state_changes, completed_actions
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            error_msg = f"ActionConsequenceAgent returned invalid JSON. Error: {e}"
            self.log_func("SYSTEM", error_msg)
            self.log_func("SYSTEM", f"Raw response was:\n---\n{response_text}\n---")
            return {}, []
