"""FastAPI REST API for Mood Journal Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mood_journal.core import (
    add_entry,
    get_recent_entries,
    analyze_entries,
    generate_weekly_report,
    generate_monthly_report,
    get_gratitude_prompt,
    get_mood_stats,
    load_entries,
    MOODS,
)

app = FastAPI(
    title="Mood Journal Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class JournalEntryRequest(BaseModel):
    """Add a journal entry."""
    mood_key: str
    text: str
    energy_level: int = 5
    gratitude: str = ""


class AnalyzeRequest(BaseModel):
    """Request to analyze entries."""
    days: int = 7


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/moods")
async def list_moods():
    """List available mood keys."""
    return {"moods": MOODS}


@app.post("/entries")
async def create_entry(request: JournalEntryRequest):
    """Add a new journal entry."""
    try:
        entry = add_entry(
            mood_key=request.mood_key,
            text=request.text,
            energy_level=request.energy_level,
            gratitude=request.gratitude,
        )
        return {"entry": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entries")
async def list_entries(days: int = 7):
    """Get recent journal entries."""
    try:
        entries = get_recent_entries(days)
        return {"entries": entries, "count": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest):
    """Analyze recent mood entries."""
    try:
        entries = get_recent_entries(request.days)
        if not entries:
            return {"analysis": "No entries found for the specified period.", "status": "success"}
        result = analyze_entries(entries)
        return {"analysis": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/weekly")
async def weekly_report():
    """Generate a weekly mood report."""
    try:
        entries = get_recent_entries(7)
        result = generate_weekly_report(entries)
        return {"report": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/monthly")
async def monthly_report():
    """Generate a monthly mood report."""
    try:
        result = generate_monthly_report()
        return {"report": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gratitude-prompt")
async def gratitude_prompt():
    """Get a gratitude journaling prompt."""
    try:
        result = get_gratitude_prompt()
        return {"prompt": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def mood_stats():
    """Get mood statistics."""
    try:
        stats = get_mood_stats()
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
