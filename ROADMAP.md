# ExpenseTracker — Improvement Roadmap

## Phase 1 — Correctness & Reliability (Fix what's broken)

### 1.1 Idempotency / Duplicate Prevention
- Add a `processed_emails` table in SQLite to store `email_id` + timestamp
- Before processing, check if the ID was already handled — skip if so
- This is the single highest-risk issue: re-running the app currently creates duplicate rows in Sheets

### 1.2 Remove All Hardcoded Configs
- `FILTER_BY_MONTH = "2025/09"` in `src/config.py` — outdated, should default to current month or `None`
- Fallback exchange rates in `src/config_manager.py` are ~5-10% off vs 2026 rates — add a scheduled refresh or at minimum a `config.json` that users can update without touching source code

### 1.3 Date Parsing Fallback Bug
- `src/date_parser.py` falls back to today's date when parsing fails — this silently assigns the wrong date to an expense rather than raising an error
- Change the fallback to raise `ExpenseParsingError` with the unparsed string included

### 1.4 Retry Logic for Transient Failures
- Gmail and Sheets API calls have no retry — a single rate-limit response or timeout silently fails the expense
- Add exponential backoff (3 attempts) around `fetch_bac_emails()`, `add_expense()`, and currency API calls

---

## Phase 2 — Robustness & Observability

### 2.1 Structured Transaction Log
- Add a `processing_log` table: `email_id`, `vendor`, `amount`, `status` (success/skipped/failed), `error_reason`, `processed_at`
- This enables auditing, re-processing failed items, and answering "why wasn't this email imported?"

### 2.2 Specific Error Types
- `"Failed to parse email"` tells you nothing — split into `AmountNotFoundError`, `VendorNotFoundError`, `DateNotFoundError`
- Surface the actual failure reason in the GUI status panel and log

### 2.3 Rate Limiting Awareness
- The current 0.5s fixed delay ignores HTTP 429 responses
- Check response status code and back off dynamically; add a per-run API call counter toward the exchangerate-api.com 1500/month limit

### 2.4 Metrics Dashboard (GUI tab)
- Add a "Stats" panel: total processed this month, success rate, top categories, most frequent vendors, currency breakdown
- All data already lives in the processing log from 2.1 — just query it

---

## Phase 3 — Configuration & UX

### 3.1 Persist GUI Config
- Config changes in the GUI aren't saved — on next launch everything resets
- Write to a `config.json` on "Save" and load it at startup; fall back to `config.py` defaults if absent

### 3.2 Configurable Sheets Columns
- Column range `B:E` is hardcoded in `src/sheets_manager.py`
- Add a column mapping config (e.g., `{"date": "B", "amount": "C", "vendor": "D", "category": "E", "notes": "F"}`)

### 3.3 Email Recovery Mode
- Currently only unread emails are fetched — if something was marked read prematurely, it's unrecoverable
- Add a "reprocess date range" option in the GUI that queries Gmail with `after:`/`before:` regardless of read state, skipping already-logged email IDs

### 3.4 Multi-Bank / Multi-Account Support
- The Gmail query is hardcoded to BAC Credomatic's sender/subject
- Refactor into a `BankProfile` configuration (sender email, subject pattern, parsing regex) stored in the database — allows adding a second bank without changing source code

---

## Phase 4 — Code Quality & Maintainability

### 4.1 Test Coverage
- Most files under `test/` are empty stubs
- Priority order: `date_parser` (6 format patterns + Spanish months), `expense_parser` (8 amount regex patterns), `currency_converter` (caching, fallback, API failure)
- Use `pytest` + `unittest.mock` to patch Gmail/Sheets calls — no real credentials needed

### 4.2 Remove Dead Code
- `src/main_old.py` and `src/main_refactored.py` are unused — delete or archive them
- `batch_add_expenses()` referenced in `main.py` appears incomplete — either finish it or remove the call path

### 4.3 Secrets Out of Source Tree
- `src/credentials.json` should not be committed — add it to `.gitignore` and provide a `credentials.json.example` template
- Document the OAuth setup in README

### 4.4 `config.py` → `config.json`
- Having user-specific values (Spreadsheet ID, month filter) in a `.py` file means any edit is a code change
- Migrate to a `config.json` in the project root, loaded at startup, editable without touching Python files

---

## Phase 5 — Future Capabilities

### 5.1 Budget Tracking
- Add a `budgets` table: `category`, `monthly_limit`, `month`
- Show budget vs. actual in the GUI; warn when a category exceeds its limit

### 5.2 Export
- Add CSV/Excel export of the local processing log — useful for tax prep or when Sheets is unavailable

### 5.3 Scheduled / Background Mode
- Add an optional headless mode (`--daemon`) that runs on a schedule (cron or `schedule` library) without needing the GUI open

### 5.4 Category Rule Editor in GUI
- Right now adding/editing categorization rules requires using `admin_database.py` CLI or direct SQLite access
- A simple CRUD table in the Config tab would make the app self-contained for non-technical users

---

## Priority Summary

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 🔴 P0 | Duplicate prevention (1.1) | Small | Critical |
| 🔴 P0 | Remove hardcoded month/rates (1.2) | Small | High |
| 🔴 P0 | Date parse fallback fix (1.3) | Small | High |
| 🟠 P1 | Retry logic (1.4) | Medium | High |
| 🟠 P1 | Transaction log (2.1) | Medium | High |
| 🟠 P1 | Persist GUI config (3.1) | Small | Medium |
| 🟡 P2 | Test coverage (4.1) | Large | High |
| 🟡 P2 | Specific error types (2.2) | Small | Medium |
| 🟡 P2 | Configurable columns (3.2) | Small | Medium |
| 🟢 P3 | Metrics dashboard (2.4) | Medium | Medium |
| 🟢 P3 | Email recovery mode (3.3) | Medium | Medium |
| 🟢 P3 | Category rule editor in GUI (5.4) | Large | Medium |
