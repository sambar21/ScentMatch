import math
import logging
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
from .base import Fragrance, RecommendationResult, NotePreference


@dataclass
class Fragrance:
   
    id: int
    name: str
    brand: str
    notes: List[str]  # All notes combined
    top_notes: List[str]
    middle_notes: List[str] 
    base_notes: List[str]
    accords: List[str]  # Main accords - this is the gold!
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


class NoteBasedRecommender:
    """
    LEVEL 1: Find fragrances based on USER'S NOTE PREFERENCES
    For users who say: "I love vanilla=9, cedar=8, hate patchouli=2"
    This is the TRUE base class for the recommendation hierarchy
    """
    
    def __init__(self, fragrances: List[Fragrance]):
        self.fragrances = {f.id: f for f in fragrances}
        self.note_frequencies = self._calculate_note_frequencies()
        self.accord_frequencies = self._calculate_accord_frequencies()
        self.max_ratings = max(f.num_ratings for f in fragrances) if fragrances else 1
        
        # Component weights for note-based matching
        self.NOTE_PREFERENCE_WEIGHT = 0.45  # User's stated note preferences
        self.ACCORD_PREFERENCE_WEIGHT = 0.30  # User's stated accord preferences  
        self.QUALITY_WEIGHT = 0.20  # Quality still matters
        self.POPULARITY_WEIGHT = 0.05  # Less important for personalized recs
        
        logging.info(f"NoteBasedRecommender initialized with {len(self.fragrances)} fragrances")

    def _calculate_note_frequencies(self) -> Dict[str, int]:
       
        frequencies = Counter()
        for fragrance in self.fragrances.values():
            for note in fragrance.notes:
                frequencies[note.lower()] += 1
        return dict(frequencies)

    def _calculate_accord_frequencies(self) -> Dict[str, int]:
        
        frequencies = Counter()
        for fragrance in self.fragrances.values():
            for accord in fragrance.accords:
                frequencies[accord.lower()] += 1
        return dict(frequencies)

    def _calculate_note_preference_match(self, fragrance_notes: List[str], 
                                       user_note_preferences: List[NotePreference]) -> float:
        """
        Calculate how well a fragrance matches user's note preferences
        Returns weighted score based on user's importance ratings
        """
        if not user_note_preferences or not fragrance_notes:
            return 0.0
            
        # Create lookup for user preferences
        user_prefs = {pref.name.lower(): pref.importance for pref in user_note_preferences}
        fragrance_note_set = {note.lower() for note in fragrance_notes}
        
        # Calculate weighted match score
        total_preference_weight = 0
        matched_weight = 0
        
        for note_name, importance in user_prefs.items():
            total_preference_weight += importance
            
            if note_name in fragrance_note_set:
                # Apply rarity bonus - rare notes that match user preference are very valuable
                frequency = self.note_frequencies.get(note_name, 1)
                rarity_multiplier = 1 + (1 / math.log(frequency + 1)) * 0.5  # Bonus up to 1.5x
                
                matched_weight += importance * rarity_multiplier
        
        if total_preference_weight == 0:
            return 0.0
            
        # Normalize by total possible weight
        preference_match = matched_weight / total_preference_weight
        
        # Apply coverage bonus - reward fragrances that match multiple preferences
        coverage = len(fragrance_note_set & set(user_prefs.keys())) / len(user_prefs)
        coverage_bonus = coverage * 0.2  # Up to 20% bonus for good coverage
        
        return min(preference_match + coverage_bonus, 1.0)

    def _calculate_accord_preference_match(self, fragrance_accords: List[str], 
                                         user_accord_preferences: List[NotePreference]) -> float:
        
        if not user_accord_preferences or not fragrance_accords:
            return 0.0
            
        user_prefs = {pref.name.lower(): pref.importance for pref in user_accord_preferences}
        fragrance_accord_set = {accord.lower() for accord in fragrance_accords}
        
        total_preference_weight = 0
        matched_weight = 0
        
        for accord_name, importance in user_prefs.items():
            total_preference_weight += importance
            
            if accord_name in fragrance_accord_set:
                frequency = self.accord_frequencies.get(accord_name, 1)
                rarity_multiplier = 1 + (1 / math.log(frequency + 1)) * 0.3
                matched_weight += importance * rarity_multiplier
        
        if total_preference_weight == 0:
            return 0.0
            
        preference_match = matched_weight / total_preference_weight
        coverage = len(fragrance_accord_set & set(user_prefs.keys())) / len(user_prefs)
        coverage_bonus = coverage * 0.25  # Accords get slightly higher coverage bonus
        
        return min(preference_match + coverage_bonus, 1.0)

    def _wilson_score(self, positive_ratings: float, total_ratings: int) -> float:
       
        if total_ratings == 0:
            return 0.0
            
        p = positive_ratings / total_ratings
        n = total_ratings
        z = 1.96
        
        if n == 0:
            return 0
            
        denominator = 1 + z * z / n
        numerator = p + z * z / (2 * n) - z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
        
        return max(numerator / denominator, 0.0)

    def _calculate_quality_score(self, avg_rating: float, num_ratings: int) -> float:
        
        if num_ratings == 0 or avg_rating == 0:
            return 0.0
            
        positive_ratio = max((avg_rating - 2.5) / 2.5, 0)
        positive_ratings = num_ratings * positive_ratio
        
        return self._wilson_score(positive_ratings, num_ratings)

    def _calculate_popularity_score(self, num_ratings: int) -> float:
        
        if num_ratings == 0:
            return 0.0
            
        normalized = math.log(num_ratings + 1) / math.log(self.max_ratings + 1)
        return min(normalized, 1.0)

    def get_recommendations(self, preferred_notes: List[NotePreference] = None,
                          preferred_accords: List[NotePreference] = None,
                          limit: int = 10) -> List[RecommendationResult]:
        """
        Get recommendations based on user's note and accord preferences
        
        Args:
            preferred_notes: List of notes with importance ratings (1-10)
            preferred_accords: List of accords with importance ratings (1-10)
            limit: Number of recommendations to return
            
        Returns:
            List of RecommendationResult objects
        """
        if not preferred_notes and not preferred_accords:
            raise ValueError("Must provide either preferred notes or preferred accords")
            
        preferred_notes = preferred_notes or []
        preferred_accords = preferred_accords or []
        
        candidates = []
        
        logging.info(f"Finding fragrances for note preferences: {[f'{p.name}={p.importance}' for p in preferred_notes[:3]]}")
        logging.info(f"Finding fragrances for accord preferences: {[f'{p.name}={p.importance}' for p in preferred_accords[:3]]}")
        
        for fragrance in self.fragrances.values():
            # Calculate component scores
            note_match = self._calculate_note_preference_match(fragrance.notes, preferred_notes)
            accord_match = self._calculate_accord_preference_match(fragrance.accords, preferred_accords)
            quality_score = self._calculate_quality_score(fragrance.avg_rating, fragrance.num_ratings)
            popularity_score = self._calculate_popularity_score(fragrance.num_ratings)
            
            # Combined weighted score
            final_score = (
                note_match * self.NOTE_PREFERENCE_WEIGHT +
                accord_match * self.ACCORD_PREFERENCE_WEIGHT +
                quality_score * self.QUALITY_WEIGHT +
                popularity_score * self.POPULARITY_WEIGHT
            )
            
            explanation = {
                'note_preference_match': note_match,
                'accord_preference_match': accord_match,
                'quality_score': quality_score,
                'popularity_score': popularity_score,
                'final_score': final_score
            }
            
            candidates.append(RecommendationResult(
                fragrance=fragrance,
                score=final_score,
                explanation=explanation
            ))
            
        # Sort by score
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        result = candidates[:limit]
        
        logging.info(f"Returning {len(result)} note-based recommendations")
        for i, rec in enumerate(result[:3]):
            logging.info(f"#{i+1}: {rec.fragrance.name} (score: {rec.score:.3f})")
            
        return result

    def explain_recommendation(self, recommendation: RecommendationResult, 
                             user_note_preferences: List[NotePreference],
                             user_accord_preferences: List[NotePreference]) -> str:
        
        exp = recommendation.explanation
        fragrance = recommendation.fragrance
        
        explanation_parts = []
        
        # Note matches
        user_notes = {p.name.lower(): p.importance for p in user_note_preferences}
        fragrance_notes = {note.lower() for note in fragrance.notes}
        matched_notes = fragrance_notes & set(user_notes.keys())
        
        if matched_notes:
            high_importance_matches = [note for note in matched_notes if user_notes[note] >= 7]
            if high_importance_matches:
                note_list = ', '.join(high_importance_matches[:3])
                explanation_parts.append(f"contains your favorite notes ({note_list})")
        
        # Accord matches  
        user_accords = {p.name.lower(): p.importance for p in user_accord_preferences}
        fragrance_accords = {accord.lower() for accord in fragrance.accords}
        matched_accords = fragrance_accords & set(user_accords.keys())
        
        if matched_accords:
            high_importance_matches = [accord for accord in matched_accords if user_accords[accord] >= 7]
            if high_importance_matches:
                accord_list = ', '.join(high_importance_matches[:2])
                explanation_parts.append(f"matches your preferred style ({accord_list})")
        
        # Quality
        if exp['quality_score'] > 0.6:
            explanation_parts.append(f"highly rated ({fragrance.avg_rating:.1f}/5)")
            
        if explanation_parts:
            return f"Recommended because it {' and '.join(explanation_parts)}."
        else:
            return f"Recommended based on your preferences (score: {recommendation.score:.2f})."

    
    
    @classmethod
    def from_database_rows(cls, rows: List[Dict]) -> 'NoteBasedRecommender':  # or SimilarityRecommender
       
        fragrances = []
        
        for row in rows:
            top_notes = cls._clean_note_list(row.get('top_notes', []))
            middle_notes = cls._clean_note_list(row.get('middle_notes', []))
            base_notes = cls._clean_note_list(row.get('base_notes', []))
            accords = cls._clean_note_list(row.get('main_accords', []))
            
            all_notes = top_notes + middle_notes + base_notes
            
            # Keep the original UUID as string - DON'T convert to integer
            fragrance_id = str(row['id'])  # Keep as UUID string
            
            fragrance = Fragrance(
                id=fragrance_id,  # Use UUID string directly
                name=str(row['name']),
                brand=str(row['brand_name']),
                notes=all_notes,
                top_notes=top_notes,
                middle_notes=middle_notes,
                base_notes=base_notes,
                accords=accords,
                avg_rating=float(row.get('average_rating', 0.0)),
                num_ratings=int(row.get('total_ratings', 0))
            )
            
            fragrances.append(fragrance)
            
        return cls(fragrances)

    @staticmethod
    def _parse_notes_string(notes_data) -> List[str]:
        
        
        # If it's already a list, clean and return it
        if isinstance(notes_data, list):
            return [note.strip().lower() for note in notes_data if note and str(note).strip()]
        
        # If it's a string, split by comma
        if isinstance(notes_data, str):
            if not notes_data:
                return []
            return [note.strip().lower() for note in notes_data.split(',') if note.strip()]
        
        # If it's None or other type, return empty list
        return []
    
    @staticmethod
    def _clean_note_list(note_list) -> List[str]:
        
        if not note_list:
            return []
        
        if isinstance(note_list, list):
            return [str(note).strip().lower() for note in note_list if note and str(note).strip()]
        
        # Fallback to string parsing if somehow it's still a string
        if isinstance(note_list, str):
            return [note.strip().lower() for note in note_list.split(',') if note.strip()]
        
        return []



