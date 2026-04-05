"""FastAPI REST API for Resume Analyzer."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.resume_analyzer.core import (
    analyze_resume,
    score_against_jd,
    simulate_ats_score,
    generate_improvement_suggestions,
)

app = FastAPI(
    title="Resume Analyzer API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ResumeRequest(BaseModel):
    """Request with resume text."""
    resume_text: str


class ResumeJDRequest(BaseModel):
    """Request with resume and job description."""
    resume_text: str
    jd_text: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/analyze")
async def analyze_endpoint(request: ResumeRequest):
    """Analyze a resume for quality and content."""
    try:
        result = analyze_resume(resume_text=request.resume_text)
        return {"analysis": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score")
async def score_endpoint(request: ResumeJDRequest):
    """Score a resume against a job description."""
    try:
        result = score_against_jd(
            resume_text=request.resume_text,
            jd_text=request.jd_text,
        )
        return {"score": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ats-score")
async def ats_score_endpoint(request: ResumeJDRequest):
    """Simulate an ATS score for a resume against a job description."""
    try:
        result = simulate_ats_score(
            resume_text=request.resume_text,
            jd_text=request.jd_text,
        )
        return {"ats_score": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggestions")
async def suggestions_endpoint(request: ResumeRequest):
    """Generate improvement suggestions for a resume."""
    try:
        result = generate_improvement_suggestions(resume_text=request.resume_text)
        return {"suggestions": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
