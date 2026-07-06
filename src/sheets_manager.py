"""
Google Sheets management functionality for ExpenseTracker
Handles adding expenses to Google Sheets
"""

import pickle
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config_manager import ConfigManager
from models import Expense, ProcessingResult, GoogleSheetsError
from logger import get_logger

logger = get_logger()

class SheetsManager:
    """Manages Google Sheets integration for expense tracking"""

    # OAuth scopes — Sheets + Drive (needed to copy template & manage folder)
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]

    # Template to copy when no spreadsheet has been configured yet
    TEMPLATE_ID     = '13P4kQm1xVlvnLSrm4Pv-mfW6t3KZyMYmIachqVDQtYU'
    DRIVE_FOLDER    = 'ExpenseTracker'
    def __init__(self):
        self.config = ConfigManager.get_config()
        self.credentials = None
        self.service = None
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize Google Sheets credentials"""
        logger.info("Initializing Google Sheets credentials")
        
        try:
            # Load existing credentials if available
            token_path = os.path.join(self.config.src_dir, 'token.pickle')
            
            if os.path.exists(token_path):
                logger.debug("Loading existing credentials from token.pickle")
                with open(token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Refresh or get new credentials if needed
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        logger.info("Refreshing expired credentials")
                        self.credentials.refresh(Request())
                    except Exception as refresh_error:
                        logger.warning(f"Token refresh failed ({refresh_error}) — deleting stale token and re-authenticating")
                        if os.path.exists(token_path):
                            os.remove(token_path)
                        self.credentials = None
                
                if not self.credentials:
                    logger.info("Getting new credentials via OAuth flow")
                    credentials_path = os.path.join(self.config.src_dir, 'credentials.json')
                    if not os.path.exists(credentials_path):
                        raise GoogleSheetsError(f"Credentials file not found: {credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for future use
                logger.debug("Saving credentials to token.pickle")
                with open(token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=self.credentials)
            logger.info("Google Sheets service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets credentials: {e}")
            raise GoogleSheetsError(f"Sheets authentication failed: {e}")
        
        # Auto-create a spreadsheet if none is configured
        self._ensure_spreadsheet_exists()

    # ── Monthly-sheet helpers ─────────────────────────────────────────────────

    def _get_target_month_key(self) -> str:
        """Return 'YYYY-MM' for the target month (from FILTER_BY_MONTH or today)."""
        fm = self.config.filter_by_month  # e.g. "2026/07"
        if fm:
            try:
                parts = fm.replace('-', '/').split('/')
                if len(parts) == 2:
                    return f"{parts[0]}-{parts[1].zfill(2)}"
            except Exception:
                pass
        return datetime.now().strftime('%Y-%m')

    def _ensure_spreadsheet_exists(self):
        """Resolve the spreadsheet for the current/configured month.
        Searches the ExpenseTracker Drive folder for 'Expense Tracker YYYY-MM';
        creates a copy of the template if none exists yet.
        Always updates self.config.google_sheet_id for this run.
        """
        month_key  = self._get_target_month_key()        # e.g. "2026-07"
        sheet_name = f"Expense Tracker {month_key}"

        drive     = build('drive', 'v3', credentials=self.credentials)
        folder_id = self._get_or_create_drive_folder(drive, self.DRIVE_FOLDER)

        existing_id = self._find_sheet_in_folder(drive, folder_id, sheet_name)
        if existing_id:
            logger.info(f"Reusing existing sheet for {month_key}: {existing_id}")
            self.config.google_sheet_id = existing_id
            self._save_sheet_id_to_config(existing_id)
            return

        # No sheet for this month yet — copy the template
        logger.info(f"No sheet found for {month_key} — copying template")
        sheet_id, sheet_url, tab_names = self._copy_template(drive, folder_id, sheet_name)
        self._save_sheet_id_to_config(sheet_id)
        self.config.google_sheet_id = sheet_id
        self.created_sheet_url      = sheet_url
        logger.info(f"New sheet for {month_key}: {sheet_url}")
        logger.info(f"Tabs: {tab_names}")
        print(f"\n✓ Google Sheet for {month_key} created: {sheet_url}\n")

    def _find_sheet_in_folder(self, drive_service, folder_id: str, name: str) -> Optional[str]:
        """Search for a spreadsheet by exact name inside a Drive folder. Returns ID or None."""
        q = (
            f"name='{name}' "
            f"and '{folder_id}' in parents "
            "and mimeType='application/vnd.google-apps.spreadsheet' "
            "and trashed=false"
        )
        res   = drive_service.files().list(q=q, fields='files(id,name)').execute()
        files = res.get('files', [])
        return files[0]['id'] if files else None

    def _copy_template(self, drive_service, folder_id: str, name: str) -> Tuple[str, str, List[str]]:
        """Copy the template spreadsheet into folder_id with the given name.
        Returns (sheet_id, url, tab_names)."""
        copy = drive_service.files().copy(
            fileId=self.TEMPLATE_ID,
            body={'name': name, 'parents': [folder_id]},
            fields='id,webViewLink',
        ).execute()

        sheet_id  = copy['id']
        sheet_url = copy.get(
            'webViewLink',
            f'https://docs.google.com/spreadsheets/d/{sheet_id}',
        )
        logger.info(f"Copied template → '{name}' (id={sheet_id})")

        # Discover tabs from the copy
        meta      = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        tab_names = [s['properties']['title'] for s in meta.get('sheets', [])]

        # Fall back to first tab if the configured tab name isn't present
        if self.config.google_sheet_tab not in tab_names and tab_names:
            logger.info(
                f"Configured tab '{self.config.google_sheet_tab}' not in template; "
                f"using '{tab_names[0]}'"
            )
            self.config.google_sheet_tab = tab_names[0]

        return sheet_id, sheet_url, tab_names

    def _get_or_create_drive_folder(self, drive_service, folder_name: str) -> str:
        """Find an existing Drive folder by name, or create it. Returns folder ID."""
        q = (
            f"name='{folder_name}' "
            "and mimeType='application/vnd.google-apps.folder' "
            "and trashed=false"
        )
        res   = drive_service.files().list(q=q, fields='files(id,name)').execute()
        files = res.get('files', [])
        if files:
            fid = files[0]['id']
            logger.info(f"Using existing Drive folder '{folder_name}': {fid}")
            return fid

        folder = drive_service.files().create(
            body={
                'name':     folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
            },
            fields='id',
        ).execute()
        fid = folder['id']
        logger.info(f"Created Drive folder '{folder_name}': {fid}")
        return fid

    def _save_sheet_id_to_config(self, sheet_id: str):
        """Write the new spreadsheet ID back to config.py so it persists across restarts."""
        config_path = os.path.join(self.config.src_dir, 'config.py')
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            updated = re.sub(
                r'^(SPREADSHEET_ID\s*=\s*)["\'].*?["\']',
                f'SPREADSHEET_ID = "{sheet_id}"',
                content,
                flags=re.MULTILINE,
            )
            with open(config_path, 'w') as f:
                f.write(updated)
            logger.info(f"Saved new SPREADSHEET_ID to config.py")
        except Exception as e:
            logger.warning(f"Could not persist spreadsheet ID to config.py: {e}")

    def add_expense_to_sheet(self, expense: Expense) -> ProcessingResult:
        logger.info(f"Adding expense to sheet: {expense.vendor} - {expense.get_display_amount()}")
        try:
            sheet_id = self.config.google_sheet_id
            tab_id   = self._get_tab_sheet_id(sheet_id)

            # Find the last data row and insert a blank row after it.
            # Sheets copies the format from the row above → date/currency cells
            # keep their format; we only write plain values.
            last_row_idx = self._get_last_data_row(sheet_id)  # 0-based
            self._insert_blank_rows(sheet_id, tab_id, last_row_idx)

            new_row = last_row_idx + 1   # 1-based sheet row
            row_data = self._format_expense_for_sheets(expense)
            range_name = f"{self.config.google_sheet_tab}!B{new_row}"

            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body={'values': [row_data]},
            ).execute()

            updated_range = result.get('updatedRange', range_name)
            logger.info(f"Added expense to sheet at {updated_range}")

            return ProcessingResult(
                success=True,
                message=f"Added to sheet: {expense.vendor} - {expense.get_display_amount()}",
                details={
                    'updated_range': updated_range,
                    'sheet_id':  sheet_id,
                    'expense_id': expense.email_id,
                }
            )
        except Exception as e:
            logger.error(f"Failed to add expense to sheet: {e}")
            return ProcessingResult(
                success=False,
                message=f"Failed to add expense to sheet: {e}",
                error=str(e),
            )
    
    def _format_expense_for_sheets(self, expense: Expense) -> List[Any]:
        """
        Format expense data for Google Sheets row
        Matches original format: Date, Amount, Vendor, Category (columns B-E)
        
        Args:
            expense: Expense object to format
            
        Returns:
            List of values for sheet row
        """
        # Format date — use MM/DD/YYYY (unambiguous for USER_ENTERED)
        date_str = expense.date.strftime('%m/%d/%Y')

        # Amount as plain number — cell inherits currency format from the row above
        amount_value = round(expense.amount, 2)
        
        # Create the row data matching original format (B, C, D, E)
        row_data = [
            date_str,                    # Column B: Date
            amount_value,                # Column C: Amount (as number)
            expense.vendor,              # Column D: Vendor
            expense.category,            # Column E: Category
        ]
        
        logger.debug(f"Formatted expense row: {row_data}")
        return row_data
    
    # ── Format-preserving helpers ────────────────────────────────────────────

    def _get_tab_sheet_id(self, spreadsheet_id: str) -> int:
        """Return the numeric sheetId for the configured tab name."""
        meta = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        for sheet in meta.get('sheets', []):
            props = sheet.get('properties', {})
            if props.get('title') == self.config.google_sheet_tab:
                return props['sheetId']
        raise GoogleSheetsError(
            f"Tab '{self.config.google_sheet_tab}' not found in spreadsheet"
        )

    def _get_last_data_row(self, spreadsheet_id: str) -> int:
        """Return the 0-based index of the row AFTER the last data row in col B."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{self.config.google_sheet_tab}!B:B",
        ).execute()
        return len(result.get('values', []))

    def _insert_blank_rows(self, spreadsheet_id: str, tab_id: int,
                           after_index: int, count: int = 1):
        """Insert `count` blank rows at `after_index` (0-based), inheriting format from the row below.
        Using inheritFromBefore=False so the first entry (inserted right after the header)
        picks up the data-row format rather than the header format."""
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [{
                'insertDimension': {
                    'range': {
                        'sheetId':    tab_id,
                        'dimension':  'ROWS',
                        'startIndex': after_index,
                        'endIndex':   after_index + count,
                    },
                    'inheritFromBefore': False,
                }
            }]}
        ).execute()

    def verify_sheet_access(self) -> ProcessingResult:
        """
        Verify that we can access the configured Google Sheet
        
        Returns:
            ProcessingResult with verification status
        """
        logger.info("Verifying Google Sheets access")
        
        try:
            sheet_id = self.config.google_sheet_id
            
            # Try to get sheet metadata
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            sheet_title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            logger.info(f"Successfully accessed sheet: {sheet_title}")
            
            # Try to read from the configured tab (sample data range)
            range_name = f"{self.config.google_sheet_tab}!B1:E1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.debug(f"Read sample data from sheet: {values}")
            
            return ProcessingResult(
                success=True,
                message=f"Sheet access verified: {sheet_title}",
                details={
                    'sheet_id': sheet_id,
                    'sheet_title': sheet_title,
                    'sheet_url': f"https://docs.google.com/spreadsheets/d/{sheet_id}",
                    'tab_name': self.config.google_sheet_tab,
                    'sample_data': values
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to verify sheet access: {e}")
            return ProcessingResult(
                success=False,
                message=f"Sheet access failed: {str(e)}",
                error=str(e)
            )
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """
        Get information about the configured Google Sheet
        
        Returns:
            Dictionary with sheet information
        """
        try:
            sheet_id = self.config.google_sheet_id
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            properties = sheet_metadata.get('properties', {})
            sheets = sheet_metadata.get('sheets', [])
            
            # Find our configured tab
            target_tab = None
            for sheet in sheets:
                sheet_props = sheet.get('properties', {})
                if sheet_props.get('title') == self.config.google_sheet_tab:
                    target_tab = sheet_props
                    break
            
            return {
                'sheet_id': sheet_id,
                'sheet_title': properties.get('title', 'Unknown'),
                'sheet_url': f"https://docs.google.com/spreadsheets/d/{sheet_id}",
                'target_tab': self.config.google_sheet_tab,
                'target_tab_found': target_tab is not None,
                'target_tab_info': target_tab,
                'total_sheets': len(sheets),
                'available_sheets': [s.get('properties', {}).get('title') for s in sheets]
            }
            
        except Exception as e:
            logger.error(f"Failed to get sheet info: {e}")
            return {'error': str(e)}
    
    def batch_add_expenses(self, expenses: List[Expense]) -> List[ProcessingResult]:
        logger.info(f"Batch adding {len(expenses)} expenses to sheet")
        if not expenses:
            return []
        results = []
        try:
            sheet_id = self.config.google_sheet_id
            tab_id   = self._get_tab_sheet_id(sheet_id)
            n        = len(expenses)

            # Insert n blank rows at once after the last data row
            last_row_idx = self._get_last_data_row(sheet_id)  # 0-based
            self._insert_blank_rows(sheet_id, tab_id, last_row_idx, count=n)

            # Write all values in one call
            first_new_row = last_row_idx + 1  # 1-based
            all_rows   = [self._format_expense_for_sheets(e) for e in expenses]
            range_name = f"{self.config.google_sheet_tab}!B{first_new_row}"

            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body={'values': all_rows},
            ).execute()

            updated_range = result.get('updatedRange', range_name)
            logger.info(f"Batch added {n} expenses at {updated_range}")

            for i, expense in enumerate(expenses):
                results.append(ProcessingResult(
                    success=True,
                    message=f"Batch added: {expense.vendor} - {expense.get_display_amount()}",
                    details={
                        'batch_operation': True,
                        'batch_size': n,
                        'batch_index': i,
                        'updated_range': updated_range,
                        'expense_id': expense.email_id,
                    }
                ))
        except Exception as e:
            logger.error(f"Batch add failed: {e}")
            for expense in expenses:
                results.append(ProcessingResult(
                    success=False,
                    message=f"Batch add failed: {e}",
                    error=str(e),
                ))
        return results
