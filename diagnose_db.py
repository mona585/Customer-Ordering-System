#!/usr/bin/env python3
"""
AURA Database Diagnostic Script
===============================
This script will:
1. Check if database file exists
2. List ALL tables with their schemas
3. Show row counts
4. Show sample data from each table
5. Verify foreign keys are working
"""

import os
import sqlite3

DB_PATH = 'instance/app.db'

def check_database():
    print("=" * 60)
    print("🔍 AURA DATABASE DIAGNOSTIC")
    print("=" * 60)

    # 1. Check if file exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file '{DB_PATH}' NOT FOUND!")
        print("Run: python -c \"from wsgi import create_app; app=create_app(); app.app_context().push(); from app.extensions import db; db.create_all()\"")
        return False

    print(f"✅ Database file found: {DB_PATH}")
    print(f"   Size: {os.path.getsize(DB_PATH)} bytes")

    # 2. Connect and check tables
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    if not tables:
        print("❌ NO TABLES FOUND in database!")
        conn.close()
        return False

    print(f"📊 Found {len(tables)} tables:")
    print("-" * 60)

    for table in tables:
        table_name = table['name']

        # Get row count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']

        # Get columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = [col['name'] for col in columns]

        print(f"📁 {table_name} ({count} rows)")
        print(f"   Columns: {', '.join(col_names)}")

        # Show sample data (first 3 rows)
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            for i, row in enumerate(rows, 1):
                row_dict = dict(row)
                # Truncate long values
                display = {k: str(v)[:50] for k, v in row_dict.items()}
                print(f"   Row {i}: {display}")

    # 3. Check foreign keys
    print("" + "=" * 60)
    print("🔗 FOREIGN KEY CONSTRAINTS")
    print("=" * 60)

    cursor.execute("PRAGMA foreign_key_list('orders')")
    fk_orders = cursor.fetchall()
    if fk_orders:
        for fk in fk_orders:
            print(f"   orders.{fk['from']} → {fk['table']}.{fk['to']}")

    cursor.execute("PRAGMA foreign_key_list('order_items')")
    fk_items = cursor.fetchall()
    if fk_items:
        for fk in fk_items:
            print(f"   order_items.{fk['from']} → {fk['table']}.{fk['to']}")

    conn.close()

    print("" + "=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    check_database()