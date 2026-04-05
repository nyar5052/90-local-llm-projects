"""FastAPI REST API for Blog Post Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from blog_gen.core import (
    generate_blog_post,
    generate_outline,
    generate_multiple_drafts,
    score_seo,
    analyze_tone,
    parse_blog_post,
    TONES,
)

app = FastAPI(
    title="Blog Post Generator API",
    description="REST API for Blog Post Generator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GenerateBlogPostRequest(BaseModel):
    topic: str = Field(..., description="Blog post topic")
    keywords: List[str] = Field(..., description="SEO keywords")
    tone: str = Field(..., description=f"Tone of the post. Options: {TONES}")
    length: int = Field(..., description="Approximate word count")


class GenerateOutlineRequest(BaseModel):
    topic: str = Field(..., description="Blog post topic")
    keywords: List[str] = Field(..., description="SEO keywords")
    tone: str = Field(..., description=f"Tone of the outline. Options: {TONES}")


class GenerateMultipleDraftsRequest(BaseModel):
    topic: str = Field(..., description="Blog post topic")
    keywords: List[str] = Field(..., description="SEO keywords")
    tone: str = Field(..., description=f"Tone of the drafts. Options: {TONES}")
    length: int = Field(..., description="Approximate word count per draft")
    num_drafts: int = Field(3, description="Number of drafts to generate")


class ScoreSeoRequest(BaseModel):
    content: str = Field(..., description="Blog post content to score")
    keywords: List[str] = Field(..., description="Target SEO keywords")


class AnalyzeToneRequest(BaseModel):
    content: str = Field(..., description="Blog post content to analyze")


class ParseBlogPostRequest(BaseModel):
    content: str = Field(..., description="Raw blog post content")
    keywords: Optional[List[str]] = Field(None, description="Optional keywords")
    tone: str = Field("professional", description=f"Tone. Options: {TONES}")


class TextResponse(BaseModel):
    result: str


class DraftsResponse(BaseModel):
    drafts: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blog-post-generator"}


@app.get("/tones")
async def get_tones():
    """Return the list of supported tones."""
    return {"tones": TONES}


@app.post("/generate", response_model=TextResponse)
async def api_generate_blog_post(req: GenerateBlogPostRequest):
    """Generate a complete blog post."""
    try:
        result = generate_blog_post(
            topic=req.topic,
            keywords=req.keywords,
            tone=req.tone,
            length=req.length,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/outline", response_model=TextResponse)
async def api_generate_outline(req: GenerateOutlineRequest):
    """Generate a blog post outline."""
    try:
        result = generate_outline(
            topic=req.topic,
            keywords=req.keywords,
            tone=req.tone,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/drafts", response_model=DraftsResponse)
async def api_generate_multiple_drafts(req: GenerateMultipleDraftsRequest):
    """Generate multiple blog post drafts."""
    try:
        drafts = generate_multiple_drafts(
            topic=req.topic,
            keywords=req.keywords,
            tone=req.tone,
            length=req.length,
            num_drafts=req.num_drafts,
        )
        return DraftsResponse(drafts=drafts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score-seo")
async def api_score_seo(req: ScoreSeoRequest):
    """Score content for SEO effectiveness."""
    try:
        return score_seo(content=req.content, keywords=req.keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-tone")
async def api_analyze_tone(req: AnalyzeToneRequest):
    """Analyze the tone of content."""
    try:
        return analyze_tone(content=req.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse")
async def api_parse_blog_post(req: ParseBlogPostRequest):
    """Parse raw content into a structured BlogPost."""
    try:
        blog_post = parse_blog_post(
            content=req.content,
            keywords=req.keywords,
            tone=req.tone,
        )
        return blog_post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
