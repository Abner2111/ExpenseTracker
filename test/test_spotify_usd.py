#!/usr/bin/env python3
"""
Test script to verify USD amount detection and conversion for Spotify format.
"""

import sys
import os
import re

# Add the src directory to the path (go up one level from test/ to project root, then to src/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'src'))

# Import the parsing function
from main import parse_expense_from_email

# Test email content similar to Spotify notification
test_email_content = """
From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Estimado Cliente,

Le informamos que se ha realizado una transacción con su tarjeta de crédito BAC.

Comercio: SPOTIFY
Monto: USD 9.99
Fecha: Ago 15, 2025, 10:30
Número de autorización: 123456
Número de referencia: 789012

Gracias por utilizar nuestros servicios.
"""

def test_spotify_usd_parsing():
    print("Testing Spotify USD 9.99 parsing...")
    print("=" * 50)
    
    print("Email content:")
    print(test_email_content)
    print("=" * 50)
    
    # Parse the expense
    result = parse_expense_from_email(test_email_content)
    
    print("\nParsing results:")
    print(f"Vendor: {result.get('vendor', 'Not found')}")
    print(f"Amount: {result.get('amount', 'Not found')}")
    print(f"Date: {result.get('date', 'Not found')}")
    print(f"Notes: {result.get('notes', 'Not found')}")
    
    # Check if conversion happened
    if result.get('amount', 0) > 50:  # Should be converted to CRC (around 5000+ CRC)
        print("\n✅ SUCCESS: USD amount appears to have been converted to CRC")
    else:
        print("\n❌ FAIL: USD amount was not converted (still showing as 9.99)")
    
    # Check if notes contain conversion info
    notes = result.get('notes', '')
    if 'USD' in notes and 'Rate:' in notes:
        print("✅ SUCCESS: Conversion information found in notes")
    else:
        print("❌ FAIL: No conversion information in notes")

if __name__ == "__main__":
    test_spotify_usd_parsing()
