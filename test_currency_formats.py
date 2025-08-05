#!/usr/bin/env python3
"""
Test script to verify CRC and EUR amount formats still work correctly.
"""

import sys
import os
import re

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the parsing function
from main import parse_expense_from_email

# Test different currency formats
test_cases = [
    {
        "name": "CRC format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: SUPERMERCADO MAXI PALI
Monto: CRC 5,650.00
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount": 5650.00,
        "expected_currency": "CRC"
    },
    {
        "name": "Colón symbol format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: RESTAURANTE OLIVE GARDEN
Monto: ₡15,500.50
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount": 15500.50,
        "expected_currency": "CRC"
    },
    {
        "name": "EUR format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: AMAZON EUROPA
Monto: EUR 45.99
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount_range": (25000, 26000),  # Around 45.99 * 550 CRC (EUR rate)
        "expected_currency": "EUR"
    },
    {
        "name": "Euro symbol format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: BOOKING DOT COM
Monto: €125.75
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount_range": (68000, 70000),  # Around 125.75 * 550 CRC (EUR rate)
        "expected_currency": "EUR"
    }
]

def test_currency_formats():
    print("Testing various currency formats...")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        result = parse_expense_from_email(test_case['content'])
        
        amount = result.get('amount', 0)
        vendor = result.get('vendor', 'Unknown')
        notes = result.get('notes', '')
        
        print(f"Vendor: {vendor}")
        print(f"Amount: {amount:.2f} CRC")
        print(f"Notes: {notes}")
        
        # Check if amount is correct
        if 'expected_amount' in test_case:
            expected = test_case['expected_amount']
            if abs(amount - expected) < 0.01:  # Allow small floating point differences
                print(f"✅ Amount SUCCESS: {amount:.2f} CRC matches expected {expected}")
            else:
                print(f"❌ Amount FAIL: {amount:.2f} CRC does not match expected {expected}")
                all_passed = False
        elif 'expected_amount_range' in test_case:
            min_expected, max_expected = test_case['expected_amount_range']
            if min_expected <= amount <= max_expected:
                print(f"✅ Amount conversion SUCCESS: {amount:.2f} CRC is in expected range ({min_expected}-{max_expected})")
            else:
                print(f"❌ Amount conversion FAIL: {amount:.2f} CRC is NOT in expected range ({min_expected}-{max_expected})")
                all_passed = False
        
        # Check currency-specific requirements
        expected_currency = test_case.get('expected_currency', 'CRC')
        if expected_currency != 'CRC':
            # Should have conversion information in notes
            if expected_currency in notes and 'Rate:' in notes:
                print(f"✅ Conversion information found for {expected_currency}")
            else:
                print(f"❌ No conversion information found for {expected_currency}")
                all_passed = False
        else:
            # Should NOT have conversion information for CRC
            if 'Rate:' not in notes:
                print("✅ No conversion needed for CRC amounts")
            else:
                print("❌ Unexpected conversion information for CRC amounts")
                all_passed = False
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Currency detection and conversion is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    test_currency_formats()
