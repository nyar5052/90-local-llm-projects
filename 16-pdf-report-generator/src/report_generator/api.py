"""FastAPI REST API for PDF Report Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.report_generator.core import (
    summarize_data,
    generate_report,
    REPORT_TEMPLATES,
)

app = FastAPI(
    title="PDF Report Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class SummarizeDataRequest(BaseModel):
    """Request to summarize tabular data."""
    headers: list[str]
    rows: list[dict]


class GenerateReportRequest(BaseModel):
    """Request to generate a report."""
    topic: str
    data_summary: str
    template: str = "executive"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/templates")
async def list_templates():
    """List available report templates."""
    return {"templates": list(REPORT_TEMPLATES.keys())}


@app.post("/summarize-data")
async def summarize_data_endpoint(request: SummarizeDataRequest):
    """Summarize tabular data."""
    try:
        result = summarize_data(headers=request.headers, rows=request.rows)
        return {"summary": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def generate_report_endpoint(request: GenerateReportRequest):
    """Generate a report from a data summary."""
    try:
        result = generate_report(
            topic=request.topic,
            data_summary=request.data_summary,
            template=request.template,
        )
        return {"report": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
