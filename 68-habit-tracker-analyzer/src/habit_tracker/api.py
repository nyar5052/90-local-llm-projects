"""Habit Tracker Analyzer - FastAPI application."""

from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .core import (
    log_habit,
    add_habit,
    delete_habit,
    load_habits,
    compute_streaks,
    get_completion_rate,
    compute_correlations,
    check_achievements,
    get_calendar_data,
    generate_weekly_report,
    generate_monthly_report,
    analyze_habits,
)

app = FastAPI(title="Habit Tracker Analyzer", version="1.0.0")


# --- Request Models ---

class AddHabitRequest(BaseModel):
    name: str
    category: str = "general"
    target: str = "daily"


class LogHabitRequest(BaseModel):
    habit_name: str
    done: bool = True
    notes: str = ""


class AnalyzeHabitsRequest(BaseModel):
    period: str
    config: Optional[dict] = None


# --- Response Models ---

class HealthResponse(BaseModel):
    status: str


class HabitResponse(BaseModel):
    habit: dict


class DeleteResponse(BaseModel):
    deleted: bool


class LogResponse(BaseModel):
    entry: dict


class StreaksResponse(BaseModel):
    streaks: dict


class CompletionRateResponse(BaseModel):
    rates: dict


class CorrelationsResponse(BaseModel):
    correlations: dict


class AchievementsResponse(BaseModel):
    achievements: List[dict]


class CalendarResponse(BaseModel):
    calendar: dict


class ReportResponse(BaseModel):
    report: str


class AnalysisResponse(BaseModel):
    analysis: str


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


@app.post("/habits", response_model=HabitResponse)
async def api_add_habit(request: AddHabitRequest):
    try:
        result = add_habit(
            name=request.name,
            category=request.category,
            target=request.target,
        )
        return HabitResponse(habit=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/habits/{habit_key}", response_model=DeleteResponse)
async def api_delete_habit(habit_key: str):
    try:
        deleted = delete_habit(habit_key=habit_key)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Habit '{habit_key}' not found")
        return DeleteResponse(deleted=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/habits/log", response_model=LogResponse)
async def api_log_habit(request: LogHabitRequest):
    try:
        result = log_habit(
            habit_name=request.habit_name,
            done=request.done,
            notes=request.notes,
        )
        return LogResponse(entry=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/habits", response_model=dict)
async def api_load_habits():
    try:
        return load_habits()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/habits/streaks", response_model=StreaksResponse)
async def api_get_streaks():
    try:
        data = load_habits()
        streaks = compute_streaks(data)
        return StreaksResponse(streaks=streaks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/habits/completion-rate", response_model=CompletionRateResponse)
async def api_get_completion_rate(days: int = 30):
    try:
        data = load_habits()
        rates = get_completion_rate(data, days=days)
        return CompletionRateResponse(rates=rates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/habits/correlations", response_model=CorrelationsResponse)
async def api_get_correlations():
    try:
        data = load_habits()
        correlations = compute_correlations(data)
        return CorrelationsResponse(correlations=correlations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/habits/achievements", response_model=AchievementsResponse)
async def api_get_achievements():
    try:
        data = load_habits()
        achievements = check_achievements(data)
        return AchievementsResponse(achievements=achievements)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/habits/{habit_key}/calendar", response_model=CalendarResponse)
async def api_get_calendar(habit_key: str, months: int = 3):
    try:
        data = load_habits()
        calendar = get_calendar_data(data, habit_key=habit_key, months=months)
        return CalendarResponse(calendar=calendar)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/weekly", response_model=ReportResponse)
async def api_weekly_report():
    try:
        data = load_habits()
        report = generate_weekly_report(data)
        return ReportResponse(report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/monthly", response_model=ReportResponse)
async def api_monthly_report():
    try:
        data = load_habits()
        report = generate_monthly_report(data)
        return ReportResponse(report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/habits/analyze", response_model=AnalysisResponse)
async def api_analyze_habits(request: AnalyzeHabitsRequest):
    try:
        data = load_habits()
        analysis = analyze_habits(
            data=data,
            period=request.period,
            config=request.config,
        )
        return AnalysisResponse(analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
