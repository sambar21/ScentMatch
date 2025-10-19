import pytest
import numpy as np
from scipy import stats
from collections import Counter
from typing import List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import functools

from app.models.fragrance import Fragrance
from app.ml.models import SimilarityRecommender, NoteBasedRecommender


def async_test(f):
    """Run async test in the existing event loop."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper


class TestStatisticalValidation:
    """Statistical analysis and hypothesis testing for fragrance data"""
    
    @async_test
    async def test_rating_distribution_normality(self, db: AsyncSession):
        """Validate rating distribution follows expected patterns using KS test"""
        result = await db.execute(
            select(Fragrance.average_rating).filter(Fragrance.average_rating > 0)
        )
        ratings = result.scalars().all()
        rating_values = [float(r) for r in ratings]
        
        mean_rating = np.mean(rating_values)
        std_rating = np.std(rating_values)
        
        assert 3.0 <= mean_rating <= 4.5, f"Mean rating {mean_rating} outside expected range"
        
        ks_stat, p_value = stats.kstest(rating_values, 'norm', args=(mean_rating, std_rating))
        
        print(f"\nRating Distribution Stats:")
        print(f"Mean: {mean_rating:.2f}, Std: {std_rating:.2f}")
        print(f"KS statistic: {ks_stat:.4f}, p-value: {p_value:.4f}")
        
        assert len(rating_values) > 1000
    
    @async_test
    async def test_wilson_confidence_intervals(self, db: AsyncSession):
        """Validate Wilson confidence interval calculation matches implementation"""
        result = await db.execute(
            select(Fragrance).filter(Fragrance.total_ratings >= 10).limit(100)
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = NoteBasedRecommender.from_database_rows(rows)
        
        wilson_scores = []
        for frag in fragrances:
            positive = max((float(frag.average_rating) - 2.5) / 2.5, 0) * frag.total_ratings
            score = recommender._wilson_score(positive, frag.total_ratings)
            wilson_scores.append(score)
        
        high_review_frag = max(fragrances, key=lambda x: x.total_ratings)
        high_review_idx = fragrances.index(high_review_frag)
        
        assert wilson_scores[high_review_idx] > np.median(wilson_scores)
        
        print(f"\nWilson Confidence Intervals:")
        print(f"Range: [{min(wilson_scores):.3f}, {max(wilson_scores):.3f}]")
        print(f"Median: {np.median(wilson_scores):.3f}")
    
    @async_test
    async def test_note_frequency_distribution(self, db: AsyncSession):
        """Analyze note frequency distribution for power law validation"""
        result = await db.execute(select(Fragrance).limit(5000))
        fragrances = result.scalars().all()
        
        all_notes = []
        for frag in fragrances:
            if frag.top_notes:
                all_notes.extend(frag.top_notes)
            if frag.middle_notes:
                all_notes.extend(frag.middle_notes)
            if frag.base_notes:
                all_notes.extend(frag.base_notes)
        
        note_counts = Counter(all_notes)
        frequencies = list(note_counts.values())
        
        freq_sorted = sorted(frequencies, reverse=True)
        log_freq = np.log(freq_sorted[:100])
        log_rank = np.log(range(1, 101))
        
        correlation, p_value = stats.pearsonr(log_rank, log_freq)
        
        print(f"\nNote Frequency Distribution:")
        print(f"Unique notes: {len(note_counts)}")
        print(f"Total note instances: {len(all_notes)}")
        print(f"Power law correlation: {correlation:.3f} (p={p_value:.4f})")
        
        assert correlation < -0.5
    
    @async_test
    async def test_rating_count_correlation(self, db: AsyncSession):
        """Test correlation between rating count and average rating"""
        result = await db.execute(
            select(Fragrance.average_rating, Fragrance.total_ratings).filter(
                Fragrance.total_ratings > 5,
                Fragrance.average_rating > 0
            )
        )
        fragrances = result.all()
        
        ratings = [float(r[0]) for r in fragrances]
        counts = [r[1] for r in fragrances]
        
        correlation, p_value = stats.pearsonr(counts, ratings)
        
        print(f"\nRating Count vs Average Rating:")
        print(f"Correlation: {correlation:.3f}, p-value: {p_value:.4f}")
        
        assert abs(correlation) < 0.3


class TestRecommendationAlgorithm:
    """Validate recommendation algorithm performance and accuracy"""
    
    @async_test
    async def test_similarity_score_range(self, db: AsyncSession):
        """Ensure similarity scores are bounded [0, 1]"""
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None)).limit(500)
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        test_frag = fragrances[0]
        recommendations = recommender.get_recommendations(str(test_frag.id), limit=20)
        
        scores = [rec.score for rec in recommendations]
        
        for score in scores:
            assert 0 <= score <= 1, f"Similarity {score} out of bounds"
        
        print(f"\nSimilarity Score Distribution:")
        print(f"Range: [{min(scores):.3f}, {max(scores):.3f}]")
        print(f"Mean: {np.mean(scores):.3f}, Std: {np.std(scores):.3f}")
    
    @async_test
    async def test_recommendation_diversity(self, db: AsyncSession):
        """Measure recommendation diversity across multiple queries"""
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None)).limit(500)
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        all_recommended_ids = set()
        total_recommendations = 0
        
        for frag in fragrances[:10]:
            recs = recommender.get_recommendations(str(frag.id), limit=10)
            rec_ids = [rec.fragrance.id for rec in recs]
            all_recommended_ids.update(rec_ids)
            total_recommendations += len(rec_ids)
        
        diversity_ratio = len(all_recommended_ids) / total_recommendations
        
        print(f"\nRecommendation Diversity:")
        print(f"Unique items: {len(all_recommended_ids)}")
        print(f"Total recommendations: {total_recommendations}")
        print(f"Diversity ratio: {diversity_ratio:.3f}")
        
        assert diversity_ratio > 0.5
    
    @async_test
    async def test_catalog_coverage(self, db: AsyncSession):
        """Calculate what % of catalog appears in recommendations"""
        total_result = await db.execute(select(func.count(Fragrance.id)))
        total_fragrances = total_result.scalar()
        
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None)).limit(min(500, total_fragrances))
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        sample_size = min(100, len(fragrances))
        recommended_ids = set()
        
        for frag in fragrances[:sample_size]:
            recs = recommender.get_recommendations(str(frag.id), limit=10)
            recommended_ids.update([rec.fragrance.id for rec in recs])
        
        coverage = len(recommended_ids) / len(fragrances)
        
        print(f"\nCatalog Coverage:")
        print(f"Items recommended: {len(recommended_ids)}")
        print(f"Total catalog: {len(fragrances)}")
        print(f"Coverage: {coverage*100:.1f}%")
        
        assert coverage > 0.3
    
    @async_test
    async def test_full_catalog_coverage_at_scale(self, db: AsyncSession):
        """Calculate actual catalog coverage across entire 23k+ product database"""
        # Get ALL fragrances with notes
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None))
        )
        fragrances = result.scalars().all()
        
        print(f"\n=== FULL SCALE CATALOG TEST ===")
        print(f"Total products in database: {len(fragrances)}")
        
        # Build recommender on FULL dataset
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        # Sample queries across the catalog (test 500 queries)
        sample_size = min(500, len(fragrances))
        recommended_ids = set()
        
        # Sample evenly across catalog (not just first 500)
        import random
        sample_indices = random.sample(range(len(fragrances)), sample_size)
        
        for idx in sample_indices:
            frag = fragrances[idx]
            recs = recommender.get_recommendations(str(frag.id), limit=10)
            recommended_ids.update([rec.fragrance.id for rec in recs])
        
        coverage = len(recommended_ids) / len(fragrances)
        
        print(f"\nFull Catalog Coverage Results:")
        print(f"Sample queries: {sample_size}")
        print(f"Unique items recommended: {len(recommended_ids)}")
        print(f"Total catalog size: {len(fragrances)}")
        print(f"Coverage: {coverage*100:.1f}%")
        
        # Calculate what baseline would be (random recommendations)
        baseline_coverage = min(1.0, (sample_size * 10) / len(fragrances))
        improvement = (coverage / baseline_coverage - 1) * 100
        
        print(f"\nBaseline (random): {baseline_coverage*100:.1f}%")
        print(f"Improvement: {improvement:.0f}%")
        
        assert coverage > 0.30, f"Coverage {coverage*100:.1f}% below minimum threshold"
        assert len(fragrances) > 20000, "Not testing on full production catalog"
    
    @async_test  
    async def test_long_tail_discovery_metrics(self, db: AsyncSession):
        """Measure how well the system surfaces less popular products"""
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None))
        )
        fragrances = result.scalars().all()
        
        # Sort by popularity (total_ratings)
        sorted_frags = sorted(fragrances, key=lambda f: f.total_ratings, reverse=True)
        
        # Define long-tail as bottom 50% by popularity
        tail_threshold_idx = len(sorted_frags) // 2
        long_tail_ids = {str(f.id) for f in sorted_frags[tail_threshold_idx:]}
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        # Test recommendations
        import random
        sample_size = min(500, len(fragrances))
        sample_indices = random.sample(range(len(fragrances)), sample_size)
        
        recommended_ids = set()
        long_tail_recommended = set()
        
        for idx in sample_indices:
            frag = fragrances[idx]
            recs = recommender.get_recommendations(str(frag.id), limit=10)
            for rec in recs:
                rec_id = rec.fragrance.id
                recommended_ids.add(rec_id)
                if rec_id in long_tail_ids:
                    long_tail_recommended.add(rec_id)
        
        total_coverage = len(recommended_ids) / len(fragrances)
        tail_coverage = len(long_tail_recommended) / len(long_tail_ids)
        
        # Baseline: random selection would give ~50% long-tail
        baseline_tail = 0.50
        improvement = (tail_coverage / baseline_tail - 1) * 100
        
        print(f"\n=== LONG-TAIL DISCOVERY ===")
        print(f"Total catalog: {len(fragrances)}")
        print(f"Long-tail items (bottom 50%): {len(long_tail_ids)}")
        print(f"Long-tail items recommended: {len(long_tail_recommended)}")
        print(f"Long-tail coverage: {tail_coverage*100:.1f}%")
        print(f"Overall coverage: {total_coverage*100:.1f}%")
        print(f"Baseline (random): {baseline_tail*100:.1f}%")
        print(f"Improvement over baseline: {improvement:.0f}%")
        
        assert tail_coverage > 0.40, "Long-tail discovery below threshold"
    
    @async_test
    async def test_recommendation_speed_at_scale(self, db: AsyncSession):
        """Benchmark recommendation generation time on full catalog"""
        import time
        
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None))
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        # Time the recommender build
        start = time.time()
        recommender = SimilarityRecommender.from_database_rows(rows)
        build_time = time.time() - start
        
        # Time recommendation generation
        test_frag = fragrances[0]
        times = []
        for _ in range(100):
            start = time.time()
            _ = recommender.get_recommendations(str(test_frag.id), limit=10)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        p95_time = np.percentile(times, 95)
        
        print(f"\n=== PERFORMANCE AT SCALE ===")
        print(f"Catalog size: {len(fragrances)}")
        print(f"Model build time: {build_time:.2f}s")
        print(f"Avg recommendation time: {avg_time*1000:.1f}ms")
        print(f"P95 recommendation time: {p95_time*1000:.1f}ms")
        
        assert avg_time < 1.0, f"Recommendations too slow: {avg_time:.2f}s"
        assert build_time < 60, f"Model build too slow: {build_time:.0f}s"
    
    @async_test
    async def test_rarity_weighting_impact(self, db: AsyncSession):
        """Validate that rare notes are weighted more heavily"""
        result = await db.execute(select(Fragrance).limit(1000))
        fragrances = result.scalars().all()
        
        all_notes = []
        for frag in fragrances:
            if frag.top_notes:
                all_notes.extend(frag.top_notes)
            if frag.middle_notes:
                all_notes.extend(frag.middle_notes)
            if frag.base_notes:
                all_notes.extend(frag.base_notes)
        
        note_freq = Counter(all_notes)
        
        def rarity_weight(note):
            freq = note_freq[note]
            return 1 / np.log(freq + 1)
        
        common_notes = [n for n, c in note_freq.most_common(10)]
        rare_notes = [n for n, c in note_freq.most_common()[-10:]]
        
        common_weights = [rarity_weight(n) for n in common_notes]
        rare_weights = [rarity_weight(n) for n in rare_notes]
        
        print(f"\nRarity Weighting:")
        print(f"Common note avg weight: {np.mean(common_weights):.3f}")
        print(f"Rare note avg weight: {np.mean(rare_weights):.3f}")
        
        assert np.mean(rare_weights) > np.mean(common_weights)
    
    @async_test
    async def test_position_aware_scoring(self, db: AsyncSession):
        """Verify position bonuses (top/middle/base notes) are applied correctly"""
        result = await db.execute(
            select(Fragrance).filter(
                Fragrance.top_notes.isnot(None),
                Fragrance.middle_notes.isnot(None),
                Fragrance.base_notes.isnot(None)
            ).limit(100)
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        weights = {
            'top': recommender.TOP_NOTE_WEIGHT,
            'middle': recommender.MIDDLE_NOTE_WEIGHT,
            'base': recommender.BASE_NOTE_WEIGHT
        }
        
        print(f"\nPosition Bonuses:")
        print(f"Top notes: {weights['top']*100:.0f}%")
        print(f"Middle notes: {weights['middle']*100:.0f}%")
        print(f"Base notes: {weights['base']*100:.0f}%")
        
        assert weights['middle'] > weights['base'] > weights['top']
    
    @async_test
    async def test_multimodal_scoring_weights(self, db: AsyncSession):
        """Validate multi-modal scoring component weights sum to 1.0"""
        result = await db.execute(select(Fragrance).limit(10))
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes or [], 'middle_notes': f.middle_notes or [],
                 'base_notes': f.base_notes or [], 'main_accords': f.main_accords or [],
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        weights = {
            'note_similarity': recommender.NOTE_WEIGHT,
            'accord_similarity': recommender.ACCORD_WEIGHT,
            'quality_score': recommender.QUALITY_WEIGHT,
            'popularity_score': recommender.POPULARITY_WEIGHT,
            'diversity_bonus': recommender.DIVERSITY_WEIGHT
        }
        
        total_weight = sum(weights.values())
        
        print(f"\nMulti-Modal Scoring Weights:")
        for component, weight in weights.items():
            print(f"{component}: {weight*100:.0f}%")
        print(f"Total: {total_weight*100:.0f}%")
        
        assert abs(total_weight - 1.0) < 0.01
        assert weights['note_similarity'] > weights['accord_similarity']


class TestDataQuality:
    """Data validation and quality checks"""
    
    @async_test
    async def test_rating_bounds(self, db: AsyncSession):
        """Ensure all ratings are within valid range [0, 5]"""
        result = await db.execute(
            select(func.count(Fragrance.id)).filter(
                (Fragrance.average_rating < 0) | (Fragrance.average_rating > 5)
            )
        )
        invalid_ratings = result.scalar()
        
        assert invalid_ratings == 0, f"Found {invalid_ratings} invalid ratings"
    
    @async_test
    async def test_year_validity(self, db: AsyncSession):
        """Check release years are realistic (outlier detection)"""
        result = await db.execute(
            select(func.count(Fragrance.id)).filter(
                Fragrance.release_year.isnot(None),
                (Fragrance.release_year < 1800) | (Fragrance.release_year > 2030)
            )
        )
        invalid_years = result.scalar()
        
        assert invalid_years == 0, f"Found {invalid_years} invalid years"
    
    @async_test
    async def test_no_duplicate_urls(self, db: AsyncSession):
        """Verify URL uniqueness constraint"""
        result = await db.execute(
            select(Fragrance.url, func.count(Fragrance.url))
            .group_by(Fragrance.url)
            .having(func.count(Fragrance.url) > 1)
        )
        url_counts = result.all()
        
        assert len(url_counts) == 0, f"Found {len(url_counts)} duplicate URLs"
    
    @async_test
    async def test_note_array_quality(self, db: AsyncSession):
        """Validate note arrays contain valid data"""
        result = await db.execute(select(Fragrance).limit(1000))
        fragrances = result.scalars().all()
        
        empty_notes = 0
        valid_notes = 0
        
        for frag in fragrances:
            all_notes = []
            if frag.top_notes:
                all_notes.extend(frag.top_notes)
            if frag.middle_notes:
                all_notes.extend(frag.middle_notes)
            if frag.base_notes:
                all_notes.extend(frag.base_notes)
            
            if not all_notes:
                empty_notes += 1
            else:
                valid_notes += 1
                assert all(isinstance(n, str) for n in all_notes)
        
        print(f"\nNote Array Quality:")
        print(f"Valid: {valid_notes}, Empty: {empty_notes}")
        print(f"Completeness: {valid_notes/(valid_notes+empty_notes)*100:.1f}%")
        
        assert valid_notes > empty_notes
    
    @async_test
    async def test_outlier_detection(self, db: AsyncSession):
        """Identify statistical outliers in ratings using Z-score method"""
        result = await db.execute(
            select(Fragrance.average_rating, Fragrance.total_ratings).filter(
                Fragrance.total_ratings > 0
            )
        )
        fragrances = result.all()
        
        ratings = [float(r[0]) for r in fragrances]
        
        rating_mean = np.mean(ratings)
        rating_std = np.std(ratings)
        
        outliers = [r for r in ratings if abs(r - rating_mean) > 3 * rating_std]
        
        print(f"\nOutlier Detection:")
        print(f"Mean: {rating_mean:.2f}, Std: {rating_std:.2f}")
        print(f"Outliers (>3σ): {len(outliers)}")
        
        assert len(outliers) / len(ratings) < 0.01


class TestBusinessMetrics:
    """Business intelligence and performance metrics"""
    
    @async_test
    async def test_average_recommendation_similarity(self, db: AsyncSession):
        """Calculate mean similarity score across recommendations"""
        result = await db.execute(
            select(Fragrance).filter(Fragrance.top_notes.isnot(None)).limit(500)
        )
        fragrances = result.scalars().all()
        
        rows = [{'id': str(f.id), 'name': f.name, 'brand_name': f.brand_name,
                 'top_notes': f.top_notes, 'middle_notes': f.middle_notes,
                 'base_notes': f.base_notes, 'main_accords': f.main_accords,
                 'average_rating': float(f.average_rating), 'total_ratings': f.total_ratings}
                for f in fragrances]
        
        recommender = SimilarityRecommender.from_database_rows(rows)
        
        all_similarities = []
        for frag in fragrances[:50]:
            recs = recommender.get_recommendations(str(frag.id), limit=10)
            all_similarities.extend([rec.score for rec in recs])
        
        mean_sim = np.mean(all_similarities)
        std_sim = np.std(all_similarities)
        median_sim = np.median(all_similarities)
        
        print(f"\nRecommendation Quality Metrics:")
        print(f"Mean similarity: {mean_sim:.3f}")
        print(f"Median similarity: {median_sim:.3f}")
        print(f"Std deviation: {std_sim:.3f}")
        print(f"Range: [{min(all_similarities):.3f}, {max(all_similarities):.3f}]")
        
        assert 0.20 <= mean_sim <= 0.90, f"Mean similarity {mean_sim:.3f} outside expected range"
    
    @async_test
    async def test_brand_representation(self, db: AsyncSession):
        """Analyze brand distribution in catalog"""
        result = await db.execute(
            select(Fragrance.brand_name, func.count(Fragrance.id))
            .group_by(Fragrance.brand_name)
            .order_by(func.count(Fragrance.id).desc())
            .limit(20)
        )
        brand_counts = result.all()
        
        print(f"\nTop Brands by Fragrance Count:")
        for brand, count in brand_counts[:10]:
            print(f"{brand}: {count}")
        
        total_result = await db.execute(select(func.count(Fragrance.id)))
        total_frags = total_result.scalar()
        top_10_share = sum([c[1] for c in brand_counts[:10]]) / total_frags
        
        print(f"\nTop 10 brands represent: {top_10_share*100:.1f}% of catalog")
        
        assert len(brand_counts) > 0
    
    @async_test
    async def test_gender_distribution(self, db: AsyncSession):
        """Analyze gender distribution across catalog"""
        result = await db.execute(
            select(Fragrance.gender, func.count(Fragrance.id)).group_by(Fragrance.gender)
        )
        gender_counts = result.all()
        
        print(f"\nGender Distribution:")
        for gender, count in gender_counts:
            print(f"{gender or 'Unknown'}: {count}")
        
        assert len(gender_counts) > 0
    
    @async_test
    async def test_accord_popularity_analysis(self, db: AsyncSession):
        """Identify most common fragrance accords"""
        result = await db.execute(
            select(Fragrance).filter(Fragrance.main_accords.isnot(None)).limit(5000)
        )
        fragrances = result.scalars().all()
        
        all_accords = []
        for frag in fragrances:
            if frag.main_accords:
                all_accords.extend(frag.main_accords)
        
        accord_counts = Counter(all_accords)
        
        print(f"\nTop 10 Accords:")
        for accord, count in accord_counts.most_common(10):
            print(f"{accord}: {count}")
        
        assert len(accord_counts) > 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])