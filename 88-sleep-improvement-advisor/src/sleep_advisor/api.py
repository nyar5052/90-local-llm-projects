"""FastAPI REST API for Sleep Improvement Advisor."""

from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from .core import (
    compute_sleep_stats,
    calculate_sleep_score,
    get_environment_checklist,
    build_bedtime_routine,
    analyze_weekly_patterns,
    ASSESSMENT_QUESTIONS,
    DISCLAIMER,
)

app = FastAPI(
    title="Sleep Improvement Advisor API",
    description=(
        "Sleep pattern analysis, scoring, and improvement recommendations. "
        f"**Disclaimer:** {DISCLAIMER}"
    ),
    version="1.0.0",
)


# ── Request / Response Models ────────────────────────────────────────────

class SleepEntry(BaseModel):
    date: str = Field(..., description="Date of the sleep entry (e.g. 2024-01-15)")
    bedtime: str = Field(..., description="Bedtime (e.g. 23:00)")
    waketime: str = Field(..., description="Wake time (e.g. 07:00)")
    quality: Optional[int] = Field(None, ge=1, le=10, description="Subjective quality 1-10")
    duration: Optional[float] = Field(None, ge=0, description="Sleep duration in hours")
    notes: Optional[str] = Field(None, description="Additional notes")


class SleepEntriesRequest(BaseModel):
    entries: List[SleepEntry] = Field(..., min_length=1, description="List of sleep log entries")


class SleepScoreRequest(BaseModel):
    stats: dict = Field(..., description="Sleep statistics from /sleep/stats")


class BedtimeRoutineRequest(BaseModel):
    wake_time: str = Field(..., description="Desired wake time (e.g. 07:00)")
    sleep_duration: float = Field(8.0, ge=4.0, le=12.0, description="Target sleep duration in hours")


class SleepStatsResponse(BaseModel):
    stats: dict


class SleepScoreResponse(BaseModel):
    score: dict


class BedtimeRoutineResponse(BaseModel):
    routine: dict


class WeeklyPatternsResponse(BaseModel):
    patterns: dict


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/sleep/stats", response_model=SleepStatsResponse)
async def sleep_stats(request: SleepEntriesRequest):
    try:
        entries = [entry.model_dump() for entry in request.entries]
        stats = compute_sleep_stats(entries)
        return SleepStatsResponse(stats=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sleep/score", response_model=SleepScoreResponse)
async def sleep_score(request: SleepScoreRequest):
    try:
        score = calculate_sleep_score(request.stats)
        return SleepScoreResponse(score=score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sleep/environment-checklist")
async def sleep_environment_checklist():
    try:
        checklist = get_environment_checklist()
        return {"checklist": checklist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sleep/bedtime-routine", response_model=BedtimeRoutineResponse)
async def sleep_bedtime_routine(request: BedtimeRoutineRequest):
    try:
        routine = build_bedtime_routine(request.wake_time, request.sleep_duration)
        return BedtimeRoutineResponse(routine=routine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sleep/weekly-patterns", response_model=WeeklyPatternsResponse)
async def sleep_weekly_patterns(request: SleepEntriesRequest):
    try:
        entries = [entry.model_dump() for entry in request.entries]
        patterns = analyze_weekly_patterns(entries)
        return WeeklyPatternsResponse(patterns=patterns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sleep/assessment-questions")
async def sleep_assessment_questions():
    return {"questions": ASSESSMENT_QUESTIONS}


@app.get("/disclaimer")
async def disclaimer():
    return {"disclaimer": DISCLAIMER}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
