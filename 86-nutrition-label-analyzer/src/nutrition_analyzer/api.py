"""FastAPI REST API for Nutrition Label Analyzer."""

from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from .core import (
    analyze_food,
    analyze_label,
    compare_foods,
    calculate_daily_values,
    check_allergens,
    DV_REFERENCE,
    COMMON_ALLERGENS,
    DISCLAIMER,
)

app = FastAPI(
    title="Nutrition Label Analyzer API",
    description=(
        "AI-powered nutrition label analysis, food comparison, and allergen checking. "
        f"**Disclaimer:** {DISCLAIMER}"
    ),
    version="1.0.0",
)


# ── Request / Response Models ────────────────────────────────────────────

class FoodAnalyzeRequest(BaseModel):
    food: str = Field(..., min_length=1, description="Food name or description to analyze")


class LabelAnalyzeRequest(BaseModel):
    label_text: str = Field(..., min_length=1, description="Raw nutrition label text")


class CompareFoodsRequest(BaseModel):
    foods: List[str] = Field(..., min_length=2, description="List of foods to compare")


class DailyValuesRequest(BaseModel):
    nutrients: dict = Field(..., description="Nutrient name to amount mapping")


class CheckAllergensRequest(BaseModel):
    food: str = Field(..., min_length=1, description="Food name or ingredient list")
    allergen_list: Optional[List[str]] = Field(
        None, description="Custom allergen list; defaults to common allergens"
    )


class AnalysisResponse(BaseModel):
    result: str


class DailyValuesResponse(BaseModel):
    daily_values: dict


class AllergensResponse(BaseModel):
    food: str
    allergens_found: List[str]


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/food/analyze", response_model=AnalysisResponse)
async def food_analyze(request: FoodAnalyzeRequest):
    try:
        result = analyze_food(request.food)
        return AnalysisResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/label/analyze", response_model=AnalysisResponse)
async def label_analyze(request: LabelAnalyzeRequest):
    try:
        result = analyze_label(request.label_text)
        return AnalysisResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/food/compare", response_model=AnalysisResponse)
async def food_compare(request: CompareFoodsRequest):
    try:
        result = compare_foods(request.foods)
        return AnalysisResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nutrition/daily-values", response_model=DailyValuesResponse)
async def nutrition_daily_values(request: DailyValuesRequest):
    try:
        result = calculate_daily_values(request.nutrients)
        return DailyValuesResponse(daily_values=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/food/check-allergens", response_model=AllergensResponse)
async def food_check_allergens(request: CheckAllergensRequest):
    try:
        allergens = check_allergens(request.food, request.allergen_list)
        return AllergensResponse(food=request.food, allergens_found=allergens)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reference/daily-values")
async def reference_daily_values():
    return {"daily_values": DV_REFERENCE}


@app.get("/reference/allergens")
async def reference_allergens():
    return {"allergens": COMMON_ALLERGENS}


@app.get("/disclaimer")
async def disclaimer():
    return {"disclaimer": DISCLAIMER}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
