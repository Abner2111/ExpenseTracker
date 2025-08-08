
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
        """Verify that all components are properly configured"""
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
        """Get comprehensive system status information"""
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

def authenticate_google_api():
    """Authenticates with Google APIs (Gmail and Sheets)"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            import pickle
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            import pickle
            pickle.dump(creds, token)
    return creds

def get_gmail_service(creds):
    """Returns a Gmail service object."""
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred with Gmail API: {error}")
        return None

def get_sheets_client(creds):
    """Returns a gspread client for Google Sheets."""
    try:
        gc = gspread.authorize(creds)
        return gc
    except Exception as e:
        print(f"An error occurred with Google Sheets API: {e}")
        return None

def fetch_expense_emails(service, query_string=None):
    """
    Fetches unread emails that are likely expense receipts.
    Refined with Spanish keywords and BAC bank notifications.
    Optionally filters by month based on FILTER_BY_MONTH config.
    """
    if query_string is None:
        base_query = 'is:unread subject:"Notificación de transacción" from:notificacion@notificacionesbaccr.com'
        
        # Add month filter if specified in config
        if FILTER_BY_MONTH:
            # Convert FILTER_BY_MONTH to Gmail date filter format
            if "/" in FILTER_BY_MONTH:  # Format like "2025/08" or "2025/07"
                year, month = FILTER_BY_MONTH.split("/")
                # Gmail uses format like "after:2025/8/1 before:2025/9/1"
                start_date = f"after:{year}/{int(month)}/1"
                next_month = int(month) + 1
                next_year = year
                if next_month > 12:
                    next_month = 1
                    next_year = str(int(year) + 1)
                end_date = f"before:{next_year}/{next_month}/1"
                query_string = f"{base_query} {start_date} {end_date}"
                print(f"Filtering emails for {FILTER_BY_MONTH}: {query_string}")
            else:
                query_string = base_query
                print(f"Invalid FILTER_BY_MONTH format: {FILTER_BY_MONTH}. Using base query.")
        else:
            query_string = base_query
            print("No month filter specified. Processing all unread emails.")
    
    try:
        results = service.users().messages().list(userId='me', q=query_string).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        print(f"An error occurred fetching emails: {error}")
        return []

def get_email_content(service, msg_id):
    """Retrieves the full content of an email."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        payload = message['payload']
        parts = payload.get('parts', [])

        email_body = ""
        if parts:
            for part in parts:
                mime_type = part.get('mimeType')
                if mime_type == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        email_body += base64.urlsafe_b64decode(data).decode('utf-8') + "\n"
                elif mime_type == 'text/html':
                    data = part['body'].get('data')
                    if data:
                        html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        email_body += soup.get_text(separator='\n') + "\n"
        else:
            data = payload['body'].get('data')
            if data:
                email_body = base64.urlsafe_b64decode(data).decode('utf-8')

        return email_body, message['id']
    except HttpError as error:
        print(f"An error occurred getting email content: {error}")
        return "", ""

def parse_expense_from_email(email_text):
    """
    Parses the email text to extract expense details, with Costa Rica specific vendors.
    """
    expense_data = {
        'date': datetime.now().strftime('%Y-%m-%d'), # Default
        'vendor': 'Unknown',
        'amount': 0.0,
        'category': 'Personal',
        'notes': 'Parsed from email receipt (CR)'
    }

    email_text_lower = email_text.lower()

    # --- Amount Parsing with Currency Detection and Conversion ---
    amount_patterns = [
        # Pattern with explicit currency - CRC format
        (r'CRC\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'CRC'), # BAC format: CRC 5,650.00
        # Pattern with explicit currency - USD format (specific patterns first)
        (r'(?:Monto|Total):\s*USD\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'USD'), # Monto: USD 9.99
        (r'USD\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'USD'), # USD 9.99
        (r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*USD\b', 'USD'), # e.g., 25.50 USD
        (r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))', 'USD'), # $25.50 (assume USD)
        # Pattern with explicit currency - EUR format
        (r'(?:Monto|Total):\s*EUR\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'EUR'), # Monto: EUR 25.50
        (r'EUR\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'EUR'), # EUR 25.50
        (r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*EUR\b', 'EUR'), # e.g., 25.50 EUR
        (r'€(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))', 'EUR'), # €25.50
        # CRC patterns with colón symbol
        (r'₡\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'CRC'), # ₡5,650.00
        (r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*(?:CRC|₡|colones)\b', 'CRC'), # 5000 CRC
        # Generic patterns (assume CRC if no currency specified)
        (r'(?:Monto|Total|Monto Total|Total a Pagar|Subtotal|Gran Total):\s*(?:CRC|₡)?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', 'CRC'), # CRC format: 1.234,56
        (r'Monto:\s*[\r\n\s]*([₡\$]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'UNKNOWN'), # Look for "Monto:" followed by amount
        (r'Total:\s*[\r\n\s]*([₡\$]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'UNKNOWN'), # Look for "Total:" followed by amount
        (r'([₡\$]?\d{1,3}(?:,\d{3})*\.\d{2})', 'UNKNOWN'), # Any amount with decimal places
    ]
    
    print(f"Debug: Searching for amounts with currency detection...")
    
    original_currency = 'CRC'  # Default currency
    conversion_rate = 1.0
    
    for i, (pattern, currency_hint) in enumerate(amount_patterns):
        match = re.search(pattern, email_text, re.IGNORECASE)
        if match:
            amount_str = match.group(1)
            detected_currency = currency_hint
            print(f"Debug: Pattern {i+1} found amount match: '{amount_str}' with currency hint: '{detected_currency}' using pattern: {pattern}")
            
            # Determine actual currency based on symbols in the amount string
            if '₡' in amount_str:
                detected_currency = 'CRC'
                amount_str = amount_str.replace('₡', '').strip()
            elif '$' in amount_str:
                detected_currency = 'USD'
                amount_str = amount_str.replace('$', '').strip()
            elif '€' in amount_str:
                detected_currency = 'EUR'
                amount_str = amount_str.replace('€', '').strip()
            elif detected_currency == 'UNKNOWN':
                # Try to infer from context or default to CRC
                detected_currency = 'CRC'
                amount_str = amount_str.replace('₡', '').replace('$', '').strip()
            
            print(f"Debug: Detected currency: {detected_currency}")
            
            # Handle different number formats: 5,650.00 should become 5650.00
            if ',' in amount_str and '.' in amount_str:
                # This is US/BAC format: 5,650.00
                # Remove commas (thousands separators)
                processed_amount = amount_str.replace(',', '')
                print(f"Debug: US/BAC format - '{amount_str}' -> '{processed_amount}'")
                amount_str = processed_amount
            elif ',' in amount_str and '.' not in amount_str:
                # This might be European format: 5650,00 (but unlikely in BAC emails)
                if len(amount_str.split(',')[1]) == 2:  # Two digits after comma means decimal
                    processed_amount = amount_str.replace(',', '.')
                    print(f"Debug: European format - '{amount_str}' -> '{processed_amount}'")
                    amount_str = processed_amount
                else:
                    # Comma is thousands separator, no decimal
                    processed_amount = amount_str.replace(',', '')
                    print(f"Debug: Thousands separator - '{amount_str}' -> '{processed_amount}'")
                    amount_str = processed_amount
            else:
                print(f"Debug: No comma processing needed for '{amount_str}'")
            
            try:
                amount_value = float(amount_str)
                print(f"Debug: Parsed amount: {amount_value} {detected_currency}")
                
                # Convert to CRC if needed
                if detected_currency.upper() != 'CRC':
                    converted_amount, original_currency, conversion_rate = convert_currency_to_crc(amount_value, detected_currency)
                    expense_data['amount'] = converted_amount
                    expense_data['notes'] += f" | Original: {amount_value} {original_currency} (Rate: {conversion_rate})"
                else:
                    expense_data['amount'] = amount_value
                    original_currency = detected_currency
                
                print(f"Debug: Final amount in CRC: {expense_data['amount']}")
                break
            except ValueError:
                print(f"Debug: Failed to parse amount: {amount_str}")
                pass
    
    if expense_data['amount'] == 0.0:
        print("Debug: No amount found, searching for any number pattern...")
        # Try to find any number in the email as backup
        backup_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        all_matches = re.findall(backup_pattern, email_text)
        print(f"Debug: All number patterns found: {all_matches}")
    
    print(f"Debug: Final amount before returning: {expense_data['amount']}")  # Debug line

    # --- Date Parsing (Added common CR date formats) ---
    print(f"Debug: Starting date parsing...")
    print(f"Debug: First 500 chars of email text for date analysis:\n{email_text[:500]}")
    
    # Special handling for BAC format with lots of whitespace/newlines
    # Look for "Fecha:" followed by date on potentially next lines
    # Updated to handle Spanish abbreviations like "Ago" for "Agosto"
    bac_date_match = re.search(r'Fecha:\s*[\r\n\s]*(\w{3}\s+\d{1,2},\s+\d{4})(?:,\s+\d{1,2}:\d{2})?', email_text, re.IGNORECASE)
    if bac_date_match:
        date_str = bac_date_match.group(1).strip()
        print(f"Debug: Found BAC date format: '{date_str}'")
        
        # Handle Spanish month abbreviations
        spanish_months = {
            'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
            'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
            'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
        }
        
        # Convert Spanish month abbreviations to English
        for spanish_abbr, english_abbr in spanish_months.items():
            if spanish_abbr.lower() in date_str.lower():
                date_str = re.sub(r'\b' + spanish_abbr + r'\b', english_abbr, date_str, flags=re.IGNORECASE)
                print(f"Debug: Converted Spanish month '{spanish_abbr}' to '{english_abbr}': '{date_str}'")
                break
        
        try:
            expense_data['date'] = datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
            print(f"Debug: Successfully parsed BAC date: {expense_data['date']}")
        except ValueError as e:
            print(f"Debug: Failed to parse BAC date: {date_str}, error: {e}")
    else:
        print("Debug: No BAC date format found, trying other patterns...")
        # Fall back to other date patterns
        date_patterns = [
            r'(?:Fecha|Date|Fecha de Compra|Fecha de Transacción):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', # DD/MM/YYYY or DD-MM-YYYY
            r'(?:procesada el|el)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})', # "procesada el DD/MM/YYYY"
            r'(\w{3}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2})', # BAC format: Jul 31, 2025, 14:29
            r'(\d{4}-\d{2}-\d{2})', # YYYY-MM-DD
            r'(\d{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s+\d{4})', # DD Mon YYYY
            r'(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},\s+\d{4}', # Month DD, YYYY (Spanish)
            r'(\w{3}\s+\d{1,2},\s+\d{4})', # English Mon DD, YYYY
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})' # General DD/MM/YYYY or MM/DD/YYYY format
        ]
        date_found = False
        for i, pattern in enumerate(date_patterns):
            match = re.search(pattern, email_text, re.IGNORECASE)  # Use original text for date parsing
            if match:
                date_str = match.group(1).replace('.', '')
                print(f"Debug: Pattern {i+1} found date: '{date_str}' using pattern: {pattern}")
                # Handle BAC datetime format by removing time portion
                if ',' in date_str and ':' in date_str:
                    # Split on comma, keep first two parts, remove time from second part
                    parts = date_str.split(',')
                    if len(parts) >= 2:
                        date_str = parts[0] + ',' + parts[1].split(' ')[0] + ' ' + parts[1].split(' ')[1]
                    print(f"Debug: Cleaned datetime format: '{date_str}'")
                
                for fmt in ['%b %d, %Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %b %Y', '%B %d, %Y', '%d %B %Y', '%m/%d/%Y']:
                    try:
                        # Handle month names in Spanish if they appear without abbreviations or with abbreviations
                        date_str_clean = date_str
                        
                        # Handle Spanish month abbreviations first
                        spanish_months = {
                            'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
                            'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
                            'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
                        }
                        
                        for spanish_abbr, english_abbr in spanish_months.items():
                            if spanish_abbr.lower() in date_str_clean.lower():
                                date_str_clean = re.sub(r'\b' + spanish_abbr + r'\b', english_abbr, date_str_clean, flags=re.IGNORECASE)
                                break
                        
                        # Handle full Spanish month names
                        if 'enero' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('enero', 'Jan')
                        elif 'febrero' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('febrero', 'Feb')
                        elif 'marzo' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('marzo', 'Mar')
                        elif 'abril' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('abril', 'Apr')
                        elif 'mayo' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('mayo', 'May')
                        elif 'junio' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('junio', 'Jun')
                        elif 'julio' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('julio', 'Jul')
                        elif 'agosto' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('agosto', 'Aug')
                        elif 'septiembre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('septiembre', 'Sep')
                        elif 'octubre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('octubre', 'Oct')
                        elif 'noviembre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('noviembre', 'Nov')
                        elif 'diciembre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('diciembre', 'Dec')

                        expense_data['date'] = datetime.strptime(date_str_clean, fmt).strftime('%Y-%m-%d')
                        print(f"Debug: Successfully parsed date: {expense_data['date']} using format: {fmt}")
                        date_found = True
                        break
                    except ValueError as e:
                        print(f"Debug: Failed to parse '{date_str_clean}' with format '{fmt}': {e}")
                        continue
                if date_found:
                    break
        
        if not date_found:
            print("Debug: No date patterns matched, keeping default date")
    
    print(f"Debug: Final date assigned: {expense_data['date']}")

    # --- Vendor Identification and Categorization (Database-based) ---
    db = ExpenseDatabase()
    # Try to extract vendor from "Comercio:" field (BAC format)
    comercio_match = re.search(r'Comercio:\s*([^\n]+?)(?=\n|$)', email_text, re.IGNORECASE)
    if comercio_match:
        comercio_name = comercio_match.group(1).strip()
        # Remove any currency amounts from the vendor name
        comercio_name = re.sub(r'\s*[\$₡€]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|CRC)?\s*$', '', comercio_name, flags=re.IGNORECASE)
        comercio_name = re.sub(r'\s*(?:USD|EUR|CRC)\s+\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*$', '', comercio_name, flags=re.IGNORECASE)
        vendor_name = comercio_name.strip()
        print(f"Debug: Found vendor in Comercio field: '{vendor_name}'")
    else:
        # Fallback: search for vendor keyword in email text using database
        print("Debug: No Comercio field found, searching vendor keywords in database...")
        vendor_name = db.find_vendor_by_text(email_text)
        if vendor_name:
            print(f"Debug: Found vendor via database keyword: '{vendor_name}'")
        else:
            vendor_name = 'Unknown'
            print("Debug: No vendor keywords matched in database, vendor remains 'Unknown'")

    expense_data['vendor'] = vendor_name

    # --- Category Inference (Database-based) ---
    category = db.categorize_vendor(vendor_name if vendor_name != 'Unknown' else email_text)
    expense_data['category'] = category
    print(f"Debug: Assigned category '{category}' using database rules")

    print(f"Debug: Final category assigned: '{expense_data['category']}'")

    # Basic Notes
    # You might want to extract a specific line from the email for notes or the email subject
    subject_match = re.search(r'Subject: (.+)', email_text, re.IGNORECASE)
    if subject_match:
        expense_data['notes'] = f"Email Subject: {subject_match.group(1).strip()}" + (expense_data['notes'] if 'Original:' in expense_data['notes'] else '')
    # If no subject found, keep existing notes (which may include currency conversion info)

    return expense_data

def get_exchange_rate(from_currency, to_currency='CRC'):
    """
    Get current exchange rate from one currency to another.
    Default converts to Costa Rican Colones (CRC).
    """
    try:
        # Using exchangerate-api.com (free tier allows 1500 requests/month)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if to_currency in data['rates']:
                rate = data['rates'][to_currency]
                print(f"Debug: Exchange rate {from_currency} to {to_currency}: {rate}")
                return rate
            else:
                print(f"Warning: {to_currency} not found in exchange rates")
                return None
        else:
            print(f"Warning: Failed to get exchange rate. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Warning: Error getting exchange rate: {e}")
        return None

def convert_currency_to_crc(amount, currency):
    """
    Convert amount from given currency to Costa Rican Colones (CRC).
    Returns tuple: (converted_amount, original_currency, conversion_rate)
    """
    if currency.upper() == 'CRC':
        return amount, currency, 1.0
    
    # Common fallback rates if API fails (approximate rates as of 2025)
    fallback_rates = {
        'USD': 520.0,  # 1 USD ≈ 520 CRC (approximate)
        'EUR': 570.0,  # 1 EUR ≈ 570 CRC (approximate)
        'GBP': 650.0,  # 1 GBP ≈ 650 CRC (approximate)
    }
    
    # Try to get current exchange rate
    rate = get_exchange_rate(currency.upper(), 'CRC')
    
    if rate is None:
        # Use fallback rate if available
        if currency.upper() in fallback_rates:
            rate = fallback_rates[currency.upper()]
            print(f"Debug: Using fallback rate for {currency}: {rate}")
        else:
            print(f"Warning: No exchange rate available for {currency}. Using original amount.")
            return amount, currency, 1.0
    
    converted_amount = amount * rate
    print(f"Debug: Converted {amount} {currency} to {converted_amount:.2f} CRC (rate: {rate})")
    return converted_amount, currency, rate

def add_expense_to_sheet(gspread_client, expense_data):
    """Appends expense data to the Expenses section of the Google Sheet with rate limiting and duplicate checking."""
    max_retries = 3
    retry_delay = 60  # Start with 60 seconds delay
    
    for attempt in range(max_retries):
        try:
            spreadsheet = gspread_client.open_by_key(SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet(SPREADSHEET_NAME)

            # Check for duplicates by getting all existing data in the Expenses section
            # Get data from columns B-E (Date, Amount, Vendor, Category) starting from row 4
            try:
                existing_data = worksheet.get('B4:E1000')  # Get a large range to catch all data
                
                # Check if this expense already exists
                for row in existing_data:
                    if len(row) >= 3:  # Make sure we have at least date, amount, vendor
                        existing_date = row[0] if len(row) > 0 else ''
                        existing_amount = row[1] if len(row) > 1 else ''
                        existing_vendor = row[2] if len(row) > 2 else ''
                        
                        # Convert existing amount to float for comparison
                        try:
                            existing_amount_float = float(str(existing_amount).replace(',', ''))
                        except (ValueError, TypeError):
                            existing_amount_float = 0.0
                        
                        # Check if this is a duplicate (same date, amount, and vendor)
                        if (existing_date == expense_data['date'] and 
                            abs(existing_amount_float - expense_data['amount']) < 0.01 and  # Allow small floating point differences
                            existing_vendor.lower() == expense_data['vendor'].lower()):
                            print(f"⚠ Duplicate expense detected: {expense_data['vendor']} - ₡{expense_data['amount']:.2f} on {expense_data['date']}. Skipping.")
                            return True  # Return True to mark as "processed" but don't add duplicate
                            
            except Exception as e:
                print(f"Warning: Could not check for duplicates: {e}. Proceeding with add.")

            # Find the next empty row in the Expenses section (columns B-E)
            # Get all values in column B (Date column for Expenses)
            expenses_col_range = worksheet.col_values(2)  # Column B (Date column for Expenses)
            
            # Find the first empty row after the headers (starting from row 4)
            next_row = 4  # Start from row 4 (after headers in row 3)
            
            # Look for the first empty cell in column B starting from row 4
            for i, cell_value in enumerate(expenses_col_range[3:], start=4):  # Skip first 3 rows (headers)
                if not cell_value or cell_value.strip() == '':
                    next_row = i
                    break
            else:
                # If no empty cell found, append to the end
                next_row = len(expenses_col_range) + 1
            
            print(f"Debug: Writing to row {next_row} in Expenses section")
            
            # Write data to specific cells in the Expenses section (columns B, C, D, E)
            worksheet.update(f'B{next_row}', expense_data['date'])
            worksheet.update(f'C{next_row}', expense_data['amount'])
            worksheet.update(f'D{next_row}', expense_data['vendor'])
            worksheet.update(f'E{next_row}', expense_data['category'])
            
            print(f"✓ Added new expense: {expense_data['vendor']} - ₡{expense_data['amount']:.2f} to Expenses section at row {next_row}.")
            return True
            
        except Exception as e:
            error_str = str(e)
            if 'RATE_LIMIT_EXCEEDED' in error_str or '429' in error_str:
                if attempt < max_retries - 1:
                    print(f"Rate limit exceeded. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"Rate limit exceeded after {max_retries} attempts. Skipping this expense.")
                    return False
            else:
                print(f"Error adding expense to sheet: {e}")
                return False
    
    return False

def mark_email_as_read(service, msg_id):
    """Marks an email as read."""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"Marked email {msg_id} as read.")
    except HttpError as error:
        print(f"Error marking email as read: {error}")

def main():
    creds = authenticate_google_api()
    if not creds:
        print("Failed to authenticate with Google APIs. Exiting.")
        return

    gmail_service = get_gmail_service(creds)
    sheets_client = get_sheets_client(creds)

    if not gmail_service or not sheets_client:
        print("Failed to get API services. Exiting.")
        return

    print("Fetching emails...")
    messages = fetch_expense_emails(gmail_service) # Using the updated query string

    if not messages:
        print("No new expense emails found.")
        return

    print(f"Found {len(messages)} emails to process.")
    processed_count = 0
    skipped_count = 0
    
    for i, msg in enumerate(messages):
        email_id = msg['id']
        print(f"\nProcessing email {i+1}/{len(messages)} - ID: {email_id}")
        
        # Add delay between processing emails to avoid rate limits
        if i > 0:  # Don't delay before first email
            print("Waiting 0.5 seconds to avoid rate limits...")
            time.sleep(0.5)
        
        email_body, fetched_email_id = get_email_content(gmail_service, email_id)

        if email_body:
            expense_data = parse_expense_from_email(email_body)
            print(f"Parsed expense: {expense_data['vendor']} - ₡{expense_data['amount']:.2f} on {expense_data['date']}")

            if expense_data['amount'] > 0:
                if add_expense_to_sheet(sheets_client, expense_data):
                    mark_email_as_read(gmail_service, email_id)
                    processed_count += 1
                    print(f"✓ Successfully processed expense from {expense_data['vendor']}")
                else:
                    print(f"✗ Failed to add expense to sheet for email {email_id}")
                    skipped_count += 1
            else:
                print(f"✗ Could not extract valid expense amount from email {email_id}. Skipping.")
                skipped_count += 1
        else:
            print(f"✗ Could not retrieve content for email {email_id}. Skipping.")
            skipped_count += 1

    print(f"\n=== PROCESSING COMPLETE ===")
    print(f"Successfully processed: {processed_count} expenses")
    print(f"Skipped: {skipped_count} emails")
    print(f"Total emails processed: {len(messages)}")

if __name__ == '__main__':
    main()