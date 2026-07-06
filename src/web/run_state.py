"""In-memory state for the currently running (or last-run) tracker job.

A single process-wide instance is shared by the /run routes. It is not
persisted - a restart of the web UI clears run history, which is fine since
the source of truth for what actually happened is the app's own logger
output and the email_history/expense_tracker databases.
"""

import logging
import threading


class RunState:
    def __init__(self):
        self._lock = threading.Lock()
        self.running = False
        self.logs: list[str] = []
        self.result: list[dict] | None = None
        self.error: str | None = None

    def reset_for_new_run(self):
        with self._lock:
            self.running = True
            self.logs = []
            self.result = None
            self.error = None

    def append_log(self, line: str):
        with self._lock:
            self.logs.append(line)

    def finish(self, result: list[dict] | None = None, error: str | None = None):
        with self._lock:
            self.running = False
            self.result = result
            self.error = error

    def snapshot_logs_from(self, offset: int) -> tuple[list[str], int]:
        with self._lock:
            new_lines = self.logs[offset:]
            return new_lines, len(self.logs)


run_state = RunState()


class RunStateLogHandler(logging.Handler):
    """Logging handler that appends formatted records to a RunState."""

    def __init__(self, state: RunState):
        super().__init__()
        self.state = state
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    def emit(self, record: logging.LogRecord):
        try:
            self.state.append_log(self.format(record))
        except Exception:
            pass
