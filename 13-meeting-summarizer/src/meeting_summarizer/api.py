"""FastAPI REST API for Meeting Summarizer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.meeting_summarizer.core import (
    summarize_meeting,
    identify_speakers,
    extract_decision_log,
    generate_followup_reminders,
)

app = FastAPI(
    title="Meeting Summarizer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class TranscriptRequest(BaseModel):
    """Request with meeting transcript."""
    transcript: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/summarize")
async def summarize_endpoint(request: TranscriptRequest):
    """Summarize a meeting transcript."""
    try:
        result = summarize_meeting(transcript=request.transcript)
        return {"summary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speakers")
async def speakers_endpoint(request: TranscriptRequest):
    """Identify speakers in a meeting transcript."""
    try:
        result = identify_speakers(transcript=request.transcript)
        return {"speakers": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decisions")
async def decisions_endpoint(request: TranscriptRequest):
    """Extract decision log from a meeting transcript."""
    try:
        result = extract_decision_log(transcript=request.transcript)
        return {"decisions": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/followups")
async def followups_endpoint(request: TranscriptRequest):
    """Generate follow-up reminders from a meeting transcript."""
    try:
        result = generate_followup_reminders(transcript=request.transcript)
        return {"followups": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
