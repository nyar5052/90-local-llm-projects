"""FastAPI REST API for Medical Literature Summarizer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.medical_summarizer.core import (
    summarize_paper,
    extract_pico,
    rate_evidence_quality,
    format_citation,
)

app = FastAPI(
    title="Medical Literature Summarizer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class PaperRequest(BaseModel):
    """Request with paper text."""
    paper_text: str
    detail_level: str = "standard"


class CitationRequest(BaseModel):
    """Request for citation formatting."""
    paper_text: str
    style: str = "APA"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/summarize")
async def summarize_endpoint(request: PaperRequest):
    """Summarize a medical paper."""
    try:
        result = summarize_paper(
            paper_text=request.paper_text,
            detail_level=request.detail_level,
        )
        return {"summary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pico")
async def pico_endpoint(request: PaperRequest):
    """Extract PICO framework from a medical paper."""
    try:
        result = extract_pico(paper_text=request.paper_text)
        return {"pico": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evidence-quality")
async def evidence_quality_endpoint(request: PaperRequest):
    """Rate the evidence quality of a medical paper."""
    try:
        result = rate_evidence_quality(paper_text=request.paper_text)
        return {"evidence_quality": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/citation")
async def citation_endpoint(request: CitationRequest):
    """Format a citation for a medical paper."""
    try:
        result = format_citation(
            paper_text=request.paper_text,
            style=request.style,
        )
        return {"citation": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)
