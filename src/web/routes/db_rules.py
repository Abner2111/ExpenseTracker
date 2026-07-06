from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from web.templating import templates

router = APIRouter()

RULE_TYPES = ("vendor_exact", "vendor_contains", "keyword_contains")

_db = None


def _get_db():
    global _db
    if _db is None:
        from database import ExpenseDatabase

        _db = ExpenseDatabase()
    return _db


@router.get("/db/rules")
def rules_page(request: Request):
    rows = _get_db().get_all_category_rules_with_id()  # (id, rule_type, pattern, category, priority)
    categories = _get_db().get_all_categories()
    return templates.TemplateResponse(
        "db_rules.html",
        {
            "request": request,
            "active_page": "db_rules",
            "rules": rows,
            "rule_types": RULE_TYPES,
            "categories": categories,
        },
    )


@router.post("/db/categories/add")
def categories_add(name: str = Form(...), description: str = Form("")):
    _get_db().add_category(name, description or None)
    return RedirectResponse(url="/db/rules", status_code=303)


@router.post("/db/rules/add")
def rules_add(
    rule_type: str = Form(...),
    pattern: str = Form(...),
    category: str = Form(...),
    priority: int = Form(1),
):
    _get_db().add_category_rule(rule_type, pattern, category, priority)
    return RedirectResponse(url="/db/rules", status_code=303)


@router.post("/db/rules/edit")
def rules_edit(
    rule_id: int = Form(...),
    rule_type: str = Form(...),
    pattern: str = Form(...),
    category: str = Form(...),
    priority: int = Form(1),
):
    _get_db().update_category_rule(rule_id, rule_type, pattern, category, priority)
    return RedirectResponse(url="/db/rules", status_code=303)


@router.post("/db/rules/delete")
def rules_delete(rule_id: int = Form(...)):
    _get_db().delete_category_rule(rule_id)
    return RedirectResponse(url="/db/rules", status_code=303)
