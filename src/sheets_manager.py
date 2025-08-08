"""
Google Sheets management functionality for ExpenseTracker
Handles adding expenses to Google Sheets
"""

import pickle
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

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
    
    # Google Sheets scopes
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
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
                    logger.info("Refreshing expired credentials")
                    self.credentials.refresh(Request())
                else:
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
    
    def add_expense_to_sheet(self, expense: Expense) -> ProcessingResult:
        """
        Add expense to Google Sheets
        
        Args:
            expense: Expense object to add
            
        Returns:
            ProcessingResult with success/failure information
        """
        logger.info(f"Adding expense to sheet: {expense.vendor} - {expense.get_display_amount()}")
        
        try:
            # Format expense data for sheets
            row_data = self._format_expense_for_sheets(expense)
            
            # Get the sheet configuration
            sheet_id = self.config.google_sheet_id
            range_name = f"{self.config.google_sheet_tab}!B:E"  # Original format: B=Date, C=Amount, D=Vendor, E=Category
            
            # Prepare the request
            values = [row_data]
            body = {
                'values': values,
                'majorDimension': 'ROWS'
            }
            
            # Append to sheet
            logger.debug(f"Appending to sheet {sheet_id}, range {range_name}")
            result = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            # Get information about the inserted row
            updates = result.get('updates', {})
            updated_range = updates.get('updatedRange', 'Unknown')
            updated_rows = updates.get('updatedRows', 0)
            
            logger.info(f"Successfully added expense to sheet. Range: {updated_range}, Rows: {updated_rows}")
            
            return ProcessingResult(
                success=True,
                message=f"Added to sheet: {expense.vendor} - {expense.get_display_amount()}",
                details={
                    'updated_range': updated_range,
                    'updated_rows': updated_rows,
                    'sheet_id': sheet_id,
                    'expense_id': expense.email_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to add expense to sheet: {e}")
            return ProcessingResult(
                success=False,
                message=f"Failed to add expense to sheet: {str(e)}",
                error=str(e)
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
        # Format date as string
        date_str = expense.date.strftime('%Y-%m-%d')
        
        # Format amount as number (not string) for spreadsheet calculations
        amount_value = expense.amount
        
        # Create the row data matching original format (B, C, D, E)
        row_data = [
            date_str,                    # Column B: Date
            amount_value,                # Column C: Amount (as number)
            expense.vendor,              # Column D: Vendor
            expense.category,            # Column E: Category
        ]
        
        logger.debug(f"Formatted expense row: {row_data}")
        return row_data
    
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
        """
        Add multiple expenses to the sheet in a batch operation
        
        Args:
            expenses: List of expense objects to add
            
        Returns:
            List of ProcessingResult objects
        """
        logger.info(f"Batch adding {len(expenses)} expenses to sheet")
        
        if not expenses:
            return []
        
        results = []
        
        try:
            # Format all expenses for sheets
            all_rows = []
            for expense in expenses:
                row_data = self._format_expense_for_sheets(expense)
                all_rows.append(row_data)
            
            # Prepare batch request
            sheet_id = self.config.google_sheet_id
            range_name = f"{self.config.google_sheet_tab}!B:E"  # Original format: B=Date, C=Amount, D=Vendor, E=Category
            
            body = {
                'values': all_rows,
                'majorDimension': 'ROWS'
            }
            
            # Execute batch append
            result = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            # Create success results for all expenses
            updates = result.get('updates', {})
            updated_range = updates.get('updatedRange', 'Unknown')
            updated_rows = updates.get('updatedRows', 0)
            
            for i, expense in enumerate(expenses):
                results.append(ProcessingResult(
                    success=True,
                    message=f"Batch added: {expense.vendor} - {expense.get_display_amount()}",
                    details={
                        'batch_operation': True,
                        'batch_size': len(expenses),
                        'batch_index': i,
                        'updated_range': updated_range,
                        'total_updated_rows': updated_rows,
                        'expense_id': expense.email_id
                    }
                ))
            
            logger.info(f"Successfully batch added {len(expenses)} expenses. Updated range: {updated_range}")
            
        except Exception as e:
            logger.error(f"Batch add failed: {e}")
            # Create failure results for all expenses
            for expense in expenses:
                results.append(ProcessingResult(
                    success=False,
                    message=f"Batch add failed: {expense.vendor} - {expense.get_display_amount()}",
                    error=str(e)
                ))
        
        return results
