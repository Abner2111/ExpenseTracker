"""
Gmail integration for ExpenseTracker
Handles email fetching and authentication with Gmail API
"""

import os
import pickle
import base64
from datetime import datetime
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

from config_manager import ConfigManager
from models import EmailData, ProcessingResult
from logger import get_logger

import os
import pickle
import base64
from typing import List, Optional
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

from config_manager import config_manager
from logger import get_logger
from models import EmailData, ProcessingError

logger = get_logger()

class EmailParser:
    """Handles Gmail integration and email parsing"""
    
    def __init__(self):
        self.config = config_manager.config
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Gmail API"""
        try:
            creds = None
            token_path = config_manager.get_token_path()
            
            # Load existing token if available
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired Google credentials")
                    creds.refresh(Request())
                else:
                    logger.info("Creating new Google credentials")
                    credentials_path = config_manager.get_credentials_path()
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, config_manager.get_google_scopes()
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Successfully authenticated with Gmail API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Gmail API: {e}")
            raise ProcessingError(f"Gmail authentication failed: {e}")
    
    def get_bac_emails(self, max_results: int = None) -> List[EmailData]:
        """
        Retrieve BAC Credomatic notification emails
        
        Args:
            max_results: Maximum number of emails to retrieve
            
        Returns:
            List of EmailData objects
        """
        try:
            logger.info("Fetching BAC Credomatic emails")
            
            # Build search query - match original BAC Credomatic patterns
            query = 'is:unread subject:"Notificación de transacción" from:notificacion@notificacionesbaccr.com'
            
            # Add month filter if specified
            if self.config.filter_by_month:
                # Convert FILTER_BY_MONTH format (2025/08) to Gmail date filter
                if "/" in self.config.filter_by_month:
                    year, month = self.config.filter_by_month.split("/")
                    start_date = f"after:{year}/{int(month)}/1"
                    
                    # Calculate next month for end date
                    next_month = int(month) + 1
                    next_year = year
                    if next_month > 12:
                        next_month = 1
                        next_year = str(int(year) + 1)
                    
                    end_date = f"before:{next_year}/{next_month}/1"
                    query += f' {start_date} {end_date}'
                    logger.info(f"Filtering emails for month: {self.config.filter_by_month}")
                else:
                    logger.warning(f"Invalid filter_by_month format: {self.config.filter_by_month}")
            
            logger.debug(f"Email search query: {query}")
            
            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results or self.config.batch_size
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread BAC emails")
            
            if not messages:
                return []
            
            # Fetch email details
            emails = []
            for message in messages:
                try:
                    email_data = self._fetch_email_details(message['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Failed to fetch email {message['id']}: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(emails)} emails")
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise ProcessingError(f"Failed to retrieve emails: {e}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving emails: {e}")
            raise ProcessingError(f"Email retrieval failed: {e}")
    
    def _fetch_email_details(self, email_id: str) -> Optional[EmailData]:
        """
        Fetch detailed information for a specific email
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            EmailData object or None if failed
        """
        try:
            # Get email message
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            sender = self._get_header_value(headers, 'From')
            subject = self._get_header_value(headers, 'Subject')
            date_str = self._get_header_value(headers, 'Date')
            
            # Parse date
            date_received = self._parse_email_date(date_str)
            
            # Extract body
            body = self._extract_email_body(message['payload'])
            
            # Create EmailData object
            email_data = EmailData(
                email_id=email_id,
                sender=sender,
                subject=subject,
                body=body,
                date_received=date_received
            )
            
            email_data.validate()
            return email_data
            
        except Exception as e:
            logger.error(f"Failed to fetch email details for {email_id}: {e}")
            return None
    
    def _get_header_value(self, headers: List[dict], name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        try:
            # Gmail date format: "Wed, 6 Aug 2025 09:00:00 +0000"
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            logger.warning(f"Failed to parse email date: {date_str}")
            return datetime.now()
    
    def _extract_email_body(self, payload: dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        try:
            # Handle multipart messages
            if 'parts' in payload:
                for part in payload['parts']:
                    body += self._extract_email_body(part)
            else:
                # Handle single part messages
                if payload.get('body', {}).get('data'):
                    data = payload['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    
                    # Parse HTML if needed
                    if payload.get('mimeType') == 'text/html':
                        soup = BeautifulSoup(body, 'html.parser')
                        body = soup.get_text()
        
        except Exception as e:
            logger.warning(f"Failed to extract email body: {e}")
        
        return body
    
    def mark_email_as_read(self, email_id: str):
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.debug(f"Marked email {email_id} as read")
        except Exception as e:
            logger.error(f"Failed to mark email {email_id} as read: {e}")
    
    def get_service(self):
        """Get the Gmail service object"""
        return self.service
    
    def verify_gmail_access(self) -> ProcessingResult:
        """
        Verify Gmail API access by attempting to fetch user profile
        
        Returns:
            ProcessingResult with verification status
        """
        logger.info("Verifying Gmail API access")
        
        try:
            # Try to get user profile to verify access
            profile = self.service.users().getProfile(userId='me').execute()
            email_address = profile.get('emailAddress', 'Unknown')
            
            logger.info(f"Gmail access verified for: {email_address}")
            
            return ProcessingResult(
                success=True,
                message=f"Gmail access verified for: {email_address}",
                details={
                    'email_address': email_address,
                    'messages_total': profile.get('messagesTotal', 0),
                    'threads_total': profile.get('threadsTotal', 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Gmail verification failed: {e}")
            return ProcessingResult(
                success=False,
                message="Gmail access verification failed",
                error=str(e)
            )
    
    def fetch_bac_emails(self, max_results: int = None) -> List[EmailData]:
        """
        Fetch BAC Credomatic emails - wrapper for get_bac_emails for consistency
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of EmailData objects
        """
        return self.get_bac_emails(max_results)
    
    def mark_email_as_processed(self, email_id: str):
        """
        Mark email as processed - wrapper for mark_email_as_read for consistency
        
        Args:
            email_id: ID of the email to mark as processed
        """
        return self.mark_email_as_read(email_id)
