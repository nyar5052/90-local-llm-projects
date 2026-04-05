"""FastAPI REST API for Stack Trace Explainer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.stack_explainer.core import (
    explain_trace,
    generate_fix_code,
    find_similar_errors,
)

app = FastAPI(
    title="Stack Trace Explainer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class TraceRequest(BaseModel):
    """Request with a stack trace."""
    trace: str
    language: str = ""


class FixRequest(BaseModel):
    """Request to generate a fix."""
    trace: str
    explanation: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/explain")
async def explain_endpoint(request: TraceRequest):
    """Explain a stack trace."""
    try:
        result = explain_trace(trace=request.trace, language=request.language)
        return {"explanation": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fix")
async def fix_endpoint(request: FixRequest):
    """Generate fix code for a stack trace."""
    try:
        result = generate_fix_code(
            trace=request.trace,
            explanation=request.explanation,
        )
        return {"fix_code": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similar")
async def similar_endpoint(request: TraceRequest):
    """Find similar errors for a stack trace."""
    try:
        result = find_similar_errors(trace=request.trace)
        return {"similar_errors": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8022)
