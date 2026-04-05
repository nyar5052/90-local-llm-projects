"""FastAPI REST API for Regex Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.regex_gen.core import (
    generate_regex,
    explain_regex,
    get_pattern_from_library,
    list_library_patterns,
)

app = FastAPI(
    title="Regex Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class GenerateRequest(BaseModel):
    """Request to generate a regex."""
    description: str
    flavor: str = "python"


class ExplainRequest(BaseModel):
    """Request to explain a regex."""
    pattern: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/generate")
async def generate_endpoint(request: GenerateRequest):
    """Generate a regex from a natural language description."""
    try:
        result = generate_regex(
            description=request.description,
            flavor=request.flavor,
        )
        return {"regex": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain")
async def explain_endpoint(request: ExplainRequest):
    """Explain a regex pattern."""
    try:
        result = explain_regex(pattern=request.pattern)
        return {"explanation": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/library")
async def library_endpoint():
    """List all patterns in the regex library."""
    try:
        patterns = list_library_patterns()
        return {"patterns": patterns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/library/{name}")
async def library_pattern_endpoint(name: str):
    """Get a specific pattern from the library."""
    try:
        pattern = get_pattern_from_library(name)
        if pattern is None:
            raise HTTPException(status_code=404, detail=f"Pattern '{name}' not found")
        return {"name": name, "pattern": pattern}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8023)
