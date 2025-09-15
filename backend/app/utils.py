"""
Fragrance API Integration for Railway Database Population
Using Fragella API - Real fragrance data only
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import aiohttp
import requests
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Fragrance(Base):
    __tablename__ = "fragrances"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand_name = Column(String)
    top_notes = Column(Text)  # JSON string
    middle_notes = Column(Text)  # JSON string
    base_notes = Column(Text)  # JSON string
    gender = Column(String)
    release_year = Column(Integer)
    perfumer = Column(String)
    description = Column(Text)
    image_url = Column(String)
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    price = Column(Float)
    api_source = Column(String)
    external_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


@dataclass
class FragranceData:
    """Standardized fragrance data structure"""
    name: str
    brand_name: str
    top_notes: List[str] = None
    middle_notes: List[str] = None
    base_notes: List[str] = None
    gender: str = None
    release_year: int = None
    perfumer: str = None
    description: str = None
    image_url: str = None
    average_rating: float = 0.0
    total_ratings: int = 0
    price: float = None
    api_source: str = None
    external_id: str = None
    
    def __post_init__(self):
        for notes_field in ['top_notes', 'middle_notes', 'base_notes']:
            value = getattr(self, notes_field)
            if value is None:
                setattr(self, notes_field, [])
            elif isinstance(value, str):
                setattr(self, notes_field, [value])


class RapidAPIClient:
    """Base client for RapidAPI services"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.rate_limit_delay = 1.5  # Conservative rate limiting
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'ScentMatch-App/1.0'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self, host: str) -> Dict[str, str]:
        return {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': host,
            'Accept': 'application/json',
            'User-Agent': 'ScentMatch-App/1.0'
        }
    
    async def _make_request(self, url: str, host: str, params: Dict = None, method: str = 'GET') -> Optional[Dict]:
        try:
            await asyncio.sleep(self.rate_limit_delay)
            headers = self._get_headers(host)
            
            logger.info(f"Making {method} request to: {url}")
            if params:
                logger.debug(f"Params: {params}")
            
            if method.upper() == 'GET':
                async with self.session.get(url, headers=headers, params=params) as response:
                    return await self._handle_response(response, url)
            elif method.upper() == 'POST':
                async with self.session.post(url, headers=headers, json=params) as response:
                    return await self._handle_response(response, url)
                    
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    async def _handle_response(self, response, url: str) -> Optional[Dict]:
        logger.info(f"Response status: {response.status} for {url}")
        
        if response.status == 200:
            try:
                data = await response.json()
                logger.info(f"✅ Request successful - got data")
                return data
            except Exception as e:
                logger.error(f"Failed to parse JSON: {e}")
                text = await response.text()
                logger.debug(f"Response text: {text[:500]}")
                return None
        elif response.status == 403:
            logger.error("❌ 403 Forbidden - Check API subscription and key")
            return None
        elif response.status == 404:
            logger.warning("⚠️ 404 Not Found - Endpoint might not exist")
            return None
        elif response.status == 429:
            logger.warning("⚠️ Rate limit exceeded, waiting...")
            await asyncio.sleep(5)
            return None
        else:
            logger.error(f"❌ API error: {response.status}")
            text = await response.text()
            logger.error(f"Response: {text[:200]}")
            return None


class FragellaAPI(RapidAPIClient):
    """Fragella API client for real fragrance data"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.host = "fragella-api.p.rapidapi.com"
        
    async def get_fragrance_matches(self) -> List[FragranceData]:
        """Get fragrance matches from Fragella API"""
        url = "https://fragella-api.p.rapidapi.com/fragrances/match"
        
        logger.info("🔄 Fetching fragrance matches from Fragella...")
        data = await self._make_request(url, self.host, method='GET')
        
        if not data:
            logger.error("❌ No data received from Fragella API")
            return []
        
        fragrances = self._parse_fragella_response(data)
        logger.info(f"✅ Parsed {len(fragrances)} fragrances from Fragella")
        return fragrances
    
    async def search_fragrances_by_brand(self, brand: str = None) -> List[FragranceData]:
        """Search fragrances by brand if the API supports it"""
        # Try different endpoints that might exist
        endpoints_to_try = [
            "https://fragella-api.p.rapidapi.com/fragrances",
            "https://fragella-api.p.rapidapi.com/search",
            "https://fragella-api.p.rapidapi.com/fragrances/all"
        ]
        
        all_fragrances = []
        
        for endpoint in endpoints_to_try:
            logger.info(f"🔄 Trying endpoint: {endpoint}")
            params = {'brand': brand} if brand else None
            data = await self._make_request(endpoint, self.host, params, method='GET')
            
            if data:
                fragrances = self._parse_fragella_response(data)
                all_fragrances.extend(fragrances)
                logger.info(f"✅ Got {len(fragrances)} fragrances from {endpoint}")
                break  # Stop if we get data from this endpoint
            else:
                logger.debug(f"⚠️ No data from {endpoint}")
        
        return all_fragrances
    
    def _parse_fragella_response(self, data: Dict) -> List[FragranceData]:
        """Parse Fragella API response to FragranceData objects"""
        fragrances = []
        
        # Handle different possible response structures
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Try different possible keys for the fragrance list
            items = (data.get('fragrances') or 
                    data.get('matches') or 
                    data.get('results') or 
                    data.get('data') or 
                    [data])  # Single item
        
        logger.info(f"📊 Processing {len(items)} items from API response")
        
        for item in items:
            try:
                fragrance = self._parse_single_fragrance(item)
                if fragrance and fragrance.name:  # Only add if we have a name
                    fragrances.append(fragrance)
            except Exception as e:
                logger.error(f"Error parsing fragrance item: {e}")
                logger.debug(f"Problematic item: {item}")
                continue
        
        return fragrances
    
    def _parse_single_fragrance(self, item: Dict) -> Optional[FragranceData]:
        """Parse a single fragrance item from Fragella API"""
        try:
            # Extract basic info
            name = item.get('name') or item.get('title') or item.get('fragrance_name')
            brand = item.get('brand') or item.get('house') or item.get('brand_name')
            
            if not name:
                logger.debug("Skipping item - no name found")
                return None
            
            # Extract notes - try different possible structures
            notes_data = item.get('notes', {})
            top_notes = self._extract_notes(notes_data, ['top', 'top_notes', 'head'])
            middle_notes = self._extract_notes(notes_data, ['middle', 'heart', 'middle_notes', 'heart_notes'])
            base_notes = self._extract_notes(notes_data, ['base', 'base_notes', 'dry_down'])
            
            # If notes are in a different structure, try alternatives
            if not any([top_notes, middle_notes, base_notes]):
                # Try if notes are directly in the item
                top_notes = item.get('top_notes', [])
                middle_notes = item.get('middle_notes', []) or item.get('heart_notes', [])
                base_notes = item.get('base_notes', [])
            
            # Extract other fields
            gender = item.get('gender') or item.get('target_gender')
            year = item.get('year') or item.get('release_year') or item.get('launched')
            if isinstance(year, str) and year.isdigit():
                year = int(year)
            elif not isinstance(year, int):
                year = None
            
            perfumer = item.get('perfumer') or item.get('nose') or item.get('creator')
            description = item.get('description') or item.get('summary') or item.get('about')
            
            image_url = item.get('image') or item.get('image_url') or item.get('picture')
            
            # Extract ratings
            rating = item.get('rating') or item.get('average_rating') or item.get('score')
            if rating:
                try:
                    rating = float(rating)
                except (ValueError, TypeError):
                    rating = 0.0
            else:
                rating = 0.0
            
            # Extract review count
            reviews = item.get('reviews') or item.get('review_count') or item.get('votes')
            if reviews:
                try:
                    reviews = int(reviews)
                except (ValueError, TypeError):
                    reviews = 0
            else:
                reviews = 0
            
            # Extract price
            price = item.get('price') or item.get('cost')
            if price:
                try:
                    # Remove currency symbols and convert to float
                    price_str = str(price).replace('$', '').replace('€', '').replace('£', '')
                    price = float(price_str)
                except (ValueError, TypeError):
                    price = None
            
            return FragranceData(
                name=name,
                brand_name=brand or "Unknown",
                top_notes=top_notes,
                middle_notes=middle_notes,
                base_notes=base_notes,
                gender=gender,
                release_year=year,
                perfumer=perfumer,
                description=description,
                image_url=image_url,
                average_rating=rating,
                total_ratings=reviews,
                price=price,
                api_source='fragella',
                external_id=item.get('id') or item.get('fragrance_id')
            )
            
        except Exception as e:
            logger.error(f"Error parsing fragrance: {e}")
            return None
    
    def _extract_notes(self, notes_data: Dict, possible_keys: List[str]) -> List[str]:
        """Extract notes from different possible key structures"""
        for key in possible_keys:
            notes = notes_data.get(key)
            if notes:
                if isinstance(notes, list):
                    return [str(note) for note in notes]
                elif isinstance(notes, str):
                    # Split by common separators
                    return [note.strip() for note in notes.replace(',', ';').split(';') if note.strip()]
        return []


class FragranceAPIManager:
    """Manager for Fragella API integration"""
    
    def __init__(self, rapidapi_key: str, db_session: Session):
        self.rapidapi_key = rapidapi_key
        self.db = db_session
        self.fragella_api = FragellaAPI(rapidapi_key)
        
    async def collect_and_save_fragrances(self, max_api_calls: int = 3) -> Dict:
        """Collect fragrances from Fragella API and save to database"""
        all_fragrances = []
        api_calls_made = 0
        
        logger.info("🚀 Starting Fragella API data collection...")
        
        async with self.fragella_api as api:
            # Try the match endpoint with different trait combinations
            trait_combinations = [
                {'gender': 'unisex', 'occasion': 'daily'},
                {'gender': 'feminine', 'season': 'spring'},
                {'gender': 'masculine', 'occasion': 'evening'},
                {'season': 'winter', 'occasion': 'special'},
                {'gender': 'unisex', 'season': 'summer'}
            ]
            
            for i, traits in enumerate(trait_combinations):
                if api_calls_made >= max_api_calls:
                    break
                    
                logger.info(f"🔄 Trying trait combination {i+1}: {traits}")
                fragrances = await api.get_fragrance_matches(traits)
                all_fragrances.extend(fragrances)
                api_calls_made += 1
                
                if fragrances:
                    logger.info(f"✅ Got {len(fragrances)} fragrances from traits: {traits}")
                else:
                    logger.warning(f"⚠️ No results from traits: {traits}")
            
            # Try search terms if we need more data
            search_terms = ["rose", "vanilla", "citrus", "musk", "sandalwood", "jasmine"]
            
            for term in search_terms:
                if api_calls_made >= max_api_calls or len(all_fragrances) >= 50:
                    break
                    
                fragrances = await api.search_fragrances_by_term(term)
                all_fragrances.extend(fragrances)
                api_calls_made += 1
                
                if fragrances:
                    logger.info(f"✅ Got {len(fragrances)} fragrances for '{term}'")
                else:
                    logger.warning(f"⚠️ No results for '{term}'")
        
        if not all_fragrances:
            logger.error("❌ No fragrances collected from Fragella API")
            return {
                'total_collected': 0,
                'saved_to_db': 0,
                'skipped_duplicates': 0,
                'api_calls_made': api_calls_made,
                'success': False
            }
        
        # Remove duplicates and save to database
        unique_fragrances = self._remove_duplicates(all_fragrances)
        saved_count = 0
        skipped_count = 0
        
        for frag in unique_fragrances:
            if self.save_fragrance_to_db(frag):
                saved_count += 1
            else:
                skipped_count += 1
        
        results = {
            'total_collected': len(unique_fragrances),
            'saved_to_db': saved_count,
            'skipped_duplicates': skipped_count,
            'api_calls_made': api_calls_made,
            'success': saved_count > 0
        }
        
        return results
    
    def _remove_duplicates(self, fragrances: List[FragranceData]) -> List[FragranceData]:
        """Remove duplicate fragrances based on name and brand"""
        seen = set()
        unique_fragrances = []
        
        for frag in fragrances:
            key = (frag.name.lower(), frag.brand_name.lower())
            if key not in seen:
                seen.add(key)
                unique_fragrances.append(frag)
        
        logger.info(f"🔧 Removed {len(fragrances) - len(unique_fragrances)} duplicates")
        return unique_fragrances
    
    def save_fragrance_to_db(self, fragrance_data: FragranceData) -> bool:
        """Save fragrance to database, avoiding duplicates"""
        try:
            # Check if fragrance already exists
            existing = self.db.query(Fragrance).filter(
                Fragrance.name == fragrance_data.name,
                Fragrance.brand_name == fragrance_data.brand_name
            ).first()
            
            if existing:
                logger.debug(f"Skipping duplicate: {fragrance_data.name} by {fragrance_data.brand_name}")
                return False
            
            # Create new fragrance
            new_fragrance = Fragrance(
                name=fragrance_data.name,
                brand_name=fragrance_data.brand_name,
                top_notes=json.dumps(fragrance_data.top_notes) if fragrance_data.top_notes else None,
                middle_notes=json.dumps(fragrance_data.middle_notes) if fragrance_data.middle_notes else None,
                base_notes=json.dumps(fragrance_data.base_notes) if fragrance_data.base_notes else None,
                gender=fragrance_data.gender,
                release_year=fragrance_data.release_year,
                perfumer=fragrance_data.perfumer,
                description=fragrance_data.description,
                image_url=fragrance_data.image_url,
                average_rating=fragrance_data.average_rating,
                total_ratings=fragrance_data.total_ratings,
                price=fragrance_data.price,
                api_source=fragrance_data.api_source,
                external_id=fragrance_data.external_id
            )
            
            self.db.add(new_fragrance)
            self.db.commit()
            
            logger.debug(f"✅ Saved: {fragrance_data.name} by {fragrance_data.brand_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving fragrance: {e}")
            self.db.rollback()
            return False
    
    def get_database_stats(self) -> Dict:
        """Get current database statistics"""
        try:
            total_fragrances = self.db.query(Fragrance).count()
            api_sources = self.db.query(Fragrance.api_source).distinct().all()
            
            return {
                'total_fragrances': total_fragrances,
                'api_sources': [source[0] for source in api_sources if source[0]]
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'total_fragrances': 0, 'api_sources': []}


def get_database_session():
    """Create database session for Railway PostgreSQL"""
    DATABASE_URL = "postgresql://postgres:DctOdYOceFkbZTBNJKxtLfZeqKwzTOFS@ballast.proxy.rlwy.net:18095/railway"
    
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


async def test_fragella_api():
    """Test Fragella API connection"""
    RAPIDAPI_KEY = "52d7279c5bmsh3d0e6d38dd7f8c1p108ad8jsn880765865b50"
    
    db = None
    try:
        db = get_database_session()
        manager = FragranceAPIManager(RAPIDAPI_KEY, db)
        
        initial_stats = manager.get_database_stats()
        logger.info(f"📊 Initial database stats: {initial_stats}")
        
        # Test with minimal API calls
        results = await manager.collect_and_save_fragrances(max_api_calls=2)
        
        if results['success']:
            logger.info(f"🎉 Fragella API test successful!")
            logger.info(f"📈 Results: {results}")
        else:
            logger.error("❌ Fragella API test failed - no data collected")
            logger.info("💡 Possible issues:")
            logger.info("   • API subscription not active on RapidAPI")
            logger.info("   • API endpoint structure changed")
            logger.info("   • Network/firewall blocking requests")
        
        final_stats = manager.get_database_stats()
        logger.info(f"📊 Final database stats: {final_stats}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db:
            db.close()


async def populate_database_with_fragella():
    """Full database population using Fragella API"""
    RAPIDAPI_KEY = "52d7279c5bmsh3d0e6d38dd7f8c1p108ad8jsn880765865b50"
    
    db = None
    try:
        db = get_database_session()
        manager = FragranceAPIManager(RAPIDAPI_KEY, db)
        
        initial_stats = manager.get_database_stats()
        logger.info(f"🎯 Starting Fragella database population...")
        logger.info(f"📊 Initial database: {initial_stats}")
        
        # Collect data with more API calls for full population
        results = await manager.collect_and_save_fragrances(max_api_calls=5)
        
        if results['success']:
            logger.info("🎉 Database population completed successfully!")
            logger.info(f"📈 Results: {results}")
        else:
            logger.error("❌ Database population failed")
            logger.info("Check API subscription and endpoint availability")
        
        final_stats = manager.get_database_stats()
        logger.info(f"📊 Final database: {final_stats}")
        
    except Exception as e:
        logger.error(f"❌ Population failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    print("🌸 ScentMatch - Fragella API Integration")
    print("=" * 50)
    print("Real fragrance data from Fragella API")
    print("No sample data - only authentic fragrance information")
    print("=" * 50)
    print("")
    print("Choose mode:")
    print("1. Test Fragella API (2 API calls)")
    print("2. Full population (5 API calls)")
    print("3. Check current database stats")
    
    mode = input("Enter choice (1, 2, or 3): ").strip()
    
    if mode == "1":
        print("🧪 Testing Fragella API connection...")
        asyncio.run(test_fragella_api())
    elif mode == "2":
        print("🚀 Running full Fragella population...")
        asyncio.run(populate_database_with_fragella())
    elif mode == "3":
        print("📊 Checking database stats...")
        db = get_database_session()
        manager = FragranceAPIManager("dummy_key", db)
        stats = manager.get_database_stats()
        print(f"Database stats: {stats}")
        db.close()
    else:
        print("❌ Invalid choice")