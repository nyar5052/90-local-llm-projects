"""FastAPI REST API for KPI Dashboard Reporter."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from kpi_reporter.core import (
    compute_kpi_trends,
    track_goals,
    detect_anomalies,
    compute_moving_average,
    generate_kpi_report,
    generate_executive_summary,
    generate_alert_summary,
    compute_analytics,
)

app = FastAPI(
    title="KPI Dashboard Reporter API",
    description="REST API for KPI Dashboard Reporter",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class KPITrendsRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of KPI data records")


class TrackGoalsRequest(BaseModel):
    trends: Dict[str, Any] = Field(..., description="KPI trends output")
    targets: Dict[str, Any] = Field(..., description="Goal targets to track against")


class DetectAnomaliesRequest(BaseModel):
    trends: Dict[str, Any] = Field(..., description="KPI trends output")
    threshold: float = Field(2.0, description="Standard-deviation threshold for anomaly detection")


class MovingAverageRequest(BaseModel):
    values: List[float] = Field(..., description="Numeric values to smooth")
    window: int = Field(3, description="Window size for moving average")


class KPIReportRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Raw KPI data records")
    trends: Dict[str, Any] = Field(..., description="Pre-computed KPI trends")
    period: str = Field(..., description="Reporting period label (e.g. 'Q1 2024')")


class ExecutiveSummaryRequest(BaseModel):
    trends: Dict[str, Any] = Field(..., description="KPI trends output")
    goals: Dict[str, Any] = Field(..., description="Goal-tracking results")
    anomalies: List[Dict[str, Any]] = Field(..., description="Detected anomalies")


class AlertSummaryRequest(BaseModel):
    trends: Dict[str, Any] = Field(..., description="KPI trends output")
    threshold_pct: float = Field(10.0, description="Percentage threshold for alerts")


class AnalyticsRequest(BaseModel):
    trends: Dict[str, Any] = Field(..., description="KPI trends output")
    goals: Dict[str, Any] = Field(..., description="Goal-tracking results")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kpi-dashboard-reporter"}


@app.post("/compute-kpi-trends")
async def api_compute_kpi_trends(request: KPITrendsRequest):
    try:
        result = compute_kpi_trends(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/track-goals")
async def api_track_goals(request: TrackGoalsRequest):
    try:
        result = track_goals(request.trends, request.targets)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-anomalies")
async def api_detect_anomalies(request: DetectAnomaliesRequest):
    try:
        result = detect_anomalies(request.trends, request.threshold)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-moving-average")
async def api_compute_moving_average(request: MovingAverageRequest):
    try:
        result = compute_moving_average(request.values, request.window)
        return {"values": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-kpi-report")
async def api_generate_kpi_report(request: KPIReportRequest):
    try:
        result = generate_kpi_report(request.data, request.trends, request.period)
        return {"report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-executive-summary")
async def api_generate_executive_summary(request: ExecutiveSummaryRequest):
    try:
        result = generate_executive_summary(request.trends, request.goals, request.anomalies)
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-alert-summary")
async def api_generate_alert_summary(request: AlertSummaryRequest):
    try:
        result = generate_alert_summary(request.trends, request.threshold_pct)
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-analytics")
async def api_compute_analytics(request: AnalyticsRequest):
    try:
        result = compute_analytics(request.trends, request.goals)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
