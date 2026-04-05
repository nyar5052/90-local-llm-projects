"""FastAPI REST API for Study Buddy Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.study_buddy.core import (
    generate_quiz,
    explain_concept,
    create_study_plan,
    generate_flashcards,
    ask_question,
    get_flashcard_set,
    record_study_session,
    get_study_stats,
)

app = FastAPI(
    title="Study Buddy Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class QuizRequest(BaseModel):
    """Request to generate a quiz."""
    subject: str
    topic: str
    num_questions: int = 5


class ConceptRequest(BaseModel):
    """Request to explain a concept."""
    subject: str
    topic: str
    depth: str = "detailed"


class StudyPlanRequest(BaseModel):
    """Request to create a study plan."""
    subject: str
    topic: str
    days: int = 7


class FlashcardRequest(BaseModel):
    """Request to generate flashcards."""
    subject: str
    topic: str
    count: int = 10


class QuestionRequest(BaseModel):
    """Ask a question on a topic."""
    subject: str
    topic: str
    question: str
    history: list[dict] = []


class SessionRequest(BaseModel):
    """Record a study session."""
    subject: str
    topic: str
    mode: str
    duration_minutes: int


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/quiz")
async def quiz_endpoint(request: QuizRequest):
    """Generate a quiz on a topic."""
    try:
        result = generate_quiz(
            subject=request.subject,
            topic=request.topic,
            num_questions=request.num_questions,
        )
        return {"quiz": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain")
async def explain_endpoint(request: ConceptRequest):
    """Explain a concept."""
    try:
        result = explain_concept(
            subject=request.subject,
            topic=request.topic,
            depth=request.depth,
        )
        return {"explanation": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/study-plan")
async def study_plan_endpoint(request: StudyPlanRequest):
    """Create a study plan."""
    try:
        result = create_study_plan(
            subject=request.subject,
            topic=request.topic,
            days=request.days,
        )
        return {"study_plan": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flashcards")
async def flashcards_endpoint(request: FlashcardRequest):
    """Generate flashcards for a topic."""
    try:
        result = generate_flashcards(
            subject=request.subject,
            topic=request.topic,
            count=request.count,
        )
        return {"flashcards": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flashcards/{subject}/{topic}")
async def get_flashcards(subject: str, topic: str):
    """Get a saved flashcard set."""
    try:
        result = get_flashcard_set(subject, topic)
        if result is None:
            raise HTTPException(status_code=404, detail="Flashcard set not found")
        return {"flashcard_set": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_endpoint(request: QuestionRequest):
    """Ask a question about a topic."""
    try:
        result = ask_question(
            subject=request.subject,
            topic=request.topic,
            question=request.question,
            history=request.history,
        )
        return {"answer": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session")
async def record_session_endpoint(request: SessionRequest):
    """Record a study session."""
    try:
        entry = record_study_session(
            subject=request.subject,
            topic=request.topic,
            mode=request.mode,
            duration_minutes=request.duration_minutes,
        )
        return {"session": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def stats_endpoint():
    """Get study statistics."""
    try:
        stats = get_study_stats()
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
