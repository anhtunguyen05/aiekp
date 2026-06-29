import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI  # noqa: E402
from .routers import health, scanner  # noqa: E402

app = FastAPI(
    title="AIEKP API",
    description="AI Engineering Knowledge Platform API",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(scanner.router)


@app.get("/")
async def root():
    return {"message": "Welcome to AIEKP API"}
