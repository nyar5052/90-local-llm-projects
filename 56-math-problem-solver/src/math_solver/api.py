"""FastAPI REST API for Math Problem Solver."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from math_solver.core import (
    solve_problem,
    generate_practice_problems,
    get_formula_library,
    get_formulas_from_llm,
    check_service,
)

app = FastAPI(
    title="Math Problem Solver API",
    description="REST API for Math Problem Solver",
    version="1.0.0",
)


# --- Request Models ---


class SolveProblemRequest(BaseModel):
    problem: str = Field(..., description="Math problem to solve")
    show_steps: bool = Field(True, description="Whether to show solution steps")
    category: str = Field("", description="Problem category (e.g. algebra, calculus)")


class GeneratePracticeRequest(BaseModel):
    category: str = Field(..., description="Problem category")
    difficulty: str = Field(..., description="Difficulty level")
    count: int = Field(5, description="Number of problems to generate")


class FormulaLibraryRequest(BaseModel):
    category: str = Field("", description="Category filter for formulas")


class FormulasFromLLMRequest(BaseModel):
    category: str = Field(..., description="Category to get formulas for")


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "math-problem-solver"}


@app.get("/service-check")
async def api_check_service():
    try:
        result = check_service()
        return {"available": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/solve")
async def api_solve_problem(request: SolveProblemRequest):
    try:
        result = solve_problem(
            problem=request.problem,
            show_steps=request.show_steps,
            category=request.category,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/practice")
async def api_generate_practice_problems(request: GeneratePracticeRequest):
    try:
        result = generate_practice_problems(
            category=request.category,
            difficulty=request.difficulty,
            count=request.count,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/formulas")
async def api_get_formula_library(request: FormulaLibraryRequest):
    try:
        result = get_formula_library(category=request.category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/formulas/llm")
async def api_get_formulas_from_llm(request: FormulasFromLLMRequest):
    try:
        result = get_formulas_from_llm(category=request.category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
