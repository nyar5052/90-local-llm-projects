"""FastAPI REST API for Presentation Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from presentation_gen.core import (
    generate_presentation,
    estimate_timing,
    export_to_markdown,
    generate_speaker_notes_only,
    get_formats,
    get_slide_templates,
    get_visual_suggestions,
)

app = FastAPI(
    title="Presentation Generator API",
    description="REST API for Presentation Generator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class PresentationRequest(BaseModel):
    topic: str = Field(..., description="Presentation topic")
    slides: int = Field(..., description="Number of slides")
    audience: str = Field(..., description="Target audience")
    format_type: str = Field(..., description="Presentation format type")


class TimingRequest(BaseModel):
    slides: int = Field(..., description="Number of slides")
    format_type: str = Field(..., description="Presentation format type")


class ExportMarkdownRequest(BaseModel):
    content: str = Field(..., description="Presentation content to export")
    topic: str = Field(..., description="Presentation topic")


class SpeakerNotesRequest(BaseModel):
    content: str = Field(..., description="Presentation content")


class TextResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "presentation-generator"}


@app.post("/generate-presentation", response_model=TextResponse)
async def api_generate_presentation(req: PresentationRequest):
    try:
        result = generate_presentation(
            topic=req.topic,
            slides=req.slides,
            audience=req.audience,
            format_type=req.format_type,
        )
        return TextResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/estimate-timing")
async def api_estimate_timing(req: TimingRequest):
    try:
        result = estimate_timing(slides=req.slides, format_type=req.format_type)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/export-to-markdown", response_model=TextResponse)
async def api_export_to_markdown(req: ExportMarkdownRequest):
    try:
        result = export_to_markdown(content=req.content, topic=req.topic)
        return TextResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/generate-speaker-notes", response_model=TextResponse)
async def api_generate_speaker_notes(req: SpeakerNotesRequest):
    try:
        result = generate_speaker_notes_only(content=req.content)
        return TextResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/formats")
async def api_get_formats():
    try:
        return get_formats()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/slide-templates")
async def api_get_slide_templates():
    try:
        return get_slide_templates()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/visual-suggestions")
async def api_get_visual_suggestions():
    try:
        return get_visual_suggestions()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
