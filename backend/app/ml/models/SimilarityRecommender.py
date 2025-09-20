import math
import logging
from typing import List, Dict, Tuple, Set, Optional, Union
from dataclasses import dataclass
from collections import defaultdict, Counter
from .base import Fragrance, RecommendationResult, NotePreference


@dataclass
class Fragrance:
   
    id: str  # Changed to str to handle UUIDs properly
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


class SimilarityRecommender:
    """
    Find fragrances similar to TARGET FRAGRANCE(S)
     supports both single fragrance and collection-based recommendations
    """
    
    def __init__(self, fragrances: List[Fragrance]):
        self.fragrances = {f.id: f for f in fragrances}
        self.note_frequencies = self._calculate_note_frequencies()
        self.accord_frequencies = self._calculate_accord_frequencies()
        self.max_ratings = max(f.num_ratings for f in fragrances) if fragrances else 1
        
        # Component weights for similarity matching
        self.NOTE_WEIGHT = 0.40
        self.ACCORD_WEIGHT = 0.25
        self.QUALITY_WEIGHT = 0.25
        self.POPULARITY_WEIGHT = 0.08
        self.DIVERSITY_WEIGHT = 0.02
        
        # Note position weights
        self.TOP_NOTE_WEIGHT = 0.25
        self.MIDDLE_NOTE_WEIGHT = 0.40
        self.BASE_NOTE_WEIGHT = 0.35
        
        logging.info(f"SimilarityRecommender initialized with {len(self.fragrances)} fragrances")

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

    def _create_collection_profile(self, target_fragrances: List[Fragrance]) -> Dict[str, any]:
       
        # Aggregate all notes and accords with frequency weighting
        note_counts = Counter()
        accord_counts = Counter()
        total_ratings = 0
        total_weighted_rating = 0
        
        for fragrance in target_fragrances:
            # Weight notes by fragrance quality (higher rated fragrances contribute more)
            quality_weight = max(fragrance.avg_rating / 5.0, 0.6)  # Minimum 0.6 weight
            
            for note in fragrance.notes:
                note_counts[note.lower()] += quality_weight
                
            for accord in fragrance.accords:
                accord_counts[accord.lower()] += quality_weight
                
            if fragrance.num_ratings > 0:
                total_ratings += fragrance.num_ratings
                total_weighted_rating += fragrance.avg_rating * fragrance.num_ratings
        
        # Convert to preference-like structure
        avg_collection_rating = total_weighted_rating / total_ratings if total_ratings > 0 else 3.5
        
        return {
            'note_preferences': note_counts,
            'accord_preferences': accord_counts,
            'collection_quality': avg_collection_rating,
            'collection_size': len(target_fragrances)
        }

    def _calculate_accord_similarity_multi(self, collection_accords: Counter, candidate_accords: List[str]) -> float:
       
        if not collection_accords or not candidate_accords:
            return 0.0
            
        candidate_set = {accord.lower().strip() for accord in candidate_accords}
        
        if not candidate_set:
            return 0.0
        
        # Calculate weighted similarity based on collection preferences
        weighted_similarity = 0.0
        total_preference_weight = sum(collection_accords.values())
        
        for accord in candidate_set:
            if accord in collection_accords:
                # Preference strength from collection
                preference_strength = collection_accords[accord] / total_preference_weight
                
                # Rarity bonus
                frequency = self.accord_frequencies.get(accord, 1)
                rarity_weight = 1 / math.log(frequency + 1)
                
                weighted_similarity += preference_strength * rarity_weight
        
        # Normalize by candidate accord coverage
        coverage_bonus = len(candidate_set & set(collection_accords.keys())) / len(candidate_set)
        
        final_similarity = (weighted_similarity * 0.7) + (coverage_bonus * 0.3)
        return min(final_similarity, 1.0)

    def _calculate_note_similarity_multi(self, collection_notes: Counter, candidate: Fragrance) -> float:
      
        if not collection_notes or not candidate.notes:
            return 0.0
            
        candidate_notes = {note.lower() for note in candidate.notes}
        
        if not candidate_notes:
            return 0.0
        
        # Calculate weighted similarity based on collection preferences
        weighted_similarity = 0.0
        total_preference_weight = sum(collection_notes.values())
        
        for note in candidate_notes:
            if note in collection_notes:
                # Preference strength from collection
                preference_strength = collection_notes[note] / total_preference_weight
                
                # Rarity bonus
                frequency = self.note_frequencies.get(note, 1)
                rarity_weight = 1 / math.log(frequency + 1)
                
                # Position bonus (if note appears in meaningful positions)
                position_bonus = self._get_collection_position_bonus(note, candidate)
                
                weighted_similarity += preference_strength * rarity_weight * position_bonus
        
        # Coverage bonus
        coverage = len(candidate_notes & set(collection_notes.keys())) / len(candidate_notes)
        
        final_similarity = (weighted_similarity * 0.8) + (coverage * 0.2)
        return min(final_similarity, 1.0)

    def _get_collection_position_bonus(self, note: str, candidate: Fragrance) -> float:
       
        bonus = 1.0
        
        # Give bonus for important positions
        if note.lower() in [n.lower() for n in candidate.middle_notes]:
            bonus += self.MIDDLE_NOTE_WEIGHT * 0.8  # Heart notes are most important
            
        if note.lower() in [n.lower() for n in candidate.base_notes]:
            bonus += self.BASE_NOTE_WEIGHT * 0.9   # Base notes for longevity
            
        if note.lower() in [n.lower() for n in candidate.top_notes]:
            bonus += self.TOP_NOTE_WEIGHT * 0.6    # Top notes less critical for similarity
            
        return min(bonus, 1.8)

    def _calculate_accord_similarity(self, target_accords: List[str], candidate_accords: List[str]) -> float:
        
        if not target_accords or not candidate_accords:
            return 0.0
            
        target_set = {accord.lower().strip() for accord in target_accords}
        candidate_set = {accord.lower().strip() for accord in candidate_accords}
        
        intersection = target_set & candidate_set
        union = target_set | candidate_set
        
        if not intersection:
            return 0.0
            
        # Apply rarity weighting for accords
        weighted_similarity = 0.0
        for accord in intersection:
            frequency = self.accord_frequencies.get(accord, 1)
            rarity_weight = 1 / math.log(frequency + 1)
            weighted_similarity += rarity_weight
            
        jaccard_base = len(intersection) / len(union)
        final_similarity = (jaccard_base * 0.3) + (min(weighted_similarity / len(union), 1.0) * 0.7)
        
        return min(final_similarity, 1.0)

    def _calculate_note_similarity(self, target_notes: List[str], candidate_notes: List[str], 
                                 target_fragrance: Fragrance, candidate_fragrance: Fragrance) -> float:
       
        if not target_notes or not candidate_notes:
            return 0.0
            
        target_set = {note.lower() for note in target_notes}
        candidate_set = {note.lower() for note in candidate_notes}
        
        intersection = target_set & candidate_set
        union = target_set | candidate_set
        
        if not intersection:
            return 0.0
            
        weighted_similarity = 0.0
        for note in intersection:
            frequency = self.note_frequencies.get(note, 1)
            rarity_weight = 1 / math.log(frequency + 1)
            position_bonus = self._get_position_bonus(note, target_fragrance, candidate_fragrance)
            weighted_similarity += rarity_weight * position_bonus
            
        jaccard_base = len(intersection) / len(union)
        final_similarity = (jaccard_base * 0.4) + (min(weighted_similarity / len(union), 1.0) * 0.6)
        
        return min(final_similarity, 1.0)

    def _get_position_bonus(self, note: str, target: Fragrance, candidate: Fragrance) -> float:
       
        bonus = 1.0
        
        if (note in [n.lower() for n in target.top_notes] and 
            note in [n.lower() for n in candidate.top_notes]):
            bonus += self.TOP_NOTE_WEIGHT
            
        if (note in [n.lower() for n in target.middle_notes] and 
            note in [n.lower() for n in candidate.middle_notes]):
            bonus += self.MIDDLE_NOTE_WEIGHT
            
        if (note in [n.lower() for n in target.base_notes] and 
            note in [n.lower() for n in candidate.base_notes]):
            bonus += self.BASE_NOTE_WEIGHT
            
        return min(bonus, 2.0)

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

    def _calculate_diversity_bonus(self, candidate: Fragrance, collection_profile: Dict, target_fragrances: List[Fragrance]) -> float:
        
        if not target_fragrances or len(target_fragrances) < 2:
            return 0.0
        
        # Check if candidate adds diversity to the collection
        candidate_accords = set(accord.lower() for accord in candidate.accords)
        
        # Find unique accords in candidate that aren't heavily represented in collection
        collection_accords = collection_profile.get('accord_preferences', Counter())
        total_accord_weight = sum(collection_accords.values())
        
        diversity_score = 0.0
        for accord in candidate_accords:
            # If accord is rare in collection, give bonus
            accord_weight = collection_accords.get(accord, 0)
            if total_accord_weight > 0:
                representation = accord_weight / total_accord_weight
                if representation < 0.3:  # Underrepresented accord
                    diversity_score += (0.3 - representation)
        
        return min(diversity_score, 0.5)  # Cap diversity bonus

    def get_recommendations(self, target_fragrance_ids: Union[str, List[str]], limit: int = 10) -> List[RecommendationResult]:
        """
        Find fragrances similar to target fragrance(s)
        
        Args:
            target_fragrance_ids: Single fragrance ID (str) or list of fragrance IDs
            limit: Number of recommendations to return
        """
        # Normalize input to list
        if isinstance(target_fragrance_ids, str):
            target_ids = [target_fragrance_ids]
        else:
            target_ids = target_fragrance_ids
            
        # Validate all target fragrances exist
        target_fragrances = []
        for target_id in target_ids:
            if target_id not in self.fragrances:
                raise ValueError(f"Fragrance {target_id} not found")
            target_fragrances.append(self.fragrances[target_id])
        
        if len(target_fragrances) == 1:
            return self._get_single_fragrance_recommendations(target_fragrances[0], limit)
        else:
            return self._get_collection_recommendations(target_fragrances, limit)

    def _get_single_fragrance_recommendations(self, target: Fragrance, limit: int) -> List[RecommendationResult]:
        
        candidates = []
        
        logging.info(f"Finding similar fragrances to: {target.name} by {target.brand}")
        
        for candidate_id, candidate in self.fragrances.items():
            if candidate_id == target.id:
                continue
                
            note_similarity = self._calculate_note_similarity(
                target.notes, candidate.notes, target, candidate
            )
            accord_similarity = self._calculate_accord_similarity(target.accords, candidate.accords)
            quality_score = self._calculate_quality_score(candidate.avg_rating, candidate.num_ratings)
            popularity_score = self._calculate_popularity_score(candidate.num_ratings)
            
            final_score = (
                note_similarity * self.NOTE_WEIGHT +
                accord_similarity * self.ACCORD_WEIGHT +
                quality_score * self.QUALITY_WEIGHT +
                popularity_score * self.POPULARITY_WEIGHT
            )
            
            explanation = {
                'note_similarity': note_similarity,
                'accord_similarity': accord_similarity,
                'quality_score': quality_score,
                'popularity_score': popularity_score,
                'final_score': final_score
            }
            
            candidates.append(RecommendationResult(
                fragrance=candidate,
                score=final_score,
                explanation=explanation
            ))
            
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]

    def _get_collection_recommendations(self, target_fragrances: List[Fragrance], limit: int) -> List[RecommendationResult]:
        
        candidates = []
        target_ids = {f.id for f in target_fragrances}
        collection_profile = self._create_collection_profile(target_fragrances)
        
        logging.info(f"Finding recommendations for collection of {len(target_fragrances)} fragrances")
        
        for candidate_id, candidate in self.fragrances.items():
            if candidate_id in target_ids:
                continue
                
            # Use multi-fragrance similarity calculations
            note_similarity = self._calculate_note_similarity_multi(
                collection_profile['note_preferences'], candidate
            )
            accord_similarity = self._calculate_accord_similarity_multi(
                collection_profile['accord_preferences'], candidate.accords
            )
            quality_score = self._calculate_quality_score(candidate.avg_rating, candidate.num_ratings)
            popularity_score = self._calculate_popularity_score(candidate.num_ratings)
            diversity_bonus = self._calculate_diversity_bonus(candidate, collection_profile, target_fragrances)
            
            # Adjust weights for collection analysis
            final_score = (
                note_similarity * self.NOTE_WEIGHT +
                accord_similarity * self.ACCORD_WEIGHT +
                quality_score * self.QUALITY_WEIGHT +
                popularity_score * self.POPULARITY_WEIGHT +
                diversity_bonus * self.DIVERSITY_WEIGHT
            )
            
            explanation = {
                'note_similarity': note_similarity,
                'accord_similarity': accord_similarity,
                'quality_score': quality_score,
                'popularity_score': popularity_score,
                'diversity_bonus': diversity_bonus,
                'final_score': final_score
            }
            
            candidates.append(RecommendationResult(
                fragrance=candidate,
                score=final_score,
                explanation=explanation
            ))
            
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]
    
    @classmethod
    def from_database_rows(cls, rows: List[Dict]) -> 'SimilarityRecommender':
        
        fragrances = []
        
        for row in rows:
            top_notes = cls._clean_note_list(row.get('top_notes', []))
            middle_notes = cls._clean_note_list(row.get('middle_notes', []))
            base_notes = cls._clean_note_list(row.get('base_notes', []))
            accords = cls._clean_note_list(row.get('main_accords', []))
            
            all_notes = top_notes + middle_notes + base_notes
            
            # Keep the original UUID as string
            fragrance_id = str(row['id'])
            
            fragrance = Fragrance(
                id=fragrance_id,
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
    def _clean_note_list(note_list) -> List[str]:
       
        if not note_list:
            return []
        
        if isinstance(note_list, list):
            return [str(note).strip().lower() for note in note_list if note and str(note).strip()]
        
        # Fallback to string parsing if somehow it's still a string
        if isinstance(note_list, str):
            return [note.strip().lower() for note in note_list.split(',') if note.strip()]
        
        return []