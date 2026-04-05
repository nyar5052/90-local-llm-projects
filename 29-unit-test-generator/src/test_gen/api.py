"""FastAPI REST API for Unit Test Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.llm_client import chat
from src.test_gen.core import (
    extract_code_info,
    analyze_coverage,
    generate_tests,
    organize_test_structure,
    SUPPORTED_FRAMEWORKS,
)

app = FastAPI(
    title="Unit Test Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class GenerateTestsRequest(BaseModel):
    """Request to generate unit tests."""
    filepath: str
    framework: str = "pytest"


class AnalyzeRequest(BaseModel):
    """Request to analyze a file for code info."""
    filepath: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/frameworks")
async def list_frameworks():
    """List supported test frameworks."""
    return {"frameworks": SUPPORTED_FRAMEWORKS}


@app.post("/generate")
async def generate_endpoint(request: GenerateTestsRequest):
    """Generate unit tests for a Python file."""
    try:
        result = generate_tests(
            filepath=request.filepath,
            chat_fn=chat,
            framework=request.framework,
        )
        return {"tests": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest):
    """Extract code info (functions, classes, etc.) from a file."""
    try:
        info = extract_code_info(filepath=request.filepath)
        return {"code_info": info, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/coverage")
async def coverage_endpoint(request: AnalyzeRequest):
    """Analyze test coverage potential for a file."""
    try:
        info = extract_code_info(filepath=request.filepath)
        coverage = analyze_coverage(code_info=info)
        return {"coverage_analysis": coverage, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/structure")
async def structure_endpoint(request: AnalyzeRequest):
    """Organize test structure for a file."""
    try:
        info = extract_code_info(filepath=request.filepath)
        structure = organize_test_structure(code_info=info)
        return {"test_structure": structure, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8028)
