"""FastAPI REST API for Poem & Lyrics Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from poem_gen.core import (
    generate_poem,
    generate_with_rhyme_scheme,
    mix_styles,
    count_syllables,
    detect_rhyme_scheme,
    analyze_poem,
    format_poem,
    STYLES,
    MOODS,
)

app = FastAPI(
    title="Poem & Lyrics Generator API",
    description="REST API for Poem & Lyrics Generator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GeneratePoemRequest(BaseModel):
    theme: str = Field(..., description="Theme or subject of the poem")
    style: str = Field(..., description=f"Poetic style. Options: {STYLES}")
    mood: Optional[str] = Field(None, description=f"Mood of the poem. Options: {MOODS}")
    title: Optional[str] = Field(None, description="Optional title for the poem")


class RhymeSchemeRequest(BaseModel):
    theme: str = Field(..., description="Theme or subject of the poem")
    scheme: str = Field(..., description="Rhyme scheme (e.g. ABAB, AABB, ABCABC)")
    mood: Optional[str] = Field(None, description=f"Mood of the poem. Options: {MOODS}")


class MixStylesRequest(BaseModel):
    theme: str = Field(..., description="Theme or subject of the poem")
    styles: List[str] = Field(..., description=f"Styles to mix. Options: {STYLES}")
    mood: Optional[str] = Field(None, description=f"Mood of the poem. Options: {MOODS}")


class TextInput(BaseModel):
    text: str = Field(..., description="Poem or lyrics text")


class FormatPoemRequest(BaseModel):
    poem_text: str = Field(..., description="Raw poem text to format")
    style: str = Field(..., description=f"Poetic style. Options: {STYLES}")


class TextResponse(BaseModel):
    result: str


class SyllablesResponse(BaseModel):
    syllables: List[int]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "poem-lyrics-generator"}


@app.get("/styles")
async def get_styles():
    """Return the list of supported poetic styles."""
    return {"styles": STYLES}


@app.get("/moods")
async def get_moods():
    """Return the list of supported moods."""
    return {"moods": MOODS}


@app.post("/generate", response_model=TextResponse)
async def api_generate_poem(req: GeneratePoemRequest):
    """Generate a poem."""
    try:
        result = generate_poem(
            theme=req.theme,
            style=req.style,
            mood=req.mood,
            title=req.title,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-rhyme-scheme", response_model=TextResponse)
async def api_generate_with_rhyme_scheme(req: RhymeSchemeRequest):
    """Generate a poem following a specific rhyme scheme."""
    try:
        result = generate_with_rhyme_scheme(
            theme=req.theme,
            scheme=req.scheme,
            mood=req.mood,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mix-styles", response_model=TextResponse)
async def api_mix_styles(req: MixStylesRequest):
    """Generate a poem mixing multiple styles."""
    try:
        result = mix_styles(
            theme=req.theme,
            styles=req.styles,
            mood=req.mood,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/count-syllables", response_model=SyllablesResponse)
async def api_count_syllables(req: TextInput):
    """Count syllables per line in a text."""
    try:
        syllables = count_syllables(text=req.text)
        return SyllablesResponse(syllables=syllables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-rhyme-scheme", response_model=TextResponse)
async def api_detect_rhyme_scheme(req: TextInput):
    """Detect the rhyme scheme of a text."""
    try:
        scheme = detect_rhyme_scheme(text=req.text)
        return TextResponse(result=scheme)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def api_analyze_poem(req: TextInput):
    """Analyze a poem's structure, meter, and other attributes."""
    try:
        return analyze_poem(text=req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/format", response_model=TextResponse)
async def api_format_poem(req: FormatPoemRequest):
    """Format a poem according to a poetic style."""
    try:
        result = format_poem(poem_text=req.poem_text, style=req.style)
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
