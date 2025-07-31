# Configuration file for Expense Tracker
import os

# Get the directory where this config file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Sheets Configuration
SPREADSHEET_ID = "1VK_hpmojtS0XfTJK46X7rz02Juyla7olwJRIjFXwLN0"  # august 25 Monthly budget sheet
SPREADSHEET_NAME = "Transactions"  # Sheet name for expense data

# Email Filtering Configuration
# Set to None to process all unread emails, or specify a month/year to filter
# Examples: "2025/07", "2025/08", "July 2025", "Aug 2025", None
FILTER_BY_MONTH = "2025/08"  # Set to None to process all months, or specify month like "2025/08"

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")  # Path to your Gmail API credentials file
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")  # Path where the access token will be stored

# Note: 
# 1. Replace SPREADSHEET_ID with your actual Google Sheets ID from the URL
# 2. Download credentials.json from Google Cloud Console and place it in the src folder
# 3. Make sure the spreadsheet has columns: Date, Amount, Description, Category
# 4. Set FILTER_BY_MONTH to process specific months:
#    - "2025/08" for August 2025
#    - "2025/07" for July 2025
#    - None to process all unread emails
