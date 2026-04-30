"""
VibeFinder Pro: Main orchestrator.
Integrates recommender, retriever, agent, and evaluator into a cohesive system.
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.recommender import load_songs, Recommender
from src.retriever import SimilarityRetriever
from src.agent import Agent
from src.evaluator import EvaluationMetrics


def print_recommendation_results(plan):
    """Pretty-print recommendation results."""
    print("\n" + "="*70)
    print(f"🎵 RECOMMENDATIONS FOR {plan.user_profile.get('favorite_genre', 'Unknown').upper()}")
    print("="*70)
    
    print(f"\nUser Profile:")
    print(f"  • Genre: {plan.user_profile.get('favorite_genre')}")
    print(f"  • Mood: {plan.user_profile.get('favorite_mood')}")
    print(f"  • Energy Level: {plan.user_profile.get('target_energy'):.1f}/1.0")
    print(f"  • Likes Acoustic: {'Yes' if plan.user_profile.get('likes_acoustic') else 'No'}")
    
    print(f"\nWorkflow Steps:")
    for step in plan.steps:
        print(f"  {step}")
    
    print(f"\nConfidence Score: {plan.confidence:.1%}")
    
    print(f"\nTop Recommendations:")
    for i, rec in enumerate(plan.recommendations, 1):
        print(f"\n  {i}. {rec['title']} by {rec['artist']}")
        print(f"     Genre: {rec['genre']} | Mood: {rec['mood']}")
        print(f"     Score: {rec['score']:.2f} | Source: {rec['source']}")
        print(f"     Reasons: {', '.join(rec['reasons'])}")
    
    print(f"\nAI Reasoning:\n{plan.reasoning}")


def run_demo():
    """Run demonstration of VibeFinder Pro."""
    logger.info("Starting VibeFinder Pro Demo")
    
    # Load songs
    songs = load_songs("data/songs.csv")
    if not songs:
        logger.error("Failed to load songs. Exiting.")
        return
    
    # Initialize components
    logger.info("Initializing AI system components...")
    recommender = Recommender(songs)
    retriever = SimilarityRetriever(songs)
    agent = Agent(recommender, retriever)
    evaluator = EvaluationMetrics()
    
    # Test profiles
    test_profiles = [
        {
            "name": "Pop/Happy Lover",
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False
        },
        {
            "name": "Chill Lofi Vibes",
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True
        },
        {
            "name": "Intense Rock Fan",
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.9,
            "likes_acoustic": False
        },
    ]
    
    print("\n" + "🎵 "*15)
    print("VIBEFINDER PRO: AI-ENHANCED MUSIC DISCOVERY SYSTEM")
    print("🎵 "*15)
    
    # Generate recommendations for each profile
    for profile_info in test_profiles:
        profile_dict = {k: v for k, v in profile_info.items() if k != "name"}
        plan = agent.plan_recommendations(profile_dict, k=5)
        print_recommendation_results(plan)
    
    # Run evaluation
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE EVALUATION")
    print("="*70)
    
    profiles_for_eval = [
        {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "likes_acoustic": False
        },
        {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "likes_acoustic": True
        },
        {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.9,
            "likes_acoustic": False
        },
        {
            "favorite_genre": "jazz",
            "favorite_mood": "relaxed",
            "target_energy": 0.45,
            "likes_acoustic": True
        },
    ]
    
    eval_results = evaluator.run_full_evaluation(agent, profiles_for_eval)
    
    print("\n" + evaluator.get_evaluation_summary())
    
    # Save results
    evaluator.save_results("evaluation_results.json")
    
    logger.info("Demo complete!")


if __name__ == "__main__":
    run_demo()
