"""FastAPI REST API for News Digest Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.news_digest.core import (
    categorize_articles,
    generate_digest,
    analyze_sentiment,
)

app = FastAPI(
    title="News Digest Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class CategorizeRequest(BaseModel):
    """Request to categorize articles."""
    articles: list[dict]
    num_topics: int = 5


class DigestRequest(BaseModel):
    """Request to generate a news digest."""
    articles: list[dict]
    categorization: str
    digest_format: str = "daily"


class SentimentRequest(BaseModel):
    """Request to analyze sentiment."""
    articles: list[dict]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/categorize")
async def categorize_endpoint(request: CategorizeRequest):
    """Categorize news articles by topic."""
    try:
        result = categorize_articles(
            articles=request.articles,
            num_topics=request.num_topics,
        )
        return {"categorization": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/digest")
async def digest_endpoint(request: DigestRequest):
    """Generate a news digest."""
    try:
        result = generate_digest(
            articles=request.articles,
            categorization=request.categorization,
            digest_format=request.digest_format,
        )
        return {"digest": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment")
async def sentiment_endpoint(request: SentimentRequest):
    """Analyze sentiment of news articles."""
    try:
        result = analyze_sentiment(articles=request.articles)
        return {"sentiment_analysis": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
