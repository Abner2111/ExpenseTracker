"""
Email processing history — stored in data/email_history.db (separate from the
rules/vendors DB so they can be backed up, cleared, or inspected independently).
"""

import sqlite3
import os
from typing import List, Tuple, Optional


class EmailHistoryDB:
    """Tracks which emails have been processed and how."""

    DB_FILENAME = "email_history.db"

    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "data", self.DB_FILENAME)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init()

    def _init(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processed_emails (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id          TEXT    NOT NULL UNIQUE,
                    vendor            TEXT,
                    amount            REAL,
                    currency          TEXT,
                    original_amount   REAL,
                    original_currency TEXT,
                    category          TEXT,
                    expense_date      TEXT,
                    status            TEXT    NOT NULL DEFAULT 'success',
                    error_reason      TEXT,
                    processed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute(
                'CREATE INDEX IF NOT EXISTS idx_pem_email_id '
                'ON processed_emails(email_id)'
            )
            conn.execute(
                'CREATE INDEX IF NOT EXISTS idx_pem_processed_at '
                'ON processed_emails(processed_at)'
            )
            conn.commit()

    # ── Idempotency ───────────────────────────────────────────────────────────
    def is_processed(self, email_id: str) -> bool:
        """True if this email was already processed successfully."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_emails "
                "WHERE email_id=? AND status='success'",
                (email_id,)
            ).fetchone()
            return row is not None

    # ── Write ─────────────────────────────────────────────────────────────────
    def log(self, email_id: str, status: str = "success",
            vendor: str = None, amount: float = None,
            currency: str = None, original_amount: float = None,
            original_currency: str = None, category: str = None,
            expense_date: str = None, error_reason: str = None) -> bool:
        """Upsert a row for this email."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO processed_emails
                        (email_id, vendor, amount, currency,
                         original_amount, original_currency,
                         category, expense_date, status, error_reason,
                         processed_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?, CURRENT_TIMESTAMP)
                    ON CONFLICT(email_id) DO UPDATE SET
                        vendor            = excluded.vendor,
                        amount            = excluded.amount,
                        currency          = excluded.currency,
                        original_amount   = excluded.original_amount,
                        original_currency = excluded.original_currency,
                        category          = excluded.category,
                        expense_date      = excluded.expense_date,
                        status            = excluded.status,
                        error_reason      = excluded.error_reason,
                        processed_at      = CURRENT_TIMESTAMP
                ''', (email_id, vendor, amount, currency,
                      original_amount, original_currency,
                      category, expense_date, status, error_reason))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"EmailHistoryDB.log error: {e}")
            return False

    # ── Read ──────────────────────────────────────────────────────────────────
    def get_history(self, limit: int = 500) -> List[Tuple]:
        """
        Returns rows: (email_id, vendor, original_amount, original_currency,
                       amount, category, expense_date, status, error_reason,
                       processed_at)
        """
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute('''
                SELECT email_id, vendor, original_amount, original_currency,
                       amount, category, expense_date, status, error_reason,
                       processed_at
                FROM processed_emails
                ORDER BY processed_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            def _count(where=""):
                q = "SELECT COUNT(*) FROM processed_emails"
                if where:
                    q += " WHERE " + where
                return conn.execute(q).fetchone()[0]
            return {
                "total":   _count(),
                "success": _count("status='success'"),
                "errors":  _count("status='error'"),
                "skipped": _count("status='skipped'"),
            }
