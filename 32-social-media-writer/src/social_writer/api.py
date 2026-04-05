"""FastAPI REST API for Social Media Writer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from social_writer.core import (
    generate_posts,
    validate_char_count,
    generate_hashtags,
    suggest_schedule,
    generate_ab_variants,
    format_for_platform,
    preview_post,
    PLATFORMS,
    TONES,
)

app = FastAPI(
    title="Social Media Writer API",
    description="REST API for Social Media Writer",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GeneratePostsRequest(BaseModel):
    platform: str = Field(..., description=f"Target platform. Options: {PLATFORMS}")
    topic: str = Field(..., description="Post topic")
    tone: str = Field(..., description=f"Tone of the post. Options: {TONES}")
    variants: int = Field(..., description="Number of post variants")


class ValidateCharCountRequest(BaseModel):
    content: str = Field(..., description="Post content to validate")
    platform: str = Field(..., description=f"Target platform. Options: {PLATFORMS}")


class GenerateHashtagsRequest(BaseModel):
    topic: str = Field(..., description="Topic for hashtag generation")
    platform: str = Field(..., description=f"Target platform. Options: {PLATFORMS}")
    count: Optional[int] = Field(None, description="Number of hashtags to generate")


class GenerateAbVariantsRequest(BaseModel):
    topic: str = Field(..., description="Post topic")
    platform: str = Field(..., description=f"Target platform. Options: {PLATFORMS}")
    tone: str = Field(..., description=f"Tone of the variants. Options: {TONES}")
    num_variants: int = Field(2, description="Number of A/B variants")


class FormatForPlatformRequest(BaseModel):
    content: str = Field(..., description="Post content to format")
    platform: str = Field(..., description=f"Target platform. Options: {PLATFORMS}")


class PreviewPostRequest(BaseModel):
    content: str = Field(..., description="Post content to preview")
    platform: str = Field(..., description=f"Target platform. Options: {PLATFORMS}")


class TextResponse(BaseModel):
    result: str


class CharCountResponse(BaseModel):
    valid: bool
    char_count: int
    max_chars: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "social-media-writer"}


@app.get("/platforms")
async def get_platforms():
    """Return the list of supported platforms."""
    return {"platforms": PLATFORMS}


@app.get("/tones")
async def get_tones():
    """Return the list of supported tones."""
    return {"tones": TONES}


@app.post("/generate", response_model=TextResponse)
async def api_generate_posts(req: GeneratePostsRequest):
    """Generate social media posts."""
    try:
        result = generate_posts(
            platform=req.platform,
            topic=req.topic,
            tone=req.tone,
            variants=req.variants,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-char-count", response_model=CharCountResponse)
async def api_validate_char_count(req: ValidateCharCountRequest):
    """Validate character count for a platform."""
    try:
        valid, char_count, max_chars = validate_char_count(
            content=req.content,
            platform=req.platform,
        )
        return CharCountResponse(
            valid=valid, char_count=char_count, max_chars=max_chars
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hashtags", response_model=TextResponse)
async def api_generate_hashtags(req: GenerateHashtagsRequest):
    """Generate hashtags for a topic."""
    try:
        result = generate_hashtags(
            topic=req.topic,
            platform=req.platform,
            count=req.count,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schedule/{platform}")
async def api_suggest_schedule(platform: str):
    """Suggest posting schedule for a platform."""
    try:
        schedule = suggest_schedule(platform=platform)
        return {"platform": platform, "schedule": schedule}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ab-variants", response_model=TextResponse)
async def api_generate_ab_variants(req: GenerateAbVariantsRequest):
    """Generate A/B test variants."""
    try:
        result = generate_ab_variants(
            topic=req.topic,
            platform=req.platform,
            tone=req.tone,
            num_variants=req.num_variants,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/format", response_model=TextResponse)
async def api_format_for_platform(req: FormatForPlatformRequest):
    """Format content for a specific platform."""
    try:
        result = format_for_platform(
            content=req.content,
            platform=req.platform,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preview")
async def api_preview_post(req: PreviewPostRequest):
    """Preview a post as it would appear on a platform."""
    try:
        return preview_post(content=req.content, platform=req.platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
