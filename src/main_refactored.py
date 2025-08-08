"""
ExpenseTracker - Main Application
Automated expense tracking from BAC Credomatic emails to Google Sheets
"""

import time
from datetime import datetime
from typing import List

# Import our modular components
from config_manager import ConfigManager
from logger import get_logger
from email_parser import EmailParser
from expense_parser import ExpenseParser
from sheets_manager import SheetsManager
from models import ProcessingResult
from database import ExpenseDatabase

# Initialize logger
logger = get_logger()

class ExpenseTracker:
    """Main application orchestrator for expense tracking"""
    
    def __init__(self):
        """Initialize the expense tracker with all components"""
        logger.info("Initializing ExpenseTracker")
        
        try:
            self.config = ConfigManager.get_config()
            self.email_parser = EmailParser()
            self.expense_parser = ExpenseParser()
            self.sheets_manager = SheetsManager()
            self.db = ExpenseDatabase()
            
            logger.info("ExpenseTracker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ExpenseTracker: {e}")
            raise
    
    def process_expenses(self) -> List[ProcessingResult]:
        """
        Main processing workflow: fetch emails, parse expenses, add to sheets
        
        Returns:
            List of ProcessingResult objects for each processed expense
        """
        logger.info("Starting expense processing workflow")
        results = []
        
        try:
            # Step 1: Fetch emails
            logger.info("Step 1: Fetching emails from Gmail")
            emails = self.email_parser.fetch_bac_emails()
            logger.info(f"Found {len(emails)} emails to process")
            
            if not emails:
                logger.info("No emails found to process")
                return results
            
            # Step 2: Process each email
            logger.info("Step 2: Processing emails and extracting expenses")
            expenses = []
            
            for email_data in emails:
                try:
                    logger.debug(f"Processing email {email_data.id}")
                    
                    # Parse expense from email
                    expense = self.expense_parser.parse_expense_from_email(
                        email_data.body, 
                        email_data.id
                    )
                    
                    expenses.append(expense)
                    logger.debug(f"Successfully parsed expense: {expense.vendor} - {expense.get_display_amount()}")
                    
                except Exception as e:
                    logger.error(f"Failed to parse expense from email {email_data.id}: {e}")
                    results.append(ProcessingResult(
                        success=False,
                        message=f"Failed to parse email {email_data.id}",
                        error=str(e)
                    ))
            
            logger.info(f"Successfully parsed {len(expenses)} expenses")
            
            # Step 3: Add expenses to Google Sheets
            if expenses:
                logger.info("Step 3: Adding expenses to Google Sheets")
                
                if len(expenses) > 1:
                    # Use batch operation for multiple expenses
                    sheet_results = self.sheets_manager.batch_add_expenses(expenses)
                    results.extend(sheet_results)
                else:
                    # Single expense
                    sheet_result = self.sheets_manager.add_expense_to_sheet(expenses[0])
                    results.append(sheet_result)
            
            # Step 4: Mark emails as processed (optional)
            logger.info("Step 4: Marking processed emails")
            for email_data in emails:
                try:
                    self.email_parser.mark_email_as_processed(email_data.id)
                except Exception as e:
                    logger.warning(f"Failed to mark email {email_data.id} as processed: {e}")
            
            logger.info(f"Expense processing completed. Processed {len(results)} items")
            return results
            
        except Exception as e:
            logger.error(f"Expense processing workflow failed: {e}")
            results.append(ProcessingResult(
                success=False,
                message="Workflow failed",
                error=str(e)
            ))
            return results
    
    def verify_setup(self) -> ProcessingResult:
        """
        Verify that all components are properly configured
        
        Returns:
            ProcessingResult with verification status
        """
        logger.info("Verifying ExpenseTracker setup")
        
        try:
            # Verify Gmail access
            gmail_result = self.email_parser.verify_gmail_access()
            if not gmail_result.success:
                return ProcessingResult(
                    success=False,
                    message="Gmail verification failed",
                    error=gmail_result.error
                )
            
            # Verify Sheets access
            sheets_result = self.sheets_manager.verify_sheet_access()
            if not sheets_result.success:
                return ProcessingResult(
                    success=False,
                    message="Google Sheets verification failed", 
                    error=sheets_result.error
                )
            
            # Verify database
            vendor_count = len(self.db.get_all_vendors())
            category_count = len(self.db.get_all_categories())
            
            logger.info(f"Setup verification successful - Gmail: OK, Sheets: OK, Database: {vendor_count} vendors, {category_count} categories")
            
            return ProcessingResult(
                success=True,
                message="All components verified successfully",
                details={
                    'gmail_status': 'OK',
                    'sheets_status': 'OK',
                    'database_vendors': vendor_count,
                    'database_categories': category_count
                }
            )
            
        except Exception as e:
            logger.error(f"Setup verification failed: {e}")
            return ProcessingResult(
                success=False,
                message="Setup verification failed",
                error=str(e)
            )
    
    def get_system_status(self) -> dict:
        """
        Get comprehensive system status information
        
        Returns:
            Dictionary with system status details
        """
        try:
            # Get configuration info
            config_info = {
                'filter_by_month': self.config.filter_by_month,
                'google_sheet_id': self.config.google_sheet_id[:10] + '...' if self.config.google_sheet_id else None,
                'google_sheet_tab': self.config.google_sheet_tab
            }
            
            # Get database stats
            db_stats = {
                'vendors': len(self.db.get_all_vendors()),
                'categories': len(self.db.get_all_categories()),
                'total_rules': sum(len(vendors) for vendors in self.db.get_all_vendors().values())
            }
            
            # Get sheets info
            sheets_info = self.sheets_manager.get_sheet_info()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'configuration': config_info,
                'database': db_stats,
                'sheets': sheets_info,
                'status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }

def main():
    """Main entry point for the application"""
    logger.info("=== ExpenseTracker Started ===")
    
    try:
        # Initialize tracker
        tracker = ExpenseTracker()
        
        # Verify setup
        logger.info("Verifying system setup...")
        setup_result = tracker.verify_setup()
        
        if not setup_result.success:
            logger.error(f"Setup verification failed: {setup_result.message}")
            print(f"❌ Setup verification failed: {setup_result.message}")
            if setup_result.error:
                print(f"Error details: {setup_result.error}")
            return 1
        
        logger.info("✅ Setup verification successful")
        print("✅ System setup verified successfully")
        
        # Process expenses
        logger.info("Starting expense processing...")
        print("🔄 Processing expenses...")
        
        results = tracker.process_expenses()
        
        # Report results
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"Processing completed: {successful} successful, {failed} failed")
        print(f"✅ Processing completed: {successful} successful, {failed} failed")
        
        # Show detailed results
        if results:
            print("\n📊 Detailed Results:")
            for i, result in enumerate(results, 1):
                status = "✅" if result.success else "❌"
                print(f"  {i}. {status} {result.message}")
                if not result.success and result.error:
                    print(f"     Error: {result.error}")
        
        # Show system status
        status = tracker.get_system_status()
        if 'database' in status:
            db_stats = status['database']
            print(f"\n📈 System Stats: {db_stats['vendors']} vendors, {db_stats['categories']} categories, {db_stats['total_rules']} rules")
        
        logger.info("=== ExpenseTracker Completed ===")
        return 0 if failed == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n⏹️  Process interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
