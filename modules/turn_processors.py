from .chronology_manager import read_chronology, overwrite_chronology

SYSTEM_PROMPT_CHRONICLER = """
You are a historian and archivist. Your task is to write a brief, factual, third-person narrative summary of a single game turn based on the actions of two characters.
*** CRITICAL RULES ***
1.  **INPUT**: You will receive the action of the user's character and the resulting action of the AI's character.
2.  **OUTPUT**: Your response MUST be a single, concise paragraph.
3.  **PERSPECTIVE**: The summary MUST be in the third-person.
4.  **NO TAGS**: Do not include any tags like [STORY], [MOTIVATION], or character names as headers.
5.  **COMBINE ACTIONS**: Do not just list the actions. Weave them into a single, coherent narrative describing what just happened.
6.  **BE OBJECTIVE**: Only record what happened. Do not include internal thoughts, motivations, or intentions unless they were explicitly stated as dialogue or action.
"""

SYSTEM_PROMPT_SUMMARIZER = """
You are a scriptwriter and editor. Your task is to take a raw game log, which includes character thoughts, actions, and dialogues, and rewrite it into a concise, third-person narrative story.
*** CRITICAL RULES ***
1.  **PRESERVE THE STORY**: The core events, actions, and the order in which they happen MUST be preserved. Do not change the plot or the meaning of the characters' actions.
2.  **REMOVE ALL TAGS**: You MUST remove all special tags like `[MOTIVATION]`, `[STORY]`, `[action]`, `[replica]`, `SUMMARY:`, and character name headers (e.g., `SVETA MUSINA:`).
3.  **CREATE A NARRATIVE**: Convert the log into a flowing, readable story. Integrate actions and dialogue naturally. For example, instead of `[replica] I see your panties`, write `Misha said, "I see your panties."`.
4.  **THIRD-PERSON PERSPECTIVE**: The entire story must be told from a third-person point of view.
5.  **BE CONCISE**: The final text must be significantly shorter than the original, but without losing critical details of what happened. Remove repetitive internal thoughts if they don't add new information to the scene.
Your response must contain ONLY the rewritten story. Do not add any extra comments, titles, or tags.
"""


def create_turn_summary(
    client, user_char_name, user_action, ai_char_name, ai_story_part, ai_motivation
):
    """Создает краткую сводку хода для записи в хронологию."""
    cleaned_ai_story = ai_story_part.replace("[STORY]", "").strip()
    prompt = f"""
Here are the actions and motivations for the turn.
Create a concise, third-person narrative summary.

- User Character ({user_char_name}) Action: "{user_action}"
- AI Character ({ai_char_name}) Motivation: "{ai_motivation}"
- AI Character ({ai_char_name}) Resulting Story: "{cleaned_ai_story}"
"""
    completion = client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_CHRONICLER},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content.strip()


def summarize_chronology_if_needed(client, word_limit=6000):
    """Проверяет длину хронологии и запускает сжатие, если она превышает лимит."""
    chronology_text = read_chronology()
    word_count = len(chronology_text.split())

    if word_count > word_limit:
        print(
            f"[SYSTEM: Chronology word count ({word_count}) exceeds limit ({word_limit}). Summarizing...]"
        )
        completion = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SUMMARIZER},
                {"role": "user", "content": chronology_text},
            ],
            temperature=0.3,
        )
        summary_text = completion.choices[0].message.content.strip()
        overwrite_chronology(summary_text)
        print("[SYSTEM: Chronology has been successfully summarized and updated.]")
