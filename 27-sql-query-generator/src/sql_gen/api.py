"""FastAPI REST API for SQL Query Generator."""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.llm_client import chat
from src.sql_gen.core import (
    generate_sql,
    generate_sql_no_schema,
    optimize_query,
    parse_schema_text,
    get_table_names,
    visualize_schema,
    load_history,
    clear_history,
    SUPPORTED_DIALECTS,
)

app = FastAPI(
    title="SQL Query Generator API",
    description="REST API powered by local Gemma 4 LLM via Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class GenerateSQLRequest(BaseModel):
    """Request to generate SQL from natural language."""
    query: str
    schema: Optional[str] = None
    dialect: str = "standard"


class OptimizeRequest(BaseModel):
    """Request to optimize a SQL query."""
    sql: str
    dialect: str = "standard"


class SchemaRequest(BaseModel):
    """Request to parse or visualize a schema."""
    schema_text: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": "gemma4"}


@app.get("/dialects")
async def list_dialects():
    """List supported SQL dialects."""
    return {"dialects": SUPPORTED_DIALECTS}


@app.post("/generate")
async def generate_endpoint(request: GenerateSQLRequest):
    """Generate SQL from a natural language query."""
    try:
        if request.schema:
            result = generate_sql(
                schema=request.schema,
                query=request.query,
                chat_fn=chat,
                dialect=request.dialect,
            )
        else:
            result = generate_sql_no_schema(
                query=request.query,
                chat_fn=chat,
                dialect=request.dialect,
            )
        return {"sql": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize")
async def optimize_endpoint(request: OptimizeRequest):
    """Optimize a SQL query."""
    try:
        result = optimize_query(
            sql=request.sql,
            chat_fn=chat,
            dialect=request.dialect,
        )
        return {"optimized_sql": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schema/parse")
async def parse_schema_endpoint(request: SchemaRequest):
    """Parse a schema into structured tables."""
    try:
        tables = parse_schema_text(request.schema_text)
        return {"tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schema/tables")
async def table_names_endpoint(request: SchemaRequest):
    """Extract table names from a schema."""
    try:
        names = get_table_names(request.schema_text)
        return {"table_names": names, "count": len(names)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schema/visualize")
async def visualize_schema_endpoint(request: SchemaRequest):
    """Visualize a schema as text."""
    try:
        tables = parse_schema_text(request.schema_text)
        result = visualize_schema(tables)
        return {"visualization": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def history_endpoint():
    """Get query generation history."""
    try:
        history = load_history()
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/history")
async def clear_history_endpoint():
    """Clear query generation history."""
    try:
        clear_history()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8026)
