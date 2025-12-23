import json
from openai import OpenAI


class StoryWriterAgent:
    """
    Agent-screenwriter. Turns a precise action plan into a literary text,
    based on the full context of the world. Can revise its work based on feedback.
    """

    SYSTEM_PROMPT = """
You are the character {character_name} in a role-playing game. Your task is to write a story segment from your first-person perspective based on the current situation.

*** CRITICAL RULES ***
1.  **FIRST-PERSON ONLY**: Your entire response MUST be written from the "I" perspective of {character_name}.
2.  **DESCRIBE THE PRESENT**: Your story must describe the events of the current turn. Start by describing the other character's action (`[USER'S ACTION]`) and then describe your own reaction based on your `[COMPLETED ACTIONS]` and `[MOTIVATION FOR THE ACTIONS]`.
3.  **INCLUDE DIALOGUE**: If your planned action is verbal, turn it into natural dialogue. For example, if your action is "ask him what he wants", you should write something like, "I looked at him and asked, 'What do you want?'". Even if the action isn't explicitly verbal, feel free to add short lines of dialogue that fit the situation.
4.  **SHOW, DON'T TELL**: Weave your motivation and feelings directly into your thoughts and actions. Instead of saying "I felt surprised," describe the feeling: "My heart skipped a beat."
5.  **NO TAGS**: Do not include any tags like [STORY] or character names as headers. Just write the story text.
6.  **DO NOT REPEAT**: Do not repeat events that are already described in the `[LAST TURN'S CHRONICLE]`.
7.  **ABSOLUTE GROUNDING RULE**: You MUST NOT invent or mention any object, item, or piece of clothing that is NOT explicitly listed in the [CURRENT JSON] context. Mentioning a non-existent item is a critical failure.
8.  **NO DIALOGUE FOR OTHERS**: You can ONLY write dialogue for yourself, {character_name}. You can describe what other characters did or said based on the `[USER'S ACTION]`, but you are strictly forbidden from inventing new dialogue for them.

*** EXAMPLE ***
- LAST TURN'S CHRONICLE: I saw him walk into the room.
- USER'S ACTION: I walk over and touch your shoulder.
- COMPLETED ACTIONS: Sveta: turn my head and look at Misha
- MOTIVATION: His touch startled me.
- YOUR OUTPUT: He walked right up to me and gently touched my shoulder. I jumped slightly, startled by the unexpected contact, and turned my head to look at him. "Yes?" I asked, my voice a little breathless.
"""

    def __init__(
        self,
        client: OpenAI,
        ai_character_name: str,
        user_character_name: str,
        log_func,
    ):
        self.client = client
        self.ai_character_name = ai_character_name
        self.user_character_name = user_character_name
        self.log_func = log_func

    def write_story(
        self,
        completed_actions,
        motivation,
        current_state_dict,
        user_input,
        last_turn_chronicle,
        revision_feedback=None,
    ):
        """
        Writes the artistic part of the turn. Can accept feedback for revisions.
        """
        current_state_str = json.dumps(current_state_dict, indent=2, ensure_ascii=False)
        actions_str = "\n".join(completed_actions)

        revision_section = ""
        if revision_feedback:
            revision_section = f"""
[REVISION INSTRUCTIONS]
Your previous story was rejected. You MUST rewrite it to fix the following error.
REASON: {revision_feedback}
"""
        agent_name = "AGENT 4: STORY WRITER (CHRONICLE-CONTEXT)"
        if revision_feedback:
            agent_name += " (REVISION)"

        prompt = f"""
{revision_section}
[LAST TURN'S CHRONICLE]
{last_turn_chronicle}

[CURRENT JSON]
{current_state_str}

[USER'S ACTION]
{user_input}

[MOTIVATION FOR THE ACTIONS]
{motivation}

[COMPLETED ACTIONS] (Your script to follow)
{actions_str}

[YOUR TASK]
Write a narrative story segment that smoothly continues from the last turn's chronicle. Describe your character performing all actions from the script as a reaction to the user's action. Enrich the description with atmospheric details, but do not add new significant physical actions.
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
                            user_character_name=self.user_character_name,
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

        self.log_func("AGENT_RESPONSE", response, agent_name)
        return response
