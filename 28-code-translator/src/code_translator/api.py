"""FastAPI REST API for Code Translator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.llm_client import chat
from src.code_translator.core import (
    translate_code,
    validate_syntax,
    compare_codes,
    generate_translation_notes,
    detect_source_language,
    get_language_name,
    SUPPORTED_LANGUAGES,
)

app = FastAPI(
    title="Code Translator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class TranslateRequest(BaseModel):
    """Request to translate code."""
    code: str
    source_lang: str
    target_lang: str


class ValidateRequest(BaseModel):
    """Request to validate syntax."""
    code: str
    language: str


class CompareRequest(BaseModel):
    """Request to compare source and translated code."""
    source: str
    translated: str


class TranslationNotesRequest(BaseModel):
    """Request for translation notes between languages."""
    source_lang: str
    target_lang: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/languages")
async def list_languages():
    """List supported programming languages."""
    return {"languages": SUPPORTED_LANGUAGES}


@app.post("/translate")
async def translate_endpoint(request: TranslateRequest):
    """Translate code from one language to another."""
    try:
        result = translate_code(
            code=request.code,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            chat_fn=chat,
        )
        return {"translated_code": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate")
async def validate_endpoint(request: ValidateRequest):
    """Validate syntax of translated code."""
    try:
        result = validate_syntax(code=request.code, language=request.language)
        return {"validation": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_endpoint(request: CompareRequest):
    """Compare source and translated code."""
    try:
        result = compare_codes(source=request.source, translated=request.translated)
        return {"comparison": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notes")
async def notes_endpoint(request: TranslationNotesRequest):
    """Get translation notes between two languages."""
    try:
        result = generate_translation_notes(
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            chat_fn=chat,
        )
        return {"notes": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8027)
