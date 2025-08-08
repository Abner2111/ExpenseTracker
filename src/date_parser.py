"""
Date parsing functionality for ExpenseTracker
Handles Spanish date formats and various date patterns
"""

import re
from datetime import datetime
from typing import Optional

from logger import get_logger

logger = get_logger()

class DateParser:
    """Handles parsing of dates from email text with Spanish support"""
    
    def __init__(self):
        # Spanish month abbreviations to English
        self.spanish_months_abbr = {
            'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
            'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
            'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
        }
        
        # Date patterns to try (in order of preference)
        self.date_patterns = [
            # BAC format: "Ago 6, 2025"
            r'(?:Fecha:|fecha:)\s*([A-Za-z]{3}\s+\d{1,2},\s+\d{4})',
            # ISO format: "2025-08-06"
            r'(\d{4}-\d{2}-\d{2})',
            # DD/MM/YYYY format
            r'(\d{1,2}/\d{1,2}/\d{4})',
            # DD-MM-YYYY format
            r'(\d{1,2}-\d{1,2}-\d{4})',
            # Month DD, YYYY format
            r'([A-Za-z]{3,}\s+\d{1,2},\s+\d{4})',
            # DD Month YYYY format
            r'(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})'
        ]
        
        # Date format strings corresponding to patterns
        self.date_formats = [
            '%b %d, %Y',  # BAC format after Spanish conversion
            '%Y-%m-%d',   # ISO format
            '%d/%m/%Y',   # DD/MM/YYYY
            '%d-%m-%Y',   # DD-MM-YYYY
            '%B %d, %Y',  # Full month name
            '%d %B %Y'    # DD Month YYYY
        ]
    
    def parse_date_from_email(self, email_text: str) -> Optional[str]:
        """
        Parse date from email text
        
        Args:
            email_text: Email content to parse
            
        Returns:
            Date string in YYYY-MM-DD format or None if not found
        """
        logger.debug("Starting date parsing...")
        
        # Log first 500 characters for debugging
        preview = email_text[:500].replace('\n', ' ').strip()
        logger.debug(f"Email text preview: {preview}")
        
        date_found = False
        parsed_date = None
        
        # Try each date pattern
        for i, pattern in enumerate(self.date_patterns):
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            
            if matches:
                logger.debug(f"Pattern {i+1} found matches: {matches}")
                
                for match in matches:
                    try:
                        parsed_date = self._parse_date_string(match, i)
                        if parsed_date:
                            date_found = True
                            break
                    except Exception as e:
                        logger.debug(f"Failed to parse date '{match}': {e}")
                        continue
                
                if date_found:
                    break
        
        if not date_found:
            logger.warning("No date patterns matched, using current date")
            parsed_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Final parsed date: {parsed_date}")
        return parsed_date
    
    def _parse_date_string(self, date_str: str, pattern_index: int) -> Optional[str]:
        """
        Parse a specific date string using the appropriate format
        
        Args:
            date_str: Date string to parse
            pattern_index: Index of the pattern that matched
            
        Returns:
            Formatted date string or None if parsing failed
        """
        date_str_clean = date_str.strip()
        
        # Handle Spanish month abbreviations for BAC format
        if pattern_index == 0:  # BAC format
            logger.debug(f"Processing BAC date format: '{date_str_clean}'")
            date_str_clean = self._convert_spanish_months(date_str_clean)
        
        # Try to parse with the corresponding format
        try:
            fmt = self.date_formats[pattern_index]
            parsed_date = datetime.strptime(date_str_clean, fmt)
            result = parsed_date.strftime('%Y-%m-%d')
            logger.debug(f"Successfully parsed '{date_str}' to '{result}' using format '{fmt}'")
            return result
            
        except ValueError as e:
            logger.debug(f"Failed to parse '{date_str_clean}' with format '{self.date_formats[pattern_index]}': {e}")
            
            # Try alternative formats for flexibility
            alternative_formats = ['%b %d, %Y', '%B %d, %Y', '%d/%m/%Y', '%m/%d/%Y']
            for alt_fmt in alternative_formats:
                try:
                    parsed_date = datetime.strptime(date_str_clean, alt_fmt)
                    result = parsed_date.strftime('%Y-%m-%d')
                    logger.debug(f"Successfully parsed with alternative format '{alt_fmt}': {result}")
                    return result
                except ValueError:
                    continue
            
            return None
    
    def _convert_spanish_months(self, date_str: str) -> str:
        """
        Convert Spanish month abbreviations to English
        
        Args:
            date_str: Date string with potential Spanish months
            
        Returns:
            Date string with English month abbreviations
        """
        date_str_lower = date_str.lower()
        
        # Replace Spanish month abbreviations
        for spanish_abbr, english_abbr in self.spanish_months_abbr.items():
            if spanish_abbr in date_str_lower:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + spanish_abbr + r'\b'
                date_str = re.sub(pattern, english_abbr, date_str, flags=re.IGNORECASE)
                logger.debug(f"Converted Spanish month '{spanish_abbr}' to '{english_abbr}'")
                break
        
        # Handle full Spanish month names
        full_spanish_months = {
            'enero': 'Jan', 'febrero': 'Feb', 'marzo': 'Mar', 'abril': 'Apr',
            'mayo': 'May', 'junio': 'Jun', 'julio': 'Jul', 'agosto': 'Aug',
            'septiembre': 'Sep', 'octubre': 'Oct', 'noviembre': 'Nov', 'diciembre': 'Dec'
        }
        
        for spanish_month, english_abbr in full_spanish_months.items():
            if spanish_month in date_str_lower:
                date_str = date_str.lower().replace(spanish_month, english_abbr)
                logger.debug(f"Converted Spanish month '{spanish_month}' to '{english_abbr}'")
                break
        
        return date_str
    
    def validate_date(self, date_str: str) -> bool:
        """
        Validate that a date string is in the correct format
        
        Args:
            date_str: Date string to validate (YYYY-MM-DD format)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
