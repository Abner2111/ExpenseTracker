# Graph Report - .  (2026-07-06)

## Corpus Check
- Corpus is ~28,851 words - fits in a single context window. You may not need a graph.

## Summary
- 536 nodes · 836 edges · 52 communities (49 shown, 3 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 72 edges (avg confidence: 0.66)
- Token cost: 84,176 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_GUI Application|GUI Application]]
- [[_COMMUNITY_Data Migration Scripts|Data Migration Scripts]]
- [[_COMMUNITY_Project Metadata & Dependencies|Project Metadata & Dependencies]]
- [[_COMMUNITY_Gmail Email Fetching|Gmail Email Fetching]]
- [[_COMMUNITY_Legacy Main Workflow|Legacy Main Workflow]]
- [[_COMMUNITY_Expense Model & Sheets Errors|Expense Model & Sheets Errors]]
- [[_COMMUNITY_Email History Tracking|Email History Tracking]]
- [[_COMMUNITY_Configuration Management|Configuration Management]]
- [[_COMMUNITY_Core Module Overview|Core Module Overview]]
- [[_COMMUNITY_Logging Infrastructure|Logging Infrastructure]]
- [[_COMMUNITY_Date Parsing Tests|Date Parsing Tests]]
- [[_COMMUNITY_Admin DB CLI|Admin DB CLI]]
- [[_COMMUNITY_Roadmap Reliability & Observability|Roadmap: Reliability & Observability]]
- [[_COMMUNITY_Currency Conversion|Currency Conversion]]
- [[_COMMUNITY_Main App Orchestrator|Main App Orchestrator]]
- [[_COMMUNITY_Custom Exception Hierarchy|Custom Exception Hierarchy]]
- [[_COMMUNITY_Config Migration Plan|Config Migration Plan]]
- [[_COMMUNITY_Sheets Provisioning|Sheets Provisioning]]
- [[_COMMUNITY_Expense Parsing|Expense Parsing]]
- [[_COMMUNITY_Roadmap Configuration & UX|Roadmap: Configuration & UX]]
- [[_COMMUNITY_Roadmap Test Coverage Targets|Roadmap: Test Coverage Targets]]
- [[_COMMUNITY_Roadmap Future Capabilities|Roadmap: Future Capabilities]]
- [[_COMMUNITY_Serialization Helpers|Serialization Helpers]]
- [[_COMMUNITY_Currency Conversion Tests|Currency Conversion Tests]]
- [[_COMMUNITY_Legacy Currency Conversion|Legacy Currency Conversion]]
- [[_COMMUNITY_Main Entry Point Variants|Main Entry Point Variants]]
- [[_COMMUNITY_Categorization Rule Types|Categorization Rule Types]]
- [[_COMMUNITY_Exchange Rate Rate-Limiting|Exchange Rate Rate-Limiting]]
- [[_COMMUNITY_Date Parsing Debug Script|Date Parsing Debug Script]]
- [[_COMMUNITY_Date Parsing Issue Test|Date Parsing Issue Test]]
- [[_COMMUNITY_GUI Rewrite Helper Script|GUI Rewrite Helper Script]]

## God Nodes (most connected - your core abstractions)
1. `ExpenseTrackerGUI` - 63 edges
2. `ExpenseTracker (BAC Credomatic Automated Expense Tracker)` - 39 edges
3. `ExpenseDatabase` - 34 edges
4. `SheetsManager` - 28 edges
5. `EmailParser` - 24 edges
6. `ProcessingResult` - 18 edges
7. `ExpenseParser` - 17 edges
8. `ConfigManager` - 15 edges
9. `ExpenseTracker` - 15 edges
10. `CurrencyConverter` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_date_parsing()` --calls--> `DateParser`  [INFERRED]
  test_date_issue.py → src/date_parser.py
- `migrate_vendor_keywords()` --calls--> `ExpenseDatabase`  [INFERRED]
  misc/migrate_data.py → src/database.py
- `migrate_categories()` --calls--> `ExpenseDatabase`  [INFERRED]
  misc/migrate_data.py → src/database.py
- `migrate_category_rules()` --calls--> `ExpenseDatabase`  [INFERRED]
  misc/migrate_data.py → src/database.py
- `test_comprehensive_dates()` --calls--> `DateParser`  [INFERRED]
  test_comprehensive_dates.py → src/date_parser.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Python Dependencies (Google APIs, Sheets, Parsing, HTTP)** — requirements_google_auth, requirements_google_auth_oauthlib, requirements_google_auth_httplib2, requirements_google_api_python_client, requirements_gspread, requirements_beautifulsoup4, requirements_requests [EXTRACTED 1.00]
- **Phase 1 Correctness & Reliability Fixes** — roadmap_idempotency_duplicate_prevention, roadmap_remove_hardcoded_configs, roadmap_date_parsing_fallback_bug, roadmap_retry_logic [EXTRACTED 1.00]
- **Categorization Rule Types** — readme_rule_type_vendor_exact, readme_rule_type_vendor_contains, readme_rule_type_keyword_contains [EXTRACTED 1.00]

## Communities (52 total, 3 thin omitted)

### Community 0 - "GUI Application"
Cohesion: 0.08
Nodes (3): ExpenseTrackerGUI, Compatibility shim used by older call-sites., Return a slightly darker hex colour.

### Community 1 - "Data Migration Scripts"
Cohesion: 0.05
Nodes (27): main(), migrate_categories(), migrate_category_rules(), migrate_vendor_keywords(), Migrate category assignment rules to database, Migrate vendor keywords from hardcoded dictionary to database, Migrate categories to database, ExpenseDatabase (+19 more)

### Community 2 - "Project Metadata & Dependencies"
Cohesion: 0.07
Nodes (33): BeautifulSoup4, data/expense_tracker.db, ExpenseTracker (BAC Credomatic Automated Expense Tracker), Gmail API, google-api-python-client, google-auth, google-auth-httplib2, google-auth-oauthlib (+25 more)

### Community 3 - "Gmail Email Fetching"
Cohesion: 0.09
Nodes (18): EmailParser, Fetch detailed information for a specific email                  Args:, Extract header value by name, Parse email date string to datetime, Extract email body from payload, Mark an email as read, Get the Gmail service object, Verify Gmail API access by attempting to fetch user profile                  Ret (+10 more)

### Community 4 - "Legacy Main Workflow"
Cohesion: 0.08
Nodes (27): add_expense_to_sheet(), authenticate_google_api(), convert_currency_to_crc(), ExpenseTracker, fetch_expense_emails(), get_email_content(), get_exchange_rate(), get_gmail_service() (+19 more)

### Community 5 - "Expense Model & Sheets Errors"
Cohesion: 0.11
Nodes (16): Expense, GoogleSheetsError, Represents a parsed expense transaction, Error during Google Sheets operations, Validate expense data integrity, Get formatted amount for display, Get conversion information for notes, Any (+8 more)

### Community 6 - "Email History Tracking"
Cohesion: 0.09
Nodes (15): EmailHistoryDB, Email processing history — stored in data/email_history.db (separate from the ru, Returns rows: (email_id, vendor, original_amount, original_currency,, Tracks which emails have been processed and how., True if this email was already processed successfully., Upsert a row for this email., main(), ExpenseTracker (+7 more)

### Community 7 - "Configuration Management"
Cohesion: 0.09
Nodes (14): Config, ConfigManager, Get the current configuration, Get the global configuration instance, Get required Google API scopes, Validate that required configuration is present, Configuration settings for ExpenseTracker, Get the full path to Gmail credentials (+6 more)

### Community 8 - "Core Module Overview"
Cohesion: 0.22
Nodes (12): datetime, Logger, Configuration management for ExpenseTracker Centralizes all configuration settin, Currency conversion functionality for ExpenseTracker Handles real-time exchange, Date parsing functionality for ExpenseTracker Handles Spanish date formats and v, Gmail integration for ExpenseTracker Handles email fetching and authentication w, Expense parsing functionality for ExpenseTracker Extracts expense data from emai, ExpenseTracker - Main Application Automated expense tracking from BAC Credomatic (+4 more)

### Community 9 - "Logging Infrastructure"
Cohesion: 0.12
Nodes (11): ExpenseTrackerLogger, get_logger(), Exception, Logging configuration for ExpenseTracker Provides structured logging with file a, Centralized logging for ExpenseTracker, Configure logging with file and console handlers, Get the configured logger instance, Log expense processing with structured data (+3 more)

### Community 10 - "Date Parsing Tests"
Cohesion: 0.13
Nodes (10): DateParser, Parse a specific date string using the appropriate format                  Args:, Convert Spanish month abbreviations to English                  Args:, Handles parsing of dates from email text with Spanish support, Validate that a date string is in the correct format                  Args:, Parse date from email text                  Args:             email_text: Email, Test various date formats that might appear in emails, test_comprehensive_dates() (+2 more)

### Community 11 - "Admin DB CLI"
Cohesion: 0.19
Nodes (15): add_category(), add_rule(), add_vendor(), delete_vendor(), list_categories(), list_rules(), list_vendors(), main() (+7 more)

### Community 12 - "Roadmap: Reliability & Observability"
Cohesion: 0.17
Nodes (13): AmountNotFoundError, DateNotFoundError, Idempotency / Duplicate Prevention (1.1), Metrics Dashboard GUI tab (2.4), Phase 1: Correctness & Reliability, Phase 2: Robustness & Observability, Priority Summary table, processed_emails table (+5 more)

### Community 13 - "Currency Conversion"
Cohesion: 0.14
Nodes (8): CurrencyConverter, Fetch rate from exchangerate-api.com, Fetch rate from fixer.io (requires API key), Handles currency conversion with caching and fallbacks, Fetch rate from currencyapi.com, Detect currency from email text                  Args:             text: Email t, Get currency symbol for currency code, Clear the exchange rate cache

### Community 14 - "Main App Orchestrator"
Cohesion: 0.20
Nodes (10): ExpenseTracker, main(), Verify that all components are properly configured                  Returns:, Get comprehensive system status information                  Returns:, Main entry point for the application, Main application orchestrator for expense tracking, Main processing workflow: fetch emails, parse expenses, add to sheets, ProcessingResult (+2 more)

### Community 15 - "Custom Exception Hierarchy"
Cohesion: 0.15
Nodes (13): Exception, CurrencyConversionError, DatabaseError, EmailParsingError, ExpenseParsingError, ExpenseTrackerError, Base exception for ExpenseTracker, Error during email parsing (+5 more)

### Community 16 - "Config Migration Plan"
Cohesion: 0.20
Nodes (12): src/config_manager.py, src/config.py, src/credentials.json, config.json (proposed), config.py to config.json migration (4.4), credentials.json.example, Fallback exchange rates in config_manager.py, FILTER_BY_MONTH hardcoded config (+4 more)

### Community 17 - "Sheets Provisioning"
Cohesion: 0.17
Nodes (6): Resolve the spreadsheet for the current/configured month.         Searches the E, Search for a spreadsheet by exact name inside a Drive folder. Returns ID or None, Copy the template spreadsheet into folder_id with the given name.         Return, Find an existing Drive folder by name, or create it. Returns folder ID., Write the new spreadsheet ID back to config.py so it persists across restarts., Return 'YYYY-MM' for the target month (from FILTER_BY_MONTH or today).

### Community 18 - "Expense Parsing"
Cohesion: 0.24
Nodes (6): ExpenseParser, Parse amount and currency from email text                  Returns:, Parse vendor from email text                  Args:             email_text: Emai, Parses expense data from BAC Credomatic email content, Generate notes for the expense                  Args:             email_text: Em, Parse expense data from email text                  Args:             email_text

### Community 19 - "Roadmap: Configuration & UX"
Cohesion: 0.25
Nodes (8): BAC Credomatic, src/sheets_manager.py, BankProfile configuration, Column mapping config, Configurable Sheets Columns (3.2), Email Recovery Mode (3.3), Multi-Bank / Multi-Account Support (3.4), Phase 3: Configuration & UX

### Community 20 - "Roadmap: Test Coverage Targets"
Cohesion: 0.29
Nodes (7): Spanish Date Parsing, src/currency_converter.py, src/date_parser.py, src/expense_parser.py, Date Parsing Fallback Bug (1.3), ExpenseParsingError, Test Coverage (4.1)

### Community 21 - "Roadmap: Future Capabilities"
Cohesion: 0.29
Nodes (7): src/admin_database.py, Budget Tracking (5.1), budgets table, Category Rule Editor in GUI (5.4), Export feature (5.2), Phase 5: Future Capabilities, Scheduled / Background Mode (5.3)

### Community 22 - "Serialization Helpers"
Cohesion: 0.29
Nodes (4): Any, Convert result to dictionary, Convert expense to dictionary for serialization, Create expense from dictionary

### Community 23 - "Currency Conversion Tests"
Cohesion: 0.38
Nodes (6): convert_currency_to_crc(), get_exchange_rate(), Get current exchange rate from one currency to another.     Default converts to, Convert amount from given currency to Costa Rican Colones (CRC).     Returns tup, Test currency detection and conversion with sample emails, test_currency_patterns()

### Community 24 - "Legacy Currency Conversion"
Cohesion: 0.33
Nodes (3): Convert amount to Costa Rican Colones (CRC)                  Args:             a, Get exchange rate between two currencies                  Args:             from, Fetch exchange rate from external API                  Args:             from_cu

### Community 25 - "Main Entry Point Variants"
Cohesion: 0.60
Nodes (5): src/main.py, batch_add_expenses(), src/main_old.py, src/main_refactored.py, Remove Dead Code (4.2)

### Community 26 - "Categorization Rule Types"
Cohesion: 0.50
Nodes (4): Automatic Categorization System, keyword_contains rule type, vendor_contains rule type, vendor_exact rule type

### Community 27 - "Exchange Rate Rate-Limiting"
Cohesion: 0.50
Nodes (4): Currency Conversion System, exchangerate-api.com, exchangerate-api.com 1500/month limit, Rate Limiting Awareness (2.3)

## Knowledge Gaps
- **33 isolated node(s):** `Gmail API`, `Google Sheets API`, `Vendor Recognition Database (100+ merchants)`, `src/gui.py`, `src/logger.py` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExpenseDatabase` connect `Data Migration Scripts` to `GUI Application`, `Legacy Main Workflow`, `Email History Tracking`, `Configuration Management`, `Admin DB CLI`, `Main App Orchestrator`, `Expense Parsing`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **Why does `ExpenseTrackerGUI` connect `GUI Application` to `Data Migration Scripts`, `Email History Tracking`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `ExpenseTracker` connect `Email History Tracking` to `GUI Application`, `Data Migration Scripts`, `Gmail Email Fetching`, `Expense Model & Sheets Errors`, `Configuration Management`, `Core Module Overview`, `Main App Orchestrator`, `Expense Parsing`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ExpenseTrackerGUI` (e.g. with `ExpenseDatabase` and `EmailHistoryDB`) actually correct?**
  _`ExpenseTrackerGUI` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ExpenseDatabase` (e.g. with `migrate_categories()` and `migrate_category_rules()`) actually correct?**
  _`ExpenseDatabase` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `SheetsManager` (e.g. with `ExpenseTracker` and `.__init__()`) actually correct?**
  _`SheetsManager` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `EmailParser` (e.g. with `ConfigManager` and `EmailData`) actually correct?**
  _`EmailParser` has 10 INFERRED edges - model-reasoned connections that need verification._