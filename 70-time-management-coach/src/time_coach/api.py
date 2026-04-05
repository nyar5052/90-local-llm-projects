"""Time Management Coach - FastAPI application."""

from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .core import (
    compute_time_breakdown,
    compute_daily_totals,
    compute_productivity_score,
    generate_time_blocks,
    analyze_time_usage,
    get_tips,
    generate_pomodoro_plan,
    generate_weekly_review,
    get_focus_time_stats,
    get_category_breakdown,
    compute_trends,
    save_time_entry,
)

app = FastAPI(title="Time Management Coach", version="1.0.0")


# --- Request Models ---

class EntriesRequest(BaseModel):
    entries: List[dict]


class ProductivityScoreRequest(BaseModel):
    breakdown: dict
    config: Optional[dict] = None


class GenerateBlocksRequest(BaseModel):
    tasks: str
    available_hours: float = 8.0
    config: Optional[dict] = None


class AnalyzeTimeRequest(BaseModel):
    entries: List[dict]
    config: Optional[dict] = None


class TipsRequest(BaseModel):
    goal: str
    config: Optional[dict] = None


class PomodoroRequest(BaseModel):
    tasks: str
    available_hours: float = 8.0
    config: Optional[dict] = None


class WeeklyReviewRequest(BaseModel):
    entries: List[dict]
    config: Optional[dict] = None


class FocusStatsRequest(BaseModel):
    entries: List[dict]
    config: Optional[dict] = None


class CategoryBreakdownRequest(BaseModel):
    entries: List[dict]
    period_days: int = 7


class TrendsRequest(BaseModel):
    entries: List[dict]
    weeks: int = 4


# --- Response Models ---

class HealthResponse(BaseModel):
    status: str


class BreakdownResponse(BaseModel):
    breakdown: dict


class DailyTotalsResponse(BaseModel):
    totals: dict


class ProductivityScoreResponse(BaseModel):
    score: float
    factors: dict
    suggestions: List[str]


class GeneratedTextResponse(BaseModel):
    result: str


class FocusStatsResponse(BaseModel):
    stats: dict


class CategoryBreakdownResponse(BaseModel):
    categories: dict


class TrendsResponse(BaseModel):
    trends: dict


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


@app.post("/time/breakdown", response_model=BreakdownResponse)
async def api_time_breakdown(request: EntriesRequest):
    try:
        breakdown = compute_time_breakdown(entries=request.entries)
        return BreakdownResponse(breakdown=breakdown)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/daily-totals", response_model=DailyTotalsResponse)
async def api_daily_totals(request: EntriesRequest):
    try:
        totals = compute_daily_totals(entries=request.entries)
        return DailyTotalsResponse(totals=totals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/productivity-score", response_model=ProductivityScoreResponse)
async def api_productivity_score(request: ProductivityScoreRequest):
    try:
        result = compute_productivity_score(
            breakdown=request.breakdown,
            config=request.config,
        )
        return ProductivityScoreResponse(
            score=result.get("score", 0.0),
            factors=result.get("factors", {}),
            suggestions=result.get("suggestions", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/generate-blocks", response_model=GeneratedTextResponse)
async def api_generate_blocks(request: GenerateBlocksRequest):
    try:
        result = generate_time_blocks(
            tasks=request.tasks,
            available_hours=request.available_hours,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/analyze", response_model=GeneratedTextResponse)
async def api_analyze_time(request: AnalyzeTimeRequest):
    try:
        breakdown = compute_time_breakdown(entries=request.entries)
        daily = compute_daily_totals(entries=request.entries)
        result = analyze_time_usage(
            entries=request.entries,
            breakdown=breakdown,
            daily=daily,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/tips", response_model=GeneratedTextResponse)
async def api_get_tips(request: TipsRequest):
    try:
        result = get_tips(goal=request.goal, config=request.config)
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/pomodoro-plan", response_model=GeneratedTextResponse)
async def api_pomodoro_plan(request: PomodoroRequest):
    try:
        result = generate_pomodoro_plan(
            tasks=request.tasks,
            available_hours=request.available_hours,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/weekly-review", response_model=GeneratedTextResponse)
async def api_weekly_review(request: WeeklyReviewRequest):
    try:
        result = generate_weekly_review(
            entries=request.entries,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/focus-stats", response_model=FocusStatsResponse)
async def api_focus_stats(request: FocusStatsRequest):
    try:
        stats = get_focus_time_stats(
            entries=request.entries,
            config=request.config,
        )
        return FocusStatsResponse(stats=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/category-breakdown", response_model=CategoryBreakdownResponse)
async def api_category_breakdown(request: CategoryBreakdownRequest):
    try:
        categories = get_category_breakdown(
            entries=request.entries,
            period_days=request.period_days,
        )
        return CategoryBreakdownResponse(categories=categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/time/trends", response_model=TrendsResponse)
async def api_trends(request: TrendsRequest):
    try:
        trends = compute_trends(
            entries=request.entries,
            weeks=request.weeks,
        )
        return TrendsResponse(trends=trends)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
