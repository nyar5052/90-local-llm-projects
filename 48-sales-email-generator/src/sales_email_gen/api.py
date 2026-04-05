"""FastAPI REST API for Sales Email Generator."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from sales_email_gen.core import (
    generate_email,
    generate_variants,
    research_prospect,
    generate_follow_up_sequence,
    score_personalization,
    get_template,
    list_templates,
)

TONE_DESCRIPTIONS = {
    "professional": "Formal and business-appropriate",
    "casual": "Friendly and conversational",
    "persuasive": "Compelling and action-oriented",
    "consultative": "Advisory and solution-focused",
}

app = FastAPI(
    title="Sales Email Generator API",
    description="REST API for Sales Email Generator",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class GenerateEmailRequest(BaseModel):
    prospect: str = Field(..., description="Name or description of the prospect")
    product: str = Field(..., description="Product or service being offered")
    tone: str = Field(..., description="Tone of the email (professional, casual, persuasive, consultative)")
    context: Optional[str] = Field("", description="Additional context for the email")
    follow_up: Optional[bool] = Field(False, description="Whether this is a follow-up email")


class GenerateVariantsRequest(BaseModel):
    prospect: str = Field(..., description="Name or description of the prospect")
    product: str = Field(..., description="Product or service being offered")
    tone: str = Field(..., description="Tone of the email")
    count: Optional[int] = Field(3, description="Number of variants to generate", ge=1, le=10)


class ResearchProspectRequest(BaseModel):
    prospect_info: str = Field(..., description="Information about the prospect to research")


class FollowUpSequenceRequest(BaseModel):
    prospect: str = Field(..., description="Name or description of the prospect")
    product: str = Field(..., description="Product or service being offered")
    tone: str = Field(..., description="Tone of the emails")
    num_emails: Optional[int] = Field(4, description="Number of emails in the sequence", ge=1, le=10)


class ScorePersonalizationRequest(BaseModel):
    email_body: str = Field(..., description="The email body text to evaluate")
    prospect_info: str = Field(..., description="Known information about the prospect")


class GetTemplateRequest(BaseModel):
    template_name: str = Field(..., description="Name of the template to retrieve")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sales-email-generator"}


@app.get("/tones")
async def get_tones():
    """Return available tone options and their descriptions."""
    return TONE_DESCRIPTIONS


@app.get("/templates")
async def api_list_templates():
    """List all available email templates."""
    try:
        result = list_templates()
        return {"templates": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-email")
async def api_generate_email(request: GenerateEmailRequest):
    """Generate a sales email for a prospect."""
    try:
        result = generate_email(
            request.prospect,
            request.product,
            request.tone,
            context=request.context,
            follow_up=request.follow_up,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-variants")
async def api_generate_variants(request: GenerateVariantsRequest):
    """Generate multiple email variants for A/B testing."""
    try:
        result = generate_variants(
            request.prospect,
            request.product,
            request.tone,
            count=request.count,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research-prospect")
async def api_research_prospect(request: ResearchProspectRequest):
    """Research a prospect and return structured information."""
    try:
        result = research_prospect(request.prospect_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-follow-up-sequence")
async def api_generate_follow_up_sequence(request: FollowUpSequenceRequest):
    """Generate a multi-email follow-up sequence."""
    try:
        result = generate_follow_up_sequence(
            request.prospect,
            request.product,
            request.tone,
            num_emails=request.num_emails,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score-personalization")
async def api_score_personalization(request: ScorePersonalizationRequest):
    """Score how well an email is personalized to a prospect."""
    try:
        result = score_personalization(request.email_body, request.prospect_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-template")
async def api_get_template(request: GetTemplateRequest):
    """Retrieve a specific email template by name."""
    try:
        result = get_template(request.template_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
