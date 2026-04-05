"""FastAPI application for Log File Analyzer."""

import dataclasses
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    LogLevel,
    FOCUS_AREAS,
    analyze_logs,
    cluster_errors,
    match_patterns,
    detect_anomalies,
    cluster_errors_local,
    build_timeline,
    evaluate_alert_rules,
)

app = FastAPI(
    title="Log File Analyzer",
    description="AI-powered log analysis, pattern matching, anomaly detection, and alert evaluation.",
    version="1.0.0",
)


# ── Request Models ───────────────────────────────────────────────────────────

class AnalyzeLogsRequest(BaseModel):
    log_content: str = Field(..., description="Raw log content to analyze")
    focus: str = Field(..., description="Focus area for analysis")
    context: Optional[str] = Field(None, description="Additional context for analysis")


class LogContentRequest(BaseModel):
    log_content: str = Field(..., description="Raw log content to process")


class EvaluateAlertsRequest(BaseModel):
    log_content: str = Field(..., description="Raw log content to evaluate")
    rules: Optional[Dict] = Field(None, description="Custom alert rules to evaluate against")


# ── Response Models ──────────────────────────────────────────────────────────

class PatternMatchResponse(BaseModel):
    pattern_name: str
    category: str
    severity: str
    description: str
    line_number: int
    line_text: str
    timestamp: Optional[str] = None


class AnomalyResultResponse(BaseModel):
    anomaly_type: str
    description: str
    severity: str
    evidence: str
    score: float


class ErrorClusterResponse(BaseModel):
    cluster_id: int
    pattern: str
    count: int
    severity: str
    first_seen: str
    last_seen: str
    example_lines: list


class TimelineEventResponse(BaseModel):
    timestamp: str
    level: str
    message: str
    line_number: int


class AlertRuleResponse(BaseModel):
    name: str
    condition: str
    threshold: float
    current_value: float
    triggered: bool


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "log-file-analyzer"}


@app.post("/logs/analyze")
async def api_analyze_logs(request: AnalyzeLogsRequest):
    if request.focus not in FOCUS_AREAS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid focus area '{request.focus}'. Must be one of: {FOCUS_AREAS}",
        )
    try:
        result = analyze_logs(
            log_content=request.log_content,
            focus=request.focus,
            context=request.context,
        )
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/cluster-errors")
async def api_cluster_errors(request: LogContentRequest):
    try:
        result = cluster_errors(request.log_content)
        return {"clusters": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/match-patterns", response_model=List[PatternMatchResponse])
async def api_match_patterns(request: LogContentRequest):
    try:
        results = match_patterns(request.log_content)
        return [dataclasses.asdict(m) for m in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/detect-anomalies", response_model=List[AnomalyResultResponse])
async def api_detect_anomalies(request: LogContentRequest):
    try:
        results = detect_anomalies(request.log_content)
        return [dataclasses.asdict(a) for a in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/cluster-errors-local", response_model=List[ErrorClusterResponse])
async def api_cluster_errors_local(request: LogContentRequest):
    try:
        results = cluster_errors_local(request.log_content)
        return [dataclasses.asdict(c) for c in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/timeline", response_model=List[TimelineEventResponse])
async def api_build_timeline(request: LogContentRequest):
    try:
        results = build_timeline(request.log_content)
        return [dataclasses.asdict(e) for e in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/evaluate-alerts", response_model=List[AlertRuleResponse])
async def api_evaluate_alerts(request: EvaluateAlertsRequest):
    try:
        results = evaluate_alert_rules(request.log_content, rules=request.rules)
        return [dataclasses.asdict(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/focus-areas")
async def api_get_focus_areas():
    return {"focus_areas": FOCUS_AREAS}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
