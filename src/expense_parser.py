"""
Expense parsing functionality for ExpenseTracker
Extracts expense data from email content using database rules
"""

import re
from datetime import datetime
from typing import Optional, Tuple

from database import ExpenseDatabase
from currency_converter import CurrencyConverter
from date_parser import DateParser
from models import Expense
from logger import get_logger

logger = get_logger()

class ExpenseParser:
    """Parses expense data from BAC Credomatic email content"""
    
    def __init__(self):
        self.db = ExpenseDatabase()
        self.currency_converter = CurrencyConverter()
        self.date_parser = DateParser()
        
        # Amount patterns with currency detection
        self.amount_patterns = [
            # Pattern 1: "CRC 1,650.97"
            r'CRC\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Pattern 2: "Monto: USD 9.99"
            r'(?:Monto|Total):\s*USD\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Pattern 3: "USD 25.50"
            r'USD\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Pattern 4: "$19.99"
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Pattern 5: "€45.99"
            r'€(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Pattern 6: "₡15,500.50"
            r'₡(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Pattern 7: "25.50 USD"
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+USD',
            # Pattern 8: "Monto: 5000.00"
            r'(?:Monto|Total):\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        # Currency hints for each pattern
        self.currency_hints = [
            'CRC', 'USD', 'USD', 'USD', 'EUR', 'CRC', 'USD', 'CRC'
        ]
    
    def parse_expense_from_email(self, email_text: str, email_id: str = None) -> Expense:
        """
        Parse expense data from email text
        
        Args:
            email_text: Email content to parse
            email_id: Email ID for tracking
            
        Returns:
            Expense object with parsed data
        """
        logger.info(f"Parsing expense from email {email_id}")
        
        try:
            # Parse amount and currency
            amount, currency, original_amount, original_currency, exchange_rate = self._parse_amount_and_currency(email_text)
            
            # Parse date
            date_str = self.date_parser.parse_date_from_email(email_text)
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse vendor
            vendor = self._parse_vendor(email_text)
            
            # Determine category
            category = self.db.categorize_vendor(vendor if vendor != 'Unknown' else email_text)
            
            # Generate notes
            notes = self._generate_notes(email_text, original_amount, original_currency, exchange_rate)
            
            # Create expense object
            expense = Expense(
                vendor=vendor,
                amount=amount,
                currency=currency,
                date=expense_date,
                category=category,
                notes=notes,
                email_id=email_id,
                original_amount=original_amount,
                original_currency=original_currency,
                exchange_rate=exchange_rate
            )
            
            logger.info(f"Successfully parsed expense: {vendor} - {expense.get_display_amount()} - {category}")
            return expense
            
        except Exception as e:
            logger.error(f"Failed to parse expense from email {email_id}: {e}")
            raise
    
    def _parse_amount_and_currency(self, email_text: str) -> Tuple[float, str, Optional[float], Optional[str], Optional[float]]:
        """
        Parse amount and currency from email text
        
        Returns:
            Tuple of (final_amount, final_currency, original_amount, original_currency, exchange_rate)
        """
        logger.debug("Searching for amounts with currency detection...")
        
        amount = None
        detected_currency = None
        original_amount = None
        original_currency = None
        exchange_rate = None
        
        # Try each amount pattern
        for i, pattern in enumerate(self.amount_patterns):
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                currency_hint = self.currency_hints[i]
                logger.debug(f"Pattern {i+1} found amount match: '{matches[0]}' with currency hint: '{currency_hint}'")
                
                # Parse the amount
                amount_str = matches[0].replace(',', '')
                try:
                    amount = float(amount_str)
                    detected_currency = currency_hint
                    logger.debug(f"Parsed amount: {amount} {detected_currency}")
                    break
                except ValueError as e:
                    logger.debug(f"Failed to parse amount '{amount_str}': {e}")
                    continue
        
        if amount is None:
            raise ValueError("No valid amount found in email")
        
        # Store original values before conversion
        original_amount = amount
        original_currency = detected_currency
        
        # Convert to CRC if needed
        if detected_currency != 'CRC':
            logger.debug(f"Converting {amount} {detected_currency} to CRC")
            converted_amount, rate = self.currency_converter.convert_to_crc(amount, detected_currency)
            
            # Update values
            amount = converted_amount
            detected_currency = 'CRC'
            exchange_rate = rate
        
        logger.debug(f"Final amount: {amount} {detected_currency}")
        return amount, detected_currency, original_amount, original_currency, exchange_rate
    
    def _parse_vendor(self, email_text: str) -> str:
        """
        Parse vendor from email text
        
        Args:
            email_text: Email content
            
        Returns:
            Vendor name or 'Unknown'
        """
        # Try to extract vendor from "Comercio:" field (BAC format)
        comercio_match = re.search(r'Comercio:\s*([^\n]+?)(?=\n|$)', email_text, re.IGNORECASE)
        if comercio_match:
            comercio_name = comercio_match.group(1).strip()
            
            # Remove any currency amounts from the vendor name
            comercio_name = re.sub(
                r'\s*[\$₡€]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|CRC)?\s*$', 
                '', comercio_name, flags=re.IGNORECASE
            )
            comercio_name = re.sub(
                r'\s*(?:USD|EUR|CRC)\s+\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*$', 
                '', comercio_name, flags=re.IGNORECASE
            )
            
            vendor_name = comercio_name.strip()
            logger.debug(f"Found vendor in Comercio field: '{vendor_name}'")
            return vendor_name
        else:
            # Fallback: search for vendor keyword in email text using database
            logger.debug("No Comercio field found, searching vendor keywords in database...")
            vendor_name = self.db.find_vendor_by_text(email_text)
            if vendor_name:
                logger.debug(f"Found vendor via database keyword: '{vendor_name}'")
                return vendor_name
            else:
                logger.debug("No vendor keywords matched in database")
                return 'Unknown'
    
    def _generate_notes(self, email_text: str, original_amount: Optional[float], 
                       original_currency: Optional[str], exchange_rate: Optional[float]) -> str:
        """
        Generate notes for the expense
        
        Args:
            email_text: Email content
            original_amount: Original amount before conversion
            original_currency: Original currency before conversion
            exchange_rate: Exchange rate used for conversion
            
        Returns:
            Notes string
        """
        notes_parts = []
        
        # Extract subject if available
        subject_match = re.search(r'Subject:\s*([^\n]+)', email_text, re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1).strip()
            notes_parts.append(f"Email Subject: {subject}")
        
        # Add standard note
        notes_parts.append("Parsed from email receipt (CR)")
        
        # Add conversion information if applicable
        if original_amount and original_currency and exchange_rate and original_currency != 'CRC':
            conversion_note = f"Original: {original_amount} {original_currency} (Rate: {exchange_rate})"
            notes_parts.append(conversion_note)
        
        return " | ".join(notes_parts)
