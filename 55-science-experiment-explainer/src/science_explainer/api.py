"""FastAPI REST API for Science Experiment Explainer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from science_explainer.core import (
    explain_experiment,
    suggest_alternatives,
    search_experiments,
    validate_experiment_data,
)

app = FastAPI(
    title="Science Experiment Explainer API",
    description="REST API for Science Experiment Explainer",
    version="1.0.0",
)


# --- Request Models ---


class ExplainExperimentRequest(BaseModel):
    experiment: str = Field(..., description="Name or description of the experiment")
    level: str = Field(..., description="Education level (e.g. elementary, middle, high)")
    detail: str = Field("medium", description="Detail level: low, medium, or high")


class SuggestAlternativesRequest(BaseModel):
    experiment: str = Field(..., description="Name or description of the experiment")
    level: str = Field(..., description="Education level")


class SearchExperimentsRequest(BaseModel):
    topic: str = Field("", description="Topic to search for")
    subject: str = Field("", description="Subject area filter")
    difficulty: str = Field("", description="Difficulty level filter")


class ValidateExperimentDataRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Experiment data to validate")


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "science-experiment-explainer"}


@app.post("/explain")
async def api_explain_experiment(request: ExplainExperimentRequest):
    try:
        result = explain_experiment(
            experiment=request.experiment,
            level=request.level,
            detail=request.detail,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest-alternatives")
async def api_suggest_alternatives(request: SuggestAlternativesRequest):
    try:
        result = suggest_alternatives(
            experiment=request.experiment,
            level=request.level,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def api_search_experiments(request: SearchExperimentsRequest):
    try:
        result = search_experiments(
            topic=request.topic,
            subject=request.subject,
            difficulty=request.difficulty,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate")
async def api_validate_experiment_data(request: ValidateExperimentDataRequest):
    try:
        result = validate_experiment_data(data=request.data)
        return {"errors": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
