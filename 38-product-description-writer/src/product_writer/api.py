"""FastAPI REST API for Product Description Writer."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from product_writer.core import (
    generate_descriptions,
    generate_ab_variants,
    map_features_to_benefits,
    calculate_seo_score,
    get_platform_configs,
    get_feature_benefit_map,
)

app = FastAPI(
    title="Product Description Writer API",
    description="REST API for Product Description Writer",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class DescriptionRequest(BaseModel):
    product: str = Field(..., description="Product name")
    features: List[str] = Field(..., description="List of product features")
    platform: str = Field(..., description="Target platform")
    length: str = Field(..., description="Desired description length")
    variants: int = Field(..., description="Number of description variants")
    keywords: Optional[List[str]] = Field(None, description="SEO keywords")


class ABVariantsRequest(BaseModel):
    product: str = Field(..., description="Product name")
    features: List[str] = Field(..., description="List of product features")
    platform: str = Field(..., description="Target platform")


class FeaturesToBenefitsRequest(BaseModel):
    features: List[str] = Field(..., description="List of product features")


class SEOScoreRequest(BaseModel):
    text: str = Field(..., description="Text to evaluate")
    keywords: List[str] = Field(..., description="Target keywords")


class TextResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-description-writer"}


@app.post("/generate-descriptions", response_model=TextResponse)
async def api_generate_descriptions(req: DescriptionRequest):
    try:
        result = generate_descriptions(
            product=req.product,
            features=req.features,
            platform=req.platform,
            length=req.length,
            variants=req.variants,
            keywords=req.keywords,
        )
        return TextResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/generate-ab-variants")
async def api_generate_ab_variants(req: ABVariantsRequest):
    try:
        result = generate_ab_variants(
            product=req.product,
            features=req.features,
            platform=req.platform,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/map-features-to-benefits")
async def api_map_features_to_benefits(req: FeaturesToBenefitsRequest):
    try:
        result = map_features_to_benefits(features=req.features)
        return {"result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/calculate-seo-score")
async def api_calculate_seo_score(req: SEOScoreRequest):
    try:
        result = calculate_seo_score(text=req.text, keywords=req.keywords)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/platform-configs")
async def api_get_platform_configs():
    try:
        return get_platform_configs()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/feature-benefit-map")
async def api_get_feature_benefit_map():
    try:
        return get_feature_benefit_map()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
