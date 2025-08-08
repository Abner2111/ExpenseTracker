"""
Database module for ExpenseTracker
Handles SQLite database operations for vendor keywords and category mappings
"""

import sqlite3
import os
from typing import Dict, List, Tuple, Optional

class ExpenseDatabase:
    def __init__(self, db_path: str = None):
        """Initialize the database connection and create tables if they don't exist"""
        if db_path is None:
            # Default to data/expense_tracker.db relative to the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'data', 'expense_tracker.db')
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create vendor_keywords table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendor_keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL UNIQUE,
                    vendor_name TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create category_rules table for category assignment logic
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS category_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL, -- 'vendor_exact', 'vendor_contains', 'keyword_contains'
                    pattern TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority INTEGER DEFAULT 1, -- Higher priority rules are checked first
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor_keywords_keyword ON vendor_keywords(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_rules_pattern ON category_rules(pattern)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_rules_priority ON category_rules(priority DESC)')
            
            conn.commit()
    
    def add_vendor_keyword(self, keyword: str, vendor_name: str, category: str = None) -> bool:
        """Add a vendor keyword to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO vendor_keywords 
                    (keyword, vendor_name, category, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (keyword.lower(), vendor_name, category))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding vendor keyword: {e}")
            return False
    
    def get_vendor_by_keyword(self, keyword: str) -> Optional[str]:
        """Get vendor name by keyword"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT vendor_name FROM vendor_keywords WHERE keyword = ?', 
                (keyword.lower(),)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def find_vendor_by_text(self, text: str) -> Optional[str]:
        """Find vendor by searching for keywords in text"""
        text_lower = text.lower()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT keyword, vendor_name FROM vendor_keywords ORDER BY LENGTH(keyword) DESC')
            for keyword, vendor_name in cursor.fetchall():
                if keyword in text_lower:
                    return vendor_name
            return None
    
    def add_category(self, name: str, description: str = None) -> bool:
        """Add a category to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO categories (name, description) 
                    VALUES (?, ?)
                ''', (name, description))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding category: {e}")
            return False
    
    def add_category_rule(self, rule_type: str, pattern: str, category: str, priority: int = 1) -> bool:
        """Add a category rule to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO category_rules 
                    (rule_type, pattern, category, priority) 
                    VALUES (?, ?, ?, ?)
                ''', (rule_type, pattern.lower(), category, priority))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding category rule: {e}")
            return False
    
    def categorize_vendor(self, vendor: str) -> str:
        """Categorize a vendor based on rules in the database"""
        vendor_lower = vendor.lower()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get rules ordered by priority (highest first)
            cursor.execute('''
                SELECT rule_type, pattern, category 
                FROM category_rules 
                WHERE active = 1 
                ORDER BY priority DESC
            ''')
            
            for rule_type, pattern, category in cursor.fetchall():
                if rule_type == 'vendor_exact' and vendor_lower == pattern:
                    return category
                elif rule_type == 'vendor_contains' and pattern in vendor_lower:
                    return category
                elif rule_type == 'keyword_contains' and pattern in vendor_lower:
                    return category
        
        return 'Personal'  # Default category
    
    def get_all_vendors(self) -> List[Tuple[str, str]]:
        """Get all vendor keywords and names"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT keyword, vendor_name FROM vendor_keywords')
            return cursor.fetchall()
    
    def get_all_categories(self) -> List[str]:
        """Get all category names"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM categories')
            return [row[0] for row in cursor.fetchall()]
    
    def get_all_category_rules(self) -> List[Tuple[str, str, str, int]]:
        """Get all category rules"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT rule_type, pattern, category, priority FROM category_rules WHERE active = 1 ORDER BY priority DESC')
            return cursor.fetchall()
    
    def delete_vendor_keyword(self, keyword: str) -> bool:
        """Delete a vendor keyword from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM vendor_keywords WHERE keyword = ?', (keyword.lower(),))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting vendor keyword: {e}")
            return False
    
    def update_vendor_keyword(self, keyword: str, vendor_name: str, category: str = None) -> bool:
        """Update a vendor keyword in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE vendor_keywords 
                    SET vendor_name = ?, category = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE keyword = ?
                ''', (vendor_name, category, keyword.lower()))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating vendor keyword: {e}")
            return False
