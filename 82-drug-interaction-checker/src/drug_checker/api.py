"""Drug Interaction Checker API - AI-powered medication interaction analysis.

⚠️ MEDICAL DISCLAIMER: This tool is for informational purposes only and does not
constitute medical advice, diagnosis, or treatment. Always consult a pharmacist or
healthcare provider before making changes to your medication regimen.
"""

from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    DISCLAIMER,
    check_interactions,
    classify_severity,
    get_alternatives,
    get_dosage_notes,
    get_food_interactions,
    parse_medications,
)

MEDICAL_DISCLAIMER = (
    "⚠️ This API is for informational purposes only and does not constitute "
    "medical advice. Always consult a pharmacist or healthcare provider before "
    "making changes to your medication regimen."
)

app = FastAPI(
    title="Drug Interaction Checker",
    description=(
        "AI-powered medication interaction checking, food interactions, dosage "
        "notes, and severity classification.\n\n"
        f"**{MEDICAL_DISCLAIMER}**"
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class InteractionsCheckRequest(BaseModel):
    medications: List[str] = Field(..., min_length=1, description="List of medication names to check for interactions.")


class InteractionsCheckResponse(BaseModel):
    interactions: str


class ParseMedicationsRequest(BaseModel):
    medications_str: str = Field(..., description="Raw string of medications to parse into a list.")


class ParseMedicationsResponse(BaseModel):
    medications: List[str]


class FoodInteractionsRequest(BaseModel):
    medication: str = Field(..., description="Medication name to look up food interactions for.")


class FoodInteractionsResponse(BaseModel):
    medication: str
    food_interactions: List[str]


class DosageNotesRequest(BaseModel):
    medication: str = Field(..., description="Medication name to retrieve dosage notes for.")


class DosageNotesResponse(BaseModel):
    medication: str
    dosage_notes: Optional[str]


class AlternativesRequest(BaseModel):
    medication: str = Field(..., description="Medication name to find alternatives for.")


class AlternativesResponse(BaseModel):
    medication: str
    alternatives: List[str]


class SeverityRequest(BaseModel):
    interaction_text: str = Field(..., description="Interaction description text to classify severity for.")


class SeverityResponse(BaseModel):
    severity: str


class DisclaimerResponse(BaseModel):
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    service: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    return HealthResponse(status="healthy", service="drug-interaction-checker")


@app.post("/interactions/check", response_model=InteractionsCheckResponse, tags=["Interactions"])
async def interactions_check(request: InteractionsCheckRequest):
    """Check for interactions between a list of medications using AI."""
    try:
        result = check_interactions(request.medications)
        return InteractionsCheckResponse(interactions=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction check failed: {e}")


@app.post("/medications/parse", response_model=ParseMedicationsResponse, tags=["Medications"])
async def medications_parse(request: ParseMedicationsRequest):
    """Parse a raw medications string into a structured list."""
    try:
        meds = parse_medications(request.medications_str)
        return ParseMedicationsResponse(medications=meds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medication parsing failed: {e}")


@app.post("/medications/food-interactions", response_model=FoodInteractionsResponse, tags=["Medications"])
async def medications_food_interactions(request: FoodInteractionsRequest):
    """Get known food interactions for a specific medication."""
    try:
        interactions = get_food_interactions(request.medication)
        return FoodInteractionsResponse(
            medication=request.medication,
            food_interactions=interactions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Food interaction lookup failed: {e}")


@app.post("/medications/dosage-notes", response_model=DosageNotesResponse, tags=["Medications"])
async def medications_dosage_notes(request: DosageNotesRequest):
    """Get dosage notes for a specific medication."""
    try:
        notes = get_dosage_notes(request.medication)
        return DosageNotesResponse(
            medication=request.medication,
            dosage_notes=notes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosage notes lookup failed: {e}")


@app.post("/medications/alternatives", response_model=AlternativesResponse, tags=["Medications"])
async def medications_alternatives(request: AlternativesRequest):
    """Get alternative medications for a given medication."""
    try:
        alts = get_alternatives(request.medication)
        return AlternativesResponse(
            medication=request.medication,
            alternatives=alts,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alternatives lookup failed: {e}")


@app.post("/interactions/classify-severity", response_model=SeverityResponse, tags=["Interactions"])
async def interactions_classify_severity(request: SeverityRequest):
    """Classify the severity level of a drug interaction description."""
    try:
        severity = classify_severity(request.interaction_text)
        return SeverityResponse(severity=severity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Severity classification failed: {e}")


@app.get("/disclaimer", response_model=DisclaimerResponse, tags=["Info"])
async def get_disclaimer():
    """Return the medical disclaimer for this service."""
    return DisclaimerResponse(disclaimer=DISCLAIMER)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
