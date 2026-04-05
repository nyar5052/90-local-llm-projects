from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from .core import (
    generate_compose,
    explain_compose,
    validate_compose,
    get_service_catalog,
    get_flat_catalog,
    get_env_profile,
    extract_yaml,
)

app = FastAPI(
    title="Docker Compose Generator",
    description="AI-powered Docker Compose file generation, explanation, and validation.",
    version="1.0.0",
)

ENVIRONMENTS = ["development", "staging", "production"]


# ── Request / Response Models ────────────────────────────────────────────────

class GenerateComposeRequest(BaseModel):
    stack_description: str = Field(..., description="Natural-language description of the desired stack")
    env: str = Field("development", description="Target environment")
    services: Optional[List[str]] = Field(None, description="Explicit list of service names to include")
    network_mode: str = Field("simple", description="Network topology: simple | overlay | host")


class ExplainComposeRequest(BaseModel):
    compose_content: str = Field(..., description="Raw docker-compose YAML to explain")


class ValidateComposeRequest(BaseModel):
    yaml_content: str = Field(..., description="Raw docker-compose YAML to validate")


class ValidateComposeResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    services: List[str] = []


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "docker-compose-generator"}


@app.post("/compose/generate")
async def compose_generate(req: GenerateComposeRequest):
    try:
        result = generate_compose(
            stack_description=req.stack_description,
            env=req.env,
            services=req.services,
            network_mode=req.network_mode,
        )
        return {"compose_yaml": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compose/explain")
async def compose_explain(req: ExplainComposeRequest):
    try:
        result = explain_compose(compose_content=req.compose_content)
        return {"explanation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compose/validate", response_model=ValidateComposeResponse)
async def compose_validate(req: ValidateComposeRequest):
    try:
        result = validate_compose(yaml_content=req.yaml_content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/catalog")
async def catalog():
    try:
        return get_service_catalog()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/catalog/flat")
async def catalog_flat():
    try:
        return get_flat_catalog()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profiles/{env}")
async def profiles(env: str):
    if env not in ENVIRONMENTS:
        raise HTTPException(status_code=404, detail=f"Unknown environment '{env}'. Choose from: {ENVIRONMENTS}")
    try:
        return get_env_profile(env=env)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/environments")
async def environments():
    return {"environments": ENVIRONMENTS}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
