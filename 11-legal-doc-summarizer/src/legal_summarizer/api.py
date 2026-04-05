"""FastAPI REST API for Legal Document Summarizer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.legal_summarizer.core import (
    summarize_document,
    extract_clauses,
    score_risks,
    generate_export_markdown,
)

app = FastAPI(
    title="Legal Document Summarizer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class SummarizeRequest(BaseModel):
    """Request to summarize a legal document."""
    text: str
    output_format: str = "bullet"


class ClauseRequest(BaseModel):
    """Request to extract clauses."""
    text: str


class RiskRequest(BaseModel):
    """Request to score risks."""
    text: str


class ExportRequest(BaseModel):
    """Request to generate export markdown."""
    summary: str
    clauses: Optional[str] = None
    risk_analysis: Optional[str] = None
    filepath: str = ""


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/summarize")
async def summarize_endpoint(request: SummarizeRequest):
    """Summarize a legal document."""
    try:
        result = summarize_document(
            text=request.text,
            output_format=request.output_format,
        )
        return {"summary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract-clauses")
async def extract_clauses_endpoint(request: ClauseRequest):
    """Extract clauses from a legal document."""
    try:
        result = extract_clauses(text=request.text)
        return {"clauses": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score-risks")
async def score_risks_endpoint(request: RiskRequest):
    """Score risks in a legal document."""
    try:
        result = score_risks(text=request.text)
        return {"risk_analysis": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export")
async def export_endpoint(request: ExportRequest):
    """Generate a Markdown export of the analysis."""
    try:
        result = generate_export_markdown(
            summary=request.summary,
            clauses=request.clauses,
            risk_analysis=request.risk_analysis,
            filepath=request.filepath,
        )
        return {"markdown": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
