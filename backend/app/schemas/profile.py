"""
Profile API Schemas
Pydantic models for profile endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime



# COMPONENT SCHEMAS 


class QuickStats(BaseModel):
    """User's quick statistics for dashboard cards"""
    fragrances_owned: int = Field(..., description="Number of fragrances in collection")
    avg_match_score: float = Field(..., ge=0, le=100, description="Average recommendation match score")
    notes_explored: int = Field(..., description="Number of unique notes user has explored")
    total_explorations: int = Field(..., description="Total fragrance exploration count")


class NoteBreakdownItem(BaseModel):
    """Single item in note breakdown donut chart"""
    name: str = Field(..., description="Note name (e.g., 'Vanilla')")
    value: float = Field(..., ge=0, le=100, description="Percentage of this note in user's profile")
    color: str = Field(..., description="Hex color for chart display")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Vanilla",
                "value": 35.0,
                "color": "#ff9ab3"
            }
        }


class AccordProfileItem(BaseModel):
    """Single item in accord/fragrance family bar chart"""
    name: str = Field(..., description="Accord/family name (e.g., 'Woody')")
    value: float = Field(..., ge=0, le=100, description="Percentage of this accord in profile")
    color: str = Field(..., description="Hex color for chart display")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Woody",
                "value": 45.0,
                "color": "#ff9ab3"
            }
        }


class RadarDataItem(BaseModel):
    """Single category in radar chart (scent personality map)"""
    category: str = Field(..., description="Fragrance family category")
    value: float = Field(..., ge=0, le=100, description="Score for this category (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Woody",
                "value": 90.0
            }
        }


class FragranceItem(BaseModel):
    """Fragrance in user's collection"""
    id: str = Field(..., description="Fragrance UUID")
    name: str = Field(..., description="Fragrance name")
    brand: str = Field(..., description="Brand name")
    match: int = Field(..., ge=0, le=100, description="Match score with user's profile")
    emoji: str = Field(..., description="Representative emoji based on fragrance type")
    top_notes: List[str] = Field(default_factory=list, description="Top notes")
    middle_notes: List[str] = Field(default_factory=list, description="Middle/heart notes")
    base_notes: List[str] = Field(default_factory=list, description="Base notes")
    accords: List[str] = Field(default_factory=list, description="Main accords/families")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Oud Wood",
                "brand": "Tom Ford",
                "match": 95,
                "emoji": "🌲",
                "top_notes": ["Rosewood", "Cardamom"],
                "middle_notes": ["Oud", "Sandalwood"],
                "base_notes": ["Vetiver", "Tonka Bean"],
                "accords": ["woody", "warm spicy", "earthy"]
            }
        }


class RecentActivityItem(BaseModel):
    """Single activity item in user's timeline"""
    action: str = Field(..., description="Description of the action")
    time: str = Field(..., description="Human-readable time (e.g., '2 hours ago')")
    timestamp: datetime = Field(..., description="Actual timestamp for sorting")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "Added Oud Wood to collection",
                "time": "2 hours ago",
                "timestamp": "2024-03-15T14:30:00Z"
            }
        }


class UserInfo(BaseModel):
    """User basic information"""
    name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    member_since: str = Field(..., description="Formatted join date (e.g., 'March 2024')")
    avatar: str = Field(..., description="User's initials for avatar display")
    quiz_completed: bool = Field(..., description="Whether user completed onboarding quiz")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sarah Mitchell",
                "email": "sarah@example.com",
                "member_since": "March 2024",
                "avatar": "SM",
                "quiz_completed": True
            }
        }



# MAIN RESPONSE SCHEMA

class ProfileResponse(BaseModel):
    """
    Complete user profile response with all analytics data
    This is returned by GET /api/v1/profile/{user_id}
    """
    user: UserInfo = Field(..., description="User basic information")
    stats: QuickStats = Field(..., description="Quick statistics for dashboard")
    note_breakdown: List[NoteBreakdownItem] = Field(..., description="Note distribution for donut chart")
    accord_profile: List[AccordProfileItem] = Field(..., description="Accord distribution for bar chart")
    radar_data: List[RadarDataItem] = Field(..., description="Fragrance personality radar chart data")
    fragrances: List[FragranceItem] = Field(..., description="User's fragrance collection")
    insights: List[str] = Field(..., description="Personalized insights and recommendations")
    recent_activity: List[RecentActivityItem] = Field(..., description="Recent user actions timeline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "name": "Sarah Mitchell",
                    "email": "sarah@example.com",
                    "member_since": "March 2024",
                    "avatar": "SM",
                    "quiz_completed": True
                },
                "stats": {
                    "fragrances_owned": 12,
                    "avg_match_score": 85.0,
                    "notes_explored": 8,
                    "total_explorations": 142
                },
                "note_breakdown": [
                    {"name": "Vanilla", "value": 35.0, "color": "#ff9ab3"},
                    {"name": "Bergamot", "value": 25.0, "color": "#ffb8a3"}
                ],
                "accord_profile": [
                    {"name": "Woody", "value": 45.0, "color": "#ff9ab3"},
                    {"name": "Fresh", "value": 30.0, "color": "#ffb8a3"}
                ],
                "radar_data": [
                    {"category": "Woody", "value": 90.0},
                    {"category": "Fresh", "value": 65.0}
                ],
                "fragrances": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Oud Wood",
                        "brand": "Tom Ford",
                        "match": 95,
                        "emoji": "🌲",
                        "top_notes": ["Rosewood", "Cardamom"],
                        "middle_notes": ["Oud", "Sandalwood"],
                        "base_notes": ["Vetiver", "Tonka Bean"],
                        "accords": ["woody", "warm spicy"]
                    }
                ],
                "insights": [
                    "You have a strong preference for woody fragrances (45%)",
                    "Consider exploring more citrus notes to balance your profile"
                ],
                "recent_activity": [
                    {
                        "action": "Added Oud Wood to collection",
                        "time": "2 hours ago",
                        "timestamp": "2024-03-15T14:30:00Z"
                    }
                ]
            }
        }



# NETWORK GRAPH SCHEMAS (For future network visualizer endpoint)


class NetworkNode(BaseModel):
    """Node in the fragrance network graph"""
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Node type: 'fragrance', 'note', 'accord'")
    community: int = Field(..., description="Community/cluster ID")
    size: Optional[float] = Field(None, description="Node size (based on importance)")
    color: Optional[str] = Field(None, description="Node color")


class NetworkEdge(BaseModel):
    """Edge/connection in the fragrance network graph"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    weight: float = Field(..., ge=0, le=1, description="Connection strength (0-1)")


class NetworkCommunity(BaseModel):
    """Detected community/cluster in network"""
    id: int = Field(..., description="Community ID")
    label: str = Field(..., description="Community label/description")
    size: int = Field(..., description="Number of nodes in community")
    color: str = Field(..., description="Community color")


class NetworkGraphResponse(BaseModel):
    """
    Network graph data response
    This will be returned by GET /api/v1/profile/{user_id}/network
    """
    nodes: List[NetworkNode] = Field(..., description="Graph nodes")
    edges: List[NetworkEdge] = Field(..., description="Graph edges/connections")
    communities: List[NetworkCommunity] = Field(..., description="Detected communities")
    stats: dict = Field(..., description="Graph statistics (num_nodes, num_edges, etc.)")



# REQUEST SCHEMAS (if needed for future endpoints)


class UpdatePreferencesRequest(BaseModel):
    """Request to update user preferences"""
    liked_notes: Optional[dict] = Field(None, description="Note ratings (note: importance)")
    liked_accords: Optional[dict] = Field(None, description="Accord ratings (accord: importance)")


class AddFragranceRequest(BaseModel):
    """Request to add fragrance to collection"""
    fragrance_id: str = Field(..., description="Fragrance UUID to add")
    owned: bool = Field(True, description="Whether user owns this fragrance")
    rating: Optional[int] = Field(None, ge=1, le=10, description="User's rating (1-10)")