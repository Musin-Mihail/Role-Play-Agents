from fastapi import APIRouter
from app.api.endpoints import game

api_router = APIRouter()

# Register the game endpoints under /game
api_router.include_router(game.router, prefix="/game", tags=["game"])
