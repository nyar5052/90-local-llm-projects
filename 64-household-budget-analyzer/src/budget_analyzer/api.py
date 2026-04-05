from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn

from .core import (
    compute_category_breakdown,
    compute_total,
    analyze_budget,
    compare_months,
    categorize_expense,
    compare_budget_vs_actual,
    detect_recurring,
    compute_monthly_trends,
    get_top_expenses,
    filter_by_month,
)

app = FastAPI(title="Household Budget Analyzer", version="1.0.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ExpensesRequest(BaseModel):
    expenses: List[dict]


class AnalyzeBudgetRequest(BaseModel):
    expenses: List[dict]
    month: str = Field(..., description="Month string, e.g. '2024-01'")


class CategorizeRequest(BaseModel):
    description: str


class BudgetVsActualRequest(BaseModel):
    categories: Dict[str, float]


class DetectRecurringRequest(BaseModel):
    expenses: List[dict]
    tolerance: float = 0.1


class TopExpensesRequest(BaseModel):
    expenses: List[dict]
    n: int = 10


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/expenses/breakdown")
def api_category_breakdown(req: ExpensesRequest):
    try:
        breakdown = compute_category_breakdown(req.expenses)
        return {"breakdown": breakdown}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/total")
def api_compute_total(req: ExpensesRequest):
    try:
        total = compute_total(req.expenses)
        return {"total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/analyze")
def api_analyze_budget(req: AnalyzeBudgetRequest):
    try:
        filtered = filter_by_month(req.expenses, req.month)
        categories = compute_category_breakdown(filtered)
        total = compute_total(filtered)
        result = analyze_budget(filtered, categories, total, req.month)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/compare-months")
def api_compare_months(req: ExpensesRequest):
    try:
        result = compare_months(req.expenses)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/categorize")
def api_categorize_expense(req: CategorizeRequest):
    try:
        category = categorize_expense(req.description)
        return {"category": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/budget-vs-actual")
def api_budget_vs_actual(req: BudgetVsActualRequest):
    try:
        comparison = compare_budget_vs_actual(req.categories)
        return {"comparison": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/detect-recurring")
def api_detect_recurring(req: DetectRecurringRequest):
    try:
        recurring = detect_recurring(req.expenses, tolerance=req.tolerance)
        return {"recurring": recurring}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/monthly-trends")
def api_monthly_trends(req: ExpensesRequest):
    try:
        trends = compute_monthly_trends(req.expenses)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/expenses/top")
def api_top_expenses(req: TopExpensesRequest):
    try:
        top = get_top_expenses(req.expenses, n=req.n)
        return {"top_expenses": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
