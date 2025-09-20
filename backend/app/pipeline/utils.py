#!/usr/bin/env python3
"""
Quick script to check database table contents
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add to Python path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent))
sys.path.append(str(current_dir.parent.parent))

try:
    from app.core.config import settings
except ImportError:
    # Fallback if import fails
    class Settings:
        database_url = "postgresql+asyncpg://postgres:DctOdYOceFkbZTBNJKxtLfZeqKwzTOFS@ballast.proxy.rlwy.net:18095/railway"
    settings = Settings()

def get_sync_db_url():
    
    async_url = settings.database_url
    if async_url.startswith("postgresql+asyncpg://"):
        return async_url.replace("postgresql+asyncpg://", "postgresql://")
    return async_url

def check_database():
    
    print("Connecting to Railway database...")
    
    engine = create_engine(get_sync_db_url())
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Check total count
        result = session.execute(text("SELECT COUNT(*) FROM fragrances"))
        total_count = result.scalar()
        print(f"Total fragrances: {total_count}")
        
        # Check rating statistics
        result = session.execute(text("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN average_rating > 0 THEN 1 END) as records_with_rating,
                MIN(average_rating) as min_rating,
                MAX(average_rating) as max_rating,
                AVG(average_rating) as avg_rating,
                COUNT(CASE WHEN average_rating = 0 THEN 1 END) as zero_ratings
            FROM fragrances
        """))
        
        stats = result.fetchone()
        print("\n--- Rating Statistics ---")
        print(f"Total records: {stats[0]}")
        print(f"Records with rating > 0: {stats[1]}")
        print(f"Records with zero rating: {stats[5]}")
        print(f"Min rating: {stats[2]}")
        print(f"Max rating: {stats[3]}")
        print(f"Average rating: {stats[4]:.2f}")
        
        # Check brand distribution
        result = session.execute(text("""
            SELECT brand_name, COUNT(*) as count 
            FROM fragrances 
            WHERE brand_name IS NOT NULL 
            GROUP BY brand_name 
            ORDER BY count DESC 
            LIMIT 10
        """))
        
        brands = result.fetchall()
        print("\n--- Top 10 Brands ---")
        for brand, count in brands:
            print(f"{brand}: {count} fragrances")
        
        # Check some sample records
        result = session.execute(text("""
            SELECT name, brand_name, average_rating, total_ratings, gender
            FROM fragrances 
            WHERE average_rating > 0
            ORDER BY average_rating DESC
            LIMIT 5
        """))
        
        samples = result.fetchall()
        print("\n--- Top 5 Highest Rated Fragrances ---")
        for name, brand, rating, total, gender in samples:
            print(f"{name} by {brand} - Rating: {rating} ({total} reviews) - {gender}")
        
        # Check for any recent inserts
        result = session.execute(text("""
            SELECT COUNT(*) as recent_count
            FROM fragrances 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """))
        
        recent_count = result.scalar()
        print(f"\n--- Recent Activity ---")
        print(f"Records created in last hour: {recent_count}")
        
        # Check array fields
        result = session.execute(text("""
            SELECT 
                COUNT(CASE WHEN perfumer IS NOT NULL AND array_length(perfumer, 1) > 0 THEN 1 END) as has_perfumer,
                COUNT(CASE WHEN top_notes IS NOT NULL AND array_length(top_notes, 1) > 0 THEN 1 END) as has_top_notes,
                COUNT(CASE WHEN main_accords IS NOT NULL AND array_length(main_accords, 1) > 0 THEN 1 END) as has_accords
            FROM fragrances
        """))
        
        arrays = result.fetchone()
        print("\n--- Array Field Statistics ---")
        print(f"Records with perfumer info: {arrays[0]}")
        print(f"Records with top notes: {arrays[1]}")
        print(f"Records with main accords: {arrays[2]}")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_database()