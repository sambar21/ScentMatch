#!/usr/bin/env python3
"""
Simple ETL Pipeline - Uses your already downloaded dataset
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
import uuid

# Add to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from ..core.database import Base
from ..models.fragrance import Fragrance
from ..core.config import settings

def get_sync_db_url():
   
    async_url = settings.database_url
    if async_url.startswith("postgresql+asyncpg://"):
        return async_url.replace("postgresql+asyncpg://", "postgresql://")
    return async_url

def load_csv_data():
    
    # Path to your downloaded dataset
    csv_path = Path(r"C:\Users\Varun\.cache\kagglehub\datasets\olgagmiufana1\fragrantica-com-fragrance-dataset\versions\3")
    
    # Find CSV files in the directory
    csv_files = list(csv_path.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {csv_path}")
    
    csv_file = csv_files[0]
    print(f"Loading CSV: {csv_file.name}")
    
    # Try different encodings with semicolon delimiter
    for encoding in ['latin1', 'utf-8', 'cp1252']:
        try:
            df = pd.read_csv(
                csv_file, 
                encoding=encoding,
                delimiter=';',           # Use semicolon as delimiter
                quotechar='"',           # Handle quoted fields
                skipinitialspace=True,   # Skip spaces after delimiter
                on_bad_lines='skip',     # Skip malformed lines
                engine='python'          # More flexible parser
            )
            print(f"Successfully loaded with {encoding} encoding")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Show first few rows to understand structure
            print("\nFirst few rows:")
            print(df.head())
            
            return df
        except Exception as e:
            print(f"Failed with {encoding}: {e}")
            continue
    
    raise RuntimeError("Could not read CSV with any encoding")

def parse_notes(notes_string):
    
    if pd.isna(notes_string) or notes_string == '':
        return []
    
    # Split by common delimiters and clean
    notes = str(notes_string).replace(',', ' ').split()
    # Remove empty strings and clean up
    notes = [note.strip() for note in notes if note.strip()]
    return notes

def parse_perfumer(perfumer1, perfumer2):
    
    perfumers = []
    
    if pd.notna(perfumer1) and perfumer1 != 'unknown':
        perfumers.append(str(perfumer1).strip())
    
    if pd.notna(perfumer2) and perfumer2 != 'unknown':
        perfumers.append(str(perfumer2).strip())
    
    return perfumers

def parse_main_accords(*accords):
    
    main_accords = []
    
    for accord in accords:
        if pd.notna(accord) and accord != '':
            main_accords.append(str(accord).strip())
    
    return main_accords

def transform_data(df):
    
    print("Transforming data...")
    
    # Create a copy
    df_clean = df.copy()
    
    # Check what columns we have
    print("Available columns:", list(df_clean.columns))
    
    # Map columns based on the CSV structure you showed
    column_mapping = {
        'url': 'url',
        'Perfume': 'name',
        'Brand': 'brand_name',
        'Country': 'country',
        'Gender': 'gender',
        'Rating Value': 'average_rating',
        'Rating Count': 'total_ratings',
        'Year': 'release_year'
    }
    
    # Apply basic column mapping for existing columns
    for old_col, new_col in column_mapping.items():
        if old_col in df_clean.columns:
            df_clean[new_col] = df_clean[old_col]
    
    # Check for required columns
    if 'url' not in df_clean.columns or 'Perfume' not in df_clean.columns:
        print("Error: Required columns 'url' or 'Perfume' not found")
        return None
    
    # Drop rows with missing essential fields EARLY
    df_clean = df_clean.dropna(subset=['name', 'url'])
    print(f"After removing rows with missing name/url: {len(df_clean)} rows")
    
    # Remove duplicates based on the unique constraints
    print("Removing duplicates...")
    # First remove URL duplicates
    df_clean = df_clean.drop_duplicates(subset=['url'], keep='first')
    print(f"After removing URL duplicates: {len(df_clean)} rows")
    
    # Then remove name+brand duplicates  
    df_clean = df_clean.drop_duplicates(subset=['name', 'brand_name'], keep='first')
    print(f"After removing name+brand duplicates: {len(df_clean)} rows")
    
    # Handle rating conversion
    if 'average_rating' in df_clean.columns:
        print(f"Before conversion - sample ratings: {df_clean['average_rating'].head().tolist()}")
        print(f"Rating data type: {df_clean['average_rating'].dtype}")
        
        # Handle European decimal format (comma to dot)
        if df_clean['average_rating'].dtype == 'object':
            df_clean['average_rating'] = df_clean['average_rating'].astype(str).str.replace(',', '.')
        
        # Convert to numeric
        df_clean['average_rating'] = pd.to_numeric(df_clean['average_rating'], errors='coerce')
        
        print(f"After conversion - sample ratings: {df_clean['average_rating'].head().tolist()}")
        print(f"Rating range: {df_clean['average_rating'].min()} to {df_clean['average_rating'].max()}")
        
        # Fill NaN values with 0
        df_clean['average_rating'] = df_clean['average_rating'].fillna(0.0)
        
        # No normalization needed - ratings are already on 1-5 scale
        print(f"Final ratings - sample: {df_clean['average_rating'].head().tolist()}")
    else:
        df_clean['average_rating'] = 0.0
    
    # Handle total_ratings
    if 'total_ratings' in df_clean.columns:
        df_clean['total_ratings'] = pd.to_numeric(df_clean['total_ratings'], errors='coerce')
        df_clean['total_ratings'] = df_clean['total_ratings'].fillna(0)
    else:
        df_clean['total_ratings'] = 0
    
    # Handle release year
    if 'release_year' in df_clean.columns:
        df_clean['release_year'] = pd.to_numeric(df_clean['release_year'], errors='coerce')
        # Set unrealistic years to None
        df_clean.loc[(df_clean['release_year'] < 1800) | (df_clean['release_year'] > 2030), 'release_year'] = None
    
    # Parse notes
    if 'Top' in df_clean.columns:
        df_clean['top_notes'] = df_clean['Top'].apply(parse_notes)
    else:
        df_clean['top_notes'] = [[] for _ in range(len(df_clean))]
    
    if 'Middle' in df_clean.columns:
        df_clean['middle_notes'] = df_clean['Middle'].apply(parse_notes)
    else:
        df_clean['middle_notes'] = [[] for _ in range(len(df_clean))]
    
    if 'Base' in df_clean.columns:
        df_clean['base_notes'] = df_clean['Base'].apply(parse_notes)
    else:
        df_clean['base_notes'] = [[] for _ in range(len(df_clean))]
    
    # Parse perfumers
    if 'Perfumer1' in df_clean.columns and 'Perfumer2' in df_clean.columns:
        df_clean['perfumer'] = df_clean.apply(lambda row: parse_perfumer(row['Perfumer1'], row['Perfumer2']), axis=1)
    else:
        df_clean['perfumer'] = [[] for _ in range(len(df_clean))]
    
    # Parse main accords
    accord_columns = ['mainaccord1', 'mainaccord2', 'mainaccord3', 'mainaccord4', 'mainaccord5']
    available_accords = [col for col in accord_columns if col in df_clean.columns]
    
    if available_accords:
        df_clean['main_accords'] = df_clean[available_accords].apply(lambda row: parse_main_accords(*row), axis=1)
    else:
        df_clean['main_accords'] = [[] for _ in range(len(df_clean))]
    
    # Add missing columns with defaults
    if 'brand_name' not in df_clean.columns:
        df_clean['brand_name'] = 'Unknown'
    else:
        # Clean brand_name
        df_clean['brand_name'] = df_clean['brand_name'].fillna('Unknown')
    
    if 'gender' not in df_clean.columns:
        df_clean['gender'] = 'unisex'
    else:
        # Clean gender values
        df_clean['gender'] = df_clean['gender'].str.lower().fillna('unisex')
        # Map common variations
        gender_mapping = {
            'women': 'female',
            'men': 'male',
            'for women': 'female',
            'for men': 'male'
        }
        df_clean['gender'] = df_clean['gender'].replace(gender_mapping)
    
    # Add missing optional fields with defaults
    optional_fields = {
        'concentration': None,
        'longevity_rating': None,
        'sillage_rating': None,
        'description': None,
        'image_url': None,
        'brand_id': None
    }
    
    for field, default_value in optional_fields.items():
        if field not in df_clean.columns:
            df_clean[field] = default_value
    
    # Add timestamps, IDs, and discontinued status
    df_clean['created_at'] = datetime.now()
    df_clean['updated_at'] = datetime.now()
    df_clean['id'] = [str(uuid.uuid4()) for _ in range(len(df_clean))]
    df_clean['discontinued'] = False  # Add discontinued column with default False
    
    # Select final columns matching the database schema
    final_columns = ['id', 'name', 'brand_name', 'brand_id', 'release_year', 'gender', 
                     'concentration', 'perfumer', 'top_notes', 'middle_notes', 'base_notes', 
                     'main_accords', 'average_rating', 'total_ratings', 'longevity_rating', 
                     'sillage_rating', 'description', 'image_url', 'discontinued', 
                     'created_at', 'updated_at', 'url']
    
    df_final = df_clean[final_columns].copy()
    
    print(f"Final dataset shape: {df_final.shape}")
    print(f"Sample transformed data:")
    print(df_final[['name', 'brand_name', 'url']].head())
    
    return df_final

def load_to_database(df):
    """Load data to your database"""
    print("Loading to database...")
    
    engine = create_engine(get_sync_db_url())
    SessionLocal = sessionmaker(bind=engine)
    
    session = SessionLocal()
    try:
        # Convert to records
        records = df.to_dict('records')
        
        # Process in batches
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Clean records to match database schema exactly
            for record in batch:
                # Ensure arrays are not None
                for array_field in ['perfumer', 'top_notes', 'middle_notes', 'base_notes', 'main_accords']:
                    if record[array_field] is None:
                        record[array_field] = []
                
                # Convert numeric fields and handle NaN values
                for field in ['average_rating', 'total_ratings', 'release_year', 'longevity_rating', 'sillage_rating']:
                    if field in record:
                        if pd.isna(record[field]) or record[field] is None:
                            if field in ['longevity_rating', 'sillage_rating', 'release_year']:
                                record[field] = None  # These can be NULL
                            else:
                                record[field] = 0  # These have defaults
                        elif isinstance(record[field], (np.integer, np.floating)):
                            record[field] = record[field].item()
                
                # Ensure boolean fields are proper booleans
                record['discontinued'] = bool(record.get('discontinued', False))
                
                # Ensure string fields are not None where they shouldn't be
                if record.get('name') is None:
                    continue  # Skip records with no name
                
                # Clean brand_name
                if record.get('brand_name') is None or pd.isna(record.get('brand_name')):
                    record['brand_name'] = 'Unknown'
                
                # Clean gender
                if record.get('gender') is None or pd.isna(record.get('gender')):
                    record['gender'] = 'unisex'
            
            try:
                # Filter out any records with missing required fields before insertion
                valid_batch = []
                for record in batch:
                    if record.get('name') and record.get('url'):
                        valid_batch.append(record)
                    else:
                        print(f"Skipping record with missing required fields: name={record.get('name')}, url={record.get('url')}")
                
                if not valid_batch:
                    print(f"No valid records in batch {i//batch_size + 1}")
                    continue
                
                # Use upsert with proper conflict resolution on URL
                stmt = insert(Fragrance).values(valid_batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['url'],
                    set_={
                        'name': stmt.excluded.name,
                        'brand_name': stmt.excluded.brand_name,
                        'gender': stmt.excluded.gender,
                        'release_year': stmt.excluded.release_year,
                        'concentration': stmt.excluded.concentration,
                        'perfumer': stmt.excluded.perfumer,
                        'top_notes': stmt.excluded.top_notes,
                        'middle_notes': stmt.excluded.middle_notes,
                        'base_notes': stmt.excluded.base_notes,
                        'main_accords': stmt.excluded.main_accords,
                        'average_rating': stmt.excluded.average_rating,
                        'total_ratings': stmt.excluded.total_ratings,
                        'longevity_rating': stmt.excluded.longevity_rating,
                        'sillage_rating': stmt.excluded.sillage_rating,
                        'description': stmt.excluded.description,
                        'image_url': stmt.excluded.image_url,
                        'discontinued': stmt.excluded.discontinued,
                        'updated_at': datetime.now()
                    }
                )
                
                session.execute(stmt)
                session.commit()
                total_inserted += len(valid_batch)
                print(f"Inserted batch {i//batch_size + 1}, valid records: {len(valid_batch)}, total: {total_inserted}")
                
            except Exception as batch_error:
                session.rollback()
                print(f"Batch {i//batch_size + 1} error: {batch_error}")
                
                # Try to identify the problematic record
                if len(batch) == 1:
                    print(f"Problematic record: {batch[0]}")
                else:
                    print(f"Batch size: {len(batch)}, trying individual inserts...")
                    # Try inserting records individually to identify the problem
                    for j, record in enumerate(batch):
                        try:
                            if record.get('name') and record.get('url'):
                                individual_stmt = insert(Fragrance).values([record])
                                individual_stmt = individual_stmt.on_conflict_do_nothing()
                                session.execute(individual_stmt)
                                session.commit()
                                total_inserted += 1
                                print(f"  Individual record {j} inserted successfully")
                        except Exception as individual_error:
                            session.rollback()
                            # Skip constraint violations during individual processing
                            if "duplicate key value violates unique constraint" in str(individual_error):
                                print(f"  Record {j} skipped - duplicate: {record.get('name', 'Unknown')} by {record.get('brand_name', 'Unknown')}")
                            else:
                                print(f"  Individual record {j} failed: {individual_error}")
                                print(f"  Record data: {record}")
                continue
        
        print(f"Successfully loaded {total_inserted} records!")
        
    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        session.close()

def main():
    """Run the ETL pipeline"""
    try:
        print("Starting ETL Pipeline...")
        
        # Extract
        df = load_csv_data()
        
        # Transform
        df_transformed = transform_data(df)
        if df_transformed is None:
            return
        
        # Load
        load_to_database(df_transformed)
        
        print("Pipeline completed successfully!")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()