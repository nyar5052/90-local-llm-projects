"""FastAPI REST API for Stock Report Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from stock_reporter.core import (
    compute_metrics,
    compute_technical_indicators,
    assess_risk,
    compare_tickers,
    generate_report,
)

app = FastAPI(
    title="Stock Report Generator API",
    description="REST API for Stock Report Generator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class StockDataRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of stock data records")


class TechnicalIndicatorsRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of stock data records")


class AssessRiskRequest(BaseModel):
    metrics: Dict[str, Any] = Field(..., description="Computed stock metrics")
    indicators: Dict[str, Any] = Field(..., description="Computed technical indicators")


class CompareTickersRequest(BaseModel):
    datasets: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Mapping of ticker symbol to its data records"
    )


class GenerateReportRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of stock data records")
    metrics: Dict[str, Any] = Field(..., description="Computed stock metrics")
    ticker: str = Field(..., description="Stock ticker symbol")
    indicators: Optional[Dict[str, Any]] = Field(None, description="Technical indicators")
    risk: Optional[Dict[str, Any]] = Field(None, description="Risk assessment")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stock-report-generator"}


@app.post("/compute-metrics")
async def api_compute_metrics(request: StockDataRequest):
    """Compute financial metrics from stock data."""
    try:
        result = compute_metrics(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-technical-indicators")
async def api_compute_technical_indicators(request: TechnicalIndicatorsRequest):
    """Compute technical indicators from stock data."""
    try:
        result = compute_technical_indicators(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assess-risk")
async def api_assess_risk(request: AssessRiskRequest):
    """Assess risk based on metrics and technical indicators."""
    try:
        result = assess_risk(request.metrics, request.indicators)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare-tickers")
async def api_compare_tickers(request: CompareTickersRequest):
    """Compare multiple tickers side-by-side."""
    try:
        result = compare_tickers(request.datasets)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-report")
async def api_generate_report(request: GenerateReportRequest):
    """Generate a full stock report for a ticker."""
    try:
        result = generate_report(
            request.data,
            request.metrics,
            request.ticker,
            indicators=request.indicators,
            risk=request.risk,
        )
        return {"report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
