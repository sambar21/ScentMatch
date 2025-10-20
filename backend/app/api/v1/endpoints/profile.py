from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
import time
import logging
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.UserFragranceProfile import UserScentProfile, UserFragrance
from app.models.user import User as UserModel
from app.models.fragrance import Fragrance as FragranceModel
from app.core.database import get_db  # ← REMOVED AsyncSessionLocal import
from app.schemas.profile import (
    ProfileResponse,
    QuickStats,
    NoteBreakdownItem,
    AccordProfileItem,
    RadarDataItem,
    FragranceItem,
    RecentActivityItem,
    UserInfo
)

router = APIRouter(prefix="/profile", tags=["profile"])
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

GRADIENT_COLORS = [
    "#ff9ab3",  # Pink
    "#ffb8a3",  # Pink-Orange
    "#ffd09e",  # Orange
    "#ffe4b8",  # Light Orange
    "#fff0d6"   # Pale Orange
]

DEFAULT_INSIGHTS = [
    "Start by completing your fragrance quiz to get personalized insights",
    "Add fragrances to your collection to see your scent profile",
    "Explore different fragrance families to discover your signature scent"
]


# ============================================================================
# HELPER FUNCTIONS (NO CHANGES HERE)
# ============================================================================

def get_user_initials(name: str) -> str:
    """Generate user avatar initials"""
    if not name:
        return "?"
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "??"


def format_time_ago(dt: Optional[datetime]) -> str:
    """Convert datetime to 'X hours/days ago' format"""
    if not dt:
        return "Recently"
    
    # ← ADDED: Ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def calculate_note_breakdown(
    user_profile: Optional[UserScentProfile],
    owned_fragrances: List[FragranceModel]
) -> List[NoteBreakdownItem]:
    """Calculate note breakdown with fallbacks for missing data"""
    note_scores = Counter()
    
    try:
        # Add user's liked notes (from quiz) with higher weight
        if user_profile and user_profile.liked_notes:
            for note, importance in user_profile.liked_notes.items():
                note_scores[note.lower()] += importance * 0.6
        
        # Add notes from owned fragrances
        for frag in owned_fragrances:
            all_notes = (frag.top_notes or []) + (frag.middle_notes or []) + (frag.base_notes or [])
            for note in all_notes:
                note_scores[note.lower()] += 0.4
        
        # Get top 5 notes
        top_notes = note_scores.most_common(5)
        
        if not top_notes:
            return []
        
        # Calculate percentages
        total = sum(score for _, score in top_notes)
        
        result = []
        for idx, (note, score) in enumerate(top_notes):
            result.append(NoteBreakdownItem(
                name=note.capitalize(),
                value=round((score / total) * 100, 1) if total > 0 else 0,
                color=GRADIENT_COLORS[idx % len(GRADIENT_COLORS)]
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating note breakdown: {str(e)}")
        return []


def calculate_accord_profile(
    user_profile: Optional[UserScentProfile],
    owned_fragrances: List[FragranceModel]
) -> List[AccordProfileItem]:
    """Calculate accord/fragrance family profile with fallbacks"""
    accord_scores = Counter()
    
    try:
        # Add user's liked accords (from quiz)
        if user_profile and user_profile.liked_accords:
            for accord, importance in user_profile.liked_accords.items():
                accord_scores[accord.lower()] += importance * 0.5
        
        # Add accords from owned fragrances
        for frag in owned_fragrances:
            if frag.main_accords:
                for accord in frag.main_accords:
                    accord_scores[accord.lower()] += 0.5
        
        # Get top 5 accords
        top_accords = accord_scores.most_common(5)
        
        if not top_accords:
            return []
        
        # Calculate percentages
        total = sum(score for _, score in top_accords)
        
        result = []
        for idx, (accord, score) in enumerate(top_accords):
            result.append(AccordProfileItem(
                name=accord.capitalize(),
                value=round((score / total) * 100, 1) if total > 0 else 0,
                color=GRADIENT_COLORS[idx % len(GRADIENT_COLORS)]
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating accord profile: {str(e)}")
        return []


def calculate_radar_data(accord_profile: List[AccordProfileItem]) -> List[RadarDataItem]:
    """Convert accord profile to radar chart format"""
    common_families = ['woody', 'fresh', 'floral', 'oriental', 'citrus', 'spicy']
    accord_lookup = {item.name.lower(): item.value for item in accord_profile}
    
    result = []
    for family in common_families:
        value = accord_lookup.get(family, 5.0)
        result.append(RadarDataItem(category=family.capitalize(), value=value))
    
    return result


def generate_insights(
    note_breakdown: List[NoteBreakdownItem],
    accord_profile: List[AccordProfileItem],
    owned_fragrances: List[FragranceModel],
    user_profile: Optional[UserScentProfile]
) -> List[str]:
    """Generate personalized insights with fallbacks"""
    try:
        insights = []
        
        # Check if user has completed quiz
        if not user_profile or not user_profile.onboarding_complete:
            return DEFAULT_INSIGHTS
        
        # Insight 1: Dominant accord
        if accord_profile:
            top_accord = accord_profile[0]
            insights.append(
                f"You have a strong preference for {top_accord.name.lower()} fragrances ({top_accord.value:.0f}%)"
            )
        
        # Insight 2: Collection analysis
        if len(owned_fragrances) >= 5:
            insights.append("Your collection leans toward evening/formal scents")
        elif len(owned_fragrances) > 0:
            insights.append("You're building a versatile fragrance wardrobe")
        else:
            insights.append("Start adding fragrances to your collection to build your profile")
        
        # Insight 3: Suggestion based on gaps
        if accord_profile:
            present_accords = {item.name.lower() for item in accord_profile}
            suggestions = []
            
            if 'citrus' not in present_accords and 'fresh' not in present_accords:
                suggestions.append('citrus')
            if 'floral' not in present_accords:
                suggestions.append('floral')
            if 'spicy' not in present_accords and 'oriental' not in present_accords:
                suggestions.append('spicy')
            
            if suggestions:
                insights.append(
                    f"Consider exploring more {suggestions[0]} notes to balance your profile"
                )
        
        return insights if insights else DEFAULT_INSIGHTS
    
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return DEFAULT_INSIGHTS


def get_fragrance_emoji(fragrance: Optional[FragranceModel]) -> str:
    """Assign emoji based on dominant accord/notes"""
    if not fragrance:
        return "💙"
    
    try:
        accords = [a.lower() for a in (fragrance.main_accords or [])]
        notes = [n.lower() for n in ((fragrance.top_notes or []) + (fragrance.middle_notes or []) + (fragrance.base_notes or []))]
        
        if any(acc in accords for acc in ['woody', 'earthy']):
            return "🌲"
        elif any(acc in accords for acc in ['fresh', 'aquatic', 'marine']):
            return "🌊"
        elif any(acc in accords for acc in ['floral', 'powdery']):
            return "🌸"
        elif any(acc in accords for acc in ['citrus']):
            return "🍋"
        elif any(acc in accords for acc in ['oriental', 'amber', 'warm spicy']):
            return "🔥"
        elif any(acc in accords for acc in ['sweet', 'gourmand']):
            return "🍰"
        elif any(note in notes for note in ['vanilla', 'tonka']):
            return "🍦"
        elif any(note in notes for note in ['rose', 'jasmine']):
            return "🌹"
        elif any(note in notes for note in ['leather', 'tobacco']):
            return "🎩"
        else:
            return "💙"
    except Exception:
        return "💙"


# ============================================================================
# MAIN ENDPOINT - THIS IS WHERE THE CHANGES ARE
# ============================================================================

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)  # ← This gives us a database session
) -> ProfileResponse:
    """
    Get comprehensive user profile with graceful fallbacks for incomplete data.
    
    Returns profile data even if user hasn't completed quiz or has no fragrances.
    """
    start_time = time.time()
    correlation_id = str(user_id)[:8]
    
    try:
        logger.info(f"[{correlation_id}] Loading profile for user {user_id}")
        logger.info(f"[{correlation_id}] User ID type: {type(user_id)}")
        
        # 1. Get user - REQUIRED
        user_result = await db.execute(
            select(UserModel).filter(UserModel.id == user_id)
        )
        user = user_result.scalars().first()
        
        logger.info(f"[{correlation_id}] Query executed. User found: {user is not None}")
        
        if not user:
            # Let's check if ANY users exist
            all_users_result = await db.execute(select(UserModel))
            all_users = all_users_result.scalars().all()
            logger.warning(f"[{correlation_id}] User not found: {user_id}")
            logger.warning(f"[{correlation_id}] Total users in database: {len(all_users)}")
            if all_users:
                logger.warning(f"[{correlation_id}] Sample user IDs: {[str(u.id) for u in all_users[:3]]}")
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}"
            )
        
        logger.info(f"[{correlation_id}] Found user: {user.email}")
        
        # 2. Get user scent profile (OPTIONAL - might not have completed quiz)
        user_profile = None
        try:
            # ← CHANGED: session.execute → db.execute
            profile_result = await db.execute(
                select(UserScentProfile).filter(UserScentProfile.user_id == user_id)
            )
            user_profile = profile_result.scalars().first()
            if user_profile:
                logger.info(f"[{correlation_id}] Found user scent profile")
            else:
                logger.info(f"[{correlation_id}] No scent profile - user hasn't completed quiz")
        except Exception as e:
            logger.warning(f"[{correlation_id}] Error fetching scent profile: {str(e)}")
        
        # 3. Get owned fragrances (OPTIONAL - might not have any)
        owned_fragrances = []
        try:
            # ← CHANGED: session.execute → db.execute
            owned_result = await db.execute(
                select(UserFragrance).filter(
                    UserFragrance.user_id == user_id,
                    UserFragrance.owned == True
                )
            )
            user_fragrances = owned_result.scalars().all()
            
            if user_fragrances:
                fragrance_ids = [uf.fragrance_id for uf in user_fragrances]
                # ← CHANGED: session.execute → db.execute
                frag_result = await db.execute(
                    select(FragranceModel).filter(FragranceModel.id.in_(fragrance_ids))
                )
                owned_fragrances = frag_result.scalars().all()
                logger.info(f"[{correlation_id}] Found {len(owned_fragrances)} owned fragrances")
            else:
                logger.info(f"[{correlation_id}] User has no owned fragrances")
        except Exception as e:
            logger.warning(f"[{correlation_id}] Error fetching fragrances: {str(e)}")
        
        # 4. Calculate analytics (all have fallbacks)
        note_breakdown = calculate_note_breakdown(user_profile, owned_fragrances)
        accord_profile = calculate_accord_profile(user_profile, owned_fragrances)
        radar_data = calculate_radar_data(accord_profile)
        insights = generate_insights(note_breakdown, accord_profile, owned_fragrances, user_profile)
        
        # 5. Build quick stats
        notes_explored = 0
        if user_profile and user_profile.liked_notes:
            notes_explored = len(user_profile.liked_notes)
        
        stats = QuickStats(
            fragrances_owned=len(owned_fragrances),
            avg_match_score=85.0,  # Placeholder
            notes_explored=notes_explored,
            total_explorations=len(owned_fragrances) * 10
        )
        
        # 6. Format fragrances
        fragrance_items = []
        for idx, frag in enumerate(owned_fragrances[:6]):
            try:
                fragrance_items.append(FragranceItem(
                    id=str(frag.id),
                    name=frag.name.replace('-', ' ').replace('_', ' ').title(),
                    brand=frag.brand_name.replace('-', ' ').replace('_', ' ').title(),
                    match=95 - (idx * 2),
                    emoji=get_fragrance_emoji(frag),
                    top_notes=frag.top_notes or [],
                    middle_notes=frag.middle_notes or [],
                    base_notes=frag.base_notes or [],
                    accords=frag.main_accords or []
                ))
            except Exception as e:
                logger.warning(f"[{correlation_id}] Error formatting fragrance {frag.id}: {str(e)}")
        
        # 7. Build recent activity
        recent_activity = []
        try:
            if user_profile and user_profile.onboarding_complete_at:
                recent_activity.append(RecentActivityItem(
                    action="Completed fragrance quiz",
                    time=format_time_ago(user_profile.onboarding_complete_at),
                    timestamp=user_profile.onboarding_complete_at
                ))
            
            if owned_fragrances:
                recent_activity.append(RecentActivityItem(
                    action=f"Added {owned_fragrances[0].name} to collection",
                    time="Recently",
                    timestamp=datetime.now(timezone.utc)
                ))
            
            if user.last_login:
                recent_activity.append(RecentActivityItem(
                    action="Last login",
                    time=format_time_ago(user.last_login),
                    timestamp=user.last_login
                ))
        except Exception as e:
            logger.warning(f"[{correlation_id}] Error building recent activity: {str(e)}")
        
        # 8. Build user info
        user_info = UserInfo(
            name=user.display_name or user.email.split('@')[0],
            email=user.email,
            member_since=user.created_at.strftime("%B %Y") if user.created_at else "Recently",
            avatar=get_user_initials(user.display_name or user.email),
            quiz_completed=user_profile.onboarding_complete if user_profile else False
        )
        
        # 9. Build response
        response = ProfileResponse(
            user=user_info,
            stats=stats,
            note_breakdown=note_breakdown,
            accord_profile=accord_profile,
            radar_data=radar_data,
            fragrances=fragrance_items,
            insights=insights,
            recent_activity=recent_activity
        )
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"[{correlation_id}] Profile loaded successfully in {processing_time:.1f}ms")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{correlation_id}] Unexpected error loading profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load user profile"
        )