from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

from .core import (
    add_book,
    update_progress,
    rate_book,
    get_genre_stats,
    recommend_similar,
    calculate_reading_speed,
    set_reading_goal,
    check_goal_progress,
    get_tbr_list,
    prioritize_tbr,
    get_summary,
    get_recommendations,
    analyze_reading_habits,
    load_books,
)

app = FastAPI(title="Reading List Manager", version="1.0.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AddBookRequest(BaseModel):
    title: str
    author: str
    genre: str = ""
    status: str = "to-read"
    rating: int = 0
    notes: str = ""
    pages: int = 0


class UpdateProgressRequest(BaseModel):
    pages_read: int


class RateBookRequest(BaseModel):
    rating: int
    review: str = ""


class SummaryRequest(BaseModel):
    title: str
    author: str


class RecommendationsRequest(BaseModel):
    genre: str = ""


class ReadingGoalRequest(BaseModel):
    year: int
    target: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/books")
def api_add_book(req: AddBookRequest):
    try:
        book = add_book(
            title=req.title,
            author=req.author,
            genre=req.genre,
            status=req.status,
            rating=req.rating,
            notes=req.notes,
            pages=req.pages,
        )
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/books/{book_id}/progress")
def api_update_progress(book_id: int, req: UpdateProgressRequest):
    result = update_progress(book_id, req.pages_read)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return result


@app.put("/books/{book_id}/rate")
def api_rate_book(book_id: int, req: RateBookRequest):
    result = rate_book(book_id, req.rating, review=req.review)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return result


@app.get("/books")
def api_list_books():
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books/genre-stats")
def api_genre_stats():
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        stats = get_genre_stats(books)
        return {"genre_stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books/recommendations/similar")
def api_recommend_similar(top_n: int = Query(default=5, ge=1)):
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        similar = recommend_similar(books, top_n=top_n)
        return {"recommendations": similar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books/tbr")
def api_get_tbr():
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        tbr = get_tbr_list(books)
        return {"tbr": tbr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books/tbr/prioritize")
def api_prioritize_tbr(sort_by: str = Query(default="genre")):
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        prioritized = prioritize_tbr(books, sort_by=sort_by)
        return {"tbr": prioritized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/books/summary")
def api_get_summary(req: SummaryRequest):
    try:
        summary = get_summary(req.title, req.author)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/books/recommendations")
def api_get_recommendations(req: RecommendationsRequest):
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        result = get_recommendations(genre=req.genre, books=books)
        return {"recommendations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/books/analyze-habits")
def api_analyze_habits():
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        result = analyze_reading_habits(books)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/goals")
def api_set_reading_goal(req: ReadingGoalRequest):
    try:
        goal = set_reading_goal(req.year, req.target)
        return goal
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/goals/{year}/progress")
def api_check_goal_progress(year: int):
    try:
        data = load_books()
        books = data if isinstance(data, list) else data.get("books", [])
        progress = check_goal_progress(year, books)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
