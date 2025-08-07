#!/usr/bin/env python3
"""
Database administration tool for ExpenseTracker
Provides a simple command-line interface to manage vendor keywords and category rules
"""

import os
import sys
import argparse

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src_path)

from database import ExpenseDatabase

def list_vendors(db):
    """List all vendor keywords"""
    vendors = db.get_all_vendors()
    print(f"\n=== VENDOR KEYWORDS ({len(vendors)}) ===")
    for keyword, vendor_name in sorted(vendors):
        print(f"'{keyword}' → '{vendor_name}'")

def list_categories(db):
    """List all categories"""
    categories = db.get_all_categories()
    print(f"\n=== CATEGORIES ({len(categories)}) ===")
    for category in sorted(categories):
        print(f"- {category}")

def list_rules(db):
    """List all category rules"""
    rules = db.get_all_category_rules()
    print(f"\n=== CATEGORY RULES ({len(rules)}) ===")
    print("Rule Type          | Pattern                    | Category          | Priority")
    print("-" * 80)
    for rule_type, pattern, category, priority in rules:
        print(f"{rule_type:<18} | {pattern:<26} | {category:<17} | {priority}")

def add_vendor(db, keyword, vendor_name, category=None):
    """Add a new vendor keyword"""
    success = db.add_vendor_keyword(keyword, vendor_name, category)
    if success:
        print(f"✓ Added vendor keyword: '{keyword}' → '{vendor_name}'")
    else:
        print(f"✗ Failed to add vendor keyword: '{keyword}'")

def add_category(db, name, description=None):
    """Add a new category"""
    success = db.add_category(name, description)
    if success:
        print(f"✓ Added category: '{name}'")
    else:
        print(f"✗ Failed to add category: '{name}'")

def add_rule(db, rule_type, pattern, category, priority=1):
    """Add a new category rule"""
    valid_types = ['vendor_exact', 'vendor_contains', 'keyword_contains']
    if rule_type not in valid_types:
        print(f"✗ Invalid rule type. Must be one of: {', '.join(valid_types)}")
        return
    
    success = db.add_category_rule(rule_type, pattern, category, priority)
    if success:
        print(f"✓ Added rule: {rule_type} '{pattern}' → '{category}' (priority: {priority})")
    else:
        print(f"✗ Failed to add rule: {rule_type} '{pattern}' → '{category}'")

def test_vendor(db, text):
    """Test vendor identification for given text"""
    vendor = db.find_vendor_by_text(text)
    if vendor:
        category = db.categorize_vendor(vendor)
        print(f"\nTest Results for: '{text}'")
        print(f"  Vendor: {vendor}")
        print(f"  Category: {category}")
    else:
        category = db.categorize_vendor(text)
        print(f"\nTest Results for: '{text}'")
        print(f"  Vendor: Unknown (no keyword match)")
        print(f"  Category: {category}")

def delete_vendor(db, keyword):
    """Delete a vendor keyword"""
    success = db.delete_vendor_keyword(keyword)
    if success:
        print(f"✓ Deleted vendor keyword: '{keyword}'")
    else:
        print(f"✗ Failed to delete vendor keyword: '{keyword}' (not found)")

def main():
    parser = argparse.ArgumentParser(description='ExpenseTracker Database Administration Tool')
    parser.add_argument('action', choices=[
        'list-vendors', 'list-categories', 'list-rules',
        'add-vendor', 'add-category', 'add-rule',
        'test-vendor', 'delete-vendor'
    ], help='Action to perform')
    
    # Arguments for adding vendors
    parser.add_argument('--keyword', help='Vendor keyword (for add-vendor, delete-vendor)')
    parser.add_argument('--vendor', help='Vendor name (for add-vendor)')
    parser.add_argument('--category', help='Category name (for add-vendor, add-category, add-rule)')
    parser.add_argument('--description', help='Category description (for add-category)')
    
    # Arguments for adding rules
    parser.add_argument('--rule-type', choices=['vendor_exact', 'vendor_contains', 'keyword_contains'],
                        help='Rule type (for add-rule)')
    parser.add_argument('--pattern', help='Pattern to match (for add-rule)')
    parser.add_argument('--priority', type=int, default=1, help='Rule priority (for add-rule)')
    
    # Arguments for testing
    parser.add_argument('--text', help='Text to test (for test-vendor)')
    
    args = parser.parse_args()
    
    # Initialize database
    db = ExpenseDatabase()
    
    # Execute action
    if args.action == 'list-vendors':
        list_vendors(db)
    
    elif args.action == 'list-categories':
        list_categories(db)
    
    elif args.action == 'list-rules':
        list_rules(db)
    
    elif args.action == 'add-vendor':
        if not args.keyword or not args.vendor:
            print("Error: --keyword and --vendor are required for add-vendor")
            return
        add_vendor(db, args.keyword, args.vendor, args.category)
    
    elif args.action == 'add-category':
        if not args.category:
            print("Error: --category is required for add-category")
            return
        add_category(db, args.category, args.description)
    
    elif args.action == 'add-rule':
        if not all([args.rule_type, args.pattern, args.category]):
            print("Error: --rule-type, --pattern, and --category are required for add-rule")
            return
        add_rule(db, args.rule_type, args.pattern, args.category, args.priority)
    
    elif args.action == 'test-vendor':
        if not args.text:
            print("Error: --text is required for test-vendor")
            return
        test_vendor(db, args.text)
    
    elif args.action == 'delete-vendor':
        if not args.keyword:
            print("Error: --keyword is required for delete-vendor")
            return
        delete_vendor(db, args.keyword)

if __name__ == "__main__":
    main()
