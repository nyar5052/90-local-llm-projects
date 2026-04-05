"""FastAPI REST API for CSV Data Analyzer."""

import io

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from csv_analyzer.core import (
    analyze_data,
    generate_statistical_summary,
    detect_column_types,
    compute_correlations,
    suggest_charts,
)

app = FastAPI(
    title="CSV Data Analyzer API",
    description="REST API for CSV Data Analyzer",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _csv_to_dataframe(csv_text: str) -> pd.DataFrame:
    """Convert raw CSV text into a pandas DataFrame."""
    try:
        return pd.read_csv(io.StringIO(csv_text))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV data: {exc}",
        )


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    csv_text: str = Field(..., description="Raw CSV text data")
    query: str = Field(..., description="Analysis query")


class CSVInput(BaseModel):
    csv_text: str = Field(..., description="Raw CSV text data")


class SuggestChartsRequest(BaseModel):
    csv_text: str = Field(..., description="Raw CSV text data")
    column_types: Optional[Dict[str, Any]] = Field(
        None,
        description="Pre-computed column types; if omitted they are detected automatically",
    )


class TextResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "csv-data-analyzer"}


@app.post("/analyze", response_model=TextResponse)
async def api_analyze_data(req: AnalyzeRequest):
    try:
        df = _csv_to_dataframe(req.csv_text)
        result = analyze_data(df=df, query=req.query)
        return TextResponse(result=result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/statistical-summary")
async def api_generate_statistical_summary(req: CSVInput):
    try:
        df = _csv_to_dataframe(req.csv_text)
        result = generate_statistical_summary(df=df)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/detect-column-types")
async def api_detect_column_types(req: CSVInput):
    try:
        df = _csv_to_dataframe(req.csv_text)
        result = detect_column_types(df=df)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/compute-correlations")
async def api_compute_correlations(req: CSVInput):
    try:
        df = _csv_to_dataframe(req.csv_text)
        result = compute_correlations(df=df)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/suggest-charts")
async def api_suggest_charts(req: SuggestChartsRequest):
    try:
        df = _csv_to_dataframe(req.csv_text)
        col_types = req.column_types if req.column_types is not None else detect_column_types(df=df)
        result = suggest_charts(df=df, column_types=col_types)
        return {"result": result}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
