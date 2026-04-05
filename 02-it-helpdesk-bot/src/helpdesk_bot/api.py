"""FastAPI REST API for IT Helpdesk Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.helpdesk_bot.core import get_response, CATEGORIES

app = FastAPI(
    title="IT Helpdesk Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    history: list[dict] = []
    model: str = "gemma4"
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    status: str = "success"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/categories")
async def list_categories():
    """List available helpdesk categories."""
    return {"categories": CATEGORIES}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Get IT helpdesk support response."""
    try:
        result = get_response(
            user_message=request.message,
            history=request.history,
            model=request.model,
            temperature=request.temperature,
        )
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
