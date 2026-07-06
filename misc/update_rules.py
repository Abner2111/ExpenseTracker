import sqlite3, os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'expense_tracker.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# --- vendor_keywords upsert ---
keywords = [
    ('maxipali',               'Maxipali',               'Groceries'),
    ('maxipali agua caliente', 'Maxipali Agua Caliente',  'Groceries'),
    ('coconut bar restaurant', 'Coconut Bar Restaurant',  'Dining Out'),
    ('da jia le supermercado', 'Da Jia Le Supermercado',  'Groceries'),
    ('la pincheta',            'La Pincheta',             'Dining Out'),
    ('dtf costa rica',         'DTF Costa Rica Socieda',  'Personal'),
    ('parqu muni',             'Parqueo Municipal',       'Transportation'),
    ('tropica by el grill',    'Tropica by El Grill',     'Dining Out'),
    ('el grill',               'El Grill',                'Dining Out'),
    ('servicentro',            'Servicentro La Tica',     'Transportation'),
    ('google cloud',           'Google Cloud',            'Personal'),
    ('seguro prf',             'Seguro PRF Plan A',       'Personal'),
    ('pequeno mundo',          'Pequeno Mundo',           'Personal'),
]
for kw, vendor, cat in keywords:
    cur.execute(
        'INSERT OR REPLACE INTO vendor_keywords (keyword, vendor_name, category, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
        (kw, vendor, cat)
    )

# Fix delimart afz (already in keywords but missing category)
cur.execute("UPDATE vendor_keywords SET category='Groceries', updated_at=CURRENT_TIMESTAMP WHERE keyword='delimart afz'")

# --- category_rules: insert if not already present ---
rules = [
    ('vendor_contains',  'maxipali',            'Groceries',      62),
    ('vendor_contains',  'coconut bar',         'Dining Out',     72),
    ('keyword_contains', 'restaurant',          'Dining Out',     68),
    ('vendor_contains',  'da jia le',           'Groceries',      62),
    ('keyword_contains', 'supermercado',        'Groceries',      58),
    ('vendor_contains',  'la pincheta',         'Dining Out',     72),
    ('vendor_contains',  'dtf costa rica',      'Personal',       82),
    ('vendor_contains',  'parqu muni',          'Transportation', 92),
    ('vendor_contains',  'tropica by el grill', 'Dining Out',     72),
    ('vendor_contains',  'el grill',            'Dining Out',     70),
    ('vendor_contains',  'delimart',            'Groceries',      62),
    ('vendor_contains',  'servicentro',         'Transportation', 57),
    ('vendor_contains',  'google cloud',        'Personal',       87),
    ('keyword_contains', 'seguro',              'Personal',       22),
    ('vendor_contains',  'pequeno mundo',       'Personal',       62),
]

added, skipped = 0, 0
for rule_type, pattern, category, priority in rules:
    cur.execute('SELECT COUNT(*) FROM category_rules WHERE rule_type=? AND pattern=?', (rule_type, pattern))
    if cur.fetchone()[0] == 0:
        cur.execute(
            'INSERT INTO category_rules (rule_type, pattern, category, priority) VALUES (?, ?, ?, ?)',
            (rule_type, pattern, category, priority)
        )
        print(f"  + {rule_type:<20} '{pattern}' -> {category}")
        added += 1
    else:
        print(f"  ~ skip (exists)       '{pattern}'")
        skipped += 1

conn.commit()
conn.close()
print(f"\nDone: {added} rules added, {skipped} skipped.")
