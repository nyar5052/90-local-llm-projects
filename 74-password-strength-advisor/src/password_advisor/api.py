"""FastAPI application for Password Strength Advisor."""

import dataclasses
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    StrengthLevel,
    calculate_entropy,
    check_breach_database,
    generate_policy,
    analyze_password_llm,
    analyze_policy_llm,
    generate_password,
    bulk_analyze,
)

app = FastAPI(
    title="Password Strength Advisor",
    description="AI-powered password analysis, entropy calculation, breach checking, and policy management.",
    version="1.0.0",
)


# ── Request Models ───────────────────────────────────────────────────────────

class PasswordRequest(BaseModel):
    password: str = Field(..., description="Password to analyze")


class GeneratePasswordRequest(BaseModel):
    length: int = Field(16, ge=4, le=128, description="Desired password length")
    requirements: str = Field(
        "upper,lower,digits,special",
        description="Comma-separated character requirements",
    )


class BulkAnalyzeRequest(BaseModel):
    passwords: List[str] = Field(..., description="List of passwords to analyze")


class PolicyGenerateRequest(BaseModel):
    requirements: Optional[Dict] = Field(None, description="Custom policy requirements")


class PolicyAnalyzeRequest(BaseModel):
    policy_text: str = Field(..., description="Password policy text to analyze")


# ── Response Models ──────────────────────────────────────────────────────────

class EntropyResultResponse(BaseModel):
    entropy_bits: float
    charset_size: int
    effective_length: int
    time_to_crack: str
    strength: str
    details: str


class BreachCheckResultResponse(BaseModel):
    is_compromised: bool
    source: str
    occurrences: int
    recommendation: str


class PolicyRuleResponse(BaseModel):
    name: str
    description: str
    enabled: bool
    value: str


class BulkAnalysisResultResponse(BaseModel):
    index: int
    masked: str
    entropy: float
    strength: str
    issues: list


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "password-strength-advisor"}


@app.post("/password/entropy", response_model=EntropyResultResponse)
async def api_calculate_entropy(request: PasswordRequest):
    try:
        result = calculate_entropy(request.password)
        return dataclasses.asdict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/password/breach-check", response_model=BreachCheckResultResponse)
async def api_check_breach(request: PasswordRequest):
    try:
        result = check_breach_database(request.password)
        return dataclasses.asdict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/password/analyze")
async def api_analyze_password(request: PasswordRequest):
    try:
        result = analyze_password_llm(request.password)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/password/generate")
async def api_generate_password(request: GeneratePasswordRequest):
    try:
        result = generate_password(length=request.length, requirements=request.requirements)
        return {"password": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/password/bulk-analyze", response_model=List[BulkAnalysisResultResponse])
async def api_bulk_analyze(request: BulkAnalyzeRequest):
    if not request.passwords:
        raise HTTPException(status_code=400, detail="Password list cannot be empty")
    try:
        results = bulk_analyze(request.passwords)
        return [dataclasses.asdict(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policy/generate", response_model=List[PolicyRuleResponse])
async def api_generate_policy(request: PolicyGenerateRequest):
    try:
        results = generate_policy(requirements=request.requirements)
        return [dataclasses.asdict(rule) for rule in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policy/analyze")
async def api_analyze_policy(request: PolicyAnalyzeRequest):
    try:
        result = analyze_policy_llm(request.policy_text)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
