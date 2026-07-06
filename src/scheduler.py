"""Daily scheduler loop for running inside a container (CasaOS/Docker).

Replaces the systemd timer: sleeps until RUN_HOUR:RUN_MINUTE each day, then
runs main.py in a fresh subprocess (same as the systemd timer did) and
repeats forever. A fresh process per run matters because main.py's
ConfigManager reads config.py into a module-level singleton once at import
time - reusing one long-lived process across days would keep serving a
stale config.py even after the web UI's Config page rewrites it.
"""

import os
import subprocess
import sys
import time
from datetime import datetime, timedelta

from logger import get_logger

logger = get_logger()

RUN_HOUR = int(os.environ.get("RUN_HOUR", "7"))
RUN_MINUTE = int(os.environ.get("RUN_MINUTE", "0"))
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))


def _seconds_until_next_run() -> float:
    now = datetime.now()
    target = now.replace(hour=RUN_HOUR, minute=RUN_MINUTE, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def main():
    logger.info(f"Scheduler started - will run daily at {RUN_HOUR:02d}:{RUN_MINUTE:02d}")
    while True:
        sleep_seconds = _seconds_until_next_run()
        logger.info(f"Sleeping {sleep_seconds / 3600:.1f}h until next scheduled run")
        time.sleep(sleep_seconds)

        logger.info("Scheduled run starting")
        try:
            result = subprocess.run(
                [sys.executable, "main.py"], cwd=_SRC_DIR, capture_output=True, text=True
            )
            logger.info(f"Scheduled run finished with exit code {result.returncode}")
            if result.stdout:
                logger.info(result.stdout)
            if result.returncode != 0 and result.stderr:
                logger.error(result.stderr)
        except Exception as e:
            logger.error(f"Scheduled run failed to start: {e}")


if __name__ == "__main__":
    main()
