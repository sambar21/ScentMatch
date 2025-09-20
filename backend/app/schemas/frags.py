from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import List, Optional, Dict, Any, Union
from enum import Enum


# =====================================================
# SIMILARITY RECOMMENDER MODELS (Find Similar to Target)
# =====================================================

class SimilarityRequest(BaseModel):
    target_fragrance_ids: Union[str, List[str]] = Field(..., description="Single fragrance ID or list of IDs")
    limit: int = Field(default=10, ge=1, le=50)
    
    @field_validator('target_fragrance_ids')
    @classmethod
    def validate_fragrance_ids(cls, v):
        if isinstance(v, str):
            try:
                UUID(v)
                return v
            except ValueError:
                raise ValueError('Invalid UUID format')
        elif isinstance(v, list):
            if len(v) > 10:
                raise ValueError('Maximum 10 fragrances allowed')
            if len(v) == 0:
                raise ValueError('At least one fragrance ID required')
            for frag_id in v:
                try:
                    UUID(frag_id)
                except ValueError:
                    raise ValueError(f'Invalid UUID format: {frag_id}')
            return v
        else:
            raise ValueError('Must be string or list of strings')


class TargetFragranceInfo(BaseModel):
    
    id: UUID = Field(..., description="Fragrance UUID")
    name: str = Field(..., description="Fragrance name")
    brand: str = Field(..., description="Brand name")


class SimilarityResponse(BaseModel):
    
    request_id: str = Field(..., description="Unique request identifier")
    target_fragrances: List[TargetFragranceInfo] = Field(..., description="Details of the target fragrance(s)")
    analysis_type: str = Field(..., description="Type of analysis: 'single' or 'collection'")
    recommendations: List['RecommendationItem'] = Field(..., description="List of similar fragrances")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


# =====================================================
# NOTE-BASED RECOMMENDER MODELS (Level 1: User Preferences)
# =====================================================

class NotePreferenceInput(BaseModel):
    
    name: str = Field(..., min_length=1, max_length=100, description="Name of the note or accord")
    importance: int = Field(..., ge=1, le=10, description="How much user likes this (1=hate, 10=love)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        # Clean and normalize the note name
        cleaned = v.strip().lower()
        if not cleaned:
            raise ValueError("Note name cannot be empty")
        return cleaned


class NoteBasedRequest(BaseModel):
   
    preferred_notes: List[NotePreferenceInput] = Field(
        default_factory=list,
        max_length=20,
        description="Notes the user likes/dislikes with importance ratings"
    )
    preferred_accords: List[NotePreferenceInput] = Field(
        default_factory=list,
        max_length=15,
        description="Accords/styles the user likes/dislikes with importance ratings"
    )
    limit: int = Field(default=10, ge=1, le=50, description="Number of recommendations to return")
    
    @field_validator('preferred_notes', 'preferred_accords')
    @classmethod
    def validate_preferences(cls, v):
        if not v:
            return v
            
        # Check for duplicates
        names = [pref.name.lower() for pref in v]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate note/accord names not allowed")
        return v
    
    def model_validate(cls, values):
       
        if not values.get('preferred_notes') and not values.get('preferred_accords'):
            raise ValueError("Must provide at least one note or accord preference")
        return values


class UserPreferenceProfile(BaseModel):
   
    loved_notes: List[str] = Field(default_factory=list, description="Notes rated 8-10")
    liked_notes: List[str] = Field(default_factory=list, description="Notes rated 6-7") 
    disliked_notes: List[str] = Field(default_factory=list, description="Notes rated 1-3")
    loved_accords: List[str] = Field(default_factory=list, description="Accords rated 8-10")
    liked_accords: List[str] = Field(default_factory=list, description="Accords rated 6-7")
    disliked_accords: List[str] = Field(default_factory=list, description="Accords rated 1-3")
    total_preferences: int = Field(..., description="Total number of preferences provided")


class NoteBasedResponse(BaseModel):
  
    request_id: str = Field(..., description="Unique request identifier")
    user_profile: UserPreferenceProfile = Field(..., description="Summary of user preferences")
    recommendations: List['RecommendationItem'] = Field(..., description="Personalized recommendations")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


# =====================================================
# SHARED RESPONSE MODELS
# =====================================================

class FragranceDetail(BaseModel):
  
    id: UUID = Field(..., description="Fragrance UUID")
    name: str = Field(..., description="Fragrance name")
    brand: str = Field(..., description="Brand name")
    top_notes: List[str] = Field(default_factory=list, description="Top notes")
    middle_notes: List[str] = Field(default_factory=list, description="Middle/heart notes")
    base_notes: List[str] = Field(default_factory=list, description="Base notes")
    accords: List[str] = Field(default_factory=list, description="Main accords/fragrance family")
    avg_rating: float = Field(..., ge=0.0, le=5.0, description="Average user rating")
    num_ratings: int = Field(..., ge=0, description="Number of ratings")


class RecommendationExplanation(BaseModel):
    
    primary_reason: str = Field(..., description="Main reason for recommendation")
    shared_notes: List[str] = Field(default_factory=list, description="Notes in common with preferences")
    shared_accords: List[str] = Field(default_factory=list, description="Accords in common with preferences")
    quality_note: Optional[str] = Field(None, description="Note about fragrance quality/ratings")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Overall similarity score")


class RecommendationItem(BaseModel):
   
    fragrance: FragranceDetail = Field(..., description="Fragrance details")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score")
    explanation: RecommendationExplanation = Field(..., description="Why this was recommended")
    rank: int = Field(..., ge=1, description="Rank in recommendation list")

class FragranceSearchResult(BaseModel):
    id: str  
    name: str
    brand: str
    full_name: str


# =====================================================
# ERROR MODELS
# =====================================================

class ValidationError(BaseModel):
   
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    invalid_value: Any = Field(None, description="The value that failed validation")


class ErrorResponse(BaseModel):
   
    error_code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: List[ValidationError] = Field(default_factory=list, description="Detailed validation errors")
    request_id: Optional[str] = Field(None, description="Request ID if available")


# =====================================================
# UTILITY FUNCTIONS FOR CONVERTING BETWEEN MODELS
# =====================================================

def convert_note_preferences(pydantic_prefs: List[NotePreferenceInput]) -> List['NotePreference']:
    
    from dataclasses import dataclass
    
    @dataclass
    class NotePreference:
        name: str
        importance: int
    
    return [NotePreference(name=pref.name, importance=pref.importance) for pref in pydantic_prefs]


def create_user_profile(note_prefs: List[NotePreferenceInput], 
                       accord_prefs: List[NotePreferenceInput]) -> UserPreferenceProfile:
    
    
    def categorize_preferences(prefs: List[NotePreferenceInput]) -> tuple:
        loved = [p.name for p in prefs if p.importance >= 8]
        liked = [p.name for p in prefs if 6 <= p.importance <= 7]
        disliked = [p.name for p in prefs if p.importance <= 3]
        return loved, liked, disliked
    
    loved_notes, liked_notes, disliked_notes = categorize_preferences(note_prefs)
    loved_accords, liked_accords, disliked_accords = categorize_preferences(accord_prefs)
    
    return UserPreferenceProfile(
        loved_notes=loved_notes,
        liked_notes=liked_notes,
        disliked_notes=disliked_notes,
        loved_accords=loved_accords,
        liked_accords=liked_accords,
        disliked_accords=disliked_accords,
        total_preferences=len(note_prefs) + len(accord_prefs)
    )


def convert_recommendation_to_api(rec: 'RecommendationResult', rank: int, 
                                user_note_prefs: List[NotePreferenceInput],
                                user_accord_prefs: List[NotePreferenceInput]) -> RecommendationItem:
   
    
    # Find shared elements
    user_notes = {p.name.lower() for p in user_note_prefs if p.importance >= 6}
    user_accords = {p.name.lower() for p in user_accord_prefs if p.importance >= 6}
    
    fragrance_notes = {note.lower() for note in rec.fragrance.notes}
    fragrance_accords = {accord.lower() for accord in rec.fragrance.accords}
    
    shared_notes = list(user_notes & fragrance_notes)
    shared_accords = list(user_accords & fragrance_accords)
    
    # Create explanation
    if shared_accords:
        primary_reason = f"Matches your preferred style: {', '.join(shared_accords[:2])}"
    elif shared_notes:
        primary_reason = f"Contains notes you love: {', '.join(shared_notes[:3])}"
    else:
        primary_reason = "Recommended based on your overall preferences"
    
    quality_note = None
    if rec.fragrance.avg_rating >= 4.0 and rec.fragrance.num_ratings >= 100:
        quality_note = f"Highly rated ({rec.fragrance.avg_rating:.1f}/5 from {rec.fragrance.num_ratings:,} reviews)"
    
    return RecommendationItem(
        fragrance=FragranceDetail(
            id=rec.fragrance.id,
            name=rec.fragrance.name,
            brand=rec.fragrance.brand,
            top_notes=rec.fragrance.top_notes,
            middle_notes=rec.fragrance.middle_notes,
            base_notes=rec.fragrance.base_notes,
            accords=rec.fragrance.accords,
            avg_rating=rec.fragrance.avg_rating,
            num_ratings=rec.fragrance.num_ratings
        ),
        score=rec.score,
        explanation=RecommendationExplanation(
            primary_reason=primary_reason,
            shared_notes=shared_notes,
            shared_accords=shared_accords,
            quality_note=quality_note,
            similarity_score=rec.score
        ),
        rank=rank
    )


def convert_similarity_recommendation_to_api(rec: 'RecommendationResult', rank: int, 
                                           target_fragrances: List['TargetFragranceInfo']) -> RecommendationItem:
   
    
    # Create explanation based on whether it's single or multiple targets
    if len(target_fragrances) == 1:
        primary_reason = f"Similar to {target_fragrances[0].name}"
    else:
        target_names = [frag.name for frag in target_fragrances[:2]]  # Show first 2 names
        if len(target_fragrances) > 2:
            primary_reason = f"Similar to {', '.join(target_names)} and {len(target_fragrances) - 2} others"
        else:
            primary_reason = f"Similar to {' and '.join(target_names)}"
    
    quality_note = None
    if rec.fragrance.avg_rating >= 4.0 and rec.fragrance.num_ratings >= 100:
        quality_note = f"Highly rated ({rec.fragrance.avg_rating:.1f}/5 from {rec.fragrance.num_ratings:,} reviews)"
    
    return RecommendationItem(
        fragrance=FragranceDetail(
            id=rec.fragrance.id,
            name=rec.fragrance.name,
            brand=rec.fragrance.brand,
            top_notes=rec.fragrance.top_notes,
            middle_notes=rec.fragrance.middle_notes,
            base_notes=rec.fragrance.base_notes,
            accords=rec.fragrance.accords,
            avg_rating=rec.fragrance.avg_rating,
            num_ratings=rec.fragrance.num_ratings
        ),
        score=rec.score,
        explanation=RecommendationExplanation(
            primary_reason=primary_reason,
            shared_notes=[],  # Could be populated with actual shared notes if needed
            shared_accords=[],  # Could be populated with actual shared accords if needed
            quality_note=quality_note,
            similarity_score=rec.score
        ),
        rank=rank
    )


# =====================================================
# EXAMPLE USAGE DOCUMENTATION
# =====================================================

class APIExamples:
  
    
    SIMILARITY_REQUEST_SINGLE_EXAMPLE = {
        "target_fragrance_ids": "123e4567-e89b-12d3-a456-426614174000",
        "limit": 10
    }
    
    SIMILARITY_REQUEST_MULTIPLE_EXAMPLE = {
        "target_fragrance_ids": [
            "123e4567-e89b-12d3-a456-426614174000",
            "456e7890-e89b-12d3-a456-426614174001"
        ],
        "limit": 10
    }
    
    NOTE_BASED_REQUEST_EXAMPLE = {
        "preferred_notes": [
            {"name": "vanilla", "importance": 9},
            {"name": "bergamot", "importance": 8},
            {"name": "cedar", "importance": 7},
            {"name": "patchouli", "importance": 2}
        ],
        "preferred_accords": [
            {"name": "woody", "importance": 8},
            {"name": "fresh", "importance": 6}
        ],
        "limit": 15
    }
    
    SIMILARITY_RESPONSE_EXAMPLE = {
        "request_id": "req_123456789",
        "target_fragrances": [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Tom Ford Oud Wood",
                "brand": "Tom Ford"
            }
        ],
        "analysis_type": "single",
        "recommendations": [
            {
                "fragrance": {
                    "id": "456e7890-e89b-12d3-a456-426614174001",
                    "name": "Creed Royal Oud",
                    "brand": "Creed",
                    "top_notes": ["pink pepper", "rhubarb"],
                    "middle_notes": ["oud", "rose"],
                    "base_notes": ["sandalwood", "amber"],
                    "accords": ["woody", "warm spicy"],
                    "avg_rating": 4.3,
                    "num_ratings": 892
                },
                "score": 0.89,
                "explanation": {
                    "primary_reason": "Similar to Tom Ford Oud Wood",
                    "shared_notes": [],
                    "shared_accords": [],
                    "quality_note": "Highly rated (4.3/5 from 892 reviews)",
                    "similarity_score": 0.89
                },
                "rank": 1
            }
        ],
        "processing_time_ms": 45.2
    }