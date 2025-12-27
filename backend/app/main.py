from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set all CORS enabled origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = create_application()


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running
    and configuration is loaded correctly.
    """
    return {
        "status": "active",
        "project": settings.PROJECT_NAME,
        "config_check": {"llm_base_url": settings.OPENAI_BASE_URL},
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Role-Play Engine API. Visit /docs for Swagger UI."
    }
