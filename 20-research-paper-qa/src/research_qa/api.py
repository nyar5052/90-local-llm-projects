"""FastAPI REST API for Research Paper QA."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.research_qa.core import (
    build_system_prompt,
    ask_question,
    suggest_followup_questions,
    extract_citations,
)

app = FastAPI(
    title="Research Paper QA API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class AskRequest(BaseModel):
    """Ask a question about a research paper."""
    question: str
    paper_content: str
    conversation_history: list[dict] = []


class FollowupRequest(BaseModel):
    """Request follow-up question suggestions."""
    paper_content: str
    conversation_history: list[dict] = []
    num_suggestions: int = 3


class CitationRequest(BaseModel):
    """Extract citations from an answer."""
    answer: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    """Ask a question about a research paper."""
    try:
        system_prompt = build_system_prompt(request.paper_content)
        answer = ask_question(
            question=request.question,
            conversation_history=request.conversation_history,
            system_prompt=system_prompt,
        )
        return {"answer": answer, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/followup")
async def followup_endpoint(request: FollowupRequest):
    """Suggest follow-up questions."""
    try:
        system_prompt = build_system_prompt(request.paper_content)
        suggestions = suggest_followup_questions(
            conversation_history=request.conversation_history,
            system_prompt=system_prompt,
            num_suggestions=request.num_suggestions,
        )
        return {"suggestions": suggestions, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/citations")
async def citations_endpoint(request: CitationRequest):
    """Extract citations from an answer."""
    try:
        citations = extract_citations(answer=request.answer)
        return {"citations": citations, "count": len(citations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
