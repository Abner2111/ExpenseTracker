import asyncio
import threading

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, StreamingResponse

from web.run_state import RunStateLogHandler, run_state
from web.templating import templates
from web.utils import spreadsheet_url

router = APIRouter()


def _execute_run(include_read: bool):
    from logger import get_logger
    from main import ExpenseTracker

    logger = get_logger()
    handler = RunStateLogHandler(run_state)
    logger.addHandler(handler)
    try:
        tracker = ExpenseTracker()
        results = tracker.process_expenses(include_read=include_read)
        run_state.finish(result=[r.to_dict() for r in results])
    except Exception as e:
        run_state.finish(error=str(e))
    finally:
        logger.removeHandler(handler)


def _current_config_summary() -> dict:
    try:
        from config_manager import ConfigManager

        cfg = ConfigManager.get_config()
        return {
            "google_sheet_id": cfg.google_sheet_id,
            "google_sheet_tab": cfg.google_sheet_tab,
            "filter_by_month": cfg.filter_by_month,
            "spreadsheet_url": spreadsheet_url(cfg.google_sheet_id),
        }
    except Exception:
        return {"google_sheet_id": "", "google_sheet_tab": "", "filter_by_month": None, "spreadsheet_url": None}


@router.get("/run")
def run_page(request: Request):
    return templates.TemplateResponse(
        "run.html",
        {
            "request": request,
            "active_page": "run",
            "config": _current_config_summary(),
            "running": run_state.running,
            "logs": run_state.logs,
            "result": run_state.result,
            "error": run_state.error,
        },
    )


@router.post("/run/start")
def run_start(include_read: bool = Form(False)):
    if not run_state.running:
        run_state.reset_for_new_run()
        threading.Thread(target=_execute_run, args=(include_read,), daemon=True).start()
    return RedirectResponse(url="/run", status_code=303)


@router.get("/run/stream")
async def run_stream(offset: int = 0):
    async def event_gen():
        pos = offset
        while True:
            lines, pos = run_state.snapshot_logs_from(pos)
            for line in lines:
                payload = "\n".join(f"data: {part}" for part in line.split("\n"))
                yield payload + "\n\n"
            if not run_state.running:
                yield "event: done\ndata: end\n\n"
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(event_gen(), media_type="text/event-stream")
