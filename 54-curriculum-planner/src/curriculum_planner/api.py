"""FastAPI REST API for Curriculum Planner."""

from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from curriculum_planner.core import (
    generate_curriculum,
    validate_curriculum_data,
    build_course_design,
)

app = FastAPI(
    title="Curriculum Planner API",
    description="REST API for Curriculum Planner",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class GenerateCurriculumRequest(BaseModel):
    course: str = Field(..., description="Course name or subject")
    weeks: int = Field(..., description="Number of weeks for the curriculum")
    level: str = Field(..., description="Difficulty / audience level (e.g. 'beginner')")
    focus: str = Field("", description="Optional focus area or emphasis")


class ValidateCurriculumRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Curriculum data to validate")


class BuildCourseDesignRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Curriculum data to build a CourseDesign from")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "curriculum-planner"}


@app.post("/generate")
async def api_generate_curriculum(request: GenerateCurriculumRequest):
    try:
        result = generate_curriculum(
            request.course, request.weeks, request.level, request.focus
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate")
async def api_validate_curriculum(request: ValidateCurriculumRequest):
    try:
        errors = validate_curriculum_data(request.data)
        return {"errors": errors, "valid": len(errors) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build-course-design")
async def api_build_course_design(request: BuildCourseDesignRequest):
    try:
        result = build_course_design(request.data)
        # CourseDesign dataclass → dict
        if hasattr(result, "__dataclass_fields__"):
            return asdict(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
