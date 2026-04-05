"""FastAPI REST API for Survey Response Analyzer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from survey_analyzer.core import (
    extract_themes,
    cluster_themes,
    highlight_verbatims,
    generate_recommendations,
    generate_insights,
)

app = FastAPI(
    title="Survey Response Analyzer API",
    description="REST API for Survey Response Analyzer",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class ResponsesRequest(BaseModel):
    responses: List[str] = Field(..., description="List of survey response texts")


class ThemesRequest(BaseModel):
    themes: Dict[str, Any] = Field(..., description="Extracted themes dictionary")


class ClusterThemesRequest(BaseModel):
    themes: Dict[str, Any] = Field(..., description="Extracted themes dictionary")


class HighlightVerbatimsRequest(BaseModel):
    responses: List[str] = Field(..., description="List of survey response texts")
    themes: Dict[str, Any] = Field(..., description="Extracted themes dictionary")


class RecommendationsRequest(BaseModel):
    responses: List[str] = Field(..., description="List of survey response texts")
    themes: Dict[str, Any] = Field(..., description="Extracted themes dictionary")


class InsightsRequest(BaseModel):
    responses: List[str] = Field(..., description="List of survey response texts")
    themes: Dict[str, Any] = Field(..., description="Extracted themes dictionary")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "survey-response-analyzer"}


@app.post("/extract-themes")
async def api_extract_themes(request: ResponsesRequest):
    """Extract themes from a list of survey responses."""
    try:
        result = extract_themes(request.responses)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cluster-themes")
async def api_cluster_themes(request: ClusterThemesRequest):
    """Cluster extracted themes into groups."""
    try:
        result = cluster_themes(request.themes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/highlight-verbatims")
async def api_highlight_verbatims(request: HighlightVerbatimsRequest):
    """Highlight verbatim quotes from responses that match themes."""
    try:
        result = highlight_verbatims(request.responses, request.themes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-recommendations")
async def api_generate_recommendations(request: RecommendationsRequest):
    """Generate recommendations based on survey responses and themes."""
    try:
        result = generate_recommendations(request.responses, request.themes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-insights")
async def api_generate_insights(request: InsightsRequest):
    """Generate a narrative insights summary from responses and themes."""
    try:
        result = generate_insights(request.responses, request.themes)
        return {"insights": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
