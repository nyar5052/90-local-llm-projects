"""FastAPI REST API for Trend Analysis Tool."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from trend_analyzer.core import (
    extract_topics,
    analyze_sentiment_trends,
    track_topic_evolution,
    correlate_sentiment_topics,
    detect_emerging_topics,
    generate_trend_report,
    generate_alert_report,
)

app = FastAPI(
    title="Trend Analysis Tool API",
    description="REST API for Trend Analysis Tool",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class DocumentsRequest(BaseModel):
    documents: List[Dict[str, Any]] = Field(..., description="List of document records to analyse")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional analysis configuration")


class CorrelateRequest(BaseModel):
    topics: Dict[str, Any] = Field(..., description="Extracted topics output")
    sentiments: Dict[str, Any] = Field(..., description="Sentiment analysis output")


class TrendReportRequest(BaseModel):
    documents: List[Dict[str, Any]] = Field(..., description="Document records")
    topics: Dict[str, Any] = Field(..., description="Extracted topics output")
    sentiments: Dict[str, Any] = Field(..., description="Sentiment trends output")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional configuration")


class AlertReportRequest(BaseModel):
    emerging_topics: List[Dict[str, Any]] = Field(..., description="Detected emerging topics")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "trend-analysis-tool"}


@app.post("/extract-topics")
async def api_extract_topics(request: DocumentsRequest):
    try:
        result = extract_topics(request.documents, request.config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-sentiment-trends")
async def api_analyze_sentiment_trends(request: DocumentsRequest):
    try:
        result = analyze_sentiment_trends(request.documents, request.config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/track-topic-evolution")
async def api_track_topic_evolution(request: DocumentsRequest):
    try:
        result = track_topic_evolution(request.documents, request.config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/correlate-sentiment-topics")
async def api_correlate_sentiment_topics(request: CorrelateRequest):
    try:
        result = correlate_sentiment_topics(request.topics, request.sentiments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-emerging-topics")
async def api_detect_emerging_topics(request: DocumentsRequest):
    try:
        result = detect_emerging_topics(request.documents, request.config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-trend-report")
async def api_generate_trend_report(request: TrendReportRequest):
    try:
        result = generate_trend_report(
            request.documents, request.topics, request.sentiments, request.config
        )
        return {"report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-alert-report")
async def api_generate_alert_report(request: AlertReportRequest):
    try:
        result = generate_alert_report(request.emerging_topics)
        return {"report": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
