"""FastAPI REST API for Support Ticket Classifier."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from ticket_classifier.core import (
    classify_ticket,
    generate_auto_response,
    route_to_team,
    compute_sla_deadlines,
    compute_analytics,
)

DEFAULT_CATEGORIES = ["billing", "technical", "account", "feature_request", "general"]

app = FastAPI(
    title="Support Ticket Classifier API",
    description="REST API for Support Ticket Classifier",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class ClassifyTicketRequest(BaseModel):
    ticket_text: str = Field(..., description="Raw text of the support ticket")
    categories: Optional[List[str]] = Field(
        None, description="Custom category list; defaults to built-in categories"
    )
    temperature: Optional[float] = Field(
        0.2, description="LLM sampling temperature", ge=0.0, le=2.0
    )


class AutoResponseRequest(BaseModel):
    ticket_text: str = Field(..., description="Raw text of the support ticket")
    classification: Dict[str, Any] = Field(
        ..., description="Classification result from /classify-ticket"
    )


class RouteToTeamRequest(BaseModel):
    classification: Dict[str, Any] = Field(
        ..., description="Classification result from /classify-ticket"
    )


class SlaDeadlinesRequest(BaseModel):
    classifications: List[Dict[str, Any]] = Field(
        ..., description="List of classification results"
    )


class AnalyticsRequest(BaseModel):
    classifications: List[Dict[str, Any]] = Field(
        ..., description="List of classification results"
    )
    categories: Optional[List[str]] = Field(
        None, description="Custom category list; defaults to built-in categories"
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "support-ticket-classifier"}


@app.get("/categories")
async def get_default_categories():
    """Return the default ticket categories."""
    return {"categories": DEFAULT_CATEGORIES}


@app.post("/classify-ticket")
async def api_classify_ticket(request: ClassifyTicketRequest):
    """Classify a support ticket into a category."""
    try:
        categories = request.categories if request.categories is not None else DEFAULT_CATEGORIES
        result = classify_ticket(
            request.ticket_text,
            categories,
            temperature=request.temperature,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-auto-response")
async def api_generate_auto_response(request: AutoResponseRequest):
    """Generate an automatic response for a classified ticket."""
    try:
        result = generate_auto_response(request.ticket_text, request.classification)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route-to-team")
async def api_route_to_team(request: RouteToTeamRequest):
    """Determine which team a ticket should be routed to."""
    try:
        result = route_to_team(request.classification)
        return {"team": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-sla-deadlines")
async def api_compute_sla_deadlines(request: SlaDeadlinesRequest):
    """Compute SLA deadlines for a batch of classified tickets."""
    try:
        result = compute_sla_deadlines(request.classifications)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-analytics")
async def api_compute_analytics(request: AnalyticsRequest):
    """Compute analytics across a batch of classified tickets."""
    try:
        categories = request.categories if request.categories is not None else DEFAULT_CATEGORIES
        result = compute_analytics(request.classifications, categories)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
