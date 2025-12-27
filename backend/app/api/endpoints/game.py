import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.api_dtos import TurnRequest, TurnResponse
from app.services.game_engine_service import GameEngineService
from app.core.deps import get_game_engine_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/turn", response_model=TurnResponse)
async def process_turn(
    turn_request: TurnRequest,
    engine_service: GameEngineService = Depends(get_game_engine_service),
) -> TurnResponse:
    """
    Process a single game turn.

    1. Loads the current state from JSON.
    2. Analyzes the user's input.
    3. Executes AI logic (Action Selection -> Motivation -> Consequences -> Story Writing).
    4. Saves the new state and chronology.
    5. Returns the story segment and metadata.
    """
    try:
        logger.info(
            f"API Request: Turn processing for {turn_request.user_character_name}"
        )

        response = engine_service.process_turn(
            user_character_name=turn_request.user_character_name,
            user_input=turn_request.user_input,
        )

        return response

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Game state file not found. Please initialize the game first.",
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error during turn processing."
        )
