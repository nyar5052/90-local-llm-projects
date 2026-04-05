"""FastAPI REST API for Code Complexity Analyzer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.llm_client import chat
from src.complexity_analyzer.core import (
    analyze_file,
    count_lines,
    calculate_halstead_volume,
    analyze_dependencies,
    get_complexity_rating,
    get_mi_rating,
    get_llm_suggestions,
    load_trends,
    save_trend,
)

app = FastAPI(
    title="Code Complexity Analyzer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class AnalyzeFileRequest(BaseModel):
    """Request to analyze a file."""
    filepath: str


class SourceCodeRequest(BaseModel):
    """Request with source code text."""
    source: str


class SuggestionsRequest(BaseModel):
    """Request for LLM improvement suggestions."""
    filepath: str
    metrics: dict


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/analyze")
async def analyze_endpoint(request: AnalyzeFileRequest):
    """Analyze complexity of a Python file."""
    try:
        metrics = analyze_file(filepath=request.filepath)
        return {"metrics": metrics, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lines")
async def lines_endpoint(request: SourceCodeRequest):
    """Count lines of code."""
    try:
        result = count_lines(source=request.source)
        return {"line_counts": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/halstead")
async def halstead_endpoint(request: SourceCodeRequest):
    """Calculate Halstead volume metric."""
    try:
        volume = calculate_halstead_volume(source=request.source)
        return {"halstead_volume": volume, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dependencies")
async def dependencies_endpoint(request: SourceCodeRequest):
    """Analyze import dependencies."""
    try:
        deps = analyze_dependencies(source=request.source)
        return {"dependencies": deps, "count": len(deps)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggestions")
async def suggestions_endpoint(request: SuggestionsRequest):
    """Get LLM-powered improvement suggestions."""
    try:
        result = get_llm_suggestions(
            filepath=request.filepath,
            metrics=request.metrics,
            chat_fn=chat,
        )
        return {"suggestions": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trends")
async def trends_endpoint():
    """Get complexity trends over time."""
    try:
        trends = load_trends()
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trends")
async def save_trend_endpoint(request: SuggestionsRequest):
    """Save complexity metrics as a trend data point."""
    try:
        save_trend(filepath=request.filepath, metrics=request.metrics)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8029)
