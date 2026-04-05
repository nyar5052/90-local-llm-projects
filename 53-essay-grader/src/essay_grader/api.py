"""FastAPI REST API for Essay Grader."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from essay_grader.core import (
    grade_essay,
    generate_annotations,
    check_plagiarism_indicators,
    calculate_grade_letter,
    validate_grade_data,
    PRESET_RUBRICS,
)

app = FastAPI(
    title="Essay Grader API",
    description="REST API for Essay Grader",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class GradeEssayRequest(BaseModel):
    essay_text: str = Field(..., description="Full text of the essay to grade")
    rubric_criteria: Optional[List[str]] = Field(None, description="Custom rubric criteria list")
    context: str = Field("", description="Additional context for grading (e.g. assignment prompt)")


class AnnotationsRequest(BaseModel):
    essay_text: str = Field(..., description="Essay text to annotate")


class PlagiarismCheckRequest(BaseModel):
    essay_text: str = Field(..., description="Essay text to check for plagiarism indicators")


class GradeLetterRequest(BaseModel):
    score: float = Field(..., description="Numeric score to convert to a letter grade")


class ValidateGradeDataRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Grade data to validate")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "essay-grader"}


@app.get("/preset-rubrics")
async def get_preset_rubrics():
    """Return available preset rubric keys and their criteria."""
    return {"rubrics": {k: v for k, v in PRESET_RUBRICS.items()}}


@app.post("/grade")
async def api_grade_essay(request: GradeEssayRequest):
    try:
        result = grade_essay(request.essay_text, request.rubric_criteria, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/annotations")
async def api_generate_annotations(request: AnnotationsRequest):
    try:
        annotations = generate_annotations(request.essay_text)
        # Ensure each annotation is a dict (handles dataclass / named-tuple objects)
        result = [
            a if isinstance(a, dict) else (a.__dict__ if hasattr(a, "__dict__") else a)
            for a in annotations
        ]
        return {"annotations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-plagiarism")
async def api_check_plagiarism(request: PlagiarismCheckRequest):
    try:
        result = check_plagiarism_indicators(request.essay_text)
        # PlagiarismIndicator → dict
        if hasattr(result, "__dict__"):
            return result.__dict__
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-grade-letter")
async def api_calculate_grade_letter(request: GradeLetterRequest):
    try:
        letter = calculate_grade_letter(request.score)
        return {"score": request.score, "letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate")
async def api_validate_grade_data(request: ValidateGradeDataRequest):
    try:
        errors = validate_grade_data(request.data)
        return {"errors": errors, "valid": len(errors) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
