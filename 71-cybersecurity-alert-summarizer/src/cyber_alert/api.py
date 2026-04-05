"""FastAPI application for Cybersecurity Alert Summarizer."""

import dataclasses
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    Severity,
    summarize_alert,
    prioritize_alerts,
    extract_iocs,
    lookup_cve,
    extract_cves,
    calculate_threat_score,
    correlate_alerts,
)

app = FastAPI(
    title="Cybersecurity Alert Summarizer",
    description="AI-powered cybersecurity alert analysis, IOC extraction, and threat scoring.",
    version="1.0.0",
)


# ── Request Models ───────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    alert_text: str = Field(..., description="Raw alert text to summarize")
    severity_filter: str = Field("all", description="Filter by severity level")


class PrioritizeRequest(BaseModel):
    alert_text: str = Field(..., description="Raw alert text to prioritize")


class ExtractIOCsRequest(BaseModel):
    text: str = Field(..., description="Text to extract IOCs from")


class ExtractCVEsRequest(BaseModel):
    text: str = Field(..., description="Text to extract CVEs from")


class ThreatScoreRequest(BaseModel):
    alert_text: str = Field(..., description="Alert text to score")


class CorrelateRequest(BaseModel):
    alerts: List[str] = Field(..., description="List of alert texts to correlate")


# ── Response Models ──────────────────────────────────────────────────────────

class IOCResultResponse(BaseModel):
    ioc_type: str
    value: str
    context: str


class CVEInfoResponse(BaseModel):
    cve_id: str
    description: str
    cvss: float
    severity: str
    affected: str
    vector: str
    found_in_db: bool


class ThreatScoreResponse(BaseModel):
    overall_score: float
    severity: str
    confidence: float
    factors: list


class AlertCorrelationResponse(BaseModel):
    alert_ids: list
    correlation_type: str
    confidence: float
    description: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cybersecurity-alert-summarizer"}


@app.post("/alerts/summarize")
async def api_summarize_alert(request: SummarizeRequest):
    try:
        result = summarize_alert(request.alert_text, severity_filter=request.severity_filter)
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/prioritize")
async def api_prioritize_alerts(request: PrioritizeRequest):
    try:
        result = prioritize_alerts(request.alert_text)
        return {"prioritization": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/extract-iocs", response_model=List[IOCResultResponse])
async def api_extract_iocs(request: ExtractIOCsRequest):
    try:
        results = extract_iocs(request.text)
        return [dataclasses.asdict(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cve/{cve_id}", response_model=CVEInfoResponse)
async def api_lookup_cve(cve_id: str):
    try:
        result = lookup_cve(cve_id)
        return dataclasses.asdict(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/extract-cves", response_model=List[CVEInfoResponse])
async def api_extract_cves(request: ExtractCVEsRequest):
    try:
        results = extract_cves(request.text)
        return [dataclasses.asdict(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/threat-score", response_model=ThreatScoreResponse)
async def api_threat_score(request: ThreatScoreRequest):
    try:
        result = calculate_threat_score(request.alert_text)
        return dataclasses.asdict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/correlate", response_model=List[AlertCorrelationResponse])
async def api_correlate_alerts(request: CorrelateRequest):
    try:
        results = correlate_alerts(request.alerts)
        return [dataclasses.asdict(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
