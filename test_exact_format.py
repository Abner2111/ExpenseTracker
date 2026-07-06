#!/usr/bin/env python3
"""
Test with the exact format from the attachment
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from date_parser import DateParser
import re

def test_exact_format():
    """Test with the exact date format from the attachment"""
    
    # Exact format from attachment: "Sep 5, 2025, 18:19"
    sample_email = """
    Fecha:              Sep 5, 2025, 18:19
    """
    
    parser = DateParser()
    
    print("Testing exact format from attachment...")
    print("=" * 50)
    print(f"Sample: {sample_email.strip()}")
    print("=" * 50)
    
    result = parser.parse_date_from_email(sample_email)
    print(f"Parsed result: {result}")
    
    # Test if the current patterns handle the time component
    print("\nAnalyzing patterns:")
    for i, pattern in enumerate(parser.date_patterns):
        matches = re.findall(pattern, sample_email, re.IGNORECASE)
        print(f"Pattern {i+1}: {pattern}")
        print(f"  Matches: {matches}")

if __name__ == "__main__":
    test_exact_format()