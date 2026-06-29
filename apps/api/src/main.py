import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI
from .routers import health
app = FastAPI(
    title="AIEKP API",
    description="AI Engineering Knowledge Platform API",
    version="0.1.0",
)

app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "Welcome to AIEKP API"}
