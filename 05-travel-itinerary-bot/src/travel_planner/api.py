"""FastAPI REST API for Travel Itinerary Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.travel_planner.core import (
    generate_itinerary,
    generate_multi_destination_itinerary,
    get_place_details,
    generate_budget_breakdown,
    generate_packing_list,
    BUDGETS,
)

app = FastAPI(
    title="Travel Itinerary Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ItineraryRequest(BaseModel):
    """Request to generate a travel itinerary."""
    destination: str
    days: int = 5
    budget: str = "moderate"
    interests: Optional[str] = None
    travelers: int = 1
    model: str = "gemma4"
    temperature: float = 0.7


class MultiDestRequest(BaseModel):
    """Request for multi-destination itinerary."""
    destinations: list[str]
    days_per_dest: int = 3
    budget: str = "moderate"
    interests: Optional[str] = None
    travelers: int = 1
    model: str = "gemma4"
    temperature: float = 0.7


class PlaceRequest(BaseModel):
    """Request for place details."""
    place: str
    destination: str
    model: str = "gemma4"
    temperature: float = 0.7


class BudgetRequest(BaseModel):
    """Request for budget breakdown."""
    itinerary: str
    budget: str = "moderate"
    travelers: int = 1
    model: str = "gemma4"


class PackingListRequest(BaseModel):
    """Request for packing list."""
    destination: str
    days: int = 5
    interests: Optional[str] = None
    model: str = "gemma4"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/budgets")
async def list_budgets():
    """List available budget levels."""
    return {"budgets": BUDGETS}


@app.post("/itinerary")
async def create_itinerary(request: ItineraryRequest):
    """Generate a travel itinerary."""
    try:
        result = generate_itinerary(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            interests=request.interests,
            travelers=request.travelers,
            model=request.model,
            temperature=request.temperature,
        )
        return {"itinerary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/itinerary/multi")
async def create_multi_itinerary(request: MultiDestRequest):
    """Generate a multi-destination itinerary."""
    try:
        result = generate_multi_destination_itinerary(
            destinations=request.destinations,
            days_per_dest=request.days_per_dest,
            budget=request.budget,
            interests=request.interests,
            travelers=request.travelers,
            model=request.model,
            temperature=request.temperature,
        )
        return {"itinerary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/place")
async def place_details(request: PlaceRequest):
    """Get details about a specific place."""
    try:
        result = get_place_details(
            place=request.place,
            destination=request.destination,
            model=request.model,
            temperature=request.temperature,
        )
        return {"details": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/budget")
async def budget_breakdown(request: BudgetRequest):
    """Generate a budget breakdown for an itinerary."""
    try:
        result = generate_budget_breakdown(
            itinerary=request.itinerary,
            budget=request.budget,
            travelers=request.travelers,
            model=request.model,
        )
        return {"breakdown": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/packing-list")
async def packing_list(request: PackingListRequest):
    """Generate a packing list for a destination."""
    try:
        result = generate_packing_list(
            destination=request.destination,
            days=request.days,
            interests=request.interests,
            model=request.model,
        )
        return {"packing_list": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
