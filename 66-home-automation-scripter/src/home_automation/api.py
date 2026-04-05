"""Home Automation Scripter - FastAPI application."""

from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .core import (
    generate_automation,
    explain_automation,
    suggest_automations,
    validate_script,
    list_templates,
    get_template,
    get_template_categories,
    generate_from_template,
    load_rules,
    save_rule,
    delete_rule,
    PLATFORM_TEMPLATES,
)

app = FastAPI(title="Home Automation Scripter", version="1.0.0")


# --- Request Models ---

class GenerateAutomationRequest(BaseModel):
    rule_description: str
    platform: str
    config: Optional[dict] = None


class ExplainAutomationRequest(BaseModel):
    script: str
    platform: str
    config: Optional[dict] = None


class SuggestAutomationsRequest(BaseModel):
    devices: str
    config: Optional[dict] = None


class ValidateScriptRequest(BaseModel):
    script: str
    platform: str


class GenerateFromTemplateRequest(BaseModel):
    platform: str
    params: dict


class SaveRuleRequest(BaseModel):
    rule: dict
    config: Optional[dict] = None


# --- Response Models ---

class HealthResponse(BaseModel):
    status: str
    platforms: List[str]


class GeneratedTextResponse(BaseModel):
    result: str


class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]


class TemplateResponse(BaseModel):
    template: dict


class RuleResponse(BaseModel):
    rule: dict


class DeleteResponse(BaseModel):
    deleted: bool


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        platforms=list(PLATFORM_TEMPLATES.keys()),
    )


@app.post("/automation/generate", response_model=GeneratedTextResponse)
async def api_generate_automation(request: GenerateAutomationRequest):
    try:
        result = generate_automation(
            rule_description=request.rule_description,
            platform=request.platform,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automation/explain", response_model=GeneratedTextResponse)
async def api_explain_automation(request: ExplainAutomationRequest):
    try:
        result = explain_automation(
            script=request.script,
            platform=request.platform,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automation/suggest", response_model=GeneratedTextResponse)
async def api_suggest_automations(request: SuggestAutomationsRequest):
    try:
        result = suggest_automations(
            devices=request.devices,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automation/validate", response_model=ValidationResponse)
async def api_validate_script(request: ValidateScriptRequest):
    try:
        result = validate_script(script=request.script, platform=request.platform)
        return ValidationResponse(
            valid=result.get("valid", False),
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates", response_model=List[dict])
async def api_list_templates(category: Optional[str] = None):
    try:
        return list_templates(category=category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates/categories", response_model=List[str])
async def api_get_template_categories():
    try:
        return get_template_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates/{template_id}", response_model=TemplateResponse)
async def api_get_template(template_id: str):
    try:
        template = get_template(template_id)
        if template is None:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
        return TemplateResponse(template=template)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/templates/{template_id}/generate", response_model=GeneratedTextResponse)
async def api_generate_from_template(template_id: str, request: GenerateFromTemplateRequest):
    try:
        result = generate_from_template(
            template_id=template_id,
            platform=request.platform,
            params=request.params,
        )
        if result is None:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
        return GeneratedTextResponse(result=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rules", response_model=List[dict])
async def api_load_rules(config: Optional[str] = None):
    try:
        cfg = None if config is None else {"path": config}
        return load_rules(config=cfg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rules", response_model=RuleResponse)
async def api_save_rule(request: SaveRuleRequest):
    try:
        result = save_rule(rule=request.rule, config=request.config)
        return RuleResponse(rule=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/rules/{rule_id}", response_model=DeleteResponse)
async def api_delete_rule(rule_id: int):
    try:
        deleted = delete_rule(rule_id=rule_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
        return DeleteResponse(deleted=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
