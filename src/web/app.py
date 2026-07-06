"""FastAPI web UI for ExpenseTracker.

Run with: cd src && uvicorn web.app:app --host 0.0.0.0 --port 8000

The rest of src/ (main.py, database.py, config_manager.py, ...) uses flat,
sibling-relative imports and resolves credentials.json/config.py/data/*.db
relative to the process CWD and each module's own __file__. To reuse that
code unmodified, we add src/ to sys.path and chdir into it here, exactly
like run_gui.py does for the Tkinter GUI.
"""

import os
import sys

_WEB_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_WEB_DIR)

if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
os.chdir(_SRC_DIR)

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from web.auth import require_auth
from web.routes import config as config_routes
from web.routes import db_history, db_rules, db_test, db_vendors
from web.routes import run as run_routes
from web.routes import status as status_routes

app = FastAPI(title="ExpenseTracker", dependencies=[Depends(require_auth)])

app.mount("/static", StaticFiles(directory=os.path.join(_WEB_DIR, "static")), name="static")

app.include_router(run_routes.router)
app.include_router(config_routes.router)
app.include_router(status_routes.router)
app.include_router(db_vendors.router)
app.include_router(db_rules.router)
app.include_router(db_test.router)
app.include_router(db_history.router)


@app.get("/")
def index():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/run")
