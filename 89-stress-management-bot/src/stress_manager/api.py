"""FastAPI REST API for Stress Management Bot."""

from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from .core import (
    calculate_stress_score,
    get_cbt_worksheet,
    get_coping_suggestions,
    BREATHING_EXERCISES,
    DISCLAIMER,
)

app = FastAPI(
    title="Stress Management Bot API",
    description=(
        "Stress assessment, CBT worksheets, coping strategies, and breathing exercises. "
        f"**Disclaimer:** {DISCLAIMER}"
    ),
    version="1.0.0",
)


# ── Request / Response Models ────────────────────────────────────────────

class StressScoreRequest(BaseModel):
    answers: dict = Field(
        ...,
        description="Question-to-rating mapping (each value should be 1-5)",
    )


class StressScoreResponse(BaseModel):
    score: dict


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/stress/score", response_model=StressScoreResponse)
async def stress_score(request: StressScoreRequest):
    try:
        result = calculate_stress_score(request.answers)
        return StressScoreResponse(score=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stress/cbt-worksheet/{worksheet_type}")
async def stress_cbt_worksheet(worksheet_type: str):
    try:
        worksheet = get_cbt_worksheet(worksheet_type)
        if not worksheet:
            raise HTTPException(
                status_code=404,
                detail=f"Worksheet type '{worksheet_type}' not found",
            )
        return worksheet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stress/coping-suggestions/{stress_level}")
async def stress_coping_suggestions(stress_level: str):
    valid_levels = ["low", "moderate", "high"]
    if stress_level.lower() not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stress level '{stress_level}'. Must be one of: {', '.join(valid_levels)}",
        )
    try:
        suggestions = get_coping_suggestions(stress_level)
        return {"stress_level": stress_level, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stress/breathing-exercises")
async def stress_breathing_exercises():
    return {"exercises": BREATHING_EXERCISES}


@app.get("/stress/breathing-exercises/{exercise_key}")
async def stress_breathing_exercise(exercise_key: str):
    if exercise_key not in BREATHING_EXERCISES:
        raise HTTPException(
            status_code=404,
            detail=f"Breathing exercise '{exercise_key}' not found. Available: {', '.join(BREATHING_EXERCISES.keys())}",
        )
    return BREATHING_EXERCISES[exercise_key]


@app.get("/disclaimer")
async def disclaimer():
    return {"disclaimer": DISCLAIMER}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
