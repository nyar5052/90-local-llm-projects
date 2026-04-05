"""FastAPI REST API for Invoice Extractor."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.invoice_extractor.core import (
    extract_invoice_data,
    categorize_items,
    export_to_csv,
)

app = FastAPI(
    title="Invoice Extractor API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class InvoiceRequest(BaseModel):
    """Request with invoice text."""
    text: str


class CategorizeRequest(BaseModel):
    """Request to categorize invoice items."""
    invoice_data: dict


class ExportRequest(BaseModel):
    """Request to export invoices to CSV."""
    invoices: list[dict]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/extract")
async def extract_endpoint(request: InvoiceRequest):
    """Extract structured data from invoice text."""
    try:
        result = extract_invoice_data(text=request.text)
        return {"invoice_data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/categorize")
async def categorize_endpoint(request: CategorizeRequest):
    """Categorize line items on an invoice."""
    try:
        result = categorize_items(invoice_data=request.invoice_data)
        return {"categorized": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-csv")
async def export_csv_endpoint(request: ExportRequest):
    """Export invoices to CSV format."""
    try:
        csv_content = export_to_csv(invoices=request.invoices)
        return {"csv": csv_content, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
