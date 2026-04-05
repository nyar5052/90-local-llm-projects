"""FastAPI application for GDPR Compliance Checker."""

import dataclasses
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    ComplianceStatus,
    CHECK_TYPES,
    check_compliance,
    generate_checklist,
    build_article_checklist,
    map_data_flows,
    generate_dpo_recommendations,
    create_audit_entry,
)

app = FastAPI(
    title="GDPR Compliance Checker",
    description="AI-powered GDPR compliance checking, data flow mapping, and audit logging.",
    version="1.0.0",
)


# ── Request Models ───────────────────────────────────────────────────────────

class ComplianceCheckRequest(BaseModel):
    content: str = Field(..., description="Content to check for GDPR compliance")
    check_type: str = Field("all", description="Type of check to perform")


class ChecklistRequest(BaseModel):
    content: str = Field(..., description="Content to generate checklist for")


class DataFlowRequest(BaseModel):
    content: str = Field(..., description="Content to map data flows from")


class DPORecommendationsRequest(BaseModel):
    content: str = Field(..., description="Content to generate DPO recommendations for")


class AuditCreateRequest(BaseModel):
    action: str = Field(..., description="Action performed")
    article: str = Field(..., description="GDPR article reference")
    status: str = Field(..., description="Compliance status")
    details: str = Field("", description="Additional details")


# ── Response Models ──────────────────────────────────────────────────────────

class ChecklistItemResponse(BaseModel):
    article: str
    title: str
    description: str
    status: str
    findings: str
    recommendation: str


class DataFlowEntryResponse(BaseModel):
    data_type: str
    source: str
    destination: str
    purpose: str
    legal_basis: str
    retention: str
    cross_border: bool


class DPORecommendationResponse(BaseModel):
    priority: str
    article: str
    finding: str
    recommendation: str
    deadline: str


class AuditLogEntryResponse(BaseModel):
    timestamp: str
    action: str
    article: str
    status: str
    details: str
    auditor: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gdpr-compliance-checker"}


@app.post("/compliance/check")
async def api_check_compliance(request: ComplianceCheckRequest):
    if request.check_type not in CHECK_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid check type '{request.check_type}'. Must be one of: {CHECK_TYPES}",
        )
    try:
        result = check_compliance(request.content, request.check_type)
        return {"compliance_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/checklist")
async def api_generate_checklist(request: ChecklistRequest):
    try:
        result = generate_checklist(request.content)
        return {"checklist": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/article-checklist", response_model=List[ChecklistItemResponse])
async def api_build_article_checklist(request: ChecklistRequest):
    try:
        results = build_article_checklist(request.content)
        return [dataclasses.asdict(item) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/data-flows", response_model=List[DataFlowEntryResponse])
async def api_map_data_flows(request: DataFlowRequest):
    try:
        results = map_data_flows(request.content)
        return [dataclasses.asdict(entry) for entry in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/dpo-recommendations", response_model=List[DPORecommendationResponse])
async def api_dpo_recommendations(request: DPORecommendationsRequest):
    try:
        checklist = build_article_checklist(request.content)
        results = generate_dpo_recommendations(checklist)
        return [dataclasses.asdict(rec) for rec in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit/create", response_model=AuditLogEntryResponse)
async def api_create_audit_entry(request: AuditCreateRequest):
    try:
        entry = create_audit_entry(
            action=request.action,
            article=request.article,
            status=request.status,
            details=request.details,
        )
        return dataclasses.asdict(entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check-types")
async def api_get_check_types():
    return {"check_types": CHECK_TYPES}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
