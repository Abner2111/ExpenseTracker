#!/usr/bin/env python3
"""
Test script for currency conversion functionality
"""

import re
import requests
from datetime import datetime

def get_exchange_rate(from_currency, to_currency='CRC'):
    """
    Get current exchange rate from one currency to another.
    Default converts to Costa Rican Colones (CRC).
    """
    try:
        # Using exchangerate-api.com (free tier allows 1500 requests/month)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if to_currency in data['rates']:
                rate = data['rates'][to_currency]
                print(f"Debug: Exchange rate {from_currency} to {to_currency}: {rate}")
                return rate
            else:
                print(f"Warning: {to_currency} not found in exchange rates")
                return None
        else:
            print(f"Warning: Failed to get exchange rate. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Warning: Error getting exchange rate: {e}")
        return None

def convert_currency_to_crc(amount, currency):
    """
    Convert amount from given currency to Costa Rican Colones (CRC).
    Returns tuple: (converted_amount, original_currency, conversion_rate)
    """
    if currency.upper() == 'CRC':
        return amount, currency, 1.0
    
    # Common fallback rates if API fails (approximate rates as of 2025)
    fallback_rates = {
        'USD': 520.0,  # 1 USD ≈ 520 CRC (approximate)
        'EUR': 570.0,  # 1 EUR ≈ 570 CRC (approximate)
        'GBP': 650.0,  # 1 GBP ≈ 650 CRC (approximate)
    }
    
    # Try to get current exchange rate
    rate = get_exchange_rate(currency.upper(), 'CRC')
    
    if rate is None:
        # Use fallback rate if available
        if currency.upper() in fallback_rates:
            rate = fallback_rates[currency.upper()]
            print(f"Debug: Using fallback rate for {currency}: {rate}")
        else:
            print(f"Warning: No exchange rate available for {currency}. Using original amount.")
            return amount, currency, 1.0
    
    converted_amount = amount * rate
    print(f"Debug: Converted {amount} {currency} to {converted_amount:.2f} CRC (rate: {rate})")
    return converted_amount, currency, rate

def test_currency_patterns():
    """Test currency detection and conversion with sample emails"""
    
    # Test cases with different currencies
    test_cases = [
        {
            'name': 'USD Dollar Amount',
            'email_text': 'Comercio: Google TikTok Videos\nMonto: $13.49 USD\nTipo: Compra',
            'expected_currency': 'USD'
        },
        {
            'name': 'CRC Colones Amount',
            'email_text': 'Comercio: COCONUT BAR RESTAURANT\nMonto: CRC 9,690.00\nTipo: Compra',
            'expected_currency': 'CRC'
        },
        {
            'name': 'USD with Dollar Sign',
            'email_text': 'Comercio: Netflix\nTotal: $15.99\nAutorización: 12345',
            'expected_currency': 'USD'
        },
        {
            'name': 'EUR Euro Amount',
            'email_text': 'Comercio: Spotify\nMonto: €9.99 EUR\nTipo: Suscripción',
            'expected_currency': 'EUR'
        },
        {
            'name': 'CRC with Colón Symbol',
            'email_text': 'Comercio: Automercado\nTotal: ₡45,500.00\nTipo: Compra',
            'expected_currency': 'CRC'
        }
    ]
    
    print("=" * 60)
    print("TESTING CURRENCY DETECTION AND CONVERSION")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        print(f"Email text: {test_case['email_text']}")
        
        # Amount parsing patterns (same as in main script)
        amount_patterns = [
            # Pattern with explicit currency - CRC format
            (r'CRC\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'CRC'),
            # Pattern with explicit currency - USD format  
            (r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*USD\b', 'USD'),
            (r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))', 'USD'),
            # Pattern with explicit currency - EUR format
            (r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*EUR\b', 'EUR'),
            (r'€(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))', 'EUR'),
            # CRC patterns with colón symbol
            (r'₡\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'CRC'),
            (r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}?))\s*(?:CRC|₡|colones)\b', 'CRC'),
            # Generic patterns
            (r'(?:Monto|Total|Monto Total|Total a Pagar|Subtotal|Gran Total):\s*(?:CRC|₡)?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', 'CRC'),
            (r'Monto:\s*[\r\n\s]*([₡\$]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'UNKNOWN'),
            (r'Total:\s*[\r\n\s]*([₡\$]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'UNKNOWN'),
        ]
        
        found_amount = False
        for j, (pattern, currency_hint) in enumerate(amount_patterns):
            match = re.search(pattern, test_case['email_text'], re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                detected_currency = currency_hint
                print(f"  Pattern {j+1} matched: '{amount_str}' with currency hint: '{detected_currency}'")
                
                # Determine actual currency based on symbols
                if '₡' in amount_str:
                    detected_currency = 'CRC'
                    amount_str = amount_str.replace('₡', '').strip()
                elif '$' in amount_str:
                    detected_currency = 'USD'
                    amount_str = amount_str.replace('$', '').strip()
                elif '€' in amount_str:
                    detected_currency = 'EUR'
                    amount_str = amount_str.replace('€', '').strip()
                elif detected_currency == 'UNKNOWN':
                    detected_currency = 'CRC'
                    amount_str = amount_str.replace('₡', '').replace('$', '').strip()
                
                # Process number format
                if ',' in amount_str and '.' in amount_str:
                    amount_str = amount_str.replace(',', '')
                elif ',' in amount_str and '.' not in amount_str:
                    if len(amount_str.split(',')) > 1 and len(amount_str.split(',')[1]) == 2:
                        amount_str = amount_str.replace(',', '.')
                    else:
                        amount_str = amount_str.replace(',', '')
                
                try:
                    amount_value = float(amount_str)
                    print(f"  Detected: {amount_value} {detected_currency}")
                    
                    # Convert to CRC if needed
                    if detected_currency.upper() != 'CRC':
                        converted_amount, original_currency, conversion_rate = convert_currency_to_crc(amount_value, detected_currency)
                        print(f"  ✓ CONVERTED: {amount_value} {original_currency} → {converted_amount:.2f} CRC (Rate: {conversion_rate})")
                    else:
                        print(f"  ✓ NO CONVERSION NEEDED: {amount_value} CRC")
                    
                    found_amount = True
                    break
                except ValueError as e:
                    print(f"  Failed to parse: {e}")
        
        if not found_amount:
            print("  ✗ No amount found")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_currency_patterns()
