"""FastAPI REST API for Email Campaign Writer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from email_campaign.core import (
    generate_campaign,
    generate_subject_variants,
    build_email_sequence,
    extract_personalization_tokens,
    preview_html,
    estimate_campaign_metrics,
    CAMPAIGN_TYPES,
)

app = FastAPI(
    title="Email Campaign Writer API",
    description="REST API for Email Campaign Writer",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GenerateCampaignRequest(BaseModel):
    product: str = Field(..., description="Product or service name")
    audience: str = Field(..., description="Target audience description")
    num_emails: int = Field(..., description="Number of emails in the campaign")
    campaign_type: str = Field(
        ..., description=f"Campaign type. Options: {CAMPAIGN_TYPES}"
    )


class GenerateSubjectVariantsRequest(BaseModel):
    product: str = Field(..., description="Product or service name")
    audience: str = Field(..., description="Target audience description")
    num_variants: int = Field(3, description="Number of subject line variants")


class BuildEmailSequenceRequest(BaseModel):
    product: str = Field(..., description="Product or service name")
    audience: str = Field(..., description="Target audience description")
    num_emails: int = Field(..., description="Number of emails in the sequence")
    campaign_type: str = Field(
        ..., description=f"Campaign type. Options: {CAMPAIGN_TYPES}"
    )


class ExtractTokensRequest(BaseModel):
    template: str = Field(..., description="Email template string")


class PreviewHtmlRequest(BaseModel):
    email_body: str = Field(..., description="Email body content (markdown/text)")


class EstimateMetricsRequest(BaseModel):
    product: str = Field(..., description="Product or service name")
    audience: str = Field(..., description="Target audience description")
    num_emails: int = Field(..., description="Number of emails in the campaign")
    campaign_type: str = Field(
        ..., description=f"Campaign type. Options: {CAMPAIGN_TYPES}"
    )


class TextResponse(BaseModel):
    result: str


class SubjectVariantsResponse(BaseModel):
    variants: List[str]


class TokensResponse(BaseModel):
    tokens: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "email-campaign-writer"}


@app.get("/campaign-types")
async def get_campaign_types():
    """Return the list of supported campaign types."""
    return {"campaign_types": CAMPAIGN_TYPES}


@app.post("/generate", response_model=TextResponse)
async def api_generate_campaign(req: GenerateCampaignRequest):
    """Generate a full email campaign."""
    try:
        result = generate_campaign(
            product=req.product,
            audience=req.audience,
            num_emails=req.num_emails,
            campaign_type=req.campaign_type,
        )
        return TextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/subject-variants", response_model=SubjectVariantsResponse)
async def api_generate_subject_variants(req: GenerateSubjectVariantsRequest):
    """Generate subject line variants."""
    try:
        variants = generate_subject_variants(
            product=req.product,
            audience=req.audience,
            num_variants=req.num_variants,
        )
        return SubjectVariantsResponse(variants=variants)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build-sequence")
async def api_build_email_sequence(req: BuildEmailSequenceRequest):
    """Build a structured email sequence (Campaign object)."""
    try:
        campaign = build_email_sequence(
            product=req.product,
            audience=req.audience,
            num_emails=req.num_emails,
            campaign_type=req.campaign_type,
        )
        return campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract-tokens", response_model=TokensResponse)
async def api_extract_personalization_tokens(req: ExtractTokensRequest):
    """Extract personalization tokens from an email template."""
    try:
        tokens = extract_personalization_tokens(template=req.template)
        return TokensResponse(tokens=tokens)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preview-html", response_model=TextResponse)
async def api_preview_html(req: PreviewHtmlRequest):
    """Preview an email body as rendered HTML."""
    try:
        html = preview_html(email_body=req.email_body)
        return TextResponse(result=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estimate-metrics")
async def api_estimate_campaign_metrics(req: EstimateMetricsRequest):
    """Estimate campaign performance metrics."""
    try:
        campaign = build_email_sequence(
            product=req.product,
            audience=req.audience,
            num_emails=req.num_emails,
            campaign_type=req.campaign_type,
        )
        return estimate_campaign_metrics(campaign=campaign)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
