"""Status page - ports gui.py's filesystem-only checks (check_credentials/
check_config_status/check_database_status, gui.py:1292-1302), plus a
"Verify Setup" button that hits the real ExpenseTracker.verify_setup() /
get_system_status() (network calls, opt-in - not run on every page load).
"""

import os

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from web.routes.config import load_config
from web.templating import templates

router = APIRouter()

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)


def _filesystem_checks() -> dict:
    creds_ok = os.path.exists(os.path.join(_SRC_DIR, "credentials.json"))
    config_ok = bool(load_config().get("google_sheet_id"))
    db_ok = os.path.exists(os.path.join(_PROJECT_ROOT, "data", "expense_tracker.db"))
    return {
        "credentials": creds_ok,
        "config": config_ok,
        "database": db_ok,
    }


@router.get("/status")
def status_page(request: Request, oauth_renewed: bool = False, oauth_error: str | None = None):
    return templates.TemplateResponse(
        "status.html",
        {
            "request": request,
            "active_page": "status",
            "checks": _filesystem_checks(),
            "oauth_renewed": oauth_renewed,
            "oauth_error": oauth_error,
        },
    )


@router.post("/status/verify")
def status_verify(request: Request):
    from main import ExpenseTracker

    try:
        tracker = ExpenseTracker()
        verify_result = tracker.verify_setup()
        system_status = tracker.get_system_status()
    except Exception as e:
        verify_result = None
        system_status = None
        error = str(e)
    else:
        error = None

    return templates.TemplateResponse(
        "status.html",
        {
            "request": request,
            "active_page": "status",
            "checks": _filesystem_checks(),
            "verify_result": verify_result.to_dict() if verify_result else None,
            "system_status": system_status,
            "verify_error": error,
        },
    )
