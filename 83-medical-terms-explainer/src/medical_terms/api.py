"""Medical Terms Explainer API - AI-powered medical terminology explanations.

⚠️ MEDICAL DISCLAIMER: This tool is for educational and informational purposes only.
It does not constitute medical advice, diagnosis, or treatment. Always seek the advice
of a qualified healthcare provider.
"""

from enum import Enum
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .core import (
    DISCLAIMER,
    decode_abbreviation,
    explain_term,
    get_pronunciation,
    get_related_conditions,
    get_visual_aid,
    search_abbreviations,
)

MEDICAL_DISCLAIMER = (
    "⚠️ This API is for educational and informational purposes only. "
    "It does not constitute medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare provider."
)

app = FastAPI(
    title="Medical Terms Explainer",
    description=(
        "AI-powered medical terminology explanations, pronunciations, "
        "visual aids, and abbreviation lookups.\n\n"
        f"**{MEDICAL_DISCLAIMER}**"
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class DetailLevel(str, Enum):
    brief = "brief"
    standard = "standard"
    comprehensive = "comprehensive"


class ExplainTermRequest(BaseModel):
    term: str = Field(..., description="Medical term to explain.")
    detail: DetailLevel = Field(
        DetailLevel.standard,
        description="Level of detail: brief, standard, or comprehensive.",
    )


class ExplainTermResponse(BaseModel):
    term: str
    detail: str
    explanation: str


class PronunciationResponse(BaseModel):
    term: str
    pronunciation: Optional[str]


class VisualAidResponse(BaseModel):
    term: str
    visual_aid: Optional[str]


class RelatedConditionsResponse(BaseModel):
    term: str
    related_conditions: List[str]


class AbbreviationResponse(BaseModel):
    abbreviation: str
    meaning: Optional[str]


class AbbreviationSearchResponse(BaseModel):
    query: str
    results: Dict[str, str]


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
    return HealthResponse(status="healthy", service="medical-terms-explainer")


@app.post("/terms/explain", response_model=ExplainTermResponse, tags=["Terms"])
async def terms_explain(request: ExplainTermRequest):
    """Explain a medical term using AI at the requested detail level."""
    try:
        explanation = explain_term(term=request.term, detail=request.detail.value)
        return ExplainTermResponse(
            term=request.term,
            detail=request.detail.value,
            explanation=explanation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Term explanation failed: {e}")


@app.get("/terms/{term}/pronunciation", response_model=PronunciationResponse, tags=["Terms"])
async def terms_pronunciation(term: str):
    """Get the phonetic pronunciation of a medical term."""
    try:
        pronunciation = get_pronunciation(term)
        return PronunciationResponse(term=term, pronunciation=pronunciation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation lookup failed: {e}")


@app.get("/terms/{term}/visual-aid", response_model=VisualAidResponse, tags=["Terms"])
async def terms_visual_aid(term: str):
    """Get a visual aid description for a medical term."""
    try:
        visual_aid = get_visual_aid(term)
        return VisualAidResponse(term=term, visual_aid=visual_aid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual aid lookup failed: {e}")


@app.get("/terms/{term}/related-conditions", response_model=RelatedConditionsResponse, tags=["Terms"])
async def terms_related_conditions(term: str):
    """Get conditions related to a medical term."""
    try:
        conditions = get_related_conditions(term)
        return RelatedConditionsResponse(term=term, related_conditions=conditions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Related conditions lookup failed: {e}")


@app.get("/abbreviations/search", response_model=AbbreviationSearchResponse, tags=["Abbreviations"])
async def abbreviations_search(
    query: str = Query(..., description="Search query for medical abbreviations."),
):
    """Search for medical abbreviations matching the query."""
    try:
        results = search_abbreviations(query)
        return AbbreviationSearchResponse(query=query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Abbreviation search failed: {e}")


@app.get("/abbreviations/{abbrev}", response_model=AbbreviationResponse, tags=["Abbreviations"])
async def abbreviations_decode(abbrev: str):
    """Decode a medical abbreviation to its full meaning."""
    try:
        meaning = decode_abbreviation(abbrev)
        return AbbreviationResponse(abbreviation=abbrev, meaning=meaning)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Abbreviation decode failed: {e}")


@app.get("/disclaimer", response_model=DisclaimerResponse, tags=["Info"])
async def get_disclaimer():
    """Return the medical disclaimer for this service."""
    return DisclaimerResponse(disclaimer=DISCLAIMER)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
