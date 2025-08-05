#!/usr/bin/env python3
"""
Debug script to test date parsing logic with sample BAC email content
"""

import re
from datetime import datetime

def debug_parse_date(email_text):
    """Test the date parsing logic with debug output"""
    print(f"Debug: Starting date parsing...")
    print(f"Debug: First 500 chars of email text for date analysis:\n{email_text[:500]}")
    print("-" * 50)
    
    # Initialize with current date as default
    parsed_date = datetime.now().strftime('%Y-%m-%d')
    
    # Special handling for BAC format with lots of whitespace/newlines
    # Look for "Fecha:" followed by date on potentially next lines
    bac_date_match = re.search(r'Fecha:\s*[\r\n\s]*(\w{3}\s+\d{1,2},\s+\d{4})(?:,\s+\d{1,2}:\d{2})?', email_text, re.IGNORECASE)
    if bac_date_match:
        date_str = bac_date_match.group(1).strip()
        print(f"Debug: Found BAC date format: '{date_str}'")
        
        # Handle Spanish month abbreviations
        spanish_months = {
            'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
            'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
            'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
        }
        
        # Convert Spanish month abbreviations to English
        for spanish_abbr, english_abbr in spanish_months.items():
            if spanish_abbr.lower() in date_str.lower():
                date_str = re.sub(r'\b' + spanish_abbr + r'\b', english_abbr, date_str, flags=re.IGNORECASE)
                print(f"Debug: Converted Spanish month '{spanish_abbr}' to '{english_abbr}': '{date_str}'")
                break
        
        try:
            parsed_date = datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')
            print(f"Debug: Successfully parsed BAC date: {parsed_date}")
            return parsed_date
        except ValueError as e:
            print(f"Debug: Failed to parse BAC date: {date_str}, error: {e}")
    else:
        print("Debug: No BAC date format found, trying other patterns...")
        # Fall back to other date patterns
        date_patterns = [
            r'(?:Fecha|Date|Fecha de Compra|Fecha de Transacción):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', # DD/MM/YYYY or DD-MM-YYYY
            r'(?:procesada el|el)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})', # "procesada el DD/MM/YYYY"
            r'(\w{3}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2})', # BAC format: Jul 31, 2025, 14:29
            r'(\d{4}-\d{2}-\d{2})', # YYYY-MM-DD
            r'(\d{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s+\d{4})', # DD Mon YYYY
            r'(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},\s+\d{4}', # Month DD, YYYY (Spanish)
            r'(\w{3}\s+\d{1,2},\s+\d{4})', # English Mon DD, YYYY
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})' # General DD/MM/YYYY or MM/DD/YYYY format
        ]
        date_found = False
        for i, pattern in enumerate(date_patterns):
            match = re.search(pattern, email_text, re.IGNORECASE)
            if match:
                date_str = match.group(1).replace('.', '')
                print(f"Debug: Pattern {i+1} found date: '{date_str}' using pattern: {pattern}")
                # Handle BAC datetime format by removing time portion
                if ',' in date_str and ':' in date_str:
                    # Split on comma, keep first two parts, remove time from second part
                    parts = date_str.split(',')
                    if len(parts) >= 2:
                        date_str = parts[0] + ',' + parts[1].split(' ')[0] + ' ' + parts[1].split(' ')[1]
                    print(f"Debug: Cleaned datetime format: '{date_str}'")
                
                for fmt in ['%b %d, %Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %b %Y', '%B %d, %Y', '%d %B %Y', '%m/%d/%Y']:
                    try:
                        # Handle month names in Spanish if they appear without abbreviations
                        date_str_clean = date_str
                        if 'enero' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('enero', 'Jan')
                        elif 'febrero' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('febrero', 'Feb')
                        elif 'marzo' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('marzo', 'Mar')
                        elif 'abril' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('abril', 'Apr')
                        elif 'mayo' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('mayo', 'May')
                        elif 'junio' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('junio', 'Jun')
                        elif 'julio' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('julio', 'Jul')
                        elif 'agosto' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('agosto', 'Aug')
                        elif 'septiembre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('septiembre', 'Sep')
                        elif 'octubre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('octubre', 'Oct')
                        elif 'noviembre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('noviembre', 'Nov')
                        elif 'diciembre' in date_str_clean.lower(): date_str_clean = date_str_clean.lower().replace('diciembre', 'Dec')

                        parsed_date = datetime.strptime(date_str_clean, fmt).strftime('%Y-%m-%d')
                        print(f"Debug: Successfully parsed date: {parsed_date} using format: {fmt}")
                        date_found = True
                        break
                    except ValueError as e:
                        print(f"Debug: Failed to parse '{date_str_clean}' with format '{fmt}': {e}")
                        continue
                if date_found:
                    break
        
        if not date_found:
            print("Debug: No date patterns matched, keeping default date")
    
    print(f"Debug: Final date assigned: {parsed_date}")
    return parsed_date

# Test with sample BAC email formats
print("=" * 60)
print("TESTING DATE PARSING")
print("=" * 60)

# Sample 1: BAC format with Fecha field
sample_email_1 = """
Subject: Notificación de transacción

Estimado cliente,

Le informamos que se procesó la siguiente transacción:

Fecha:
Aug 5, 2025

Comercio: MSJ PARQUIMETROS
Monto: CRC 32.00
Tipo: Compra

Detalles adicionales...
"""

print("\n--- Test 1: BAC format with 'Fecha:' field ---")
result1 = debug_parse_date(sample_email_1)
print(f"RESULT: {result1}")

# Sample 2: BAC format with datetime
sample_email_2 = """
Subject: Notificación de transacción

Fecha: Aug 5, 2025, 14:29
Comercio: COCONUT BAR RESTAURANTE
Monto: CRC 9,690.00
"""

print("\n--- Test 2: BAC format with datetime ---")
result2 = debug_parse_date(sample_email_2)
print(f"RESULT: {result2}")

# Sample 3: Alternative format
sample_email_3 = """
Transacción procesada el 05/08/2025
Comercio: Google TikTok Videos
Monto: 1349 USD
"""

print("\n--- Test 3: DD/MM/YYYY format ---")
result3 = debug_parse_date(sample_email_3)
print(f"RESULT: {result3}")

# Sample 4: Spanish month abbreviation like in your email
sample_email_4 = """
Hola ABNER JESUS ARROYO QUESADA

A continuación le detallamos la transacción realizada:

Comercio: COCONUT BAR RESTAURANT
Ciudad y país: SAN JOSE, Costa Rica
Fecha: Ago 4, 2025, 12:59
VISA: ************7082
Autorización: 008479
Referencia: 521618008479
Tipo de Transacción: COMPRA
"""

print("\n--- Test 4: Spanish 'Ago' abbreviation ---")
result4 = debug_parse_date(sample_email_4)
print(f"RESULT: {result4}")

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"Test 1: {result1}")
print(f"Test 2: {result2}")
print(f"Test 3: {result3}")
print(f"Test 4 (Spanish Ago): {result4}")
print("=" * 60)
