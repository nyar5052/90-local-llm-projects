"""Family Story Creator - FastAPI application."""

from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .core import (
    create_story,
    create_chapter,
    create_book,
    continue_story,
    create_poem,
    create_character,
    load_stories,
    save_story,
    delete_story,
    export_story,
    STORY_STYLES,
)

app = FastAPI(title="Family Story Creator", version="1.0.0")


# --- Request Models ---

class CreateStoryRequest(BaseModel):
    members: str
    event: str
    style: str = "heartwarming"
    details: str = ""
    photos: str = ""
    length: str = "medium"
    config: Optional[dict] = None


class CreateChapterRequest(BaseModel):
    chapter_num: int
    title: str
    members: str
    events: str
    style: str = "heartwarming"
    config: Optional[dict] = None


class CreateBookRequest(BaseModel):
    title: str
    chapters: List[dict]
    members: str
    config: Optional[dict] = None


class ContinueStoryRequest(BaseModel):
    existing_story: str
    prompt: str
    config: Optional[dict] = None


class CreatePoemRequest(BaseModel):
    members: str
    event: str
    style: str = "rhyming"
    config: Optional[dict] = None


class CreateCharacterRequest(BaseModel):
    name: str
    age: Optional[int] = None
    personality: str = ""
    relationship: str = ""
    appearance: str = ""


class SaveStoryRequest(BaseModel):
    story: dict
    stories_file: Optional[str] = None


class ExportStoryRequest(BaseModel):
    story: dict
    format: str = "markdown"


# --- Response Models ---

class HealthResponse(BaseModel):
    status: str
    styles: List[str]


class GeneratedTextResponse(BaseModel):
    result: str


class BookResponse(BaseModel):
    title: str
    toc: list
    chapters: list


class CharacterResponse(BaseModel):
    character: dict


class StoryMetaResponse(BaseModel):
    story: dict


class DeleteResponse(BaseModel):
    deleted: bool


class ExportResponse(BaseModel):
    exported: str


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        styles=list(STORY_STYLES.keys()),
    )


@app.post("/stories/create", response_model=GeneratedTextResponse)
async def api_create_story(request: CreateStoryRequest):
    try:
        result = create_story(
            members=request.members,
            event=request.event,
            style=request.style,
            details=request.details,
            photos=request.photos,
            length=request.length,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stories/chapter", response_model=GeneratedTextResponse)
async def api_create_chapter(request: CreateChapterRequest):
    try:
        result = create_chapter(
            chapter_num=request.chapter_num,
            title=request.title,
            members=request.members,
            events=request.events,
            style=request.style,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stories/book", response_model=BookResponse)
async def api_create_book(request: CreateBookRequest):
    try:
        result = create_book(
            title=request.title,
            chapters=request.chapters,
            members=request.members,
            config=request.config,
        )
        return BookResponse(
            title=result.get("title", ""),
            toc=result.get("toc", []),
            chapters=result.get("chapters", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stories/continue", response_model=GeneratedTextResponse)
async def api_continue_story(request: ContinueStoryRequest):
    try:
        result = continue_story(
            existing_story=request.existing_story,
            prompt=request.prompt,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stories/poem", response_model=GeneratedTextResponse)
async def api_create_poem(request: CreatePoemRequest):
    try:
        result = create_poem(
            members=request.members,
            event=request.event,
            style=request.style,
            config=request.config,
        )
        return GeneratedTextResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/characters", response_model=CharacterResponse)
async def api_create_character(request: CreateCharacterRequest):
    try:
        result = create_character(
            name=request.name,
            age=request.age,
            personality=request.personality,
            relationship=request.relationship,
            appearance=request.appearance,
        )
        return CharacterResponse(character=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stories", response_model=List[dict])
async def api_load_stories():
    try:
        return load_stories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stories/save", response_model=StoryMetaResponse)
async def api_save_story(request: SaveStoryRequest):
    try:
        result = save_story(story=request.story, stories_file=request.stories_file)
        return StoryMetaResponse(story=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/stories/{story_id}", response_model=DeleteResponse)
async def api_delete_story(story_id: str):
    try:
        deleted = delete_story(story_id=story_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")
        return DeleteResponse(deleted=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stories/export", response_model=ExportResponse)
async def api_export_story(request: ExportStoryRequest):
    try:
        result = export_story(story=request.story, format=request.format)
        return ExportResponse(exported=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/styles", response_model=dict)
async def api_get_styles():
    return STORY_STYLES


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
