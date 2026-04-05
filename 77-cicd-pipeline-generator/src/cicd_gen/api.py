from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from .core import (
    generate_pipeline,
    explain_pipeline,
    validate_pipeline_config,
    get_platforms,
    get_stage_catalog,
    get_secret_template,
    get_matrix_preset,
)

app = FastAPI(
    title="CI/CD Pipeline Generator",
    description="AI-powered CI/CD pipeline generation, explanation, and validation for multiple platforms.",
    version="1.0.0",
)

SUPPORTED_PLATFORMS = ["github-actions", "gitlab-ci", "jenkins", "azure-pipelines", "circleci"]


# ── Request / Response Models ────────────────────────────────────────────────

class GeneratePipelineRequest(BaseModel):
    platform: str = Field(..., description="CI/CD platform target")
    language: str = Field(..., description="Primary programming language")
    steps: str = Field(..., description="Natural-language description of desired pipeline steps")
    project_name: Optional[str] = Field(None, description="Project name for labelling")
    matrix: bool = Field(False, description="Enable build-matrix strategy")
    secrets: Optional[List[str]] = Field(None, description="Secret names the pipeline should reference")


class ExplainPipelineRequest(BaseModel):
    config_content: str = Field(..., description="Raw pipeline configuration to explain")
    platform: Optional[str] = Field(None, description="CI/CD platform hint")


class ValidatePipelineRequest(BaseModel):
    config_text: str = Field(..., description="Raw pipeline configuration to validate")
    platform: str = Field(..., description="CI/CD platform the config targets")


class ValidatePipelineResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    stages: List[str] = []


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cicd-pipeline-generator"}


@app.post("/pipeline/generate")
async def pipeline_generate(req: GeneratePipelineRequest):
    if req.platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform '{req.platform}'. Choose from: {SUPPORTED_PLATFORMS}",
        )
    try:
        result = generate_pipeline(
            platform=req.platform,
            language=req.language,
            steps=req.steps,
            project_name=req.project_name,
            matrix=req.matrix,
            secrets=req.secrets,
        )
        return {"pipeline_config": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/explain")
async def pipeline_explain(req: ExplainPipelineRequest):
    try:
        result = explain_pipeline(
            config_content=req.config_content,
            platform=req.platform,
        )
        return {"explanation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/validate", response_model=ValidatePipelineResponse)
async def pipeline_validate(req: ValidatePipelineRequest):
    if req.platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform '{req.platform}'. Choose from: {SUPPORTED_PLATFORMS}",
        )
    try:
        result = validate_pipeline_config(
            config_text=req.config_text,
            platform=req.platform,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/platforms")
async def platforms():
    try:
        return get_platforms()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stages")
async def stages():
    try:
        return get_stage_catalog()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/secrets/{platform}")
async def secrets(platform: str):
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown platform '{platform}'. Choose from: {SUPPORTED_PLATFORMS}",
        )
    try:
        return get_secret_template(platform=platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/matrix/{language}")
async def matrix(language: str):
    try:
        return get_matrix_preset(language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
