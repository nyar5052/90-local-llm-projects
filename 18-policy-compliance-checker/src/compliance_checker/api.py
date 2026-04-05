"""FastAPI REST API for Policy Compliance Checker."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.compliance_checker.core import (
    check_compliance,
    filter_violations,
    get_score_label,
)

app = FastAPI(
    title="Policy Compliance Checker API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ComplianceRequest(BaseModel):
    """Request to check compliance."""
    document: str
    policy: str


class FilterRequest(BaseModel):
    """Request to filter violations by severity."""
    violations: list
    severity: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/check")
async def check_endpoint(request: ComplianceRequest):
    """Check document compliance against a policy."""
    try:
        result = check_compliance(
            document=request.document,
            policy=request.policy,
        )
        return {"compliance": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/filter-violations")
async def filter_violations_endpoint(request: FilterRequest):
    """Filter violations by severity level."""
    try:
        result = filter_violations(
            violations=request.violations,
            severity=request.severity,
        )
        return {"filtered_violations": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/score-label/{score}")
async def score_label_endpoint(score: int):
    """Get the label for a compliance score."""
    try:
        label = get_score_label(score)
        return {"score": score, "label": label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8017)
