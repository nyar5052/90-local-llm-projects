"""FastAPI application for Incident Report Generator."""

import dataclasses
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    Priority,
    INCIDENT_TYPES,
    generate_report,
    generate_timeline,
    build_timeline,
    calculate_impact,
    generate_lessons_learned,
    get_template,
)

app = FastAPI(
    title="Incident Report Generator",
    description="AI-powered incident report generation with timeline building and impact assessment.",
    version="1.0.0",
)


# ── Request Models ───────────────────────────────────────────────────────────

class GenerateReportRequest(BaseModel):
    logs: str = Field(..., description="Raw log data for the incident")
    incident_type: str = Field(..., description="Type of incident")
    title: Optional[str] = Field(None, description="Optional report title")
    priority: str = Field("P2", description="Priority level (P1, P2, P3, P4)")


class TimelineRequest(BaseModel):
    logs: str = Field(..., description="Raw log data to build timeline from")


class ImpactRequest(BaseModel):
    logs: str = Field(..., description="Raw log data for the incident")
    affected_users: int = Field(0, description="Number of affected users")
    downtime_minutes: int = Field(0, description="Duration of downtime in minutes")


class LessonsLearnedRequest(BaseModel):
    logs: str = Field(..., description="Raw log data for the incident")
    incident_type: str = Field(..., description="Type of incident")


# ── Response Models ──────────────────────────────────────────────────────────

class TimelineEntryResponse(BaseModel):
    timestamp: str
    event: str
    severity: str
    actor: str
    system: str


class ImpactAssessmentResponse(BaseModel):
    affected_users: int
    affected_systems: list
    data_compromised: bool
    revenue_impact: float
    downtime_minutes: int
    severity_score: float
    severity_label: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "incident-report-generator"}


@app.post("/reports/generate")
async def api_generate_report(request: GenerateReportRequest):
    if request.incident_type not in INCIDENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid incident type '{request.incident_type}'. Must be one of: {INCIDENT_TYPES}",
        )
    try:
        priority = Priority[request.priority]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority '{request.priority}'. Must be one of: P1, P2, P3, P4",
        )
    try:
        result = generate_report(
            logs=request.logs,
            incident_type=request.incident_type,
            title=request.title,
            priority=priority,
        )
        return {"report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reports/timeline")
async def api_generate_timeline(request: TimelineRequest):
    try:
        result = generate_timeline(request.logs)
        return {"timeline": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reports/timeline/structured", response_model=List[TimelineEntryResponse])
async def api_build_timeline(request: TimelineRequest):
    try:
        results = build_timeline(request.logs)
        return [dataclasses.asdict(entry) for entry in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reports/impact", response_model=ImpactAssessmentResponse)
async def api_calculate_impact(request: ImpactRequest):
    try:
        result = calculate_impact(
            logs=request.logs,
            affected_users=request.affected_users,
            downtime_minutes=request.downtime_minutes,
        )
        data = dataclasses.asdict(result)
        data["severity_label"] = result.severity_label
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reports/lessons-learned")
async def api_lessons_learned(request: LessonsLearnedRequest):
    if request.incident_type not in INCIDENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid incident type '{request.incident_type}'. Must be one of: {INCIDENT_TYPES}",
        )
    try:
        result = generate_lessons_learned(request.logs, request.incident_type)
        return {"lessons_learned": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates/{priority}")
async def api_get_template(priority: str):
    try:
        priority_enum = Priority[priority]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority '{priority}'. Must be one of: P1, P2, P3, P4",
        )
    try:
        template = get_template(priority_enum)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/incident-types")
async def api_get_incident_types():
    return {"incident_types": INCIDENT_TYPES}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
