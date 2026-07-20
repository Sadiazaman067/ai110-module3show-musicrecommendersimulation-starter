# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube generally blend two approaches. **Collaborative filtering** looks at what similar users did — plays, skips, likes, saves, playlist adds — and recommends songs that people with similar behavior enjoyed, without knowing anything about the song itself. **Content-based filtering** looks at the song's own attributes — genre, tempo, energy, mood/valence — and recommends songs whose attributes are close to what a listener has already responded to. Production systems usually combine both: collaborative signals surface what's broadly popular among "taste twins," while content signals cover new songs/users (the "cold start" problem) and keep recommendations explainable.

This simulation has a single listener and no interaction history (no play counts, skips, or other users to compare against), so it implements a **pure content-based recommender**: it compares one `UserProfile`'s stated preferences directly against each `Song`'s attributes and scores how close the match is.

**`Song` features used:** `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`

**`UserProfile` features used:** `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`

**Scoring Rule (one song):** categorical matches (`genre`, `mood`) act as weighted bonuses since they're strong identity signals, while numeric features like `energy` are scored by *closeness* to the user's target (e.g. `1 - abs(song.energy - user.target_energy)`) rather than "higher is always better" — a user who wants energy 0.5 shouldn't have songs at energy 1.0 outrank songs at energy 0.5.

**Ranking Rule (a list of songs):** once every song has a score, the system sorts the catalog by score and takes the top `k`. The Scoring Rule and Ranking Rule are kept as separate steps because they answer different questions — scoring asks "how well does this one song fit this one user," while ranking asks "given all these scores, what's the best ordered set to show" (ties, diversity across artists, and how many results to return are list-level decisions, not song-level ones).

### Algorithm Recipe (finalized)

Data flow: `Input (UserProfile)` → `Process (loop: score_song(user, song) for every song in songs.csv)` → `Output (sort by score, take top k)`.

| Signal | Points |
|---|---|
| Genre match (`favorite_genre == song.genre`) | +2.0 |
| Mood match (`favorite_mood == song.mood`) | +1.0 |
| Energy closeness | up to +1.0, via `1 - abs(song.energy - target_energy)` |
| Acoustic bonus (`likes_acoustic` and `song.acousticness >= 0.6`) | +0.5 |

Genre is weighted 2x mood because it behaves more like a hard identity filter (a rock fan usually won't accept jazz even if the mood fits), while mood is a softer, more situational preference. Energy is capped at 1.0 so a single continuous feature can't outweigh two categorical matches, and the acoustic bonus is a small nudge rather than a deciding factor.

**Expected biases:** this recipe over-prioritizes `genre` — a song in the right genre but a poor mood/energy fit can still outscore a song that's a near-perfect mood/energy match in an "adjacent" genre (e.g. indie pop vs. pop). It also can't represent a listener who enjoys more than one genre or mood at once, since `UserProfile` only stores a single favorite of each, so it will systematically under-recommend genre-diverse listeners' true favorites.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` with the default profile (`genre=pop, mood=happy, energy=0.8`):

```
Loaded songs: 18

Top Recommendations
========================================
1. Sunrise City - Neon Echo (pop/happy)
   Score: 3.98
   Reasons: genre match (+2.0); mood match (+1.0); energy closeness (+0.98)

2. Gym Hero - Max Pulse (pop/intense)
   Score: 2.87
   Reasons: genre match (+2.0); energy closeness (+0.87)

3. Rooftop Lights - Indigo Parade (indie pop/happy)
   Score: 1.96
   Reasons: mood match (+1.0); energy closeness (+0.96)

4. Night Drive Loop - Neon Echo (synthwave/moody)
   Score: 0.95
   Reasons: energy closeness (+0.95)

5. Neon Fiesta - DJ Solara (reggaeton/playful)
   Score: 0.92
   Reasons: energy closeness (+0.92)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



