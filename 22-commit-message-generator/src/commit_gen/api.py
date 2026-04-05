"""FastAPI REST API for Commit Message Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.commit_gen.core import (
    generate_commit_messages,
    generate_batch_messages,
)
from src.commit_gen.config import CommitConfig

app = FastAPI(
    title="Commit Message Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class CommitRequest(BaseModel):
    """Request to generate commit messages."""
    diff: str
    msg_type: str = ""


class BatchCommitRequest(BaseModel):
    """Request to generate batch commit messages."""
    diffs: list[dict]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/generate")
async def generate_endpoint(request: CommitRequest):
    """Generate commit messages from a diff."""
    try:
        result = generate_commit_messages(
            diff=request.diff,
            msg_type=request.msg_type,
        )
        return {"messages": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/batch")
async def batch_generate_endpoint(request: BatchCommitRequest):
    """Generate commit messages for multiple diffs."""
    try:
        results = generate_batch_messages(diffs=request.diffs)
        return {"messages": results, "count": len(results), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
