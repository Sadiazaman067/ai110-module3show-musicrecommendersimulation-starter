"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# Diverse profiles plus two adversarial / edge-case profiles that give
# genre, mood, and energy conflicting signals on purpose.
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    "Adversarial: Energetic but Sad": {"genre": "pop", "mood": "sad", "energy": 0.9},
    "Adversarial: Punk Genre, Peaceful Mood": {
        "genre": "punk", "mood": "peaceful", "energy": 0.1, "likes_acoustic": True,
    },
}


def print_recommendations(profile_name, user_prefs, songs, k=5) -> None:
    print(f"\n{'=' * 60}")
    print(f"Profile: {profile_name}  {user_prefs}")
    print("=" * 60)
    recommendations = recommend_songs(user_prefs, songs, k=k)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']} ({song['genre']}/{song['mood']})")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for profile_name, user_prefs in PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs, k=5)


if __name__ == "__main__":
    main()
