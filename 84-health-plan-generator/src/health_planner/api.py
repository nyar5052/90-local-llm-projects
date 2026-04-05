"""Health Plan Generator API - AI-powered personalized health plan creation.

⚠️ MEDICAL DISCLAIMER: This tool is for informational and educational purposes only.
Generated plans do not constitute medical advice. Always consult a qualified healthcare
provider before starting any health or fitness program.
"""

from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import DISCLAIMER, generate_plan, get_milestones_for_goal

MEDICAL_DISCLAIMER = (
    "⚠️ This API is for informational and educational purposes only. "
    "Generated plans do not constitute medical advice. Always consult a "
    "qualified healthcare provider before starting any health or fitness program."
)

app = FastAPI(
    title="Health Plan Generator",
    description=(
        "AI-powered personalized health plan generation with milestone tracking.\n\n"
        f"**{MEDICAL_DISCLAIMER}**"
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class GeneratePlanRequest(BaseModel):
    goal: str = Field(..., description="Health or fitness goal to generate a plan for.")
    age: Optional[int] = Field(None, ge=1, le=150, description="Age of the individual.")
    lifestyle: Optional[str] = Field(None, description="Current lifestyle description (e.g., sedentary, active).")
    duration: Optional[str] = Field(None, description="Desired plan duration (e.g., '4 weeks', '3 months').")


class GeneratePlanResponse(BaseModel):
    goal: str
    plan: str


class MilestoneItem(BaseModel):
    """A single milestone entry."""
    # The exact keys depend on the core implementation; keep it flexible with a dict.
    pass


class MilestonesResponse(BaseModel):
    goal: str
    milestones: List[dict]


class DisclaimerResponse(BaseModel):
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    service: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    return HealthResponse(status="healthy", service="health-plan-generator")


@app.post("/plans/generate", response_model=GeneratePlanResponse, tags=["Plans"])
async def plans_generate(request: GeneratePlanRequest):
    """Generate a personalized health plan using AI."""
    try:
        plan = generate_plan(
            goal=request.goal,
            age=request.age,
            lifestyle=request.lifestyle,
            duration=request.duration,
        )
        return GeneratePlanResponse(goal=request.goal, plan=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}")


@app.get("/plans/milestones/{goal}", response_model=MilestonesResponse, tags=["Plans"])
async def plans_milestones(goal: str):
    """Get suggested milestones for a given health goal."""
    try:
        milestones = get_milestones_for_goal(goal)
        return MilestonesResponse(goal=goal, milestones=milestones)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Milestone retrieval failed: {e}")


@app.get("/disclaimer", response_model=DisclaimerResponse, tags=["Info"])
async def get_disclaimer():
    """Return the medical disclaimer for this service."""
    return DisclaimerResponse(disclaimer=DISCLAIMER)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
