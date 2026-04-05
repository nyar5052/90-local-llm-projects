"""FastAPI REST API for Reading Comprehension Builder."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from reading_comp.core import (
    generate_comprehension,
    score_exercise,
    get_answer_key,
    check_service,
    ReadingExercise,
)

app = FastAPI(
    title="Reading Comprehension Builder API",
    description="REST API for Reading Comprehension Builder",
    version="1.0.0",
)


# --- Request Models ---


class GenerateComprehensionRequest(BaseModel):
    topic: str = Field(..., description="Topic for the reading passage")
    level: str = Field("high school", description="Reading level")
    num_questions: int = Field(5, description="Number of comprehension questions")
    passage_length: str = Field("medium", description="Passage length: short, medium, or long")


class QuestionModel(BaseModel):
    question: str
    options: List[str] = []
    correct_answer: str = ""
    explanation: str = ""
    question_type: str = ""


class ExerciseModel(BaseModel):
    topic: str = ""
    level: str = ""
    passage: str = ""
    questions: List[QuestionModel] = []
    metadata: Dict[str, Any] = {}


class ScoreExerciseRequest(BaseModel):
    exercise: ExerciseModel = Field(..., description="The reading exercise to score against")
    user_answers: Dict[int, str] = Field(..., description="Map of question index to user answer")


class AnswerKeyRequest(BaseModel):
    exercise: ExerciseModel = Field(..., description="The reading exercise to get answers for")


# --- Helpers ---


def _exercise_from_dict(data: ExerciseModel) -> ReadingExercise:
    """Reconstruct a ReadingExercise from the Pydantic model."""
    return ReadingExercise(
        topic=data.topic,
        level=data.level,
        passage=data.passage,
        questions=[q.model_dump() for q in data.questions],
        metadata=data.metadata,
    )


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "reading-comprehension-builder"}


@app.get("/service-check")
async def api_check_service():
    try:
        result = check_service()
        return {"available": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def api_generate_comprehension(request: GenerateComprehensionRequest):
    try:
        result = generate_comprehension(
            topic=request.topic,
            level=request.level,
            num_questions=request.num_questions,
            passage_length=request.passage_length,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score")
async def api_score_exercise(request: ScoreExerciseRequest):
    try:
        exercise = _exercise_from_dict(request.exercise)
        result = score_exercise(
            exercise=exercise,
            user_answers=request.user_answers,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer-key")
async def api_get_answer_key(request: AnswerKeyRequest):
    try:
        exercise = _exercise_from_dict(request.exercise)
        result = get_answer_key(exercise=exercise)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
