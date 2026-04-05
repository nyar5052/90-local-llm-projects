from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from .core import (
    add_note,
    delete_note,
    get_note,
    search_notes,
    summarize_kb,
    get_all_tags,
    tag_cloud,
    get_notes_by_tag,
    find_backlinks,
    find_all_backlinks,
    search_fulltext,
    get_templates,
    get_template,
    apply_template,
    export_notes,
    load_kb,
)

app = FastAPI(title="Personal Knowledge Base", version="1.0.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AddNoteRequest(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None


class SearchRequest(BaseModel):
    query: str


class FulltextSearchRequest(BaseModel):
    query: str
    case_sensitive: bool = False


class ApplyTemplateRequest(BaseModel):
    kwargs: Dict[str, str] = Field(default_factory=dict)


class ExportRequest(BaseModel):
    filepath: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/notes")
def api_add_note(req: AddNoteRequest):
    try:
        result = add_note(title=req.title, content=req.content, tags=req.tags)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/{note_id}")
def api_get_note(note_id: int):
    note = get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    return note


@app.delete("/notes/{note_id}")
def api_delete_note(note_id: int):
    success = delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
    return {"deleted": True, "note_id": note_id}


@app.post("/notes/search")
def api_search_notes(req: SearchRequest):
    try:
        result = search_notes(req.query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notes/search/fulltext")
def api_search_fulltext(req: FulltextSearchRequest):
    try:
        results = search_fulltext(req.query, case_sensitive=req.case_sensitive)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/tags/all")
def api_get_all_tags():
    try:
        kb = load_kb()
        tags = get_all_tags(kb)
        return {"tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/tags/cloud")
def api_tag_cloud():
    try:
        cloud = tag_cloud()
        return {"cloud": cloud}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/by-tag/{tag}")
def api_get_notes_by_tag(tag: str):
    try:
        notes = get_notes_by_tag(tag)
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/{note_id}/backlinks")
def api_find_backlinks(note_id: int):
    try:
        backlinks = find_backlinks(note_id)
        return {"backlinks": backlinks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes/backlinks/all")
def api_find_all_backlinks():
    try:
        backlinks = find_all_backlinks()
        return {"backlinks": backlinks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kb/summary")
def api_summarize_kb():
    try:
        summary = summarize_kb()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates")
def api_get_templates():
    try:
        templates = get_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates/{name}")
def api_get_template(name: str):
    template = get_template(name)
    if template is None:
        raise HTTPException(status_code=404, detail=f"Template '{name}' not found")
    return template


@app.post("/templates/{name}/apply")
def api_apply_template(name: str, req: ApplyTemplateRequest):
    result = apply_template(name, **req.kwargs)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Template '{name}' not found")
    return result


@app.post("/notes/export")
def api_export_notes(req: ExportRequest):
    try:
        result = export_notes(filepath=req.filepath)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
