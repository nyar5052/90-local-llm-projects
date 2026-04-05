"""FastAPI REST API for Meal Planner Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.meal_planner.core import (
    generate_meal_plan,
    get_recipe_details,
    generate_shopping_list,
    DIETS,
)

app = FastAPI(
    title="Meal Planner Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class MealPlanRequest(BaseModel):
    """Request to generate a meal plan."""
    diet: str = "omnivore"
    days: int = 7
    allergies: Optional[str] = None
    calories: Optional[int] = None
    model: str = "gemma4"
    temperature: float = 0.7


class MealPlanResponse(BaseModel):
    """Meal plan response."""
    meal_plan: str
    status: str = "success"


class RecipeRequest(BaseModel):
    """Request for recipe details."""
    meal_name: str
    diet: str = "omnivore"
    model: str = "gemma4"
    temperature: float = 0.7


class ShoppingListRequest(BaseModel):
    """Request to generate a shopping list."""
    meal_plan: str
    model: str = "gemma4"
    temperature: float = 0.3


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/diets")
async def list_diets():
    """List available diet types."""
    return {"diets": DIETS}


@app.post("/meal-plan", response_model=MealPlanResponse)
async def create_meal_plan(request: MealPlanRequest):
    """Generate a meal plan based on preferences."""
    try:
        result = generate_meal_plan(
            diet=request.diet,
            days=request.days,
            allergies=request.allergies,
            calories=request.calories,
            model=request.model,
            temperature=request.temperature,
        )
        return MealPlanResponse(meal_plan=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recipe")
async def get_recipe(request: RecipeRequest):
    """Get detailed recipe for a specific meal."""
    try:
        result = get_recipe_details(
            meal_name=request.meal_name,
            diet=request.diet,
            model=request.model,
            temperature=request.temperature,
        )
        return {"recipe": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/shopping-list")
async def create_shopping_list(request: ShoppingListRequest):
    """Generate a shopping list from a meal plan."""
    try:
        result = generate_shopping_list(
            meal_plan=request.meal_plan,
            model=request.model,
            temperature=request.temperature,
        )
        return {"shopping_list": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
