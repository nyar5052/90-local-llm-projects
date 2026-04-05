"""FastAPI REST API for Fitness Coach Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.fitness_coach.core import (
    generate_workout_plan,
    get_exercise_details,
    LEVELS,
    GOALS,
)

app = FastAPI(
    title="Fitness Coach Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class WorkoutPlanRequest(BaseModel):
    """Request to generate a workout plan."""
    level: str = "beginner"
    goal: str = "general-fitness"
    equipment: str = "none"
    days_per_week: int = 4
    session_minutes: int = 45
    model: str = "gemma4"
    temperature: float = 0.7


class WorkoutPlanResponse(BaseModel):
    """Workout plan response."""
    workout_plan: str
    status: str = "success"


class ExerciseRequest(BaseModel):
    """Request for exercise details."""
    exercise_name: str
    level: str = "beginner"
    model: str = "gemma4"
    temperature: float = 0.7


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/levels")
async def list_levels():
    """List available fitness levels."""
    return {"levels": LEVELS}


@app.get("/goals")
async def list_goals():
    """List available fitness goals."""
    return {"goals": GOALS}


@app.post("/workout-plan", response_model=WorkoutPlanResponse)
async def create_workout_plan(request: WorkoutPlanRequest):
    """Generate a personalized workout plan."""
    try:
        result = generate_workout_plan(
            level=request.level,
            goal=request.goal,
            equipment=request.equipment,
            days_per_week=request.days_per_week,
            session_minutes=request.session_minutes,
            model=request.model,
            temperature=request.temperature,
        )
        return WorkoutPlanResponse(workout_plan=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/exercise")
async def exercise_details(request: ExerciseRequest):
    """Get detailed information about a specific exercise."""
    try:
        result = get_exercise_details(
            exercise_name=request.exercise_name,
            level=request.level,
            model=request.model,
            temperature=request.temperature,
        )
        return {"details": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
