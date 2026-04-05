"""FastAPI REST API for Veterinary Advisor Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.vet_advisor.core import (
    get_response,
    check_symptoms,
    get_breed_advice,
    get_nutrition_advice,
    load_pet_profiles,
    add_pet_profile,
    get_pet_profile,
    record_symptom,
    get_symptom_history_for_pet,
    PET_TYPES,
)

app = FastAPI(
    title="Veterinary Advisor Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ChatRequest(BaseModel):
    """Chat with the vet advisor."""
    message: str
    history: list[dict] = []
    pet_profile: dict = {}


class SymptomCheckRequest(BaseModel):
    """Check pet symptoms."""
    symptoms: str
    pet_profile: dict = {}


class BreedAdviceRequest(BaseModel):
    """Get breed-specific advice."""
    pet_type: str
    breed: str


class PetProfileRequest(BaseModel):
    """Add a pet profile."""
    name: str
    pet_type: str
    breed: str = "unknown"
    age: str = "unknown"
    weight: str = "unknown"


class SymptomRecordRequest(BaseModel):
    """Record a symptom entry."""
    pet_name: str
    symptoms: str
    severity: str = "unknown"
    notes: str = ""


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/pet-types")
async def list_pet_types():
    """List supported pet types."""
    return {"pet_types": PET_TYPES}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with the veterinary advisor."""
    try:
        result = get_response(
            user_message=request.message,
            history=request.history,
            pet_profile=request.pet_profile,
        )
        return {"response": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-symptoms")
async def check_symptoms_endpoint(request: SymptomCheckRequest):
    """Check pet symptoms and get advice."""
    try:
        result = check_symptoms(
            symptoms=request.symptoms,
            pet_profile=request.pet_profile,
        )
        return {"assessment": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/breed-advice")
async def breed_advice_endpoint(request: BreedAdviceRequest):
    """Get breed-specific care advice."""
    try:
        result = get_breed_advice(pet_type=request.pet_type, breed=request.breed)
        return {"advice": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nutrition-advice")
async def nutrition_advice_endpoint(request: ChatRequest):
    """Get nutrition advice for a pet."""
    try:
        result = get_nutrition_advice(pet_profile=request.pet_profile)
        return {"advice": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pets")
async def list_pets():
    """List all pet profiles."""
    try:
        profiles = load_pet_profiles()
        return {"profiles": profiles, "count": len(profiles)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pets/{name}")
async def get_pet(name: str):
    """Get a specific pet profile."""
    try:
        profile = get_pet_profile(name)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Pet '{name}' not found")
        return {"profile": profile}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pets")
async def create_pet(request: PetProfileRequest):
    """Add a new pet profile."""
    try:
        profile = add_pet_profile(
            name=request.name,
            pet_type=request.pet_type,
            breed=request.breed,
            age=request.age,
            weight=request.weight,
        )
        return {"profile": profile, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/symptoms")
async def record_symptom_endpoint(request: SymptomRecordRequest):
    """Record a symptom for a pet."""
    try:
        entry = record_symptom(
            pet_name=request.pet_name,
            symptoms=request.symptoms,
            severity=request.severity,
            notes=request.notes,
        )
        return {"entry": entry, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/symptoms/{pet_name}")
async def get_symptom_history(pet_name: str):
    """Get symptom history for a pet."""
    try:
        history = get_symptom_history_for_pet(pet_name)
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
