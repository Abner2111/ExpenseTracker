"""
Data models and validation for ExpenseTracker
Defines the structure and validation rules for expense data
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any
import re

@dataclass
class Expense:
    """Represents a parsed expense transaction"""
    
    vendor: str
    amount: float
    currency: str
    date: date
    category: str
    notes: Optional[str] = None
    email_id: Optional[str] = None
    original_amount: Optional[float] = None
    original_currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    
    def __post_init__(self):
        """Validate expense data after initialization"""
        self.validate()
    
    def validate(self):
        """Validate expense data integrity"""
        errors = []
        
        # Vendor validation
        if not self.vendor or not self.vendor.strip():
            errors.append("Vendor cannot be empty")
        
        # Amount validation
        if self.amount <= 0:
            errors.append("Amount must be positive")
        
        # Currency validation
        if not self.currency or len(self.currency) != 3:
            errors.append("Currency must be a 3-letter code (e.g., USD, CRC)")
        
        # Date validation
        if not isinstance(self.date, date):
            errors.append("Date must be a valid date object")
        
        # Category validation
        if not self.category or not self.category.strip():
            errors.append("Category cannot be empty")
        
        if errors:
            raise ValueError(f"Expense validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert expense to dictionary for serialization"""
        return {
            'vendor': self.vendor,
            'amount': self.amount,
            'currency': self.currency,
            'date': self.date.isoformat(),
            'category': self.category,
            'notes': self.notes,
            'email_id': self.email_id,
            'original_amount': self.original_amount,
            'original_currency': self.original_currency,
            'exchange_rate': self.exchange_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create expense from dictionary"""
        # Convert date string back to date object
        if isinstance(data['date'], str):
            data['date'] = datetime.fromisoformat(data['date']).date()
        
        return cls(**data)
    
    def get_display_amount(self) -> str:
        """Get formatted amount for display"""
        if self.currency == 'CRC':
            return f"₡{self.amount:,.2f}"
        elif self.currency == 'USD':
            return f"${self.amount:,.2f}"
        elif self.currency == 'EUR':
            return f"€{self.amount:,.2f}"
        else:
            return f"{self.amount:,.2f} {self.currency}"
    
    def get_conversion_note(self) -> str:
        """Get conversion information for notes"""
        if self.original_amount and self.original_currency and self.exchange_rate:
            return f"Original: {self.original_amount} {self.original_currency} (Rate: {self.exchange_rate})"
        return ""

@dataclass
class EmailData:
    """Represents raw email data for processing"""
    
    email_id: str
    sender: str
    subject: str
    body: str
    date_received: datetime
    is_processed: bool = False
    
    def validate(self):
        """Validate email data"""
        errors = []
        
        if not self.email_id:
            errors.append("Email ID cannot be empty")
        
        if not self.body or not self.body.strip():
            errors.append("Email body cannot be empty")
        
        if errors:
            raise ValueError(f"Email validation failed: {'; '.join(errors)}")

@dataclass
class ProcessingResult:
    """Represents the result of processing an operation"""
    
    success: bool
    message: str
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'error': self.error,
            'details': self.details
        }

# Custom exceptions
class ExpenseTrackerError(Exception):
    """Base exception for ExpenseTracker"""
    pass

class EmailParsingError(ExpenseTrackerError):
    """Error during email parsing"""
    pass

class ExpenseParsingError(ExpenseTrackerError):
    """Error during expense parsing"""
    pass

class DatabaseError(ExpenseTrackerError):
    """Error during database operations"""
    pass

class GoogleSheetsError(ExpenseTrackerError):
    """Error during Google Sheets operations"""
    pass

class CurrencyConversionError(ExpenseTrackerError):
    """Error during currency conversion"""
    pass

class ValidationError(ExpenseTrackerError):
    """Custom exception for validation errors"""
    pass

class ProcessingError(ExpenseTrackerError):
    """Custom exception for processing errors"""
    pass
