#!/usr/bin/env python3
"""
Quick script to check if fragrances table exists and show its structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect

def get_db_url():
    """Get database URL from environment"""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    hostname = os.getenv("DATABASE_HOSTNAME")
    port = os.getenv("DATABASE_PORT")
    password = os.getenv("DATABASE_PASSWORD")
    name = os.getenv("DATABASE_NAME")
    username = os.getenv("DATABASE_USERNAME")
    
    return f"postgresql://{username}:{password}@{hostname}:{port}/{name}"

def check_table_exists():
    
    
    engine = create_engine(get_db_url())
    inspector = inspect(engine)
    
    # Check if table exists
    tables = inspector.get_table_names()
    
    print(f" Database contains {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    if 'fragrances' in tables:
        print("\n fragrances table EXISTS!")
        
        # Get table structure
        columns = inspector.get_columns('fragrances')
        print(f"\n fragrances table has {len(columns)} columns:")
        
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  - {col['name']}: {col['type']} ({nullable})")
        
        # Get indexes
        indexes = inspector.get_indexes('fragrances')
        print(f"\n fragrances table has {len(indexes)} indexes:")
        for idx in indexes:
            unique = "UNIQUE" if idx['unique'] else ""
            print(f"  - {idx['name']}: {idx['column_names']} {unique}")
        
        # Count rows
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM fragrances"))
            row_count = result.scalar()
            print(f"\n fragrances table contains {row_count} rows")
    
    else:
        print("\n fragrances table does NOT exist")
        print("   Ready to create it with alembic migration!")

if __name__ == "__main__":
    check_table_exists()