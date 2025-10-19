from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from typing import List
from uuid import uuid4, UUID
import time
import logging
import re
from app.models.UserFragranceProfile import UserScentProfile, UserFragrance
from app.models.user import User as UserModel
from app.core.database import get_db, AsyncSessionLocal
from app.models.fragrance import Fragrance as FragranceModel
from app.schemas.frags import (
    NoteBasedRequest, 
    NoteBasedResponse, 
    SimilarityRequest, 
    SimilarityResponse,
    TargetFragranceInfo,
    FragranceSearchResult,
    convert_note_preferences,
    create_user_profile,
    convert_recommendation_to_api,
    convert_similarity_recommendation_to_api,
    SaveProfileResponse,
    SaveQuizRatingsRequest,
    SaveOwnedFragrancesRequest
)
from app.ml.models import NoteBasedRecommender, SimilarityRecommender

router = APIRouter(prefix="/recommendations", tags=["fragrance-recommendations"])
logger = logging.getLogger(__name__)

# Global recommender instances
note_based_recommender = None
similarity_recommender = None

def normalize_search_text(text):
    
    if not text:
        return ""
    
    
    text = text.lower().strip()
    
    
    text = re.sub(r'[-_]+', ' ', text)
    
   
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def create_search_variants(query):
  
    variants = [query]
    
   
    dash_variant = re.sub(r'\s+', '-', query)
    if dash_variant != query:
        variants.append(dash_variant)
    
   
    space_variant = re.sub(r'[-_]+', ' ', query)
    if space_variant != query:
        variants.append(space_variant)
    
    return list(set(variants))  


async def get_recommenders():
   
    global note_based_recommender, similarity_recommender
    
    if note_based_recommender is None or similarity_recommender is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation service not initialized"
        )
    
    return note_based_recommender, similarity_recommender


@router.post("/note-based", 
             response_model=NoteBasedResponse,
             summary="Get recommendations based on note preferences",
             description="Level 1: Users specify notes/accords they like with importance ratings (1-10)")
async def get_note_based_recommendations(
    request: NoteBasedRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized fragrance recommendations based on user's note and accord preferences.
    
    This endpoint is for users who don't own any fragrances yet but know what notes/accords they like.
    Users rate their preferences from 1 (hate) to 10 (love).
    """
    start_time = time.time()
    request_id = str(uuid4())
    
    try:
        logger.info(f"[{request_id}] Note-based recommendation request with {len(request.preferred_notes)} notes, {len(request.preferred_accords)} accords")
        
        # Get recommender instance
        note_recommender, _ = await get_recommenders()
        
        # Convert Pydantic models to internal dataclasses
        internal_note_prefs = convert_note_preferences(request.preferred_notes)
        internal_accord_prefs = convert_note_preferences(request.preferred_accords)
        
        # Get recommendations from algorithm
        recommendations = note_recommender.get_recommendations(
            preferred_notes=internal_note_prefs,
            preferred_accords=internal_accord_prefs,
            limit=request.limit
        )
        
        # Create user profile summary
        user_profile = create_user_profile(request.preferred_notes, request.preferred_accords)
        
        # Convert internal results to API response format
        api_recommendations = [
            convert_recommendation_to_api(rec, rank + 1, request.preferred_notes, request.preferred_accords)
            for rank, rec in enumerate(recommendations)
        ]
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"[{request_id}] Returning {len(api_recommendations)} recommendations in {processing_time:.1f}ms")
        
        return NoteBasedResponse(
            request_id=request_id,
            user_profile=user_profile,
            recommendations=api_recommendations,
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        logger.error(f"[{request_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.post("/similarity",
             response_model=SimilarityResponse, 
             summary="Find fragrances similar to target fragrance(s)",
             description="Find fragrances similar to one or more specific fragrances. Supports both single fragrance similarity and collection-based analysis.")
async def get_similar_fragrances(
    request: SimilarityRequest,
    db: Session = Depends(get_db)
):
    """
    Find fragrances similar to target fragrances.
    
    Supports two modes:
    - Single fragrance: Finds fragrances similar to one target fragrance
    - Collection analysis: Analyzes multiple fragrances to find recommendations that complement the collection
    """
    start_time = time.time()
    request_id = str(uuid4())
    
    try:
        # Normalize target_fragrance_ids to list
        target_ids = request.target_fragrance_ids
        if isinstance(target_ids, str):
            target_ids = [target_ids]
        
        logger.info(f"[{request_id}] Similarity request for {len(target_ids)} fragrance(s): {target_ids}")
        
        # Get recommender instance
        _, similarity_recommender_instance = await get_recommenders()
        
        # Verify all target fragrances exist in database and collect their info
        target_fragrances_db = []
        async with AsyncSessionLocal() as db_session:
            for target_id in target_ids:
                stmt = select(FragranceModel).filter(FragranceModel.id == target_id)
                result = await db_session.execute(stmt)
                fragrance_db = result.scalars().first()
                
                if not fragrance_db:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Fragrance with ID {target_id} not found"
                    )
                
                target_fragrances_db.append(fragrance_db)
        
        # Create target fragrance info for response
        target_fragrances_info = [
            TargetFragranceInfo(
                id=frag.id,
                name=frag.name,
                brand=frag.brand_name
            )
            for frag in target_fragrances_db
        ]
        
        # Determine analysis type
        analysis_type = "single" if len(target_ids) == 1 else "collection"
        
        # Get recommendations from algorithm
        recommendations = similarity_recommender_instance.get_recommendations(
            target_fragrance_ids=request.target_fragrance_ids,
            limit=request.limit
        )
        
        # Convert to API response format using the new conversion function
        api_recommendations = [
            convert_similarity_recommendation_to_api(rec, rank + 1, target_fragrances_info)
            for rank, rec in enumerate(recommendations)
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        if analysis_type == "single":
            logger.info(f"[{request_id}] Returning {len(api_recommendations)} similar fragrances to '{target_fragrances_db[0].name}' in {processing_time:.1f}ms")
        else:
            logger.info(f"[{request_id}] Returning {len(api_recommendations)} collection-based recommendations for {len(target_ids)} fragrances in {processing_time:.1f}ms")
        
        return SimilarityResponse(
            request_id=request_id,
            target_fragrances=target_fragrances_info,
            analysis_type=analysis_type,
            recommendations=api_recommendations,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"[{request_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


async def initialize_recommenders():
    
    global note_based_recommender, similarity_recommender
    
    logger.info("Initializing recommendation engines...")
    
    try:
        # Load fragrance data from database
        async with AsyncSessionLocal() as session:
            stmt = select(FragranceModel)
            result = await session.execute(stmt)
            fragrances_db = result.scalars().all()
            
            logger.info(f"Loaded {len(fragrances_db)} fragrances from database")
            
            if not fragrances_db:
                raise ValueError("No fragrances found in database!")
            
            # Process fragrance data for recommenders
            fragrance_rows = []
            for frag_db in fragrances_db:
                fragrance_rows.append({
                    'id': str(frag_db.id),
                    'name': frag_db.name,
                    'brand_name': frag_db.brand_name,
                    'top_notes': frag_db.top_notes if frag_db.top_notes else [],
                    'middle_notes': frag_db.middle_notes if frag_db.middle_notes else [],
                    'base_notes': frag_db.base_notes if frag_db.base_notes else [],
                    'main_accords': frag_db.main_accords if frag_db.main_accords else [],
                    'average_rating': float(frag_db.average_rating) if frag_db.average_rating else 0.0,
                    'total_ratings': int(frag_db.total_ratings) if frag_db.total_ratings else 0
                })
            
            
            logger.info("Creating NoteBasedRecommender...")
            note_based_recommender = NoteBasedRecommender.from_database_rows(fragrance_rows)
            
            logger.info("Creating SimilarityRecommender...")
            similarity_recommender = SimilarityRecommender.from_database_rows(fragrance_rows)
            
            logger.info("Recommendation engines initialized successfully!")
            
    except Exception as e:
        logger.error(f"Failed to initialize recommenders: {str(e)}")
        raise


# Debug and testing endpoints
@router.post("/debug/initialize")
async def debug_initialize():
    
    try:
        await initialize_recommenders()
        return {"status": "success", "message": "Recommenders initialized"}
    except Exception as e:
        logger.error(f"Debug initialize error: {str(e)}")
        return {"status": "error", "message": str(e), "type": type(e).__name__}


@router.get("/health")
async def health_check():
   
    global note_based_recommender, similarity_recommender
    
    status_info = {
        "status": "healthy" if (note_based_recommender and similarity_recommender) else "unavailable",
        "note_based_recommender": "loaded" if note_based_recommender else "not_loaded",
        "similarity_recommender": "loaded" if similarity_recommender else "not_loaded",
        "timestamp": time.time()
    }
    
    if status_info["status"] == "unavailable":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=status_info
        )
    
    return status_info


@router.post("/test-note-based")
async def test_note_based_recommendations():
   
    sample_request = NoteBasedRequest(
        preferred_notes=[
            {"name": "vanilla", "importance": 9},
            {"name": "bergamot", "importance": 8},
            {"name": "cedar", "importance": 7},
            {"name": "patchouli", "importance": 2}
        ],
        preferred_accords=[
            {"name": "woody", "importance": 8},
            {"name": "fresh", "importance": 6}
        ],
        limit=5
    )
    
    return await get_note_based_recommendations(sample_request)


@router.post("/test-similarity-single")
async def test_similarity_single():
    
    
    sample_request = SimilarityRequest(
        target_fragrance_ids="123e4567-e89b-12d3-a456-426614174000",  # Replace with real UUID
        limit=5
    )
    
    return await get_similar_fragrances(sample_request)


@router.post("/test-similarity-collection")
async def test_similarity_collection():
  
    
    sample_request = SimilarityRequest(
        target_fragrance_ids=[
            "123e4567-e89b-12d3-a456-426614174000",  # Replace with real UUIDs
            "456e7890-e89b-12d3-a456-426614174001"
        ],
        limit=5
    )
    
    return await get_similar_fragrances(sample_request)

@router.get("/search", 
            response_model=List[FragranceSearchResult],
            summary="Search fragrances by name",
            description="Full text search for fragrances")
async def search_fragrances(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    
    try:
        logger.info(f"Searching fragrances: '{q}'")
        
        async with AsyncSessionLocal() as session:
            # Normalize the search query
            normalized_query = normalize_search_text(q)
            search_variants = create_search_variants(normalized_query)
            
            # Build search conditions for all variants
            search_conditions = []
            
            for variant in search_variants:
                search_conditions.extend([
                    # Search in normalized fragrance names
                    func.lower(func.replace(func.replace(FragranceModel.name, '-', ' '), '_', ' ')).contains(variant),
                    # Search in normalized brand names  
                    func.lower(func.replace(func.replace(FragranceModel.brand_name, '-', ' '), '_', ' ')).contains(variant),
                    # Search in combined normalized name
                    func.lower(func.replace(func.replace(
                        func.concat(FragranceModel.brand_name, ' ', FragranceModel.name), '-', ' '
                    ), '_', ' ')).contains(variant),
                ])
            
            # Combine all search conditions with OR
            combined_condition = or_(*search_conditions)
            
            stmt = select(FragranceModel).filter(
                combined_condition
            ).order_by(
                FragranceModel.total_ratings.desc()  # Most popular first
            ).limit(limit)
            
            result = await session.execute(stmt)
            fragrances = result.scalars().all()
            
            return [
                FragranceSearchResult(
                    id=str(frag.id),
                    name=frag.name.replace('-', ' ').replace('_', ' ').title(),  # Display with spaces
                    brand=frag.brand_name.replace('-', ' ').replace('_', ' ').title(),  # Display with spaces
                    full_name=f"{frag.brand_name.replace('-', ' ').replace('_', ' ').title()} {frag.name.replace('-', ' ').replace('_', ' ').title()}"
                )
                for frag in fragrances
            ]
            
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search service error"
        )
@router.get("/autocomplete",
            response_model=List[FragranceSearchResult],
            summary="Autocomplete fragrance suggestions", 
            description="Fast autocomplete suggestions as user types")
async def autocomplete_fragrances(
    q: str = Query(..., min_length=1, max_length=100, description="Partial search query"),
    limit: int = Query(default=8, ge=1, le=20, description="Max suggestions"),
    db: Session = Depends(get_db)
):
    
    try:
        async with AsyncSessionLocal() as session:
            # Normalize the search query
            normalized_query = normalize_search_text(q)
            search_variants = create_search_variants(normalized_query)
            
            # Build search conditions for all variants
            search_conditions = []
            
            for variant in search_variants:
                search_conditions.extend([
                    # Search in normalized fragrance names
                    func.lower(func.replace(func.replace(FragranceModel.name, '-', ' '), '_', ' ')).contains(variant),
                    # Search in normalized brand names
                    func.lower(func.replace(func.replace(FragranceModel.brand_name, '-', ' '), '_', ' ')).contains(variant),
                    # Search in combined normalized name
                    func.lower(func.replace(func.replace(
                        func.concat(FragranceModel.brand_name, ' ', FragranceModel.name), '-', ' '
                    ), '_', ' ')).contains(variant),
                ])
            
            # Combine all search conditions with OR
            combined_condition = or_(*search_conditions)
            
            stmt = select(FragranceModel).filter(
                combined_condition,
                FragranceModel.total_ratings >= 5  # Only suggest somewhat popular fragrances
            ).order_by(
                FragranceModel.total_ratings.desc()
            ).limit(limit * 2)  # Get more results to deduplicate
            
            result = await session.execute(stmt)
            fragrances = result.scalars().all()
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_fragrances = []
            for frag in fragrances:
                if frag.id not in seen_ids and len(unique_fragrances) < limit:
                    seen_ids.add(frag.id)
                    unique_fragrances.append(frag)
            
            return [
                FragranceSearchResult(
                    id=str(frag.id),
                    name=frag.name.replace('-', ' ').replace('_', ' ').title(),  # Display with spaces
                    brand=frag.brand_name.replace('-', ' ').replace('_', ' ').title(),  # Display with spaces
                    full_name=f"{frag.brand_name.replace('-', ' ').replace('_', ' ').title()} {frag.name.replace('-', ' ').replace('_', ' ').title()}"
                )
                for frag in unique_fragrances
            ]
            
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Autocomplete service error"
        )



@router.get("/popular",
            response_model=List[FragranceSearchResult],
            summary="Get popular fragrances",
            description="Get most popular fragrances for initial suggestions")
async def get_popular_fragrances(
    limit: int = Query(default=10, ge=1, le=50, description="Number of popular fragrances"),
    db: Session = Depends(get_db)
):
    
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(FragranceModel).filter(
                FragranceModel.total_ratings >= 100  # Well rated fragrances only
            ).order_by(
                FragranceModel.total_ratings.desc()
            ).limit(limit)
            
            result = await session.execute(stmt)
            fragrances = result.scalars().all()
            
            return [
                FragranceSearchResult(
                    id=str(frag.id),
                    name=frag.name,
                    brand=frag.brand_name,
                    full_name=f"{frag.brand_name} {frag.name}"
                )
                for frag in fragrances
            ]
            
    except Exception as e:
        logger.error(f"Popular fragrances error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Popular fragrances service error"
        )
@router.post("/save-quiz-profile", 
             response_model=SaveProfileResponse,
             summary="Save quiz results to user profile",
             description="Saves all quiz note/accord ratings. Replaces existing quiz data if user retakes.")
async def save_quiz_to_profile(
    request: SaveQuizRatingsRequest,
    db: Session = Depends(get_db)
):
    """
    Save user's complete quiz results to their profile.
    - Stores ALL ratings (1-10), not just liked ones
    - REPLACES existing quiz data if user retakes quiz
    - Sets onboarding_complete flag
    """
    start_time = time.time()
    request_id = str(uuid4())
    
    try:
        logger.info(f"[{request_id}] Saving quiz profile for user {request.user_id}")
        
        # 1. Transform note/accord lists into rating dictionaries
        # Convert: [NotePreferenceInput(name='vanilla', importance=9), ...]
        # Into: {'vanilla': 9, 'bergamot': 8, ...}
        
        note_ratings = {
            pref.name.lower().strip(): pref.importance 
            for pref in request.preferred_notes
        }
        
        accord_ratings = {
            pref.name.lower().strip(): pref.importance 
            for pref in request.preferred_accords
        }
        
        logger.info(f"[{request_id}] Transformed {len(note_ratings)} notes, {len(accord_ratings)} accords")
        
        # 2. UPSERT UserScentProfile (replace if exists)
        async with AsyncSessionLocal() as session:
            # Check if profile exists
            stmt = select(UserScentProfile).filter(
                UserScentProfile.user_id == request.user_id
            )
            result = await session.execute(stmt)
            profile = result.scalars().first()
            
            if profile:
                # REPLACE existing quiz data
                logger.info(f"[{request_id}] Updating existing profile (REPLACE mode)")
                profile.liked_notes = note_ratings  # OVERWRITES old data
                profile.liked_accords = accord_ratings  # OVERWRITES old data
                profile.onboarding_complete = True
                profile.onboarding_complete_at = func.now()
                profile.updated_at = func.now()
            else:
                # INSERT new profile
                logger.info(f"[{request_id}] Creating new profile")
                profile = UserScentProfile(
                    user_id=request.user_id,
                    liked_notes=note_ratings,
                    liked_accords=accord_ratings,
                    onboarding_complete=True,
                    onboarding_complete_at=func.now()
                )
                session.add(profile)
            
            await session.commit()
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"[{request_id}] Profile saved successfully in {processing_time:.1f}ms")
            
            return SaveProfileResponse(
                status="success",
                message="Quiz preferences saved to profile",
                items_saved=len(note_ratings) + len(accord_ratings)
            )
            
    except Exception as e:
        logger.error(f"[{request_id}] Error saving profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save profile: {str(e)}"
        )
@router.post("/save-owned-fragrances",
             response_model=SaveProfileResponse,
             summary="Save user's owned/liked fragrances",
             description="Save fragrances to user's collection from onboarding or manual addition")
async def save_owned_fragrances(
    request: SaveOwnedFragrancesRequest,
    db: Session = Depends(get_db)
):
    """
    Save fragrances to user's collection.
    - Used after onboarding when user selects fragrances they own
    - Can also be used to add fragrances to collection later
    """
    start_time = time.time()
    request_id = str(uuid4())
    
    try:
        logger.info(f"[{request_id}] Saving {len(request.fragrance_ids)} fragrances for user {request.user_id}")
        
        async with AsyncSessionLocal() as session:
            # 1. Verify user exists
            user_stmt = select(UserModel).filter(UserModel.id == request.user_id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {request.user_id} not found"
                )
            
            # 2. Verify all fragrances exist
            frag_stmt = select(FragranceModel).filter(
                FragranceModel.id.in_(request.fragrance_ids)
            )
            frag_result = await session.execute(frag_stmt)
            existing_fragrances = frag_result.scalars().all()
            existing_ids = {str(frag.id) for frag in existing_fragrances}
            
            # Check for invalid IDs
            requested_ids = {str(fid) for fid in request.fragrance_ids}
            invalid_ids = requested_ids - existing_ids
            
            if invalid_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Fragrances not found: {list(invalid_ids)}"
                )
            
            # 3. Check which fragrances already exist for this user
            existing_stmt = select(UserFragrance).filter(
                UserFragrance.user_id == request.user_id,
                UserFragrance.fragrance_id.in_(request.fragrance_ids)
            )
            existing_result = await session.execute(existing_stmt)
            existing_user_frags = existing_result.scalars().all()
            existing_user_frag_ids = {str(uf.fragrance_id) for uf in existing_user_frags}
            
            # 4. Insert only new fragrances (avoid duplicates)
            new_fragrances = []
            for frag_id in request.fragrance_ids:
                if str(frag_id) not in existing_user_frag_ids:
                    new_frag = UserFragrance(
                        user_id=request.user_id,
                        fragrance_id=frag_id,
                        source='onboarding',  # Or 'added_later' based on context
                        owned=True
                    )
                    new_fragrances.append(new_frag)
            
            # 5. Bulk insert
            if new_fragrances:
                session.add_all(new_fragrances)
                await session.commit()
                logger.info(f"[{request_id}] Added {len(new_fragrances)} new fragrances")
            else:
                logger.info(f"[{request_id}] All fragrances already in user's collection")
            
            processing_time = (time.time() - start_time) * 1000
            
            return SaveProfileResponse(
                status="success",
                message=f"Saved {len(new_fragrances)} fragrances to collection",
                items_saved=len(new_fragrances)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error saving fragrances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save fragrances: {str(e)}"
        )