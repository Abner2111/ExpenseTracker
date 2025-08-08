#!/usr/bin/env python3
"""
Final integration test to verify the complete Spotify USD 9.99 parsing scenario.
"""

import sys
import os
import re

# Add the src directory to the path (go up one level from test/ to project root, then to src/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'src'))

# Import the parsing function
from main import parse_expense_from_email

# Real-world Spotify email format based on the original issue
spotify_email = """From: notificacion@notificacionesbaccr.com
Subject: Notificación de transacción

Estimado Cliente,

Le informamos que se ha realizado una transacción con su tarjeta de crédito BAC.

Detalles de la transacción:

Comercio: SPOTIFY
Monto: USD 9.99
Fecha: Ago 15, 2025, 10:30
Número de autorización: 123456789
Número de referencia: REF987654321

Esta transacción ha sido procesada exitosamente.

Si no reconoce esta transacción, por favor contacte inmediatamente a nuestro centro de atención al cliente.

Gracias por utilizar nuestros servicios.

BAC Credomatic
"""

def test_spotify_integration():
    print("FINAL INTEGRATION TEST: Spotify USD 9.99")
    print("=" * 60)
    print("Testing complete parsing pipeline for real-world Spotify email...")
    print()
    
    result = parse_expense_from_email(spotify_email)
    
    print("RESULTS:")
    print("-" * 30)
    print(f"Vendor: '{result.get('vendor', 'ERROR: Not found')}'")
    print(f"Amount: {result.get('amount', 'ERROR: Not found')} CRC")
    print(f"Date: {result.get('date', 'ERROR: Not found')}")
    print(f"Category: {result.get('category', 'ERROR: Not found')}")
    print(f"Notes: {result.get('notes', 'ERROR: Not found')}")
    print()
    
    # Validation
    success_count = 0
    total_tests = 5
    
    # Test 1: Vendor should be just "SPOTIFY"
    if result.get('vendor') == 'SPOTIFY':
        print("✅ Test 1 PASSED: Vendor correctly parsed as 'SPOTIFY'")
        success_count += 1
    else:
        print(f"❌ Test 1 FAILED: Expected 'SPOTIFY', got '{result.get('vendor')}'")
    
    # Test 2: Amount should be converted to CRC (around 5000)
    amount = result.get('amount', 0)
    if 4500 <= amount <= 5500:
        print(f"✅ Test 2 PASSED: Amount correctly converted to CRC ({amount:.2f})")
        success_count += 1
    else:
        print(f"❌ Test 2 FAILED: Expected ~5000 CRC, got {amount}")
    
    # Test 3: Date should be correctly parsed to 2025-08-15
    if result.get('date') == '2025-08-15':
        print("✅ Test 3 PASSED: Date correctly parsed from 'Ago 15, 2025'")
        success_count += 1
    else:
        print(f"❌ Test 3 FAILED: Expected '2025-08-15', got '{result.get('date')}'")
    
    # Test 4: Category should be assigned (preferably 'Streaming')
    category = result.get('category', '')
    if category and category != 'Unknown':
        print(f"✅ Test 4 PASSED: Category assigned as '{category}'")
        success_count += 1
    else:
        print(f"❌ Test 4 FAILED: No category assigned (got '{category}')")
    
    # Test 5: Notes should contain conversion information
    notes = result.get('notes', '')
    if 'USD' in notes and '9.99' in notes and 'Rate:' in notes:
        print("✅ Test 5 PASSED: Conversion information found in notes")
        success_count += 1
    else:
        print("❌ Test 5 FAILED: No conversion information in notes")
    
    print()
    print("=" * 60)
    print(f"FINAL SCORE: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 COMPLETE SUCCESS! All parsing issues have been resolved.")
        print("✨ The Spotify USD 9.99 issue is now fixed!")
    else:
        print("⚠️  Some issues remain. Check the failed tests above.")
        
    return success_count == total_tests

if __name__ == "__main__":
    test_spotify_integration()
