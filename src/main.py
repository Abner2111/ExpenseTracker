import os.path
import base64
import re
import time
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import gspread
from bs4 import BeautifulSoup

# Import configurations
from config import SPREADSHEET_ID, SPREADSHEET_NAME, GMAIL_CREDENTIALS_PATH, TOKEN_PATH, FILTER_BY_MONTH

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/spreadsheets']

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
        'category': 'General',
        'notes': ''
    }

    email_text_lower = email_text.lower()

    # --- Amount Parsing (Added CRC - Costa Rican Colón) ---
    amount_patterns = [
        r'CRC\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', # BAC format: CRC 5,650.00 - prioritize this
        r'(?:Monto|Total|Monto Total|Total a Pagar|Subtotal|Gran Total):\s*(?:CRC|₡)?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', # CRC format: 1.234,56
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*(?:USD|CRC|₡|colones|dolares)\b', # e.g., 25.50 USD or 5000 CRC
        r'[\$£€₡]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\b' # general currency symbol
    ]
    
    print(f"Debug: Searching for amounts in email text (first 500 chars): {repr(email_text[:500])}")  # Debug line
    
    for i, pattern in enumerate(amount_patterns):
        match = re.search(pattern, email_text, re.IGNORECASE)
        if match:
            amount_str = match.group(1)
            print(f"Debug: Pattern {i+1} found amount match: '{amount_str}' using pattern: {pattern}")
            
            # Handle BAC format specifically: 5,650.00 should become 5650.00
            if ',' in amount_str and '.' in amount_str:
                # This is US/BAC format: 5,650.00
                # Remove commas (thousands separators)
                processed_amount = amount_str.replace(',', '')
                print(f"Debug: BAC/US format - '{amount_str}' -> '{processed_amount}'")
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
                expense_data['amount'] = float(amount_str)
                print(f"Debug: Final parsed amount: {expense_data['amount']}")
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
    date_patterns = [
        r'(?:Fecha|Date|Fecha de Compra|Fecha de Transacción):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', # DD/MM/YYYY or DD-MM-YYYY
        r'(\w{3}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2})', # BAC format: Jul 31, 2025, 14:29
        r'(\d{4}-\d{2}-\d{2})', # YYYY-MM-DD
        r'(\d{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s+\d{4})', # DD Mon YYYY
        r'(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},\s+\d{4}', # Month DD, YYYY (Spanish)
        r'(\w{3}\s+\d{1,2},\s+\d{4})' # English Mon DD, YYYY
    ]
    for pattern in date_patterns:
        match = re.search(pattern, email_text, re.IGNORECASE)  # Use original text for date parsing
        if match:
            date_str = match.group(1).replace('.', '')
            # Handle BAC datetime format by removing time portion
            if ',' in date_str and ':' in date_str:
                date_str = date_str.split(',')[0] + ',' + date_str.split(',')[1].split(',')[0]  # Remove time
            
            for fmt in ['%b %d, %Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %b %Y', '%B %d, %Y', '%d %B %Y']:
                try:
                    # Handle month names in Spanish if they appear without abbreviations
                    if 'enero' in date_str: date_str = date_str.replace('enero', 'Jan')
                    elif 'febrero' in date_str: date_str = date_str.replace('febrero', 'Feb')
                    elif 'marzo' in date_str: date_str = date_str.replace('marzo', 'Mar')
                    elif 'abril' in date_str: date_str = date_str.replace('abril', 'Apr')
                    elif 'mayo' in date_str: date_str = date_str.replace('mayo', 'May')
                    elif 'junio' in date_str: date_str = date_str.replace('junio', 'Jun')
                    elif 'julio' in date_str: date_str = date_str.replace('julio', 'Jul')
                    elif 'agosto' in date_str: date_str = date_str.replace('agosto', 'Aug')
                    elif 'septiembre' in date_str: date_str = date_str.replace('septiembre', 'Sep')
                    elif 'octubre' in date_str: date_str = date_str.replace('octubre', 'Oct')
                    elif 'noviembre' in date_str: date_str = date_str.replace('noviembre', 'Nov')
                    elif 'diciembre' in date_str: date_str = date_str.replace('diciembre', 'Dec')

                    expense_data['date'] = datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    pass
            break

    # --- Vendor Identification (Costa Rica Specific & Common) ---
    # All vendor keywords in lowercase for case-insensitive matching
    vendor_keywords = {
        # Fast Food Chains
        'kfc': 'KFC', 'kfc express': 'KFC Express', 'mcdonalds': 'McDonalds CR',
        'burger king': 'Burger King CR', 'pizza hut': 'Pizza Hut CR', 'dominos pizza': 'Dominos Pizza CR',
        'subway': 'Subway CR', 'taco bell': 'Taco Bell CR',
        
        # Supermarkets
        'automercado': 'Automercado', 'mas x menos': 'Mas x Menos', 'maxi pali': 'Maxi Pali',
        'pali': 'Pali', 'pricesmart': 'PriceSmart', 'mega super': 'Mega Super',
        'super compro': 'Super Compro', 'perimercados': 'Perimercados',
        'walmart': 'Walmart Costa Rica', 'pequeño mundo': 'Pequeño Mundo',
        'vindi': 'Vindi (Convenience)', 'am pm': 'AM PM (Convenience)', 'fresh market': 'Fresh Market (Convenience)',

        # Ride-sharing / Transportation
        'uber': 'Uber', 'didi': 'DiDi (Transportation)', 'indriver': 'inDrive (Transportation)',
        'ticoride': 'TicoRide', 'interbus': 'Interbus (Shuttle)', 'ride cr': 'RIDE CR (Transportation)',
        'transportes': 'Transportation (General)', 'shuttle': 'Shuttle Service',
        'dlc* uber rides': 'Uber Rides',

        # Food Delivery & Dining
        'uber eats': 'Uber Eats', 'dlc* uber eats': 'Uber Eats',
        'fiesta express': 'Fiesta Express Delivery',
        'rappi': 'Rappi (Delivery)', 'glovo': 'Glovo (Delivery)',
        'comidas el shaddai': 'Comidas El Shaddai',
        'coral ibm': 'Coral IBM',

        # Snacks / Convenience
        'pronto snack': 'Pronto Snack',
        'delimart afz': 'Delimart AFZ',

        # Cafes/Restaurants (examples)
        'cafe britt': 'Café Britt', 'café britt': 'Café Britt', 'cafe del barista': 'Café del Barista', 'cafeoteca': 'Cafeoteca',
        'soda': 'Soda (Local Restaurant)', 'pollo rostizado': 'Pollo Rostizado (Food)',

        # Banks
        'banco nacional': 'Banco Nacional', 'banco de costa rica': 'Banco de Costa Rica (BCR)',
        'banco popular': 'Banco Popular', 'bac credomatic': 'BAC Credomatic',
        'scotiabank': 'Scotiabank CR', 'banco lafise': 'Banco Lafise', 'banco bct': 'Banco BCT',
        'banco improsa': 'Banco Improsa',

        # Utilities / Services
        'ice electricidad': 'ICE (Electricity/Telecom)', 'aya agua': 'AyA (Water)', 'kolbi': 'Kolbi (Telecom)',
        'claro': 'Claro (Telecom)', 'movistar': 'Movistar (Telecom)', 'cnfl': 'CNFL (Electricity)',
        'jasec': 'Jasec (Electricity/Water)', 'coopeguanacaste': 'CoopeGuanacaste (Electricity)',

        # Retail / Other common stores
        'el gallo mas gallo': 'El Gallo Mas Gallo (Electronics/Home)',
        'tienda el rey': 'Tienda El Rey (Variety Store)',
        'ferreteria': 'Hardware Store', 'farmacia': 'Pharmacy', 'gasolinera': 'Gas Station',
        'gas station': 'Gas Station', 'mascotas': 'Pet Store', 'cemaco': 'Cemaco (Home Goods)',
        'universal': 'Universal (Department Store/Books)', 'libreria': 'Bookstore',
        'correos de costa rica': 'Correos de Costa Rica (Post Office)',
        'siman': 'Siman (Department Store)', 'multiplaza': 'Multiplaza (Mall)', 'city mall': 'City Mall (Mall)',

        # General
        'hotel': 'Hotel', 'restaurante': 'Restaurant', 'tour': 'Tour/Activity',
        'parque nacional': 'National Park', 'entrada': 'Entrance Fee',
        'peaje': 'Toll', 'tax': 'Tax', 'impuesto': 'Tax',
        'servicio': 'Service Fee', 'alquiler': 'Rental', 'rent a car': 'Car Rental',
        'lavanderia': 'Laundry', 'clinica': 'Clinic/Medical'
    }

    # Check for vendor in "Comercio:" field (BAC format)
    # Handle multi-line vendor names by looking for the next field after Comercio
    comercio_match = re.search(r'Comercio:\s*(.+?)(?=\n\s*(?:Ciudad y país|Fecha|VISA|Autorización))', email_text, re.IGNORECASE | re.DOTALL)
    if comercio_match:
        comercio_name = comercio_match.group(1).strip()
        # Clean up any extra whitespace and newlines, join multiple lines with space
        comercio_name = ' '.join(comercio_name.split())
        expense_data['vendor'] = comercio_name
        print(f"Debug: Found vendor in Comercio field: '{comercio_name}'")
    else:
        # Only check general vendor keywords if we didn't find a vendor in Comercio field
        print("Debug: No Comercio field found, checking vendor keywords...")
        for keyword, vendor_name in vendor_keywords.items():
            if keyword in email_text_lower:
                expense_data['vendor'] = vendor_name
                print(f"Debug: Found vendor via keyword '{keyword}': '{vendor_name}'")
                break
        
        if expense_data['vendor'] == 'Unknown':
            print("Debug: No vendor keywords matched, vendor remains 'Unknown'")

    # --- Category Inference (Costa Rica Specific & General) ---
    # This can be refined further with more specific keywords or logic
    vendor_lower = expense_data['vendor'].lower()
    print(f"Debug: Categorizing vendor '{expense_data['vendor']}' (lowercase: '{vendor_lower}')")
    
    # Convert all comparison lists to lowercase for case-insensitive matching
    fast_food_vendors = ['kfc', 'kfc express', 'mcdonalds cr', 'burger king cr', 'pizza hut cr', 'dominos pizza cr', 'subway cr', 'taco bell cr']
    grocery_vendors = ['automercado', 'mas x menos', 'maxi pali', 'pali', 'pricesmart', 'mega super', 'super compro', 'perimercados', 'walmart costa rica', 'pequeño mundo', 'vindi (convenience)', 'am pm (convenience)', 'fresh market (convenience)']
    transport_vendors = ['uber', 'didi (transportation)', 'indrive (transportation)', 'ticoride', 'interbus (shuttle)', 'ride cr (transportation)', 'uber rides', 'dlc* uber rides']
    dining_vendors = ['uber eats', 'dlc* uber eats', 'fiesta express delivery', 'rappi (delivery)', 'glovo (delivery)', 'soda (local restaurant)', 'pollo rostizado (food)', 'comidas el shaddai', 'coral ibm']
    snack_vendors = ['pronto snack', 'delimart afz']
    coffee_vendors = ['café britt', 'café del barista', 'cafeoteca', 'cafe britt', 'cafe del barista']
    bank_vendors = ['bac credomatic', 'banco nacional', 'banco de costa rica (bcr)', 'banco popular', 'scotiabank cr', 'banco lafise', 'banco bct', 'banco improsa']
    utility_vendors = ['ice (electricity/telecom)', 'aya (water)', 'kolbi (telecom)', 'claro (telecom)', 'movistar (telecom)', 'cnfl (electricity)', 'jasec (electricity/water)', 'coopeguanacaste (electricity)']
    retail_vendors = ['el gallo mas gallo (electronics/home)', 'tienda el rey (variety store)', 'cemaco (home goods)', 'universal (department store/books)', 'siman (department store)']
    
    # Dining Out (restaurants, food delivery, fast food) - case-insensitive exact matches
    if (vendor_lower in fast_food_vendors 
        or vendor_lower in dining_vendors 
        or vendor_lower in snack_vendors
        or 'subway' in vendor_lower
        or 'dlc* uber eats' in vendor_lower 
        or 'uber eats' in vendor_lower 
        or 'comidas el shaddai' in vendor_lower 
        or 'coral ibm' in vendor_lower
        or 'pronto snack' in vendor_lower
        or 'restaurante' in vendor_lower
        or 'soda' in vendor_lower):
        expense_data['category'] = 'Dining Out'
        print(f"Debug: Assigned category 'Dining Out' (restaurant/delivery vendor match)")
    
    # Groceries (groceries and supermarkets) - use partial matching for supermarkets (case-insensitive)
    elif (vendor_lower in grocery_vendors
          or 'auto mercado' in vendor_lower 
          or 'automercado' in vendor_lower 
          or 'mas x menos' in vendor_lower 
          or 'maxi pali' in vendor_lower 
          or ('pali' in vendor_lower and not any(x in vendor_lower for x in ['tpali', 'epali']))  # avoid false positives
          or 'pricesmart' in vendor_lower 
          or 'walmart' in vendor_lower 
          or 'pequeño mundo' in vendor_lower 
          or 'mega super' in vendor_lower
          or 'super compro' in vendor_lower
          or 'perimercados' in vendor_lower):
        expense_data['category'] = 'Groceries'
        print(f"Debug: Assigned category 'Groceries' (grocery store match)")
    
    # Transportation - case-insensitive exact matches
    elif (vendor_lower in transport_vendors 
          or 'dlc* uber rides' in vendor_lower 
          or 'uber rides' in vendor_lower):
        expense_data['category'] = 'Transportation'
        print(f"Debug: Assigned category 'Transportation' (lowercase exact match)")
    
    # Health/medical - case-insensitive exact matches
    elif ('farmacia' in vendor_lower or 'medicamentos' in vendor_lower or 'clinica' in vendor_lower
          or 'hospital' in vendor_lower or 'medico' in vendor_lower or 'doctor' in vendor_lower):
        expense_data['category'] = 'Health/medical'
        print(f"Debug: Assigned category 'Health/medical' (health vendor match)")
    
    # Home - case-insensitive exact matches  
    elif (vendor_lower in retail_vendors
          or 'ferreteria' in vendor_lower 
          or 'cemaco' in vendor_lower
          or 'el gallo mas gallo' in vendor_lower):
        expense_data['category'] = 'Home'
        print(f"Debug: Assigned category 'Home' (home/retail vendor match)")
    
    # Utilities - case-insensitive exact matches
    elif (vendor_lower in utility_vendors
          or 'ice electricidad' in vendor_lower or 'ice' in vendor_lower
          or 'kolbi' in vendor_lower or 'claro' in vendor_lower or 'movistar' in vendor_lower
          or 'aya agua' in vendor_lower or 'cnfl' in vendor_lower):
        expense_data['category'] = 'Utilities'
        print(f"Debug: Assigned category 'Utilities' (utility vendor match)")
    
    # Debt - banking related
    elif vendor_lower in bank_vendors:
        expense_data['category'] = 'Debt'
        print(f"Debug: Assigned category 'Debt' (bank vendor match)")
    
    # Travel - case-insensitive exact matches
    elif ('hotel' in vendor_lower or 'alojamiento' in vendor_lower
          or 'tour' in vendor_lower or 'actividad' in vendor_lower or 'aventura' in vendor_lower
          or 'rent a car' in vendor_lower or 'alquiler de vehiculos' in vendor_lower):
        expense_data['category'] = 'Travel'
        print(f"Debug: Assigned category 'Travel' (travel vendor match)")
    
    # Car maintenance - fuel and car related
    elif ('gasolinera' in vendor_lower or 'gas station' in vendor_lower
          or 'combustible' in vendor_lower or 'taller' in vendor_lower 
          or 'mecanico' in vendor_lower or 'neumaticos' in vendor_lower):
        expense_data['category'] = 'Car maintenance'
        print(f"Debug: Assigned category 'Car maintenance' (car maintenance match)")
    
    # Personal - coffee, personal care
    elif (vendor_lower in coffee_vendors
          or 'cafe' in vendor_lower or 'café' in vendor_lower
          or 'peluqueria' in vendor_lower or 'salon' in vendor_lower
          or 'barberia' in vendor_lower):
        expense_data['category'] = 'Personal'
        print(f"Debug: Assigned category 'Personal' (personal care/coffee match)")
    
    # Parking - check for parquimetro pattern
    elif ('parquimetro' in vendor_lower or 'parquímetro' in vendor_lower
          or 'parqueo' in vendor_lower or 'parking' in vendor_lower):
        expense_data['category'] = 'Transportation'  # Parking goes under Transportation
        print(f"Debug: Assigned category 'Transportation' (parking match)")
    
    # Pets - pet related
    elif ('mascotas' in vendor_lower or 'veterinaria' in vendor_lower 
          or 'pet' in vendor_lower or 'animal' in vendor_lower):
        expense_data['category'] = 'Pets'
        print(f"Debug: Assigned category 'Pets' (pet vendor match)")
    
    # Streaming - entertainment services
    elif ('netflix' in vendor_lower or 'spotify' in vendor_lower 
          or 'amazon prime' in vendor_lower or 'disney' in vendor_lower
          or 'streaming' in vendor_lower):
        expense_data['category'] = 'Streaming'
        print(f"Debug: Assigned category 'Streaming' (streaming service match)")
    
    # Education - educational expenses
    elif ('universidad' in vendor_lower or 'colegio' in vendor_lower 
          or 'escuela' in vendor_lower or 'curso' in vendor_lower
          or 'libro' in vendor_lower or 'libreria' in vendor_lower):
        expense_data['category'] = 'Education'
        print(f"Debug: Assigned category 'Education' (education vendor match)")
    
    # Gifts - gift related
    elif ('regalo' in vendor_lower or 'gift' in vendor_lower 
          or 'flores' in vendor_lower or 'floreria' in vendor_lower or 'joyeria' in vendor_lower):
        expense_data['category'] = 'Gifts'
        print(f"Debug: Assigned category 'Gifts' (gift vendor match)")
    
    # Default to General if no specific category matches
    else:
        expense_data['category'] = 'General'
        print(f"Debug: Assigned default category 'General' (no specific match)")

    print(f"Debug: Final category assigned: '{expense_data['category']}'")

    # Basic Notes
    # You might want to extract a specific line from the email for notes or the email subject
    subject_match = re.search(r'Subject: (.+)', email_text, re.IGNORECASE)
    if subject_match:
        expense_data['notes'] = f"Email Subject: {subject_match.group(1).strip()}"
    else:
        expense_data['notes'] = "Parsed from email receipt (CR)."


    return expense_data

def add_expense_to_sheet(gspread_client, expense_data):
    """Appends expense data to the Expenses section of the Google Sheet with rate limiting."""
    max_retries = 3
    retry_delay = 60  # Start with 60 seconds delay
    
    for attempt in range(max_retries):
        try:
            spreadsheet = gspread_client.open_by_key(SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet(SPREADSHEET_NAME)

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
            
            print(f"Added expense: {expense_data['vendor']} - ₡{expense_data['amount']:.2f} to Expenses section at row {next_row}.")
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
    
    for i, msg in enumerate(messages):
        email_id = msg['id']
        print(f"Processing email {i+1}/{len(messages)} - ID: {email_id}")
        
        # Add delay between processing emails to avoid rate limits
        if i > 0:  # Don't delay before first email
            print("Waiting 0.5 seconds to avoid rate limits...")
            time.sleep(0.5)
        
        email_body, fetched_email_id = get_email_content(gmail_service, email_id)

        if email_body:
            expense_data = parse_expense_from_email(email_body)

            if expense_data['amount'] > 0:
                if add_expense_to_sheet(sheets_client, expense_data):
                    mark_email_as_read(gmail_service, email_id)
                    processed_count += 1
                else:
                    print(f"Skipping email {email_id} due to Google Sheets error.")
            else:
                print(f"Could not extract valid expense amount from email {email_id}. Skipping.")
        else:
            print(f"Could not retrieve content for email {email_id}. Skipping.")

    print(f"\nFinished processing. Added {processed_count} expenses to Google Sheet.")

if __name__ == '__main__':
    main()