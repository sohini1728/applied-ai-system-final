"""
Retrieval-Augmented Generation (RAG) component.
Uses semantic similarity to find related songs and enable discovery.
"""

from typing import List, Tuple, Dict
import logging
import math
from src.recommender import Song

logger = logging.getLogger(__name__)


class SimilarityRetriever:
    """
    Retrieves similar songs using content-based similarity metrics.
    This enables discovery beyond exact genre/mood matching.
    """
    
    def __init__(self, songs: List[Song]):
        self.songs = songs
        self.similarity_cache: Dict[int, Dict[int, float]] = {}
        logger.info(f"Initialized retriever with {len(songs)} songs")

    def compute_similarity(self, song1: Song, song2: Song) -> float:
        """
        Compute semantic similarity between two songs (0.0 to 1.0).
        Based on genre, mood, energy, acousticness, tempo, and valence.
        """
        if song1.id == song2.id:
            return 1.0
        
        # Check cache
        if song1.id in self.similarity_cache and song2.id in self.similarity_cache[song1.id]:
            return self.similarity_cache[song1.id][song2.id]
        
        similarity_score = 0.0
        
        # Genre similarity (fuzzy: exact match = 1.0, different = 0.0)
        genre_similarity = 1.0 if song1.genre.lower() == song2.genre.lower() else 0.3
        similarity_score += genre_similarity * 0.25
        
        # Mood similarity (fuzzy: exact match = 1.0, close moods = 0.7)
        mood_similarity = self._mood_similarity(song1.mood, song2.mood)
        similarity_score += mood_similarity * 0.20
        
        # Energy similarity (continuous: penalize distance)
        energy_diff = abs(song1.energy - song2.energy)
        energy_similarity = max(0, 1.0 - energy_diff)
        similarity_score += energy_similarity * 0.20
        
        # Tempo similarity (normalize to 0-1)
        tempo_diff = abs(song1.tempo_bpm - song2.tempo_bpm)
        tempo_similarity = max(0, 1.0 - (tempo_diff / 200.0))
        similarity_score += tempo_similarity * 0.15
        
        # Acousticness similarity
        acoustic_diff = abs(song1.acousticness - song2.acousticness)
        acoustic_similarity = max(0, 1.0 - acoustic_diff)
        similarity_score += acoustic_similarity * 0.10
        
        # Valence similarity (mood positivity)
        valence_diff = abs(song1.valence - song2.valence)
        valence_similarity = max(0, 1.0 - valence_diff)
        similarity_score += valence_similarity * 0.10
        
        # Cache result
        if song1.id not in self.similarity_cache:
            self.similarity_cache[song1.id] = {}
        self.similarity_cache[song1.id][song2.id] = similarity_score
        
        return similarity_score

    def _mood_similarity(self, mood1: str, mood2: str) -> float:
        """
        Define fuzzy mood similarity relationships.
        Enables discovery: "happy" is similar to "energetic", etc.
        """
        mood1, mood2 = mood1.lower(), mood2.lower()
        
        if mood1 == mood2:
            return 1.0
        
        # Define mood clusters
        mood_clusters = {
            'energetic': {'happy', 'intense', 'energetic', 'excited'},
            'chill': {'chill', 'relaxed', 'calm', 'peaceful'},
            'moody': {'moody', 'melancholic', 'dreamy', 'exotic'},
            'focused': {'focused', 'intense', 'energetic'},
        }
        
        # Check if moods are in the same cluster
        for cluster_moods in mood_clusters.values():
            if mood1 in cluster_moods and mood2 in cluster_moods:
                return 0.7
        
        return 0.2

    def retrieve_similar(self, query_song: Song, k: int = 5, exclude_exact: bool = False) -> List[Tuple[Song, float]]:
        """
        Retrieve k most similar songs to query_song.
        If exclude_exact=True, don't return songs with identical genre/mood.
        """
        similarities = []
        
        for candidate in self.songs:
            if candidate.id == query_song.id:
                continue
            
            similarity = self.compute_similarity(query_song, candidate)
            
            # Optional: exclude exact matches for discovery
            if exclude_exact and candidate.genre.lower() == query_song.genre.lower():
                similarity *= 0.5  # Penalize exact genre matches
            
            similarities.append((candidate, similarity))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Retrieved {min(k, len(similarities))} similar songs to '{query_song.title}'")
        return similarities[:k]

    def retrieve_by_exploration(self, genre: str, exclude_genres: List[str] = None, k: int = 3) -> List[Song]:
        """
        Retrieve songs for genre exploration.
        Useful for discovery recommendations.
        """
        exclude_genres = exclude_genres or []
        candidates = [
            song for song in self.songs
            if song.genre.lower() not in [g.lower() for g in exclude_genres]
        ]
        
        # Score by energy variety and acousticness for discovery
        scored = [(song, song.energy + song.acousticness * 0.5) for song in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Retrieved {min(k, len(scored))} exploration recommendations")
        return [song for song, _ in scored[:k]]
