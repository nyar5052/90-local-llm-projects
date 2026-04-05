"""FastAPI REST API for Code Review Bot."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.code_reviewer.core import (
    review_single_file,
    review_multiple_files,
    generate_autofix,
    export_report,
)
from src.code_reviewer.config import ReviewConfig

app = FastAPI(
    title="Code Review Bot API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ReviewRequest(BaseModel):
    """Request to review a single file."""
    filepath: str
    focus_areas: Optional[list[str]] = None


class MultiReviewRequest(BaseModel):
    """Request to review multiple files."""
    filepaths: list[str]
    focus_areas: Optional[list[str]] = None


class AutofixRequest(BaseModel):
    """Request to generate an autofix."""
    filepath: str
    review_text: str


class ExportRequest(BaseModel):
    """Request to export a review report."""
    results: list[dict]
    output_path: str
    fmt: str = "markdown"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/review")
async def review_endpoint(request: ReviewRequest):
    """Review a single code file."""
    try:
        result = review_single_file(
            filepath=request.filepath,
            focus_areas=request.focus_areas,
        )
        return {"review": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review/batch")
async def batch_review_endpoint(request: MultiReviewRequest):
    """Review multiple code files."""
    try:
        results = review_multiple_files(
            filepaths=request.filepaths,
            focus_areas=request.focus_areas,
        )
        return {"reviews": results, "count": len(results), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/autofix")
async def autofix_endpoint(request: AutofixRequest):
    """Generate an autofix for reviewed code."""
    try:
        result = generate_autofix(
            filepath=request.filepath,
            review_text=request.review_text,
        )
        return {"autofix": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export")
async def export_endpoint(request: ExportRequest):
    """Export review results to a file."""
    try:
        path = export_report(
            results=request.results,
            output_path=request.output_path,
            fmt=request.fmt,
        )
        return {"output_path": path, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
