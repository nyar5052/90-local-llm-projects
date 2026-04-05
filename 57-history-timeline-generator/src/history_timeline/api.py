"""FastAPI REST API for History Timeline Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dataclasses import asdict
import uvicorn

from history_timeline.core import (
    generate_timeline,
    get_figure_profiles,
    get_cause_effect_chains,
    check_service,
)

app = FastAPI(
    title="History Timeline Generator API",
    description="REST API for History Timeline Generator",
    version="1.0.0",
)


# --- Request Models ---


class GenerateTimelineRequest(BaseModel):
    topic: str = Field(..., description="Historical topic for the timeline")
    detail: str = Field("medium", description="Detail level: low, medium, or high")
    start_year: str = Field("", description="Optional start year filter")
    end_year: str = Field("", description="Optional end year filter")


class FigureProfilesRequest(BaseModel):
    topic: str = Field(..., description="Historical topic")
    figures: Optional[List[str]] = Field(None, description="Specific figures to profile")


class CauseEffectRequest(BaseModel):
    topic: str = Field(..., description="Historical topic for cause-effect analysis")


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "history-timeline-generator"}


@app.get("/service-check")
async def api_check_service():
    try:
        result = check_service()
        return {"available": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/timeline")
async def api_generate_timeline(request: GenerateTimelineRequest):
    try:
        result = generate_timeline(
            topic=request.topic,
            detail=request.detail,
            start_year=request.start_year,
            end_year=request.end_year,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/figure-profiles")
async def api_get_figure_profiles(request: FigureProfilesRequest):
    try:
        result = get_figure_profiles(
            topic=request.topic,
            figures=request.figures,
        )
        return [asdict(profile) for profile in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cause-effect")
async def api_get_cause_effect_chains(request: CauseEffectRequest):
    try:
        result = get_cause_effect_chains(topic=request.topic)
        return [asdict(chain) for chain in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
