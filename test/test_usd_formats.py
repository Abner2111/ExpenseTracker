#!/usr/bin/env python3
"""
Test script to verify various USD amount formats are detected and converted correctly.
"""

import sys
import os
import re

# Add the src directory to the path (go up one level from test/ to project root, then to src/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'src'))

# Import the parsing function
from main import parse_expense_from_email

# Test different USD formats
test_cases = [
    {
        "name": "Monto: USD format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: SPOTIFY
Monto: USD 9.99
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount_range": (5000, 5100)  # Around 5028 CRC
    },
    {
        "name": "USD amount format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: AMAZON
USD 25.50
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount_range": (12800, 12900)  # Around 25.50 * 503 CRC
    },
    {
        "name": "Amount USD format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: PAYPAL
25.50 USD
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount_range": (12800, 12900)  # Around 25.50 * 503 CRC
    },
    {
        "name": "Dollar symbol format",
        "content": """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Comercio: APPLE
$19.99
Fecha: Ago 15, 2025, 10:30
""",
        "expected_amount_range": (10000, 10100)  # Around 19.99 * 503 CRC
    }
]

def test_usd_formats():
    print("Testing various USD amount formats...")
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
        
        # Check if amount is in expected range (converted to CRC)
        min_expected, max_expected = test_case['expected_amount_range']
        if min_expected <= amount <= max_expected:
            print(f"✅ Amount conversion SUCCESS: {amount:.2f} CRC is in expected range ({min_expected}-{max_expected})")
        else:
            print(f"❌ Amount conversion FAIL: {amount:.2f} CRC is NOT in expected range ({min_expected}-{max_expected})")
            all_passed = False
        
        # Check if conversion info is in notes
        if 'USD' in notes and 'Rate:' in notes:
            print("✅ Conversion information found in notes")
        else:
            print("❌ No conversion information in notes")
            all_passed = False
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! USD amount detection and conversion is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    test_usd_formats()
