"""
Logging configuration for ExpenseTracker
Provides structured logging with file and console output
"""

import logging
import os
from datetime import datetime
from typing import Optional

class ExpenseTrackerLogger:
    """Centralized logging for ExpenseTracker"""
    
    def __init__(self, log_level: str = 'INFO', log_file_path: Optional[str] = None):
        self.log_level = log_level.upper()
        self.log_file_path = log_file_path
        self._logger = None
        self.setup_logger()
    
    def setup_logger(self):
        """Configure logging with file and console handlers"""
        
        # Create logger
        self._logger = logging.getLogger('expense_tracker')
        self._logger.setLevel(getattr(logging, self.log_level))
        
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler (if log file path is provided)
        if self.log_file_path:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            
            # Add date to log file name
            base_name, ext = os.path.splitext(self.log_file_path)
            dated_log_file = f"{base_name}_{datetime.now().strftime('%Y%m%d')}{ext}"
            
            file_handler = logging.FileHandler(dated_log_file)
            file_handler.setLevel(getattr(logging, self.log_level))
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
    
    @property
    def logger(self):
        """Get the configured logger instance"""
        return self._logger
    
    def log_expense_processing(self, email_id: str, vendor: str, amount: float, category: str):
        """Log expense processing with structured data"""
        self._logger.info(
            f"Processed expense - Email: {email_id}, Vendor: {vendor}, "
            f"Amount: {amount}, Category: {category}"
        )
    
    def log_error_with_context(self, error: Exception, context: dict):
        """Log error with additional context"""
        context_str = ", ".join([f"{k}: {v}" for k, v in context.items()])
        self._logger.error(f"Error: {str(error)} | Context: {context_str}", exc_info=True)
    
    def log_performance(self, operation: str, duration: float, count: int = 1):
        """Log performance metrics"""
        self._logger.info(f"Performance - {operation}: {duration:.2f}s for {count} items")

def get_logger() -> logging.Logger:
    """Get the expense tracker logger instance"""
    from config_manager import config_manager
    
    # Create logger with configuration
    logger_instance = ExpenseTrackerLogger(
        log_level=config_manager.config.log_level,
        log_file_path=config_manager.config.log_file_path
    )
    
    return logger_instance.logger
