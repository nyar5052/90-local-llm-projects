"""Symptom Checker Bot API - AI-powered symptom analysis and urgency assessment.

⚠️ MEDICAL DISCLAIMER: This tool is for informational purposes only and does not
constitute medical advice, diagnosis, or treatment. Always seek the advice of a
qualified healthcare provider with any questions regarding a medical condition.
"""

from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import DISCLAIMER, assess_urgency, check_symptoms, get_body_regions

MEDICAL_DISCLAIMER = (
    "⚠️ This API is for informational purposes only and does not constitute "
    "medical advice, diagnosis, or treatment. Always consult a qualified "
    "healthcare provider for medical concerns."
)

app = FastAPI(
    title="Symptom Checker Bot",
    description=(
        "AI-powered symptom analysis, urgency assessment, and body region mapping.\n\n"
        f"**{MEDICAL_DISCLAIMER}**"
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class SymptomsCheckRequest(BaseModel):
    symptoms: str = Field(..., description="Description of the symptoms to analyze.")
    conversation_history: Optional[List[dict]] = Field(
        None,
        description="Optional prior conversation history for context.",
    )


class SymptomsCheckResponse(BaseModel):
    analysis: str


class UrgencyRequest(BaseModel):
    symptoms_text: str = Field(..., description="Symptoms text to assess urgency for.")


class UrgencyResponse(BaseModel):
    urgency_score: int = Field(..., ge=1, le=10, description="Urgency score from 1 (low) to 10 (critical).")
    urgency_level: str
    explanation: str


class BodyRegionsRequest(BaseModel):
    symptoms_text: str = Field(..., description="Symptoms text to identify body regions for.")


class BodyRegionsResponse(BaseModel):
    body_regions: List[str]


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
    return HealthResponse(status="healthy", service="symptom-checker-bot")


@app.post("/symptoms/check", response_model=SymptomsCheckResponse, tags=["Symptoms"])
async def symptoms_check(request: SymptomsCheckRequest):
    """Analyze symptoms using AI and return a detailed assessment."""
    try:
        result = check_symptoms(
            symptoms=request.symptoms,
            conversation_history=request.conversation_history,
        )
        return SymptomsCheckResponse(analysis=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Symptom check failed: {e}")


@app.post("/symptoms/assess-urgency", response_model=UrgencyResponse, tags=["Symptoms"])
async def symptoms_assess_urgency(request: UrgencyRequest):
    """Assess the urgency of reported symptoms on a 1-10 scale."""
    try:
        urgency_score, urgency_level, explanation = assess_urgency(request.symptoms_text)
        return UrgencyResponse(
            urgency_score=urgency_score,
            urgency_level=urgency_level,
            explanation=explanation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Urgency assessment failed: {e}")


@app.post("/symptoms/body-regions", response_model=BodyRegionsResponse, tags=["Symptoms"])
async def symptoms_body_regions(request: BodyRegionsRequest):
    """Identify relevant body regions from the symptoms description."""
    try:
        regions = get_body_regions(request.symptoms_text)
        return BodyRegionsResponse(body_regions=regions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Body region detection failed: {e}")


@app.get("/disclaimer", response_model=DisclaimerResponse, tags=["Info"])
async def get_disclaimer():
    """Return the medical disclaimer for this service."""
    return DisclaimerResponse(disclaimer=DISCLAIMER)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
