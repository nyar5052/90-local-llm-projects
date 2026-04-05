"""FastAPI REST API for Code Snippet Search."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.llm_client import chat
from src.code_search.core import (
    scan_directory,
    rank_files,
    search_code,
    load_bookmarks,
    save_bookmark,
    remove_bookmark,
)

app = FastAPI(
    title="Code Snippet Search API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class SearchRequest(BaseModel):
    """Request to search code snippets."""
    directory: str
    query: str


class ScanRequest(BaseModel):
    """Request to scan a directory."""
    directory: str
    max_files: int = 100


class BookmarkRequest(BaseModel):
    """Bookmark a code snippet."""
    bookmark: dict


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.post("/search")
async def search_endpoint(request: SearchRequest):
    """Search for code snippets using LLM."""
    try:
        result = search_code(
            directory=request.directory,
            query=request.query,
            chat_fn=chat,
        )
        return {"results": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan")
async def scan_endpoint(request: ScanRequest):
    """Scan a directory for code files."""
    try:
        files = scan_directory(
            directory=request.directory,
            max_files=request.max_files,
        )
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bookmarks")
async def list_bookmarks():
    """List all bookmarked snippets."""
    try:
        bookmarks = load_bookmarks()
        return {"bookmarks": bookmarks, "count": len(bookmarks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bookmarks")
async def add_bookmark(request: BookmarkRequest):
    """Add a bookmark."""
    try:
        save_bookmark(request.bookmark)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/bookmarks/{index}")
async def delete_bookmark(index: int):
    """Remove a bookmark by index."""
    try:
        success = remove_bookmark(index)
        if not success:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8025)
