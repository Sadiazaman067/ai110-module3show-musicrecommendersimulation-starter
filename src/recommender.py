from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# Algorithm Recipe weights (see README.md > How The System Works)
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_MATCH_POINTS = 1.0
ACOUSTIC_BONUS_POINTS = 0.5
ACOUSTIC_THRESHOLD = 0.6

NUMERIC_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}


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


def _score(genre: str, mood: str, energy: float, acousticness: float,
           favorite_genre: str, favorite_mood: str, target_energy: float,
           likes_acoustic: bool) -> Tuple[float, List[str]]:
    """Applies the Algorithm Recipe to one song's attributes and returns (score, reasons)."""
    score = 0.0
    reasons = []

    if genre == favorite_genre:
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS})")

    if mood == favorite_mood:
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS})")

    energy_points = ENERGY_MATCH_POINTS * (1 - abs(energy - target_energy))
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    if likes_acoustic and acousticness >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS_POINTS
        reasons.append(f"acoustic bonus (+{ACOUSTIC_BONUS_POINTS})")

    return score, reasons


class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Scores every song for this user and returns the top-k, highest score first."""
        scored = [
            (song, _score(song.genre, song.mood, song.energy, song.acousticness,
                          user.favorite_genre, user.favorite_mood,
                          user.target_energy, user.likes_acoustic)[0])
            for song in self.songs
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable score breakdown for one song and user."""
        score, reasons = _score(song.genre, song.mood, song.energy, song.acousticness,
                                 user.favorite_genre, user.favorite_mood,
                                 user.target_energy, user.likes_acoustic)
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file, converting numeric columns to float."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            for field in NUMERIC_FIELDS:
                row[field] = float(row[field])
            row["id"] = int(row["id"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song dict against user_prefs, returning (score, reasons)."""
    return _score(
        song["genre"], song["mood"], song["energy"], song["acousticness"],
        user_prefs.get("genre"), user_prefs.get("mood"),
        user_prefs.get("energy", 0.0), user_prefs.get("likes_acoustic", False),
    )


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song and returns the top-k as (song, score, explanation), highest first."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in scored[:k]]
