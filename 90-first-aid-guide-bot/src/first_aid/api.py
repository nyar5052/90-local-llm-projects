"""FastAPI REST API for First Aid Guide Bot."""

from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uvicorn

from .core import (
    evaluate_emergency,
    get_supply_checklist,
    get_cpr_steps,
    COMMON_SCENARIOS,
    EMERGENCY_DECISION_TREE,
    EMERGENCY_DISCLAIMER,
)

app = FastAPI(
    title="First Aid Guide Bot API",
    description=(
        "Emergency evaluation, first aid guidance, CPR steps, and supply checklists. "
        f"**Disclaimer:** {EMERGENCY_DISCLAIMER}"
    ),
    version="1.0.0",
)


# ── Request / Response Models ────────────────────────────────────────────

class EmergencyEvaluateRequest(BaseModel):
    conscious: bool = Field(..., description="Is the person conscious?")
    breathing: bool = Field(..., description="Is the person breathing?")
    severe_bleeding: bool = Field(False, description="Is there severe bleeding?")


class EmergencyEvaluateResponse(BaseModel):
    evaluation: dict


class ScenarioItem(BaseModel):
    name: str
    description: str
    emoji: str
    severity: str


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/emergency/evaluate", response_model=EmergencyEvaluateResponse)
async def emergency_evaluate(request: EmergencyEvaluateRequest):
    try:
        result = evaluate_emergency(
            conscious=request.conscious,
            breathing=request.breathing,
            severe_bleeding=request.severe_bleeding,
        )
        return EmergencyEvaluateResponse(evaluation=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/supplies")
async def supplies(priority: str = Query("all", description="Filter priority: all, essential, recommended, optional")):
    try:
        checklist = get_supply_checklist(priority=priority)
        return {"priority": priority, "supplies": checklist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cpr-steps")
async def cpr_steps():
    try:
        steps = get_cpr_steps()
        return {"steps": steps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios")
async def scenarios():
    items = [
        ScenarioItem(name=name, description=desc, emoji=emoji, severity=severity).model_dump()
        for name, desc, emoji, severity in COMMON_SCENARIOS
    ]
    return {"scenarios": items}


@app.get("/disclaimer")
async def disclaimer():
    return {"disclaimer": EMERGENCY_DISCLAIMER}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
