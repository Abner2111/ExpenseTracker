"""
Configuration management for ExpenseTracker
Centralizes all configuration settings and provides environment-based overrides
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration settings for ExpenseTracker"""
    
    # Google API Configuration - using original names for compatibility
    google_sheet_id: str  # Original: SPREADSHEET_ID 
    google_sheet_tab: str  # Original: SPREADSHEET_NAME
    gmail_credentials_path: str
    token_path: str
    
    # Processing Configuration
    filter_by_month: Optional[str]
    
    # Currency Configuration
    exchange_rate_api_key: Optional[str]
    fallback_exchange_rates: dict
    
    # Database Configuration
    database_path: Optional[str]
    
    # Logging Configuration
    log_level: str
    log_file_path: str
    
    # Email Processing Configuration
    batch_size: int
    rate_limit_delay: float
    
    # Derived paths
    src_dir: Optional[str] = None
    
    def __post_init__(self):
        """Set derived configuration after initialization"""
        if self.src_dir is None:
            self.src_dir = os.path.dirname(os.path.abspath(__file__))

class ConfigManager:
    """Manages configuration loading from various sources"""
    
    def __init__(self):
        self._config = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables and config files"""
        
        # Import original config for backwards compatibility
        try:
            from config import (
                SPREADSHEET_ID, SPREADSHEET_NAME, 
                GMAIL_CREDENTIALS_PATH, TOKEN_PATH, FILTER_BY_MONTH
            )
        except ImportError:
            # Fallback values if config.py doesn't exist
            SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '')
            SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Expenses')
            GMAIL_CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
            TOKEN_PATH = os.getenv('TOKEN_PATH', 'token.pickle')
            FILTER_BY_MONTH = os.getenv('FILTER_BY_MONTH')
        
        self._config = Config(
            # Google API Configuration - map to expected names
            google_sheet_id=os.getenv('SPREADSHEET_ID', SPREADSHEET_ID),
            google_sheet_tab=os.getenv('SPREADSHEET_NAME', SPREADSHEET_NAME),
            gmail_credentials_path=os.getenv('GMAIL_CREDENTIALS_PATH', GMAIL_CREDENTIALS_PATH),
            token_path=os.getenv('TOKEN_PATH', TOKEN_PATH),
            
            # Processing Configuration
            filter_by_month=os.getenv('FILTER_BY_MONTH', FILTER_BY_MONTH),
            
            # Currency Configuration
            exchange_rate_api_key=os.getenv('EXCHANGE_RATE_API_KEY'),
            fallback_exchange_rates={
                'USD': 500.0,  # Fallback USD to CRC rate
                'EUR': 550.0,  # Fallback EUR to CRC rate
                'GBP': 650.0   # Fallback GBP to CRC rate
            },
            
            # Database Configuration
            database_path=os.getenv('DATABASE_PATH'),  # None = use default
            
            # Logging Configuration
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file_path=os.getenv('LOG_FILE_PATH', 'logs/expense_tracker.log'),
            
            # Email Processing Configuration
            batch_size=int(os.getenv('BATCH_SIZE', '50')),
            rate_limit_delay=float(os.getenv('RATE_LIMIT_DELAY', '0.5'))
        )
    
    @property
    def config(self) -> Config:
        """Get the current configuration"""
        return self._config
    
    @classmethod
    def get_config(cls) -> Config:
        """Get the global configuration instance"""
        return config_manager.config
    
    def get_google_scopes(self) -> list:
        """Get required Google API scopes"""
        return [
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    def validate_config(self):
        """Validate that required configuration is present"""
        errors = []
        
        if not self._config.google_sheet_id:
            errors.append("SPREADSHEET_ID is required")
        
        if not os.path.exists(self._config.gmail_credentials_path):
            errors.append(f"Gmail credentials file not found: {self._config.gmail_credentials_path}")
        
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))
    
    def get_credentials_path(self) -> str:
        """Get the full path to Gmail credentials"""
        if os.path.isabs(self._config.gmail_credentials_path):
            return self._config.gmail_credentials_path
        else:
            # Make relative to src directory
            src_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(src_dir, self._config.gmail_credentials_path)
    
    def get_token_path(self) -> str:
        """Get the full path to token file"""
        if os.path.isabs(self._config.token_path):
            return self._config.token_path
        else:
            # Make relative to src directory
            src_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(src_dir, self._config.token_path)

# Global config manager instance
config_manager = ConfigManager()
