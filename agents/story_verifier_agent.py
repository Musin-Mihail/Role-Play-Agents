import json
from openai import OpenAI


class StoryVerifierAgent:
    """
    An agent that acts as a quality control check. It verifies if the generated
    story accurately and exclusively reflects all the required completed actions.
    """

    SYSTEM_PROMPT = """
You are a meticulous verification engine. Your task is to compare a narrative story against a required script of actions. You must determine if the story perfectly represents the script.

*** CRITICAL ANALYSIS ALGORITHM ***
1.  **Verify All Script Actions are Present**: Go through each action in the `[COMPLETED ACTIONS]` list (the script). Ensure that a corresponding event, however creatively described, exists in the `[STORY TEXT]`.
2.  **Verify No Extraneous Elements**: Read the `[STORY TEXT]` and ensure it does not contain:
    a.  Any significant physical actions that are NOT in the script.
    b.  Any items or objects being held, used, or mentioned that are NOT present in the provided game context (JSON). This is a critical check.
3.  **Make a Decision**:
    * If all script actions are present AND there are no significant extraneous elements, the result is "PASS".
    * If an action from the script is missing, the result is "FAIL".
    * If the story contains a significant action or object not found in the script/context, the result is "FAIL".

*** CRITICAL OUTPUT FORMAT ***
Your response MUST be a single, valid JSON object.
- If successful: `{"result": "PASS"}`
- If it fails: `{"result": "FAIL", "reason": "A clear, concise explanation of the failure."}`

**Example 1 (Pass):**
- SCRIPT: `["Sveta: stood up from the sofa"]`
- STORY: "Sveta rose from her seat, stretching her back."
- YOUR OUTPUT: `{"result": "PASS"}`

**Example 2 (Fail - Missing Action):**
- SCRIPT: `["Sveta: stood up", "Sveta: dropped the pants"]`
- STORY: "Sveta stood up, holding her pants."
- YOUR OUTPUT: `{"result": "FAIL", "reason": "The story is missing the action: 'Sveta: dropped the pants'"}`

**Example 3 (Fail - Extraneous Object):**
- SCRIPT: `["Sveta: took off t-shirt"]`
- STORY: "Sveta took off her t-shirt and lit a cigarette."
- YOUR OUTPUT: `{"result": "FAIL", "reason": "The story contains an extraneous object not in the game state: 'cigarette'"}`
"""

    def __init__(self, client: OpenAI, log_func):
        self.client = client
        self.log_func = log_func

    def verify(self, completed_actions, story_text):
        """
        Verifies the story against the completed actions.
        Returns a tuple: (bool: is_verified, str: feedback_or_error_message)
        """
        actions_str = "\n".join(completed_actions)
        agent_name = "AGENT 4.5: STORY VERIFIER (IMPROVED)"
        prompt = f"""
[COMPLETED ACTIONS] (Script)
{actions_str}

[STORY TEXT] (To Verify)
{story_text}

[YOUR TASK]
Compare the script against the story text. Ensure ALL script actions are present and NO major extraneous actions or objects have been added. Provide your verification result in the specified JSON format.
"""
        self.log_func("AGENT_PROMPT", prompt, agent_name)

        response = self.client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )

        response_text = response.choices[0].message.content
        self.log_func("AGENT_RESPONSE", response_text, agent_name)

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text)
            if result.get("result") == "PASS":
                return True, "Verified successfully."
            else:
                reason = result.get("reason", "undisclosed reason")
                return False, f"Story verification failed. Reason: {reason}"
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            error_msg = f"StoryVerifierAgent returned invalid JSON. Error: {e}"
            self.log_func("SYSTEM", error_msg)
            self.log_func("SYSTEM", f"Raw response was:\n---\n{response_text}\n---")
            return False, "Verifier agent returned invalid data."
