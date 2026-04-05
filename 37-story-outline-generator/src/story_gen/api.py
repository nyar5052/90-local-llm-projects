"""FastAPI REST API for Story Outline Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from story_gen.core import (
    generate_outline,
    generate_character_profile,
    visualize_plot_arc,
    get_character_archetypes,
    get_plot_structures,
    get_worldbuilding_categories,
)

app = FastAPI(
    title="Story Outline Generator API",
    description="REST API for Story Outline Generator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class OutlineRequest(BaseModel):
    genre: str = Field(..., description="Genre of the story")
    premise: str = Field(..., description="Story premise or concept")
    chapters: int = Field(..., description="Number of chapters")
    characters: int = Field(..., description="Number of characters")
    plot_structure: Optional[str] = Field(None, description="Plot structure type")
    worldbuilding: bool = Field(False, description="Include worldbuilding details")


class CharacterProfileRequest(BaseModel):
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character role in the story")
    genre: str = Field(..., description="Genre of the story")
    archetype: Optional[str] = Field(None, description="Character archetype")


class PlotArcRequest(BaseModel):
    structure: str = Field("three_act", description="Plot structure type")


class TextResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "story-outline-generator"}


@app.post("/generate-outline", response_model=TextResponse)
async def api_generate_outline(req: OutlineRequest):
    try:
        result = generate_outline(
            genre=req.genre,
            premise=req.premise,
            chapters=req.chapters,
            characters=req.characters,
            plot_structure=req.plot_structure,
            worldbuilding=req.worldbuilding,
        )
        return TextResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/generate-character-profile", response_model=TextResponse)
async def api_generate_character_profile(req: CharacterProfileRequest):
    try:
        result = generate_character_profile(
            name=req.name,
            role=req.role,
            genre=req.genre,
            archetype=req.archetype,
        )
        return TextResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/visualize-plot-arc")
async def api_visualize_plot_arc(req: PlotArcRequest):
    try:
        result = visualize_plot_arc(structure=req.structure)
        return {"result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/character-archetypes")
async def api_get_character_archetypes():
    try:
        return get_character_archetypes()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/plot-structures")
async def api_get_plot_structures():
    try:
        return get_plot_structures()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/worldbuilding-categories")
async def api_get_worldbuilding_categories():
    try:
        return get_worldbuilding_categories()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
