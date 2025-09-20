
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Fragrance:
  
    id: str  # Change from int to str to handle UUIDs
    name: str
    brand: str
    notes: List[str]  # All notes combined
    top_notes: List[str]
    middle_notes: List[str] 
    base_notes: List[str]
    accords: List[str]  
    avg_rating: float  # 1-5 scale
    num_ratings: int

@dataclass 
class RecommendationResult:
    
    fragrance: Fragrance
    score: float
    explanation: Dict[str, float]  # Component scores for transparency

@dataclass
class NotePreference:
    
    name: str
    importance: int  # 1-10 scale
