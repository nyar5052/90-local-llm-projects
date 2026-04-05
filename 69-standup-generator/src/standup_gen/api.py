"""Standup Generator - FastAPI application."""

from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .core import (
    generate_standup,
    generate_weekly_summary,
    generate_sprint_review,
    categorize_tasks,
    extract_ticket_refs,
    get_git_log,
    get_git_branches,
    save_standup,
    load_standup_history,
    STANDUP_TEMPLATES,
)

app = FastAPI(title="Standup Generator", version="1.0.0")


# --- Request Models ---

class GenerateStandupRequest(BaseModel):
    tasks: str
    git_log: str = ""
    team: str = ""
    project: str = ""
    template: str = "daily"
    config: Optional[dict] = None


class WeeklySummaryRequest(BaseModel):
    tasks: str
    git_log: str = ""
    config: Optional[dict] = None


class SprintReviewRequest(BaseModel):
    tasks: str
    sprint_name: str = "Current Sprint"
    config: Optional[dict] = None


class CategorizeTasksRequest(BaseModel):
    tasks: str


class ExtractTicketsRequest(BaseModel):
    text: str


class SaveStandupRequest(BaseModel):
    standup: str
    team_member: str = ""


# --- Response Models ---

class HealthResponse(BaseModel):
    status: str
    templates: List[str]


class GeneratedTextResponse(BaseModel):
    result: str


class CategorizedTasksResponse(BaseModel):
    completed: List[str]
    in_progress: List[str]
    planned: List[str]
    blocked: List[str]


class TicketRefsResponse(BaseModel):
    tickets: List[str]


class SavedStandupResponse(BaseModel):
    standup: dict


class TemplatesResponse(BaseModel):
    templates: dict


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        templates=list(STANDUP_TEMPLATES.keys()),
    )


@app.post("/standup/generate", response_model=GeneratedTextResponse)
async def api_generate_standup(request: GenerateStandupRequest):
    try:
        result = generate_standup(
            tasks=request.tasks,
            git_log=request.git_log,
            team=request.team,
            project=request.project,
            template=request.template,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/standup/weekly-summary", response_model=GeneratedTextResponse)
async def api_weekly_summary(request: WeeklySummaryRequest):
    try:
        result = generate_weekly_summary(
            tasks=request.tasks,
            git_log=request.git_log,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/standup/sprint-review", response_model=GeneratedTextResponse)
async def api_sprint_review(request: SprintReviewRequest):
    try:
        result = generate_sprint_review(
            tasks=request.tasks,
            sprint_name=request.sprint_name,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/categorize", response_model=CategorizedTasksResponse)
async def api_categorize_tasks(request: CategorizeTasksRequest):
    try:
        result = categorize_tasks(tasks=request.tasks)
        return CategorizedTasksResponse(
            completed=result.get("completed", []),
            in_progress=result.get("in_progress", []),
            planned=result.get("planned", []),
            blocked=result.get("blocked", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/extract-tickets", response_model=TicketRefsResponse)
async def api_extract_tickets(request: ExtractTicketsRequest):
    try:
        tickets = extract_ticket_refs(text=request.text)
        return TicketRefsResponse(tickets=tickets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/standup/save", response_model=SavedStandupResponse)
async def api_save_standup(request: SaveStandupRequest):
    try:
        result = save_standup(
            standup=request.standup,
            team_member=request.team_member,
        )
        return SavedStandupResponse(standup=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/standup/history", response_model=List[dict])
async def api_standup_history(days: int = 7):
    try:
        return load_standup_history(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates", response_model=TemplatesResponse)
async def api_get_templates():
    return TemplatesResponse(templates=STANDUP_TEMPLATES)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
