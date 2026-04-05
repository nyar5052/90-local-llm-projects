"""FastAPI REST API for Sentiment Analysis Dashboard."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from sentiment_analyzer.core import (
    analyze_sentiment,
    batch_analyze,
    compute_sentiment_distribution,
    compute_trend_over_time,
    extract_word_cloud_data,
    compare_sources,
)

app = FastAPI(
    title="Sentiment Analysis Dashboard API",
    description="REST API for Sentiment Analysis Dashboard",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class SentimentRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")


class BatchAnalyzeRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze")
    source: str = Field("default", description="Source label for the texts")


class DistributionRequest(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Sentiment analysis results")


class TrendRequest(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Sentiment analysis results")
    window: int = Field(5, description="Rolling window size")


class WordCloudRequest(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Sentiment analysis results")


class CompareSourcesRequest(BaseModel):
    source_results: Dict[str, Any] = Field(
        ..., description="Mapping of source names to their sentiment results"
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sentiment-analysis-dashboard"}


@app.post("/analyze-sentiment")
async def api_analyze_sentiment(req: SentimentRequest):
    try:
        result = analyze_sentiment(text=req.text)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/batch-analyze")
async def api_batch_analyze(req: BatchAnalyzeRequest):
    try:
        result = batch_analyze(texts=req.texts, source=req.source)
        return {"result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/sentiment-distribution")
async def api_compute_sentiment_distribution(req: DistributionRequest):
    try:
        result = compute_sentiment_distribution(results=req.results)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/trend-over-time")
async def api_compute_trend_over_time(req: TrendRequest):
    try:
        result = compute_trend_over_time(results=req.results, window=req.window)
        return {"result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/word-cloud-data")
async def api_extract_word_cloud_data(req: WordCloudRequest):
    try:
        result = extract_word_cloud_data(results=req.results)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/compare-sources")
async def api_compare_sources(req: CompareSourcesRequest):
    try:
        result = compare_sources(source_results=req.source_results)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
