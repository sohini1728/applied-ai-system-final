"""
Core recommendation logic using content-based filtering.
This is the foundation that VibeFinder Pro builds upon.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP implementation of recommendation logic."""
    
    def __init__(self, songs: List[Song]):
        self.songs = songs
        logger.info(f"Initialized recommender with {len(songs)} songs")

    def recommend(self, user: UserProfile, k: int = 5) -> List[Tuple[Song, float, List[str]]]:
        """
        Recommend top k songs for a user.
        Returns list of (song, score, reasons) tuples.
        """
        scored_songs = []
        
        for song in self.songs:
            score, reasons = self._score_song(user, song)
            scored_songs.append((song, score, reasons))
        
        # Sort by score descending
        ranked_songs = sorted(scored_songs, key=lambda x: x[1], reverse=True)
        
        logger.info(f"Generated {len(ranked_songs)} recommendations for user")
        return ranked_songs[:k]

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Score a single song against user preferences.
        Returns (total_score, list_of_reasons).
        """
        score = 0.0
        reasons = []
        
        # Genre match: +2.0 points
        if song.genre.lower() == user.favorite_genre.lower():
            score += 2.0
            reasons.append("genre match (+2.0)")
        
        # Mood match: +1.0 point
        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
            reasons.append("mood match (+1.0)")
        
        # Energy similarity: up to +2.0 points
        energy_diff = abs(user.target_energy - song.energy)
        energy_score = max(0, 2.0 - (energy_diff * 2.0))
        score += energy_score
        reasons.append(f"energy similarity (+{energy_score:.2f})")
        
        # Acousticness fit: 0-1.0 points
        if user.likes_acoustic:
            acoustic_score = song.acousticness
        else:
            acoustic_score = 1.0 - song.acousticness
        score += acoustic_score
        reasons.append(f"acoustic fit (+{acoustic_score:.2f})")
        
        return (score, reasons)

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Generate human-readable explanation for why a song was recommended."""
        score, reasons = self._score_song(user, song)
        return ", ".join(reasons)


def load_songs(csv_path: str) -> List[Song]:
    """Load songs from CSV and return as Song objects."""
    songs = []
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                song = Song(
                    id=int(row['id']),
                    title=row['title'],
                    artist=row['artist'],
                    genre=row['genre'],
                    mood=row['mood'],
                    energy=float(row['energy']),
                    tempo_bpm=float(row['tempo_bpm']),
                    valence=float(row['valence']),
                    danceability=float(row['danceability']),
                    acousticness=float(row['acousticness']),
                )
                songs.append(song)
        logger.info(f"✓ Loaded {len(songs)} songs from {csv_path}")
        return songs
    except FileNotFoundError:
        logger.error(f"✗ Error: Could not find {csv_path}")
        return []
    except Exception as e:
        logger.error(f"✗ Error loading songs: {e}")
        return []
