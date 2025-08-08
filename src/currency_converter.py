"""
Currency conversion functionality for ExpenseTracker
Handles real-time exchange rates with fallback mechanisms
"""

import requests
import json
from typing import Optional, Dict
from datetime import datetime, timedelta

from config_manager import config_manager
from logger import get_logger

logger = get_logger()

class CurrencyConverter:
    """Handles currency conversion with caching and fallbacks"""
    
    def __init__(self):
        self.config = config_manager.config
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache rates for 1 hour
    
    def convert_to_crc(self, amount: float, from_currency: str) -> tuple[float, float]:
        """
        Convert amount to Costa Rican Colones (CRC)
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (USD, EUR, etc.)
            
        Returns:
            Tuple of (converted_amount, exchange_rate)
        """
        if from_currency == 'CRC':
            return amount, 1.0
        
        try:
            rate = self.get_exchange_rate(from_currency, 'CRC')
            converted_amount = amount * rate
            
            logger.info(f"Converted {amount} {from_currency} to {converted_amount:.2f} CRC (rate: {rate})")
            return converted_amount, rate
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {e}")
            # Use fallback rate
            fallback_rate = self.config.fallback_exchange_rates.get(from_currency, 500.0)
            converted_amount = amount * fallback_rate
            
            logger.warning(f"Using fallback rate for {from_currency}: {fallback_rate}")
            return converted_amount, fallback_rate
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate between two currencies
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate as float
        """
        cache_key = f"{from_currency}_{to_currency}_{datetime.now().date()}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                logger.debug(f"Using cached exchange rate for {from_currency} to {to_currency}")
                return cached_data['rate']
        
        # Fetch from API
        try:
            rate = self._fetch_exchange_rate_from_api(from_currency, to_currency)
            
            # Cache the result
            self.cache[cache_key] = {
                'rate': rate,
                'timestamp': datetime.now()
            }
            
            return rate
            
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate from API: {e}")
            
            # Try fallback
            if from_currency in self.config.fallback_exchange_rates:
                rate = self.config.fallback_exchange_rates[from_currency]
                logger.warning(f"Using fallback exchange rate for {from_currency}: {rate}")
                return rate
            
            raise ValueError(f"No exchange rate available for {from_currency} to {to_currency}")
    
    def _fetch_exchange_rate_from_api(self, from_currency: str, to_currency: str) -> float:
        """
        Fetch exchange rate from external API
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate as float
        """
        # Try multiple APIs for reliability
        apis = [
            self._fetch_from_exchangerate_api,
            self._fetch_from_fixer_api,
            self._fetch_from_currencyapi
        ]
        
        for api_func in apis:
            try:
                rate = api_func(from_currency, to_currency)
                if rate:
                    return rate
            except Exception as e:
                logger.debug(f"API {api_func.__name__} failed: {e}")
                continue
        
        raise ValueError("All exchange rate APIs failed")
    
    def _fetch_from_exchangerate_api(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch rate from exchangerate-api.com"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rate = data['rates'].get(to_currency)
            
            if rate:
                logger.debug(f"Got rate from exchangerate-api: {from_currency} to {to_currency} = {rate}")
                return float(rate)
            
        except Exception as e:
            logger.debug(f"exchangerate-api failed: {e}")
        
        return None
    
    def _fetch_from_fixer_api(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch rate from fixer.io (requires API key)"""
        try:
            api_key = self.config.exchange_rate_api_key
            if not api_key:
                return None
            
            url = f"http://data.fixer.io/api/latest"
            params = {
                'access_key': api_key,
                'base': from_currency,
                'symbols': to_currency
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                rate = data['rates'].get(to_currency)
                if rate:
                    logger.debug(f"Got rate from fixer.io: {from_currency} to {to_currency} = {rate}")
                    return float(rate)
            
        except Exception as e:
            logger.debug(f"fixer.io API failed: {e}")
        
        return None
    
    def _fetch_from_currencyapi(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch rate from currencyapi.com"""
        try:
            url = f"https://api.currencyapi.com/v3/latest"
            params = {
                'apikey': self.config.exchange_rate_api_key,
                'base_currency': from_currency,
                'currencies': to_currency
            }
            
            if not self.config.exchange_rate_api_key:
                return None
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rate = data.get('data', {}).get(to_currency, {}).get('value')
            
            if rate:
                logger.debug(f"Got rate from currencyapi: {from_currency} to {to_currency} = {rate}")
                return float(rate)
            
        except Exception as e:
            logger.debug(f"currencyapi failed: {e}")
        
        return None
    
    def detect_currency_from_text(self, text: str) -> tuple[str, str]:
        """
        Detect currency from email text
        
        Args:
            text: Email text content
            
        Returns:
            Tuple of (currency_code, currency_symbol)
        """
        text_lower = text.lower()
        
        # Currency patterns with their codes
        currency_patterns = {
            'USD': ['usd', '$', 'dolar', 'dollar'],
            'EUR': ['eur', '€', 'euro'],
            'CRC': ['crc', '₡', 'colon', 'colones'],
            'GBP': ['gbp', '£', 'pound', 'libra']
        }
        
        for currency_code, patterns in currency_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    symbol = self._get_currency_symbol(currency_code)
                    logger.debug(f"Detected currency: {currency_code} (symbol: {symbol})")
                    return currency_code, symbol
        
        # Default to CRC if no currency detected
        logger.debug("No currency detected, defaulting to CRC")
        return 'CRC', '₡'
    
    def _get_currency_symbol(self, currency_code: str) -> str:
        """Get currency symbol for currency code"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'CRC': '₡',
            'GBP': '£'
        }
        return symbols.get(currency_code, currency_code)
    
    def clear_cache(self):
        """Clear the exchange rate cache"""
        self.cache.clear()
        logger.info("Exchange rate cache cleared")
