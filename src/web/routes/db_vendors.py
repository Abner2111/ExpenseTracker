from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from web.templating import templates

router = APIRouter()

_db = None


def _get_db():
    global _db
    if _db is None:
        from database import ExpenseDatabase

        _db = ExpenseDatabase()
    return _db


@router.get("/db/vendors")
def vendors_page(request: Request, q: str = ""):
    rows = _get_db().get_all_vendors_full()  # (id, keyword, vendor_name, category)
    if q:
        q_lower = q.lower()
        rows = [r for r in rows if q_lower in r[1].lower() or q_lower in r[2].lower() or q_lower in (r[3] or "").lower()]
    return templates.TemplateResponse(
        "db_vendors.html",
        {"request": request, "active_page": "db_vendors", "vendors": rows, "q": q},
    )


@router.post("/db/vendors/add")
def vendors_add(keyword: str = Form(...), vendor_name: str = Form(...), category: str = Form("")):
    _get_db().add_vendor_keyword(keyword, vendor_name, category or None)
    return RedirectResponse(url="/db/vendors", status_code=303)


@router.post("/db/vendors/edit")
def vendors_edit(keyword: str = Form(...), vendor_name: str = Form(...), category: str = Form("")):
    _get_db().update_vendor_keyword(keyword, vendor_name, category or None)
    return RedirectResponse(url="/db/vendors", status_code=303)


@router.post("/db/vendors/delete")
def vendors_delete(keyword: str = Form(...)):
    _get_db().delete_vendor_keyword(keyword)
    return RedirectResponse(url="/db/vendors", status_code=303)
