from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from .core import (
    generate_docs,
    generate_diagram,
    generate_dependency_map,
    detect_config_type,
    extract_dependencies,
)

app = FastAPI(
    title="Infrastructure Documentation Generator",
    description="AI-powered documentation, diagrams, and dependency maps for infrastructure-as-code.",
    version="1.0.0",
)

CONFIG_TYPES = [
    "terraform",
    "kubernetes",
    "docker-compose",
    "dockerfile",
    "ansible",
    "cloudformation",
]


# ── Request / Response Models ────────────────────────────────────────────────

class GenerateDocsRequest(BaseModel):
    content: str = Field(..., description="Raw infrastructure configuration content")
    config_type: str = Field(..., description="Type of infrastructure config")
    output_format: str = Field("markdown", description="Output format: markdown | html | rst")
    include_diagram: bool = Field(False, description="Include an architecture diagram in the output")


class DiagramRequest(BaseModel):
    content: str = Field(..., description="Raw infrastructure configuration content")
    config_type: str = Field(..., description="Type of infrastructure config")


class DependencyMapRequest(BaseModel):
    content: str = Field(..., description="Raw infrastructure configuration content")
    config_type: str = Field(..., description="Type of infrastructure config")


class DetectTypeRequest(BaseModel):
    content: str = Field(..., description="Raw file content")
    filename: str = Field(..., description="Original filename (used as a hint)")


class ExtractDependenciesRequest(BaseModel):
    content: str = Field(..., description="Raw infrastructure configuration content")
    config_type: str = Field(..., description="Type of infrastructure config")


# ── Helper ───────────────────────────────────────────────────────────────────

def _validate_config_type(config_type: str) -> None:
    if config_type not in CONFIG_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported config_type '{config_type}'. Choose from: {CONFIG_TYPES}",
        )


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "infra-doc-generator"}


@app.post("/docs/generate")
async def docs_generate(req: GenerateDocsRequest):
    _validate_config_type(req.config_type)
    try:
        result = generate_docs(
            content=req.content,
            config_type=req.config_type,
            output_format=req.output_format,
            include_diagram=req.include_diagram,
        )
        return {"documentation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/docs/diagram")
async def docs_diagram(req: DiagramRequest):
    _validate_config_type(req.config_type)
    try:
        result = generate_diagram(
            content=req.content,
            config_type=req.config_type,
        )
        return {"diagram": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/docs/dependency-map")
async def docs_dependency_map(req: DependencyMapRequest):
    _validate_config_type(req.config_type)
    try:
        result = generate_dependency_map(
            content=req.content,
            config_type=req.config_type,
        )
        return {"dependency_map": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/docs/detect-type")
async def docs_detect_type(req: DetectTypeRequest):
    try:
        result = detect_config_type(
            filepath=req.filename,
            content=req.content,
        )
        return {"config_type": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/docs/extract-dependencies")
async def docs_extract_dependencies(req: ExtractDependenciesRequest):
    _validate_config_type(req.config_type)
    try:
        result = extract_dependencies(
            content=req.content,
            config_type=req.config_type,
        )
        return {"dependencies": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
