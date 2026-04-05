"""FastAPI REST API for Vocabulary Builder."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from vocab_builder.core import (
    generate_vocabulary,
    run_quiz,
    score_quiz,
    check_service,
    WordEntry,
)

app = FastAPI(
    title="Vocabulary Builder API",
    description="REST API for Vocabulary Builder",
    version="1.0.0",
)


# --- Request Models ---


class GenerateVocabularyRequest(BaseModel):
    topic: str = Field(..., description="Topic for vocabulary generation")
    count: int = Field(10, description="Number of words to generate")
    level: str = Field("", description="Difficulty level filter")


class WordEntryModel(BaseModel):
    word: str
    definition: str
    part_of_speech: str = ""
    example_sentence: str = ""
    synonyms: List[str] = []
    antonyms: List[str] = []
    difficulty: str = ""


class RunQuizRequest(BaseModel):
    words: List[WordEntryModel] = Field(..., description="List of word entries for the quiz")


class ScoreQuizRequest(BaseModel):
    answers: List[Dict[str, Any]] = Field(..., description="List of quiz answers to score")


# --- Endpoints ---


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vocabulary-builder"}


@app.get("/service-check")
async def api_check_service():
    try:
        result = check_service()
        return {"available": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def api_generate_vocabulary(request: GenerateVocabularyRequest):
    try:
        result = generate_vocabulary(
            topic=request.topic,
            count=request.count,
            level=request.level,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quiz")
async def api_run_quiz(request: RunQuizRequest):
    try:
        word_entries = [
            WordEntry(
                word=w.word,
                definition=w.definition,
                part_of_speech=w.part_of_speech,
                example_sentence=w.example_sentence,
                synonyms=w.synonyms,
                antonyms=w.antonyms,
                difficulty=w.difficulty,
            )
            for w in request.words
        ]
        result = run_quiz(words=word_entries)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score")
async def api_score_quiz(request: ScoreQuizRequest):
    try:
        result = score_quiz(answers=request.answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
