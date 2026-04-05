"""EHR De-Identifier API - AI and regex-powered PHI removal for electronic health records.

⚠️ HIPAA DISCLAIMER: This tool is provided as-is for de-identification purposes.
It does not guarantee full HIPAA compliance. Always verify de-identification results
and consult your compliance team before using in production environments.
"""

from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import (
    DISCLAIMER,
    HIPAA_IDENTIFIERS,
    configurable_regex_preprocess,
    deidentify_text,
    regex_preprocess,
)

HIPAA_DISCLAIMER = (
    "⚠️ This tool is provided as-is for de-identification purposes. "
    "It does not guarantee full HIPAA compliance. Always verify results "
    "and consult your compliance team before using in production."
)

app = FastAPI(
    title="EHR De-Identifier",
    description=(
        "AI-powered and regex-based de-identification of Protected Health "
        "Information (PHI) from electronic health records.\n\n"
        f"**{HIPAA_DISCLAIMER}**"
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class DeidentifyRequest(BaseModel):
    text: str = Field(..., description="Clinical text containing PHI to de-identify.")


class DeidentifyResponse(BaseModel):
    deidentified_text: str
    replacements: Optional[List[dict]] = None
    # Additional fields returned by core may be included dynamically.


class RegexDeidentifyResponse(BaseModel):
    processed_text: str
    replacements: List[dict]


class ConfigurableDeidentifyRequest(BaseModel):
    text: str = Field(..., description="Clinical text containing PHI to de-identify.")
    rules: Optional[Dict] = Field(
        None,
        description="Optional custom regex rules to apply during de-identification.",
    )


class ConfigurableDeidentifyResponse(BaseModel):
    processed_text: str
    replacements: List[dict]


class HipaaIdentifiersResponse(BaseModel):
    identifiers: List[str]


class DisclaimerResponse(BaseModel):
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    service: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    return HealthResponse(status="healthy", service="ehr-deidentifier")


@app.post("/deidentify", response_model=DeidentifyResponse, tags=["De-identify"])
async def deidentify(request: DeidentifyRequest):
    """De-identify clinical text using AI to remove Protected Health Information."""
    try:
        result = deidentify_text(request.text)
        return DeidentifyResponse(
            deidentified_text=result.get("deidentified_text", ""),
            replacements=result.get("replacements"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI de-identification failed: {e}")


@app.post("/deidentify/regex", response_model=RegexDeidentifyResponse, tags=["De-identify"])
async def deidentify_regex(request: DeidentifyRequest):
    """De-identify clinical text using regex-based pattern matching only."""
    try:
        processed_text, replacements = regex_preprocess(request.text)
        return RegexDeidentifyResponse(
            processed_text=processed_text,
            replacements=replacements,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regex de-identification failed: {e}")


@app.post("/deidentify/configurable", response_model=ConfigurableDeidentifyResponse, tags=["De-identify"])
async def deidentify_configurable(request: ConfigurableDeidentifyRequest):
    """De-identify clinical text using configurable regex rules."""
    try:
        processed_text, replacements = configurable_regex_preprocess(
            text=request.text,
            rules=request.rules,
        )
        return ConfigurableDeidentifyResponse(
            processed_text=processed_text,
            replacements=replacements,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configurable de-identification failed: {e}")


@app.get("/hipaa-identifiers", response_model=HipaaIdentifiersResponse, tags=["Info"])
async def get_hipaa_identifiers():
    """Return the list of HIPAA-defined identifier categories."""
    return HipaaIdentifiersResponse(identifiers=list(HIPAA_IDENTIFIERS))


@app.get("/disclaimer", response_model=DisclaimerResponse, tags=["Info"])
async def get_disclaimer():
    """Return the HIPAA disclaimer for this service."""
    return DisclaimerResponse(disclaimer=DISCLAIMER)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
