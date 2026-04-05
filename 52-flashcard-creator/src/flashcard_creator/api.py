"""FastAPI REST API for Flashcard Creator."""

from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from flashcard_creator.core import (
    create_flashcards,
    dict_to_flashcards,
)

app = FastAPI(
    title="Flashcard Creator API",
    description="REST API for Flashcard Creator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class GenerateFlashcardsRequest(BaseModel):
    topic: str = Field(..., description="Topic for flashcard generation")
    count: int = Field(10, description="Number of flashcards to create")
    difficulty: str = Field("medium", description="Difficulty level")


class ConvertFlashcardsRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Raw dictionary data to convert into structured flashcards")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "flashcard-creator"}


@app.post("/generate")
async def api_generate_flashcards(request: GenerateFlashcardsRequest):
    """Generate a set of flashcards for the given topic."""
    try:
        result = create_flashcards(request.topic, request.count, request.difficulty)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert")
async def api_convert_flashcards(request: ConvertFlashcardsRequest):
    """Convert a raw dictionary into structured Flashcard objects."""
    try:
        flashcards = dict_to_flashcards(request.data)
        # Return each Flashcard as a plain dict (handles dataclass objects)
        result = [asdict(fc) if hasattr(fc, "__dataclass_fields__") else fc for fc in flashcards]
        return {"flashcards": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
