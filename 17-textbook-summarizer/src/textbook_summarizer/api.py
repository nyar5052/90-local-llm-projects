"""FastAPI REST API for Textbook Summarizer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.textbook_summarizer.core import (
    summarize_chapter,
    generate_glossary,
    generate_concept_map,
    generate_study_questions,
)

app = FastAPI(
    title="Textbook Summarizer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ChapterRequest(BaseModel):
    """Request with chapter text."""
    text: str
    style: str = "concise"


class StudyQuestionsRequest(BaseModel):
    """Request for study questions."""
    text: str
    num_questions: int = 5


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/summarize")
async def summarize_endpoint(request: ChapterRequest):
    """Summarize a textbook chapter."""
    try:
        result = summarize_chapter(text=request.text, style=request.style)
        return {"summary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glossary")
async def glossary_endpoint(request: ChapterRequest):
    """Generate a glossary from chapter text."""
    try:
        result = generate_glossary(text=request.text)
        return {"glossary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/concept-map")
async def concept_map_endpoint(request: ChapterRequest):
    """Generate a concept map from chapter text."""
    try:
        result = generate_concept_map(text=request.text)
        return {"concept_map": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/study-questions")
async def study_questions_endpoint(request: StudyQuestionsRequest):
    """Generate study questions from chapter text."""
    try:
        result = generate_study_questions(
            text=request.text,
            num_questions=request.num_questions,
        )
        return {"questions": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016)
