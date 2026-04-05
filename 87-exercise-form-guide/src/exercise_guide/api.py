"""FastAPI REST API for Exercise Form Guide."""

from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from .core import (
    generate_guide,
    list_exercises,
    generate_routine,
    get_warmup_routine,
    get_cooldown_routine,
    get_exercise_variations,
    get_muscle_info,
    VALID_LEVELS,
    VALID_MUSCLE_GROUPS,
    VALID_GOALS,
    DISCLAIMER,
)

app = FastAPI(
    title="Exercise Form Guide API",
    description=(
        "AI-powered exercise form guidance, routine generation, and muscle information. "
        f"**Disclaimer:** {DISCLAIMER}"
    ),
    version="1.0.0",
)


# ── Request / Response Models ────────────────────────────────────────────

class GuideRequest(BaseModel):
    exercise: str = Field(..., min_length=1, description="Exercise name")
    level: str = Field(..., description="Fitness level: beginner, intermediate, or advanced")


class ListExercisesRequest(BaseModel):
    muscle_group: str = Field(..., description="Target muscle group")


class RoutineRequest(BaseModel):
    goal: str = Field(..., description="Training goal: strength, hypertrophy, endurance, or flexibility")
    level: str = Field(..., description="Fitness level: beginner, intermediate, or advanced")


class AIResponse(BaseModel):
    result: str


# ── Helpers ───────────────────────────────────────────────────────────────

def _validate_level(level: str) -> None:
    if level.lower() not in VALID_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid level '{level}'. Must be one of: {', '.join(VALID_LEVELS)}",
        )


def _validate_muscle_group(muscle_group: str) -> None:
    if muscle_group.lower() not in VALID_MUSCLE_GROUPS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid muscle group '{muscle_group}'. Must be one of: {', '.join(VALID_MUSCLE_GROUPS)}",
        )


def _validate_goal(goal: str) -> None:
    if goal.lower() not in VALID_GOALS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid goal '{goal}'. Must be one of: {', '.join(VALID_GOALS)}",
        )


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/exercises/guide", response_model=AIResponse)
async def exercises_guide(request: GuideRequest):
    _validate_level(request.level)
    try:
        result = generate_guide(request.exercise, request.level)
        return AIResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/exercises/list", response_model=AIResponse)
async def exercises_list(request: ListExercisesRequest):
    _validate_muscle_group(request.muscle_group)
    try:
        result = list_exercises(request.muscle_group)
        return AIResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/exercises/routine", response_model=AIResponse)
async def exercises_routine(request: RoutineRequest):
    _validate_goal(request.goal)
    _validate_level(request.level)
    try:
        result = generate_routine(request.goal, request.level)
        return AIResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exercises/warmup/{muscle_group}")
async def exercises_warmup(muscle_group: str):
    _validate_muscle_group(muscle_group)
    try:
        routine = get_warmup_routine(muscle_group)
        return {"muscle_group": muscle_group, "warmup_routine": routine}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exercises/cooldown/{muscle_group}")
async def exercises_cooldown(muscle_group: str):
    _validate_muscle_group(muscle_group)
    try:
        routine = get_cooldown_routine(muscle_group)
        return {"muscle_group": muscle_group, "cooldown_routine": routine}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exercises/variations/{exercise}")
async def exercises_variations(exercise: str):
    try:
        variations = get_exercise_variations(exercise)
        return {"exercise": exercise, "variations": variations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/muscles/{muscle_group}")
async def muscles_info(muscle_group: str):
    _validate_muscle_group(muscle_group)
    try:
        info = get_muscle_info(muscle_group)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reference/levels")
async def reference_levels():
    return {"levels": VALID_LEVELS}


@app.get("/reference/muscle-groups")
async def reference_muscle_groups():
    return {"muscle_groups": VALID_MUSCLE_GROUPS}


@app.get("/reference/goals")
async def reference_goals():
    return {"goals": VALID_GOALS}


@app.get("/disclaimer")
async def disclaimer():
    return {"disclaimer": DISCLAIMER}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
