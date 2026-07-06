from fastapi import APIRouter, Form, Request

from web.templating import templates

router = APIRouter()

_db = None


def _get_db():
    global _db
    if _db is None:
        from database import ExpenseDatabase

        _db = ExpenseDatabase()
    return _db


@router.get("/db/test")
def test_page(request: Request):
    return templates.TemplateResponse(
        "db_test.html",
        {"request": request, "active_page": "db_test", "text": "", "vendor": None, "category": None},
    )


@router.post("/db/test")
def test_run(request: Request, text: str = Form(...)):
    vendor, category = _get_db().test_text(text)
    return templates.TemplateResponse(
        "db_test.html",
        {"request": request, "active_page": "db_test", "text": text, "vendor": vendor, "category": category},
    )
