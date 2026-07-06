#!/usr/bin/env python3
"""
Test script to debug date parsing issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from date_parser import DateParser

def test_date_parsing():
    """Test date parsing with the problematic email format"""
    
    # Sample email text from your attachment
    sample_email = """
    Hola ABNER JESUS ARROYO QUESADA

    A continuación le detallamos la transacción realizada:

    Comercio:           DOGGERS
    Ciudad y país:      CARTAGO, Costa Rica  
    Fecha:              Sep 5, 2025, 18:19
    VISA               ************7082
    Autorización:       000364
    Referencia:         524900000364
    Tipo de Transacción: COMPRA

    Monto:             CRC 5,000.00
    """
    
    parser = DateParser()
    
    print("Testing date parsing...")
    print("=" * 50)
    print(f"Sample email preview:\n{sample_email[:200]}...")
    print("=" * 50)
    
    # Test the date parsing
    result = parser.parse_date_from_email(sample_email)
    print(f"Parsed date result: {result}")
    
    # Let's also test the patterns directly
    print("\nTesting individual patterns:")
    print("-" * 30)
    
    import re
    for i, pattern in enumerate(parser.date_patterns):
        matches = re.findall(pattern, sample_email, re.IGNORECASE)
        if matches:
            print(f"Pattern {i+1}: {pattern}")
            print(f"  Matches: {matches}")
            for match in matches:
                parsed = parser._parse_date_string(match, i)
                print(f"  Parsed result: {parsed}")
        else:
            print(f"Pattern {i+1}: No matches")

if __name__ == "__main__":
    test_date_parsing()