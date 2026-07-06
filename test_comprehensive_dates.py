#!/usr/bin/env python3
"""
Comprehensive test for date parsing functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from date_parser import DateParser

def test_comprehensive_dates():
    """Test various date formats that might appear in emails"""
    
    test_cases = [
        # Your specific case
        ("Fecha: Sep 5, 2025, 18:19", "2025-09-05"),
        
        # Spanish months
        ("Fecha: Ago 15, 2025", "2025-08-15"),
        ("Fecha: Dic 25, 2025", "2025-12-25"),
        
        # Different formats
        ("Fecha: 2025-09-05", "2025-09-05"),
        ("Fecha: 05/09/2025", "2025-09-05"),
        ("Fecha: 5-9-2025", "2025-09-05"),
        ("Fecha: September 5, 2025", "2025-09-05"),
        ("Fecha: 5 September 2025", "2025-09-05"),
        
        # Edge cases
        ("fecha: sep 1, 2025", "2025-09-01"),  # lowercase
        ("No date here", None),  # Should use current date
    ]
    
    parser = DateParser()
    
    print("Comprehensive Date Parsing Test")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for i, (email_text, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {email_text[:50]}...")
        result = parser.parse_date_from_email(email_text)
        
        if expected is None:
            # Should be current date (today)
            from datetime import datetime
            expected = datetime.now().strftime('%Y-%m-%d')
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print(f"  Status:   {status}")
        
        if result == expected:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Date parsing is working correctly.")
    else:
        print("❌ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    test_comprehensive_dates()