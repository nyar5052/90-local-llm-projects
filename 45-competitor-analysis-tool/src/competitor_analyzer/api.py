"""FastAPI REST API for Competitor Analysis Tool."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from competitor_analyzer.core import (
    generate_swot,
    generate_feature_matrix,
    generate_pricing_comparison,
    generate_market_positioning,
    generate_comparison,
    generate_action_items,
    generate_recommendations,
)

app = FastAPI(
    title="Competitor Analysis Tool API",
    description="REST API for Competitor Analysis Tool",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class CompetitorBaseRequest(BaseModel):
    company: str = Field(..., description="Name of the company to analyse")
    competitors: List[str] = Field(..., description="List of competitor names")
    industry: str = Field(..., description="Industry vertical")


class ActionItemsRequest(BaseModel):
    company: str = Field(..., description="Name of the company to analyse")
    competitors: List[str] = Field(..., description="List of competitor names")
    industry: str = Field(..., description="Industry vertical")
    swot: Dict[str, Any] = Field(..., description="Previously generated SWOT analysis")


class RecommendationsRequest(BaseModel):
    company: str = Field(..., description="Name of the company to analyse")
    competitors: List[str] = Field(..., description="List of competitor names")
    industry: str = Field(..., description="Industry vertical")
    swot: Dict[str, Any] = Field(..., description="Previously generated SWOT analysis")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "competitor-analysis-tool"}


@app.post("/generate-swot")
async def api_generate_swot(request: CompetitorBaseRequest):
    """Generate a SWOT analysis for the company against its competitors."""
    try:
        result = generate_swot(request.company, request.competitors, request.industry)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-feature-matrix")
async def api_generate_feature_matrix(request: CompetitorBaseRequest):
    """Generate a feature comparison matrix."""
    try:
        result = generate_feature_matrix(request.company, request.competitors, request.industry)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-pricing-comparison")
async def api_generate_pricing_comparison(request: CompetitorBaseRequest):
    """Generate a pricing comparison across competitors."""
    try:
        result = generate_pricing_comparison(request.company, request.competitors, request.industry)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-market-positioning")
async def api_generate_market_positioning(request: CompetitorBaseRequest):
    """Generate a market positioning analysis."""
    try:
        result = generate_market_positioning(request.company, request.competitors, request.industry)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-comparison")
async def api_generate_comparison(request: CompetitorBaseRequest):
    """Generate a full competitor comparison narrative."""
    try:
        result = generate_comparison(request.company, request.competitors, request.industry)
        return {"comparison": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-action-items")
async def api_generate_action_items(request: ActionItemsRequest):
    """Generate actionable items based on SWOT analysis."""
    try:
        result = generate_action_items(
            request.company, request.competitors, request.industry, request.swot
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-recommendations")
async def api_generate_recommendations(request: RecommendationsRequest):
    """Generate strategic recommendations based on SWOT analysis."""
    try:
        result = generate_recommendations(
            request.company, request.competitors, request.industry, request.swot
        )
        return {"recommendations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
