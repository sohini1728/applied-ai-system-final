"""
Agentic Workflow component.
Multi-step reasoning: Score → Discover → Explore → Validate.
Implements planning and self-improvement.
"""

from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStep(Enum):
    """Workflow stages."""
    SCORE = "score"
    DISCOVER = "discover"
    EXPLORE = "explore"
    VALIDATE = "validate"


@dataclass
class RecommendationPlan:
    """Represents the AI's reasoning plan."""
    user_profile: Dict[str, Any]
    steps: List[str]
    recommendations: List[Dict[str, Any]]
    confidence: float
    reasoning: str


class Agent:
    """
    Multi-step reasoning agent for music recommendations.
    Plans, acts, and validates its own recommendations.
    """
    
    def __init__(self, recommender, retriever):
        """
        Initialize agent with recommender and retriever.
        Args:
            recommender: Recommender instance (scoring logic)
            retriever: SimilarityRetriever instance (discovery logic)
        """
        self.recommender = recommender
        self.retriever = retriever
        self.execution_log: List[Dict[str, Any]] = []
        logger.info("Initialized agentic workflow")

    def plan_recommendations(self, user_prefs: Dict[str, any], k: int = 5) -> RecommendationPlan:
        """
        Multi-step planning workflow:
        1. Score direct matches
        2. Discover similar songs
        3. Explore adjacent genres
        4. Validate and rank final recommendations
        """
        steps = []
        all_recommendations = []
        
        # Convert user_prefs dict to UserProfile
        from src.recommender import UserProfile
        user = UserProfile(
            favorite_genre=user_prefs.get('favorite_genre', 'pop'),
            favorite_mood=user_prefs.get('favorite_mood', 'happy'),
            target_energy=user_prefs.get('target_energy', 0.5),
            likes_acoustic=user_prefs.get('likes_acoustic', False),
        )
        
        logger.info(f"Planning recommendations for user: {user_prefs}")
        
        # STEP 1: Score direct matches
        step_1_recommendations = self.recommender.recommend(user, k=3)
        steps.append("✓ Step 1: Scored direct matches (genre, mood, energy)")
        all_recommendations.extend([
            {
                'title': song.title,
                'artist': song.artist,
                'genre': song.genre,
                'mood': song.mood,
                'score': score,
                'reasons': reasons,
                'source': 'direct_match',
            }
            for song, score, reasons in step_1_recommendations
        ])
        logger.info(f"Step 1: Found {len(step_1_recommendations)} direct matches")
        
        # STEP 2: Discover similar songs (RAG-like retrieval)
        if step_1_recommendations:
            top_song, _, _ = step_1_recommendations[0]
            similar_songs = self.retriever.retrieve_similar(top_song, k=2, exclude_exact=True)
            steps.append("✓ Step 2: Retrieved similar songs (semantic discovery)")
            
            for similar_song, similarity in similar_songs:
                # Boost score based on discovery quality
                discovery_score = similarity * 4.0  # Scale to comparable range
                all_recommendations.append({
                    'title': similar_song.title,
                    'artist': similar_song.artist,
                    'genre': similar_song.genre,
                    'mood': similar_song.mood,
                    'score': discovery_score,
                    'reasons': [f"semantic similarity (+{similarity:.2f})", "discovery recommendation"],
                    'source': 'discovery',
                })
            logger.info(f"Step 2: Retrieved {len(similar_songs)} similar songs")
        
        # STEP 3: Explore adjacent genres
        explore_genres = self._find_adjacent_genres(user.favorite_genre)
        if explore_genres:
            exploration_songs = self.retriever.retrieve_by_exploration(
                user.favorite_genre,
                exclude_genres=[user.favorite_genre],
                k=2
            )
            steps.append(f"✓ Step 3: Explored adjacent genres ({', '.join(explore_genres[:2])})")
            
            for explore_song in exploration_songs:
                exploration_score = 2.5 + (explore_song.energy * 1.0)
                all_recommendations.append({
                    'title': explore_song.title,
                    'artist': explore_song.artist,
                    'genre': explore_song.genre,
                    'mood': explore_song.mood,
                    'score': exploration_score,
                    'reasons': [f"genre exploration (similar to {user.favorite_genre})"],
                    'source': 'exploration',
                })
            logger.info(f"Step 3: Explored {len(exploration_songs)} songs in adjacent genres")
        
        # STEP 4: Validate and rank
        all_recommendations.sort(key=lambda x: x['score'], reverse=True)
        final_recommendations = all_recommendations[:k]
        
        # Compute confidence score
        confidence = self._compute_confidence(final_recommendations, user_prefs)
        steps.append(f"✓ Step 4: Validated and ranked top {len(final_recommendations)} recommendations")
        logger.info(f"Step 4: Final confidence score: {confidence:.2f}")
        
        # Create reasoning narrative
        reasoning = self._create_reasoning_narrative(user_prefs, final_recommendations, confidence)
        
        # Log execution
        self.execution_log.append({
            'user_profile': user_prefs,
            'steps': steps,
            'recommendations_count': len(final_recommendations),
            'confidence': confidence,
        })
        
        return RecommendationPlan(
            user_profile=user_prefs,
            steps=steps,
            recommendations=final_recommendations,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _find_adjacent_genres(self, primary_genre: str) -> List[str]:
        """Find adjacent genres for exploration."""
        genre_graph = {
            'pop': ['indie pop', 'electronic', 'dance'],
            'rock': ['metal', 'indie', 'blues'],
            'lofi': ['ambient', 'electronic', 'indie'],
            'jazz': ['blues', 'classical', 'world'],
            'ambient': ['lofi', 'classical', 'electronic'],
            'indie': ['indie pop', 'rock', 'folk'],
            'hip-hop': ['electronic', 'pop', 'world'],
            'electronic': ['dance', 'synthwave', 'ambient'],
            'folk': ['indie', 'country', 'acoustic'],
            'classical': ['ambient', 'jazz', 'world'],
            'dance': ['pop', 'electronic', 'hip-hop'],
            'metal': ['rock', 'electronic', 'intense'],
            'blues': ['jazz', 'rock', 'folk'],
            'synthwave': ['electronic', 'pop', 'indie'],
            'world': ['jazz', 'ambient', 'folk'],
        }
        return genre_graph.get(primary_genre.lower(), ['pop', 'indie', 'electronic'])

    def _compute_confidence(self, recommendations: List[Dict], user_prefs: Dict) -> float:
        """
        Compute confidence score (0.0 to 1.0) for recommendations.
        Higher if: multiple sources contribute, high match quality, diverse genres.
        """
        if not recommendations:
            return 0.0
        
        # Factor 1: Average score (normalized to 0-1)
        avg_score = sum(rec['score'] for rec in recommendations) / len(recommendations)
        score_confidence = min(1.0, avg_score / 6.0)  # Max score is ~6
        
        # Factor 2: Diversity (different genres and sources)
        genres = set(rec['genre'] for rec in recommendations)
        sources = set(rec['source'] for rec in recommendations)
        diversity_confidence = (len(genres) + len(sources)) / 6.0
        
        # Factor 3: Match quality (direct matches are more confident)
        direct_matches = sum(1 for rec in recommendations if rec['source'] == 'direct_match')
        match_confidence = min(1.0, direct_matches / 2.0)
        
        # Weighted average
        confidence = (
            score_confidence * 0.4 +
            diversity_confidence * 0.3 +
            match_confidence * 0.3
        )
        
        return min(1.0, max(0.0, confidence))

    def _create_reasoning_narrative(self, user_prefs: Dict, recommendations: List[Dict], confidence: float) -> str:
        """Generate human-readable reasoning narrative."""
        genre = user_prefs.get('favorite_genre', 'pop')
        mood = user_prefs.get('favorite_mood', 'happy')
        
        sources_count = {}
        for rec in recommendations:
            source = rec['source']
            sources_count[source] = sources_count.get(source, 0) + 1
        
        narrative = f"""
Recommendation reasoning for {genre.title()} {mood.title()} lover:

1. Analyzed your taste profile: {genre.title()} music with {mood} vibes
2. Found {sources_count.get('direct_match', 0)} direct genre/mood matches
3. Discovered {sources_count.get('discovery', 0)} similar songs using semantic analysis
4. Explored {sources_count.get('exploration', 0)} adjacent genres for variety
5. Confidence score: {confidence:.1%} based on match quality and diversity

The system prioritized songs that match your stated preferences while introducing discovery 
opportunities from related genres. Higher confidence indicates strong alignment with your taste profile.
""".strip()
        
        return narrative

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Return execution log for debugging/analysis."""
        return self.execution_log
