# Configuration file for Expense Tracker
import os

# Get the directory where this config file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Sheets Configuration
# Leave SPREADSHEET_ID empty ("") and the app will create a new sheet automatically
# on first run and save the generated ID here.
SPREADSHEET_ID = "1P462_QI7sUrCyVfu1laMWYa_Xca3YJk3H_ALpX11uNU"
SPREADSHEET_NAME = "Transactions"

# Email Filtering Configuration
# Set to None to process all unread emails, or specify a month/year to filter
# Examples: "2025/07", "2025/08", "July 2025", "Aug 2025", None
FILTER_BY_MONTH = '2026/07'

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")  # Path to your Gmail API credentials file
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")  # Path where the access token will be stored

# Note: 
# - Make sure you have credentials.json in the same directory as this config file
# - The token.pickle file will be automatically created when you first authenticate
# - Set FILTER_BY_MONTH to None to process all unread emails, or specify a month like "2025/08"
