"""FastAPI REST API for Gift Recommendation Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gift_recommender.core import (
    generate_recommendations,
    get_gift_details,
    compare_prices,
    add_to_wishlist,
    get_wishlist,
    mark_purchased,
    add_occasion,
    get_upcoming_occasions,
    OCCASIONS,
    RELATIONSHIPS,
)

app = FastAPI(
    title="Gift Recommendation Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class RecommendRequest(BaseModel):
    """Request for gift recommendations."""
    occasion: str
    relationship: str
    budget: int
    interests: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None


class GiftDetailRequest(BaseModel):
    """Request for gift details."""
    gift_name: str
    budget: int


class WishlistAddRequest(BaseModel):
    """Add item to wishlist."""
    person: str
    gift: str
    price: str = ""
    occasion: str = ""
    notes: str = ""


class OccasionAddRequest(BaseModel):
    """Add an occasion to calendar."""
    person: str
    occasion: str
    date: str
    notes: str = ""


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/occasions")
async def list_occasions():
    """List available occasion types."""
    return {"occasions": OCCASIONS, "relationships": RELATIONSHIPS}


@app.post("/recommend")
async def recommend_gifts(request: RecommendRequest):
    """Get gift recommendations."""
    try:
        result = generate_recommendations(
            occasion=request.occasion,
            relationship=request.relationship,
            budget=request.budget,
            interests=request.interests,
            age=request.age,
            gender=request.gender,
        )
        return {"recommendations": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gift-details")
async def gift_details(request: GiftDetailRequest):
    """Get details about a specific gift."""
    try:
        result = get_gift_details(gift_name=request.gift_name, budget=request.budget)
        return {"details": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prices/{gift_name}")
async def price_comparison(gift_name: str):
    """Compare prices for a gift."""
    try:
        result = compare_prices(gift_name)
        return {"comparison": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wishlist/{person}")
async def get_wishlist_endpoint(person: str):
    """Get wishlist for a person."""
    try:
        items = get_wishlist(person)
        return {"wishlist": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/wishlist")
async def add_wishlist_item(request: WishlistAddRequest):
    """Add an item to a wishlist."""
    try:
        entry = add_to_wishlist(
            person=request.person,
            gift=request.gift,
            price=request.price,
            occasion=request.occasion,
            notes=request.notes,
        )
        return {"entry": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/wishlist/{person}/{item_id}/purchased")
async def mark_item_purchased(person: str, item_id: int):
    """Mark a wishlist item as purchased."""
    try:
        success = mark_purchased(person, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar")
async def add_calendar_occasion(request: OccasionAddRequest):
    """Add an occasion to the calendar."""
    try:
        entry = add_occasion(
            person=request.person,
            occasion=request.occasion,
            date=request.date,
            notes=request.notes,
        )
        return {"entry": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calendar/upcoming")
async def upcoming_occasions(days: int = 30):
    """Get upcoming occasions."""
    try:
        occasions = get_upcoming_occasions(days)
        return {"occasions": occasions, "count": len(occasions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
