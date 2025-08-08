#!/usr/bin/env python3
"""
Migration script to populate the SQLite database with existing vendor keywords and category rules
from the hardcoded dictionaries in main.py
"""

import os
import sys

# Add src directory to path (go up one level from misc/ to project root, then to src/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

from database import ExpenseDatabase

def migrate_vendor_keywords():
    """Migrate vendor keywords from hardcoded dictionary to database"""
    
    # Initialize database
    db = ExpenseDatabase()
    
    # Vendor keywords from main.py (converted to lowercase keys)
    vendor_keywords = {
        # Fast Food Chains
        'kfc': 'KFC', 'kfc express': 'KFC Express', 'mcdonalds': 'McDonalds CR',
        'burger king': 'Burger King CR', 'pizza hut': 'Pizza Hut CR', 'dominos pizza': 'Dominos Pizza CR',
        'subway': 'Subway CR', 'taco bell': 'Taco Bell CR',
        
        # Supermarkets
        'automercado': 'Automercado', 'mas x menos': 'Mas x Menos', 'maxi pali': 'Maxi Pali',
        'pali': 'Pali', 'pricesmart': 'PriceSmart', 'mega super': 'Mega Super',
        'super compro': 'Super Compro', 'perimercados': 'Perimercados',
        'walmart': 'Walmart Costa Rica', 'pequeño mundo': 'Pequeño Mundo',
        'vindi': 'Vindi (Convenience)', 'am pm': 'AM PM (Convenience)', 'fresh market': 'Fresh Market (Convenience)',

        # Ride-sharing / Transportation
        'uber': 'Uber', 'didi': 'DiDi (Transportation)', 'indriver': 'inDrive (Transportation)',
        'ticoride': 'TicoRide', 'interbus': 'Interbus (Shuttle)', 'ride cr': 'RIDE CR (Transportation)',
        'transportes': 'Transportation (General)', 'shuttle': 'Shuttle Service',
        'dlc* uber rides': 'Uber Rides',

        # Food Delivery & Dining
        'uber eats': 'Uber Eats', 'dlc* uber eats': 'Uber Eats',
        'fiesta express': 'Fiesta Express Delivery',
        'rappi': 'Rappi (Delivery)', 'glovo': 'Glovo (Delivery)',
        'comidas el shaddai': 'Comidas El Shaddai',
        'coral ibm': 'Coral IBM',

        # Snacks / Convenience
        'pronto snack': 'Pronto Snack',
        'delimart afz': 'Delimart AFZ',

        # Cafes/Restaurants (examples)
        'cafe britt': 'Café Britt', 'café britt': 'Café Britt', 'cafe del barista': 'Café del Barista', 'cafeoteca': 'Cafeoteca',
        'soda': 'Soda (Local Restaurant)', 'pollo rostizado': 'Pollo Rostizado (Food)',

        # Banks
        'banco nacional': 'Banco Nacional', 'banco de costa rica': 'Banco de Costa Rica (BCR)',
        'banco popular': 'Banco Popular', 'bac credomatic': 'BAC Credomatic',
        'scotiabank': 'Scotiabank CR', 'banco lafise': 'Banco Lafise', 'banco bct': 'Banco BCT',
        'banco improsa': 'Banco Improsa',

        # Utilities / Services
        'ice electricidad': 'ICE (Electricity/Telecom)', 'aya agua': 'AyA (Water)', 'kolbi': 'Kolbi (Telecom)',
        'claro': 'Claro (Telecom)', 'movistar': 'Movistar (Telecom)', 'cnfl': 'CNFL (Electricity)',
        'jasec': 'Jasec (Electricity/Water)', 'coopeguanacaste': 'CoopeGuanacaste (Electricity)',

        # Retail / Other common stores
        'el gallo mas gallo': 'El Gallo Mas Gallo (Electronics/Home)',
        'tienda el rey': 'Tienda El Rey (Variety Store)',
        'ferreteria': 'Hardware Store', 'farmacia': 'Pharmacy', 'gasolinera': 'Gas Station',
        'gas station': 'Gas Station', 'mascotas': 'Pet Store', 'cemaco': 'Cemaco (Home Goods)',
        'universal': 'Universal (Department Store/Books)', 'libreria': 'Bookstore',
        'correos de costa rica': 'Correos de Costa Rica (Post Office)',
        'siman': 'Siman (Department Store)', 'multiplaza': 'Multiplaza (Mall)', 'city mall': 'City Mall (Mall)',

        # General
        'hotel': 'Hotel', 'restaurante': 'Restaurant', 'tour': 'Tour/Activity',
        'parque nacional': 'National Park', 'entrada': 'Entrance Fee',
        'peaje': 'Toll', 'tax': 'Tax', 'impuesto': 'Tax',
        'servicio': 'Service Fee', 'alquiler': 'Rental', 'rent a car': 'Car Rental',
        'lavanderia': 'Laundry', 'clinica': 'Clinic/Medical'
    }
    
    print("Migrating vendor keywords...")
    for keyword, vendor_name in vendor_keywords.items():
        success = db.add_vendor_keyword(keyword, vendor_name)
        if success:
            print(f"✓ Added vendor keyword: '{keyword}' -> '{vendor_name}'")
        else:
            print(f"✗ Failed to add vendor keyword: '{keyword}'")
    
    return len(vendor_keywords)

def migrate_categories():
    """Migrate categories to database"""
    
    db = ExpenseDatabase()
    
    categories = [
        ('Dining Out', 'Restaurants, fast food, food delivery'),
        ('Groceries', 'Supermarkets, grocery stores, convenience stores'),
        ('Transportation', 'Ride-sharing, public transport, parking, fuel'),
        ('Health/medical', 'Pharmacies, clinics, medical services'),
        ('Home', 'Hardware stores, home goods, furniture'),
        ('Utilities', 'Electricity, water, telecom, internet'),
        ('Debt', 'Bank fees, loan payments, credit card payments'),
        ('Travel', 'Hotels, tours, car rentals, travel activities'),
        ('Car maintenance', 'Gas stations, mechanic, tires, car repairs'),
        ('Personal', 'Coffee, personal care, general purchases'),
        ('Pets', 'Pet stores, veterinary, pet supplies'),
        ('Streaming', 'Netflix, Spotify, entertainment subscriptions'),
        ('Education', 'Schools, books, courses, educational materials'),
        ('Gifts', 'Gift purchases, flowers, jewelry')
    ]
    
    print("\nMigrating categories...")
    for name, description in categories:
        success = db.add_category(name, description)
        if success:
            print(f"✓ Added category: '{name}'")
        else:
            print(f"✗ Failed to add category: '{name}'")
    
    return len(categories)

def migrate_category_rules():
    """Migrate category assignment rules to database"""
    
    db = ExpenseDatabase()
    
    # Define category rules based on the logic from main.py
    # Higher priority numbers are checked first
    category_rules = [
        # Transportation rules (high priority for specific payment methods)
        ('keyword_contains', 'sinpe-tp', 'Transportation', 100),
        ('vendor_contains', 'dlc* uber rides', 'Transportation', 95),
        ('vendor_contains', 'uber rides', 'Transportation', 95),
        ('keyword_contains', 'parquimetro', 'Transportation', 90),
        ('keyword_contains', 'parquímetro', 'Transportation', 90),
        ('keyword_contains', 'parqueo', 'Transportation', 90),
        ('keyword_contains', 'parking', 'Transportation', 90),
        
        # Streaming services (high priority)
        ('vendor_contains', 'netflix', 'Streaming', 85),
        ('vendor_contains', 'spotify', 'Streaming', 85),
        ('vendor_contains', 'amazon prime', 'Streaming', 85),
        ('vendor_contains', 'disney', 'Streaming', 85),
        ('keyword_contains', 'streaming', 'Streaming', 85),
        ('vendor_contains', 'google wm max llc', 'Streaming', 85),
        
        # Fast Food vendors (exact matches)
        ('vendor_exact', 'kfc', 'Dining Out', 80),
        ('vendor_exact', 'kfc express', 'Dining Out', 80),
        ('vendor_exact', 'mcdonalds cr', 'Dining Out', 80),
        ('vendor_exact', 'burger king cr', 'Dining Out', 80),
        ('vendor_exact', 'pizza hut cr', 'Dining Out', 80),
        ('vendor_exact', 'dominos pizza cr', 'Dining Out', 80),
        ('vendor_exact', 'subway cr', 'Dining Out', 80),
        ('vendor_exact', 'taco bell cr', 'Dining Out', 80),
        
        # Food delivery services
        ('vendor_contains', 'dlc* uber eats', 'Dining Out', 75),
        ('vendor_contains', 'uber eats', 'Dining Out', 75),
        ('vendor_exact', 'rappi (delivery)', 'Dining Out', 75),
        ('vendor_exact', 'glovo (delivery)', 'Dining Out', 75),
        ('vendor_exact', 'fiesta express delivery', 'Dining Out', 75),
        
        # Dining vendors
        ('vendor_contains', 'subway', 'Dining Out', 70),
        ('vendor_contains', 'comidas el shaddai', 'Dining Out', 70),
        ('vendor_contains', 'coral ibm', 'Dining Out', 70),
        ('vendor_contains', 'pronto snack', 'Dining Out', 70),
        ('keyword_contains', 'restaurante', 'Dining Out', 70),
        ('keyword_contains', 'soda', 'Dining Out', 70),
        
        # Grocery stores (exact matches)
        ('vendor_exact', 'automercado', 'Groceries', 65),
        ('vendor_exact', 'mas x menos', 'Groceries', 65),
        ('vendor_exact', 'maxi pali', 'Groceries', 65),
        ('vendor_exact', 'pali', 'Groceries', 65),
        ('vendor_exact', 'pricesmart', 'Groceries', 65),
        ('vendor_exact', 'walmart costa rica', 'Groceries', 65),
        ('vendor_exact', 'pequeño mundo', 'Groceries', 65),
        ('vendor_exact', 'mega super', 'Groceries', 65),
        ('vendor_exact', 'super compro', 'Groceries', 65),
        ('vendor_exact', 'perimercados', 'Groceries', 65),
        
        # Grocery stores (contains)
        ('vendor_contains', 'auto mercado', 'Groceries', 60),
        ('vendor_contains', 'automercado', 'Groceries', 60),
        ('vendor_contains', 'mas x menos', 'Groceries', 60),
        ('vendor_contains', 'maxi pali', 'Groceries', 60),
        ('vendor_contains', 'pricesmart', 'Groceries', 60),
        ('vendor_contains', 'walmart', 'Groceries', 60),
        ('vendor_contains', 'pequeño mundo', 'Groceries', 60),
        ('vendor_contains', 'mega super', 'Groceries', 60),
        ('vendor_contains', 'super compro', 'Groceries', 60),
        ('vendor_contains', 'perimercados', 'Groceries', 60),
        ('vendor_contains', 'musi', 'Groceries', 60),
        
        # Transportation vendors
        ('vendor_exact', 'uber', 'Transportation', 55),
        ('vendor_exact', 'didi (transportation)', 'Transportation', 55),
        ('vendor_exact', 'indrive (transportation)', 'Transportation', 55),
        ('vendor_exact', 'ticoride', 'Transportation', 55),
        ('vendor_exact', 'interbus (shuttle)', 'Transportation', 55),
        ('vendor_exact', 'ride cr (transportation)', 'Transportation', 55),
        
        # Health/medical
        ('keyword_contains', 'farmacia', 'Health/medical', 50),
        ('keyword_contains', 'medicamentos', 'Health/medical', 50),
        ('keyword_contains', 'clinica', 'Health/medical', 50),
        ('keyword_contains', 'hospital', 'Health/medical', 50),
        ('keyword_contains', 'medico', 'Health/medical', 50),
        ('keyword_contains', 'doctor', 'Health/medical', 50),
        
        # Home/retail
        ('keyword_contains', 'ferreteria', 'Home', 45),
        ('vendor_contains', 'cemaco', 'Home', 45),
        ('vendor_contains', 'el gallo mas gallo', 'Home', 45),
        
        # Utilities
        ('vendor_contains', 'ice electricidad', 'Utilities', 40),
        ('vendor_contains', 'ice', 'Utilities', 40),
        ('vendor_contains', 'kolbi', 'Utilities', 40),
        ('vendor_contains', 'claro', 'Utilities', 40),
        ('vendor_contains', 'movistar', 'Utilities', 40),
        ('vendor_contains', 'aya agua', 'Utilities', 40),
        ('vendor_contains', 'cnfl', 'Utilities', 40),
        
        # Banks (Debt category)
        ('vendor_exact', 'bac credomatic', 'Debt', 35),
        ('vendor_exact', 'banco nacional', 'Debt', 35),
        ('vendor_exact', 'banco de costa rica (bcr)', 'Debt', 35),
        ('vendor_exact', 'banco popular', 'Debt', 35),
        ('vendor_exact', 'scotiabank cr', 'Debt', 35),
        ('vendor_exact', 'banco lafise', 'Debt', 35),
        ('vendor_exact', 'banco bct', 'Debt', 35),
        ('vendor_exact', 'banco improsa', 'Debt', 35),
        
        # Travel
        ('keyword_contains', 'hotel', 'Travel', 30),
        ('keyword_contains', 'alojamiento', 'Travel', 30),
        ('keyword_contains', 'tour', 'Travel', 30),
        ('keyword_contains', 'actividad', 'Travel', 30),
        ('keyword_contains', 'aventura', 'Travel', 30),
        ('keyword_contains', 'rent a car', 'Travel', 30),
        ('keyword_contains', 'alquiler de vehiculos', 'Travel', 30),
        
        # Car maintenance
        ('keyword_contains', 'gasolinera', 'Car maintenance', 25),
        ('keyword_contains', 'gas station', 'Car maintenance', 25),
        ('keyword_contains', 'combustible', 'Car maintenance', 25),
        ('keyword_contains', 'taller', 'Car maintenance', 25),
        ('keyword_contains', 'mecanico', 'Car maintenance', 25),
        ('keyword_contains', 'neumaticos', 'Car maintenance', 25),
        
        # Personal (coffee, personal care)
        ('vendor_contains', 'cafe', 'Personal', 20),
        ('vendor_contains', 'café', 'Personal', 20),
        ('keyword_contains', 'peluqueria', 'Personal', 20),
        ('keyword_contains', 'salon', 'Personal', 20),
        ('keyword_contains', 'barberia', 'Personal', 20),
        
        # Pets
        ('keyword_contains', 'mascotas', 'Pets', 15),
        ('keyword_contains', 'veterinaria', 'Pets', 15),
        ('keyword_contains', 'pet', 'Pets', 15),
        ('keyword_contains', 'animal', 'Pets', 15),
        
        # Education
        ('keyword_contains', 'universidad', 'Education', 10),
        ('keyword_contains', 'colegio', 'Education', 10),
        ('keyword_contains', 'escuela', 'Education', 10),
        ('keyword_contains', 'curso', 'Education', 10),
        ('keyword_contains', 'libro', 'Education', 10),
        ('keyword_contains', 'libreria', 'Education', 10),
        
        # Gifts
        ('keyword_contains', 'regalo', 'Gifts', 5),
        ('keyword_contains', 'gift', 'Gifts', 5),
        ('keyword_contains', 'flores', 'Gifts', 5),
        ('keyword_contains', 'floreria', 'Gifts', 5),
        ('keyword_contains', 'joyeria', 'Gifts', 5),
    ]
    
    print("\nMigrating category rules...")
    for rule_type, pattern, category, priority in category_rules:
        success = db.add_category_rule(rule_type, pattern, category, priority)
        if success:
            print(f"✓ Added rule: {rule_type} '{pattern}' -> '{category}' (priority: {priority})")
        else:
            print(f"✗ Failed to add rule: {rule_type} '{pattern}' -> '{category}'")
    
    return len(category_rules)

def main():
    """Run the migration"""
    print("Starting database migration...")
    print("=" * 50)
    
    # Run migrations
    vendor_count = migrate_vendor_keywords()
    category_count = migrate_categories()
    rule_count = migrate_category_rules()
    
    print("=" * 50)
    print("Migration completed!")
    print(f"- Migrated {vendor_count} vendor keywords")
    print(f"- Migrated {category_count} categories")
    print(f"- Migrated {rule_count} category rules")
    print("\nDatabase is ready for use!")

if __name__ == "__main__":
    main()
