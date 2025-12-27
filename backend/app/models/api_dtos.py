from typing import List, Optional
from pydantic import BaseModel


class TurnRequest(BaseModel):
    """
    Данные, отправляемые клиентом для совершения хода.
    """

    user_character_name: str
    user_input: str


class TurnResponse(BaseModel):
    """
    Ответ сервера после обработки хода ИИ.
    """

    ai_character_name: str
    motivation: str
    story_part: str
    completed_actions: List[str]
    is_success: bool = True
    error_message: Optional[str] = None
