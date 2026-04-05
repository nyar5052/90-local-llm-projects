"""FastAPI REST API for Newsletter Editor."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from newsletter_editor.core import (
    generate_newsletter,
    export_to_html,
    archive_newsletter,
    list_archive,
    get_section_templates,
    get_subscriber_segments,
)

app = FastAPI(
    title="Newsletter Editor API",
    description="REST API for Newsletter Editor",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GenerateNewsletterRequest(BaseModel):
    raw_content: str = Field(..., description="Raw content / notes for the newsletter")
    name: str = Field(..., description="Newsletter name or edition title")
    sections: int = Field(..., description="Number of sections to generate")
    tone: str = Field(..., description="Writing tone")
    template: Optional[str] = Field(None, description="Optional template name")
    segment: Optional[str] = Field(None, description="Optional subscriber segment")


class ExportHtmlRequest(BaseModel):
    markdown_content: str = Field(..., description="Newsletter content in Markdown")
    newsletter_name: str = Field(..., description="Newsletter name for HTML title")


class ArchiveRequest(BaseModel):
    content: str = Field(..., description="Newsletter content to archive")
    name: str = Field(..., description="Newsletter name or edition title")


class TextResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "newsletter-editor"}


@app.post("/generate", response_model=TextResponse)
async def api_generate_newsletter(req: GenerateNewsletterRequest):
    """Generate a newsletter from raw content."""
    try:
        result = generate_newsletter(
            raw_content=req.raw_content,
            name=req.name,
            sections=req.sections,
            tone=req.tone,
            template=req.template,
            segment=req.segment,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-html", response_model=TextResponse)
async def api_export_to_html(req: ExportHtmlRequest):
    """Export Markdown newsletter content to HTML."""
    try:
        html = export_to_html(
            markdown_content=req.markdown_content,
            newsletter_name=req.newsletter_name,
        )
        return TextResponse(result=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/archive", response_model=TextResponse)
async def api_archive_newsletter(req: ArchiveRequest):
    """Archive a newsletter edition."""
    try:
        result = archive_newsletter(content=req.content, name=req.name)
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/archive")
async def api_list_archive():
    """List all archived newsletter editions."""
    try:
        return {"archives": list_archive()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates")
async def api_get_section_templates():
    """Get available section templates."""
    try:
        return get_section_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/segments")
async def api_get_subscriber_segments():
    """Get available subscriber segments."""
    try:
        return get_subscriber_segments()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
