import uvicorn

if __name__ == "__main__":
    """
    Entry point for the Role-Play Engine API.
    Run this script to start the server: python backend/run.py
    """
    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
