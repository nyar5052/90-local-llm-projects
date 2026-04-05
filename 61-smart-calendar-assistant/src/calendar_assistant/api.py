from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any
import uvicorn

from .core import (
    optimize_schedule,
    suggest_meeting_time,
    analyze_workload,
    detect_conflicts,
    score_priority,
    generate_daily_agenda,
    convert_timezone,
)

app = FastAPI(title="Smart Calendar Assistant", version="1.0.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class EventItem(BaseModel):
    title: str = ""
    start: str = ""
    end: str = ""
    priority: Optional[int] = None
    attendees: Optional[List[str]] = None
    location: Optional[str] = None
    description: Optional[str] = None

    class Config:
        extra = "allow"


class OptimizeRequest(BaseModel):
    events: List[dict]


class SuggestMeetingRequest(BaseModel):
    events: List[dict]
    meeting_duration: int = 30
    attendees: Optional[str] = None


class AnalyzeWorkloadRequest(BaseModel):
    events: List[dict]


class DetectConflictsRequest(BaseModel):
    events: List[dict]
    timezone: Optional[str] = None


class ScorePriorityRequest(BaseModel):
    event: dict


class DailyAgendaRequest(BaseModel):
    events: List[dict]
    date: Optional[str] = None
    timezone: Optional[str] = None


class ConvertTimezoneRequest(BaseModel):
    events: List[dict]
    from_tz: str
    to_tz: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/schedule/optimize")
def api_optimize_schedule(req: OptimizeRequest):
    try:
        result = optimize_schedule(req.events)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/suggest-meeting")
def api_suggest_meeting(req: SuggestMeetingRequest):
    try:
        result = suggest_meeting_time(
            req.events,
            meeting_duration=req.meeting_duration,
            attendees=req.attendees,
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/analyze-workload")
def api_analyze_workload(req: AnalyzeWorkloadRequest):
    try:
        result = analyze_workload(req.events)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/detect-conflicts")
def api_detect_conflicts(req: DetectConflictsRequest):
    try:
        conflicts = detect_conflicts(req.events, timezone=req.timezone)
        return {"conflicts": conflicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/score-priority")
def api_score_priority(req: ScorePriorityRequest):
    try:
        score = score_priority(req.event)
        return {"score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/daily-agenda")
def api_daily_agenda(req: DailyAgendaRequest):
    try:
        agenda = generate_daily_agenda(
            req.events, date=req.date, timezone=req.timezone
        )
        return {"agenda": agenda}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule/convert-timezone")
def api_convert_timezone(req: ConvertTimezoneRequest):
    try:
        converted = convert_timezone(req.events, req.from_tz, req.to_tz)
        return {"events": converted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
