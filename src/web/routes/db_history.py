from fastapi import APIRouter, Request

from web.templating import templates

router = APIRouter()

_history_db = None


def _get_history_db():
    global _history_db
    if _history_db is None:
        from email_history import EmailHistoryDB

        _history_db = EmailHistoryDB()
    return _history_db


@router.get("/db/history")
def history_page(request: Request, status: str = "", q: str = ""):
    history_db = _get_history_db()
    stats = history_db.get_stats()
    # (email_id, vendor, original_amount, original_currency, amount, category,
    #  expense_date, status, error_reason, processed_at)
    rows = history_db.get_history(limit=500)

    if status:
        rows = [r for r in rows if r[7] == status]
    if q:
        q_lower = q.lower()
        rows = [r for r in rows if q_lower in (r[1] or "").lower() or q_lower in (r[0] or "").lower()]

    return templates.TemplateResponse(
        "db_history.html",
        {
            "request": request,
            "active_page": "db_history",
            "stats": stats,
            "rows": rows,
            "status": status,
            "q": q,
        },
    )
