"""FastAPI REST API for Language Learning Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.language_learner.core import (
    get_response,
    get_lesson,
    get_pronunciation_tips,
    generate_lesson_plan,
    load_vocabulary,
    add_vocabulary_word,
    get_vocabulary_quiz,
    record_session,
    get_progress_summary,
    LANGUAGES,
    LEVELS,
)

app = FastAPI(
    title="Language Learning Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ChatRequest(BaseModel):
    """Chat with the language tutor."""
    message: str
    history: list[dict] = []
    language: str = "spanish"
    level: str = "beginner"


class LessonRequest(BaseModel):
    """Request a lesson on a topic."""
    topic: str
    language: str = "spanish"
    level: str = "beginner"


class PronunciationRequest(BaseModel):
    """Request pronunciation tips."""
    word: str
    language: str = "spanish"


class LessonPlanRequest(BaseModel):
    """Request a lesson plan."""
    language: str = "spanish"
    level: str = "beginner"
    duration_weeks: int = 4


class VocabAddRequest(BaseModel):
    """Add a vocabulary word."""
    language: str
    word: str
    translation: str
    example: str = ""
    notes: str = ""


class QuizRequest(BaseModel):
    """Generate a vocabulary quiz."""
    language: str = "spanish"
    count: int = 5


class SessionRecordRequest(BaseModel):
    """Record a study session."""
    language: str
    level: str
    duration_minutes: int
    topic: str = "conversation"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/languages")
async def list_languages():
    """List available languages."""
    return {"languages": LANGUAGES, "levels": LEVELS}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with the language tutor."""
    try:
        result = get_response(
            user_message=request.message,
            history=request.history,
            language=request.language,
            level=request.level,
        )
        return {"response": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lesson")
async def lesson_endpoint(request: LessonRequest):
    """Get a lesson on a specific topic."""
    try:
        result = get_lesson(
            topic=request.topic,
            language=request.language,
            level=request.level,
        )
        return {"lesson": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pronunciation")
async def pronunciation_endpoint(request: PronunciationRequest):
    """Get pronunciation tips for a word."""
    try:
        result = get_pronunciation_tips(word=request.word, language=request.language)
        return {"tips": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lesson-plan")
async def lesson_plan_endpoint(request: LessonPlanRequest):
    """Generate a structured lesson plan."""
    try:
        result = generate_lesson_plan(
            language=request.language,
            level=request.level,
            duration_weeks=request.duration_weeks,
        )
        return {"lesson_plan": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vocabulary/{language}")
async def get_vocabulary(language: str):
    """Get vocabulary list for a language."""
    try:
        vocab = load_vocabulary(language)
        return {"vocabulary": vocab, "count": len(vocab)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vocabulary")
async def add_vocab(request: VocabAddRequest):
    """Add a vocabulary word."""
    try:
        entry = add_vocabulary_word(
            language=request.language,
            word=request.word,
            translation=request.translation,
            example=request.example,
            notes=request.notes,
        )
        return {"entry": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quiz")
async def quiz_endpoint(request: QuizRequest):
    """Generate a vocabulary quiz."""
    try:
        result = get_vocabulary_quiz(language=request.language, count=request.count)
        return {"quiz": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session")
async def record_session_endpoint(request: SessionRecordRequest):
    """Record a study session."""
    try:
        entry = record_session(
            language=request.language,
            level=request.level,
            duration_minutes=request.duration_minutes,
            topic=request.topic,
        )
        return {"session": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/progress/{language}")
async def progress_endpoint(language: str):
    """Get progress summary for a language."""
    try:
        result = get_progress_summary(language)
        return {"summary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
