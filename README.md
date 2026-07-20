# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project is a small, content-based music recommender simulation. A listener is represented as a `UserProfile` (favorite genre, favorite mood, target energy, and whether they like acoustic songs), and an 18-song catalog is represented as `Song` objects with genre, mood, energy, tempo, valence, danceability, and acousticness. A weighted scoring rule compares the two directly — no play history or other users involved — and a separate ranking step sorts the whole catalog to return the top-k matches, each with a plain-language list of exactly why it scored the way it did. Testing it against several profiles, including two deliberately contradictory ones, showed both where the simple recipe works well (an internally consistent profile like "Chill Lofi" gets clean, intuitive results) and where it breaks down (exact-string genre matching can let a wrong-mood song outrank a better mood match just because it shares a genre label).

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

**Weight shift — genre 2.0 → 1.0, energy 1.0 → 2.0.** Tested on the "High-Energy Pop" profile (`genre=pop, mood=happy, energy=0.9`), where the baseline recipe ranked *Gym Hero* (pop/intense) above *Rooftop Lights* (indie pop/happy) — the mood match lost to the genre match. After halving genre's weight and doubling energy's, Gym Hero (2.94) *still* narrowly beat Rooftop Lights (2.72). This told me the ordering wasn't sensitive to that weight ratio at all — the real cause is that genre matching is exact-string equality (`"indie pop" != "pop"`), so no amount of reweighting can give Rooftop Lights credit for being genre-*adjacent*. The change made the scores different, but not more accurate; a real fix would need genre-similarity matching, not different point values. Weights were reverted back to the original recipe (genre 2.0, mood 1.0, energy 1.0) after the test.

- Tested five profiles end-to-end (three typical listeners, two adversarial/contradictory ones) — full output and analysis in `model_card.md` > Evaluation.
- Confirmed the scoring rule has no way to detect an internally contradictory profile (e.g. `mood=sad, energy=0.9`): it still returns a confident top-5, burying the one real mood match behind unrelated high-energy songs.

---

## Limitations and Risks

- The catalog is tiny (18 songs) and most genres have exactly one representative, so once a user's exact genre is exhausted, the rest of the top-k list is filled in by energy-closeness alone, regardless of genre or mood fit.
- Genre and mood are matched by exact string equality, not semantic closeness — related genres (e.g. "pop" vs. "indie pop") get zero credit for each other even though a listener would consider them similar. This is the single biggest limitation; see `model_card.md` for the experiment that confirmed it isn't just a weight-tuning problem.
- The system has no concept of lyrics, language, instrumentation beyond the given numeric tags, or listening context (time of day, activity, device).
- `UserProfile` only stores one favorite genre and one favorite mood, so it can't represent a listener with broad or mixed taste — it will systematically under-recommend to genre-diverse listeners.
- The scoring rule can't detect an internally contradictory profile (e.g. wanting `mood=sad` and `energy=0.9` at the same time); it still confidently returns a ranked list instead of flagging the conflict.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

> **Draft — personalize before submitting.** The paragraphs below are a first pass grounded in what actually happened while building and testing this project; read them over and rewrite anything that doesn't sound like your own take.

Building even this small a recommender made it clear that "recommendation" is really just a weighted sum, sorted. Every song became a small vector of numbers (genre, mood, energy, tempo, valence, danceability, acousticness), and the entire "algorithm" boiled down to comparing that vector to a user's stated preferences and adding up points. What surprised me was how much the *shape* of a comparison matters more than its exact weight — reworking the genre/energy weight ratio in an experiment didn't fix a bad recommendation (Gym Hero outranking Rooftop Lights for a "Happy Pop" listener), because the real problem was that genre was being compared with exact string equality instead of anything resembling closeness. That was a bigger lesson than I expected: a recommender's biases often live in *how* a comparison is defined, not just in how much weight it's given.

Testing adversarial profiles showed me where unfairness can quietly creep in. A profile that wanted `mood=sad, energy=0.9` never surfaced the one song actually tagged "sad" near the top — it got buried under two upbeat pop songs that merely matched on energy, and the system never signaled that anything was wrong. In a real streaming app, a version of this same bias could mean a user with a niche or self-contradictory taste (or a taste the underlying data barely represents) just gets steered toward whatever is popular and "close enough" on the majority signal, without ever being told that's what's happening. That changed how I think about these systems — a ranked list looks authoritative even when it's built on a handful of brittle rules underneath.



