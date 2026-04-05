from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn

from .core import (
    parse_env_file,
    detect_secrets,
    compare_envs,
    generate_migration_script,
    validate_env,
    generate_env_template,
    suggest_missing_vars,
    generate_env_documentation,
)

app = FastAPI(
    title="Environment Config Manager",
    description="AI-powered .env file parsing, validation, secret detection, and template generation.",
    version="1.0.0",
)

PROJECT_TYPES = [
    "flask",
    "django",
    "fastapi",
    "express",
    "nextjs",
    "rails",
    "spring-boot",
    "laravel",
    "dotnet",
    "generic",
]


# ── Request / Response Models ────────────────────────────────────────────────

class ParseEnvRequest(BaseModel):
    filepath: str = Field(..., description="Path to the .env file")


class DetectSecretsRequest(BaseModel):
    env_vars: Dict[str, str] = Field(..., description="Key-value map of environment variables")


class CompareEnvsRequest(BaseModel):
    env1: Dict[str, str] = Field(..., description="First environment variable set")
    env2: Dict[str, str] = Field(..., description="Second environment variable set")


class MigrationScriptRequest(BaseModel):
    env_from: Dict[str, str] = Field(..., description="Source environment variables")
    env_to: Dict[str, str] = Field(..., description="Target environment variables")
    target_name: str = Field("target", description="Label for the target environment")


class ValidateEnvRequest(BaseModel):
    filepath: str = Field(..., description="Path to the .env file to validate")


class GenerateTemplateRequest(BaseModel):
    project_type: str = Field(..., description="Project framework type")
    env: str = Field("development", description="Target environment")


class SuggestMissingRequest(BaseModel):
    filepath: str = Field(..., description="Path to the .env file")
    project_type: str = Field(..., description="Project framework type")


class GenerateDocsRequest(BaseModel):
    filepath: str = Field(..., description="Path to the .env file")


# ── Helper ───────────────────────────────────────────────────────────────────

def _validate_project_type(project_type: str) -> None:
    if project_type not in PROJECT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported project_type '{project_type}'. Choose from: {PROJECT_TYPES}",
        )


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "env-config-manager"}


@app.post("/env/parse")
async def env_parse(req: ParseEnvRequest):
    try:
        result = parse_env_file(filepath=req.filepath)
        return {"variables": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {req.filepath}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/detect-secrets")
async def env_detect_secrets(req: DetectSecretsRequest):
    try:
        result = detect_secrets(env_vars=req.env_vars)
        return {"secrets": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/compare")
async def env_compare(req: CompareEnvsRequest):
    try:
        result = compare_envs(env1=req.env1, env2=req.env2)
        return {"diff": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/migration-script")
async def env_migration_script(req: MigrationScriptRequest):
    try:
        result = generate_migration_script(
            env_from=req.env_from,
            env_to=req.env_to,
            target_name=req.target_name,
        )
        return {"script": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/validate")
async def env_validate(req: ValidateEnvRequest):
    try:
        result = validate_env(filepath=req.filepath)
        return {"validation": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {req.filepath}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/generate-template")
async def env_generate_template(req: GenerateTemplateRequest):
    _validate_project_type(req.project_type)
    try:
        result = generate_env_template(
            project_type=req.project_type,
            env=req.env,
        )
        return {"template": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/suggest-missing")
async def env_suggest_missing(req: SuggestMissingRequest):
    _validate_project_type(req.project_type)
    try:
        result = suggest_missing_vars(
            filepath=req.filepath,
            project_type=req.project_type,
        )
        return {"suggestions": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {req.filepath}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/env/generate-docs")
async def env_generate_docs(req: GenerateDocsRequest):
    try:
        result = generate_env_documentation(filepath=req.filepath)
        return {"documentation": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {req.filepath}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/project-types")
async def project_types():
    return {"project_types": PROJECT_TYPES}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
