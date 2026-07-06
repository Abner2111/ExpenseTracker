"""Config page - ports gui.py's extract_sheet_id_from_url/load_config/save_config/
test_config (gui.py:1181, 1214, 1229, 1272) so it rewrites src/config.py the same
way the Tkinter GUI does.
"""

import importlib
import os
import re

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from web.templating import templates

router = APIRouter()

_CONFIG_PY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.py")


def extract_sheet_id_from_url(url_or_id: str) -> str:
    url_or_id = url_or_id.strip()
    for pattern in [
        r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)",
        r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
        r"d/([a-zA-Z0-9-_]+)",
    ]:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    if re.match(r"^[a-zA-Z0-9-_]+$", url_or_id) and len(url_or_id) > 20:
        return url_or_id
    return url_or_id


def load_config() -> dict:
    try:
        import config

        importlib.reload(config)
        return {
            "google_sheet_id": getattr(config, "SPREADSHEET_ID", ""),
            "google_sheet_tab": getattr(config, "SPREADSHEET_NAME", "Transactions"),
            "filter_by_month": getattr(config, "FILTER_BY_MONTH", None),
        }
    except Exception:
        return {
            "google_sheet_id": "",
            "google_sheet_tab": "Transactions",
            "filter_by_month": None,
        }


def save_config(raw_sheet_id: str, sheet_tab: str, month_filter: str | None) -> tuple[bool, str]:
    sheet_id = extract_sheet_id_from_url(raw_sheet_id)
    sheet_tab = sheet_tab.strip() or "Transactions"
    month_filter = (month_filter or "").strip() or None

    if not sheet_id:
        return False, "El ID de Google Sheet es obligatorio"

    content = (
        "# Configuration file for Expense Tracker\n"
        "import os\n\n"
        "BASE_DIR = os.path.dirname(os.path.abspath(__file__))\n\n"
        f'SPREADSHEET_ID = "{sheet_id}"\n'
        f'SPREADSHEET_NAME = "{sheet_tab}"\n'
        f"FILTER_BY_MONTH = {month_filter!r}\n\n"
        'GMAIL_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")\n'
        'TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")\n'
    )

    with open(_CONFIG_PY_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    return True, "Guardado correctamente"


@router.get("/config")
def config_page(request: Request, saved: bool = False, error: str | None = None):
    return templates.TemplateResponse(
        "config.html",
        {
            "request": request,
            "active_page": "config",
            "config": load_config(),
            "saved": saved,
            "error": error,
        },
    )


@router.post("/config")
def config_save(
    sheet_id: str = Form(...),
    sheet_tab: str = Form("Transactions"),
    filter_by_month: str = Form(""),
):
    ok, message = save_config(sheet_id, sheet_tab, filter_by_month)
    if not ok:
        return RedirectResponse(url=f"/config?error={message}", status_code=303)
    return RedirectResponse(url="/config?saved=true", status_code=303)


@router.post("/config/validate")
def config_validate(sheet_id: str = Form(...)):
    raw = sheet_id.strip()
    if not raw:
        return {"valid": False, "message": "Ingresa una URL o ID primero"}
    extracted = extract_sheet_id_from_url(raw)
    if len(extracted) < 20:
        return {"valid": False, "message": "El ID parece muy corto. Verifica que sea correcto."}
    if not re.match(r"^[a-zA-Z0-9-_]+$", extracted):
        return {"valid": False, "message": "El ID contiene caracteres no válidos."}
    preview = extracted[:24] + ("…" if len(extracted) > 24 else "")
    return {"valid": True, "message": f"Formato correcto. ID: {preview}", "sheet_id": extracted}
