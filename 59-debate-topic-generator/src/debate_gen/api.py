"""FastAPI REST API for Debate Topic Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dataclasses import asdict
import uvicorn

from debate_gen.core import (
    generate_debate_topics,
    generate_moderator_guide,
    rate_evidence_strength,
    check_service,
)

app = FastAPI(
    title="Debate Topic Generator API",
    description="REST API for Debate Topic Generator",
    version="1.0.0",
)


# --- Request Models ---


class GenerateDebateTopicsRequest(BaseModel):
    subject: str = Field(..., description="Subject area for debate topics")
    complexity: str = Field("intermediate", description="Complexity level")
    num_topics: int = Field(3, description="Number of topics to generate")


class ModeratorGuideRequest(BaseModel):
    motion: str = Field(..., description="Debate motion to generate a guide for")


class RateEvidenceRequest(BaseModel):
    evidence: str = Field(..., description="Evidence text to rate")


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "debate-topic-generator"}


@app.get("/service-check")
async def api_check_service():
    try:
        result = check_service()
        return {"available": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def api_generate_debate_topics(request: GenerateDebateTopicsRequest):
    try:
        result = generate_debate_topics(
            subject=request.subject,
            complexity=request.complexity,
            num_topics=request.num_topics,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/moderator-guide")
async def api_generate_moderator_guide(request: ModeratorGuideRequest):
    try:
        result = generate_moderator_guide(motion=request.motion)
        return asdict(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rate-evidence")
async def api_rate_evidence_strength(request: RateEvidenceRequest):
    try:
        result = rate_evidence_strength(evidence=request.evidence)
        return {"rating": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
