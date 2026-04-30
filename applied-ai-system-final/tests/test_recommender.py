"""
Comprehensive test suite for VibeFinder Pro.
Tests all components: recommender, retriever, agent, evaluator.
"""

import pytest
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recommender import Song, UserProfile, Recommender, load_songs
from src.retriever import SimilarityRetriever
from src.agent import Agent
from src.evaluator import EvaluationMetrics


class TestRecommender:
    """Test core recommender logic."""
    
    def test_load_songs(self):
        """Test song loading from CSV."""
        songs = load_songs("data/songs.csv")
        assert len(songs) > 0, "Should load at least one song"
        assert all(isinstance(s, Song) for s in songs), "All items should be Song objects"
    
    def test_score_song(self):
        """Test song scoring."""
        songs = load_songs("data/songs.csv")
        rec = Recommender(songs)
        
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False
        )
        
        # Find a pop song
        pop_songs = [s for s in songs if s.genre.lower() == "pop"]
        assert len(pop_songs) > 0, "Should have pop songs in dataset"
        
        pop_song = pop_songs[0]
        score, reasons = rec._score_song(user, pop_song)
        
        assert score > 0, "Score should be positive"
        assert len(reasons) > 0, "Should have explanation reasons"
        assert any("genre match" in r for r in reasons), "Should mention genre match"
    
    def test_recommend_returns_sorted_results(self):
        """Test that recommendations are sorted by score."""
        songs = load_songs("data/songs.csv")
        rec = Recommender(songs)
        
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False
        )
        
        results = rec.recommend(user, k=5)
        assert len(results) > 0, "Should return at least one recommendation"
        
        scores = [score for _, score, _ in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by score descending"
    
    def test_recommend_respects_k(self):
        """Test that k parameter is respected."""
        songs = load_songs("data/songs.csv")
        rec = Recommender(songs)
        
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False
        )
        
        for k in [1, 3, 5, 10]:
            results = rec.recommend(user, k=k)
            assert len(results) == min(k, len(songs)), f"Should return {min(k, len(songs))} results for k={k}"


class TestRetriever:
    """Test retrieval and similarity computation."""
    
    def test_similarity_computation(self):
        """Test similarity between songs."""
        songs = load_songs("data/songs.csv")
        retriever = SimilarityRetriever(songs)
        
        song1 = songs[0]
        song2 = songs[0]
        
        # Same song should have similarity 1.0
        sim = retriever.compute_similarity(song1, song2)
        assert sim == 1.0, "Same song should have similarity 1.0"
    
    def test_retrieve_similar_returns_results(self):
        """Test retrieving similar songs."""
        songs = load_songs("data/songs.csv")
        retriever = SimilarityRetriever(songs)
        
        query_song = songs[0]
        similar = retriever.retrieve_similar(query_song, k=5)
        
        assert len(similar) > 0, "Should return similar songs"
        assert len(similar) <= 5, "Should respect k parameter"
    
    def test_similarity_symmetry(self):
        """Test that similarity is symmetric."""
        songs = load_songs("data/songs.csv")
        retriever = SimilarityRetriever(songs)
        
        if len(songs) >= 2:
            sim_12 = retriever.compute_similarity(songs[0], songs[1])
            sim_21 = retriever.compute_similarity(songs[1], songs[0])
            assert sim_12 == sim_21, "Similarity should be symmetric"


class TestAgent:
    """Test agentic workflow."""
    
    def test_agent_generates_plan(self):
        """Test that agent generates a valid recommendation plan."""
        songs = load_songs("data/songs.csv")
        recommender = Recommender(songs)
        retriever = SimilarityRetriever(songs)
        agent = Agent(recommender, retriever)
        
        user_prefs = {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
        }
        
        plan = agent.plan_recommendations(user_prefs, k=5)
        
        assert plan is not None, "Should generate a plan"
        assert len(plan.steps) > 0, "Plan should have steps"
        assert len(plan.recommendations) > 0, "Plan should have recommendations"
        assert 0.0 <= plan.confidence <= 1.0, "Confidence should be between 0 and 1"
    
    def test_agent_plan_has_diverse_sources(self):
        """Test that agent recommendations come from multiple sources."""
        songs = load_songs("data/songs.csv")
        recommender = Recommender(songs)
        retriever = SimilarityRetriever(songs)
        agent = Agent(recommender, retriever)
        
        user_prefs = {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False,
        }
        
        plan = agent.plan_recommendations(user_prefs, k=5)
        sources = set(rec['source'] for rec in plan.recommendations)
        
        # Should have recommendations from at least 2 sources
        assert len(sources) >= 2, f"Should have diverse sources, got {sources}"


class TestEvaluator:
    """Test evaluation metrics."""
    
    def test_diversity_metric(self):
        """Test diversity score computation."""
        evaluator = EvaluationMetrics()
        
        recommendations = [
            {'genre': 'pop', 'artist': 'Artist A'},
            {'genre': 'pop', 'artist': 'Artist B'},
            {'genre': 'rock', 'artist': 'Artist C'},
        ]
        
        diversity = evaluator.evaluate_diversity(recommendations)
        assert 0.0 <= diversity <= 1.0, "Diversity should be between 0 and 1"
    
    def test_relevance_metric(self):
        """Test relevance score computation."""
        evaluator = EvaluationMetrics()
        
        recommendations = [
            {'genre': 'pop', 'mood': 'happy'},
            {'genre': 'rock', 'mood': 'intense'},
            {'genre': 'lofi', 'mood': 'chill'},
        ]
        
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
        }
        
        relevance = evaluator.evaluate_relevance(recommendations, user_prefs)
        assert 0.0 <= relevance <= 1.0, "Relevance should be between 0 and 1"
        assert relevance > 0, "Should have some relevance since one rec matches"
    
    def test_novelty_metric(self):
        """Test novelty score computation."""
        evaluator = EvaluationMetrics()
        
        recommendations = [
            {'genre': 'pop'},
            {'genre': 'rock'},
            {'genre': 'jazz'},
        ]
        
        user_prefs = {'favorite_genre': 'pop'}
        
        novelty = evaluator.evaluate_novelty(recommendations, user_prefs)
        assert 0.0 <= novelty <= 1.0, "Novelty should be between 0 and 1"
        assert novelty > 0, "Should have some novelty since 2/3 are different genres"
    
    def test_full_evaluation(self):
        """Test full evaluation suite."""
        songs = load_songs("data/songs.csv")
        recommender = Recommender(songs)
        retriever = SimilarityRetriever(songs)
        agent = Agent(recommender, retriever)
        evaluator = EvaluationMetrics()
        
        test_profiles = [
            {
                "favorite_genre": "pop",
                "favorite_mood": "happy",
                "target_energy": 0.8,
                "likes_acoustic": False,
            },
            {
                "favorite_genre": "lofi",
                "favorite_mood": "chill",
                "target_energy": 0.35,
                "likes_acoustic": True,
            },
        ]
        
        results = evaluator.run_full_evaluation(agent, test_profiles)
        
        assert 'average_diversity' in results, "Should have diversity metric"
        assert 'average_relevance' in results, "Should have relevance metric"
        assert 'average_novelty' in results, "Should have novelty metric"
        assert 'overall_quality_score' in results, "Should have overall score"
        assert 0.0 <= results['overall_quality_score'] <= 1.0, "Quality score should be 0-1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
