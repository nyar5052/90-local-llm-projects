"""FastAPI REST API for API Documentation Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api_doc_gen.core import (
    generate_docs,
    generate_openapi,
    export_docs,
)

app = FastAPI(
    title="API Documentation Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class DocGenRequest(BaseModel):
    """Request to generate API documentation."""
    source_path: str


class ExportRequest(BaseModel):
    """Request to export documentation."""
    content: str
    output_path: str
    fmt: str = "markdown"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/generate")
async def generate_endpoint(request: DocGenRequest):
    """Generate API documentation from source code."""
    try:
        result = generate_docs(source_path=request.source_path)
        return {"documentation": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-openapi")
async def openapi_endpoint(request: DocGenRequest):
    """Generate OpenAPI specification from source code."""
    try:
        result = generate_openapi(source_path=request.source_path)
        return {"openapi_spec": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export")
async def export_endpoint(request: ExportRequest):
    """Export documentation to a file."""
    try:
        path = export_docs(
            content=request.content,
            output_path=request.output_path,
            fmt=request.fmt,
        )
        return {"output_path": path, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8024)
