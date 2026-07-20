# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

This is a classroom simulation, not a production recommender. It takes one hard-coded listener "taste profile" (favorite genre, favorite mood, target energy, and an acoustic preference) and ranks a small, fixed catalog of songs (`data/songs.csv`) by how well each one matches that profile. It assumes a listener's taste can be reasonably summarized by a single favorite genre and mood plus a numeric energy target — a real listener's taste is obviously richer than that, but the simplification keeps the scoring logic easy to trace and explain. It's meant for exploring how a content-based recommender turns song attributes and a stated preference into a ranked, explained list of results, not for recommending music to real users.

---

## 3. How the Model Works  

Every song in the catalog carries a handful of attributes: its genre, its mood, how energetic it is, its tempo, how positive it sounds (valence), how danceable it is, and how acoustic it is. A listener is represented the same simple way — a favorite genre, a favorite mood, a target energy level, and whether they like acoustic-sounding music.

To score a song, the program checks whether the song's genre matches the listener's favorite genre and gives it 2 points if so, checks mood the same way for 1 point, and then looks at how close the song's energy is to the target energy — the closer, the more of a possible 1 point it earns, whether the song's energy is above or below the target. If the listener likes acoustic music and the song is acoustic enough, it gets a small half-point bonus on top. Every song in the catalog gets scored this way, then the whole list is sorted from highest to lowest score and the top handful are shown, along with a plain-language list of exactly which bonuses each song earned.

The starter file had all of this stubbed out with `TODO`s and placeholder return values (`return []`, `return self.songs[:k]`) — the genre/mood matching, the energy-closeness math, the sorting, and the human-readable explanation strings are all things I designed and implemented on top of the starter scaffold.

---

## 4. Data  

The catalog started as the 10 songs in the starter `data/songs.csv` and I expanded it to 18 by adding 8 more songs, specifically chosen to cover genres and moods the original set didn't have: R&B, punk, country, classical, reggaeton, blues, hip-hop, and folk, with moods like romantic, angry, nostalgic, sad, playful, lonesome, confident, and peaceful. Even at 18 songs, most genres still have only one representative, so an exact-genre match usually narrows the catalog down to just one or two candidates. Missing entirely from the dataset: anything about lyrics, language, vocal style, or cultural/regional context — "mood" and "genre" are single hand-picked labels per song rather than something derived from the actual audio or text, so two songs tagged with the same mood could still sound very different in practice.

---

## 5. Strengths  

The system does well on profiles that are internally consistent — a "Chill Lofi" listener (genre=lofi, mood=chill, low target energy, likes acoustic) gets a clean top-2 of actual lofi/chill songs with near-maximum scores, which matches intuition exactly. It also correctly separates very different listener types: a "Deep Intense Rock" profile and a "High-Energy Pop" profile produce completely different #1 picks, showing that the genre+mood+energy combination is doing real discriminating work rather than returning the same songs regardless of input. The reasons list is also a genuine strength — seeing "genre match (+2.0); mood match (+1.0); energy closeness (+0.92)" next to every recommendation makes it easy to audit *why* a song ranked where it did, which is exactly what surfaced the genre-matching bias described below.

---

## 6. Limitations and Bias 

The biggest bias is that genre matching is **exact string equality**, not "closeness of vibe." A "High-Energy Pop" profile (`genre=pop, mood=happy, energy=0.9`) ranks *Gym Hero* (pop/intense) above *Rooftop Lights* (indie pop/happy) — even though Rooftop Lights is the mood match — purely because `"pop" == "pop"` scores +2.0 while `"indie pop" != "pop"` scores 0. I confirmed this isn't just a weight-tuning problem: halving the genre weight and doubling the energy weight in an experiment (see README > Experiments You Tried) still left Gym Hero ahead of Rooftop Lights, so the real fix would need to be genre *similarity* (e.g. a genre-family map), not different point values. Second, with only 18 songs spread across 15 genres, most genres have exactly one song in the catalog, so once a user's exact genre is exhausted the remaining top-k slots get filled by energy-closeness alone regardless of genre or mood — the bottom half of almost every list is "filler" that only agrees with the user on energy. Third, the system has no way to detect an internally contradictory profile (e.g. `mood=sad, energy=0.9`): it still confidently returns a ranked top-5, silently burying the one song that actually matches the requested mood (*Piano in the Rain*, mood=sad) behind two unrelated high-energy pop songs that merely share the energy target — a real user would notice the mismatch, but the scoring rule has no way to flag it.

---

## 7. Evaluation  

I tested five profiles through `python -m src.main`: three "normal" listener types (High-Energy Pop, Chill Lofi, Deep Intense Rock) and two adversarial ones designed to give the scorer contradictory signals (Energetic-but-Sad, and Punk-genre-but-Peaceful-mood at very low target energy).

```
============================================================
Profile: High-Energy Pop  {'genre': 'pop', 'mood': 'happy', 'energy': 0.9}
============================================================
1. Sunrise City - Neon Echo (pop/happy)
   Score: 3.92
   Reasons: genre match (+2.0); mood match (+1.0); energy closeness (+0.92)

2. Gym Hero - Max Pulse (pop/intense)
   Score: 2.97
   Reasons: genre match (+2.0); energy closeness (+0.97)

3. Rooftop Lights - Indigo Parade (indie pop/happy)
   Score: 1.86
   Reasons: mood match (+1.0); energy closeness (+0.86)

4. Storm Runner - Voltline (rock/intense)
   Score: 0.99
   Reasons: energy closeness (+0.99)

5. Neon Fiesta - DJ Solara (reggaeton/playful)
   Score: 0.98
   Reasons: energy closeness (+0.98)


============================================================
Profile: Chill Lofi  {'genre': 'lofi', 'mood': 'chill', 'energy': 0.3, 'likes_acoustic': True}
============================================================
1. Library Rain - Paper Lanterns (lofi/chill)
   Score: 4.45
   Reasons: genre match (+2.0); mood match (+1.0); energy closeness (+0.95); acoustic bonus (+0.5)

2. Midnight Coding - LoRoom (lofi/chill)
   Score: 4.38
   Reasons: genre match (+2.0); mood match (+1.0); energy closeness (+0.88); acoustic bonus (+0.5)

3. Focus Flow - LoRoom (lofi/focused)
   Score: 3.40
   Reasons: genre match (+2.0); energy closeness (+0.90); acoustic bonus (+0.5)

4. Spacewalk Thoughts - Orbit Bloom (ambient/chill)
   Score: 2.48
   Reasons: mood match (+1.0); energy closeness (+0.98); acoustic bonus (+0.5)

5. Northern Lights - Aurora Fields (folk/peaceful)
   Score: 1.45
   Reasons: energy closeness (+0.95); acoustic bonus (+0.5)


============================================================
Profile: Deep Intense Rock  {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}
============================================================
1. Storm Runner - Voltline (rock/intense)
   Score: 3.99
   Reasons: genre match (+2.0); mood match (+1.0); energy closeness (+0.99)

2. Gym Hero - Max Pulse (pop/intense)
   Score: 1.97
   Reasons: mood match (+1.0); energy closeness (+0.97)

3. Neon Fiesta - DJ Solara (reggaeton/playful)
   Score: 0.98
   Reasons: energy closeness (+0.98)

4. Broken Amps - Rustbelt Kids (punk/angry)
   Score: 0.95
   Reasons: energy closeness (+0.95)

5. Sunrise City - Neon Echo (pop/happy)
   Score: 0.92
   Reasons: energy closeness (+0.92)


============================================================
Profile: Adversarial: Energetic but Sad  {'genre': 'pop', 'mood': 'sad', 'energy': 0.9}
============================================================
1. Gym Hero - Max Pulse (pop/intense)
   Score: 2.97
   Reasons: genre match (+2.0); energy closeness (+0.97)

2. Sunrise City - Neon Echo (pop/happy)
   Score: 2.92
   Reasons: genre match (+2.0); energy closeness (+0.92)

3. Piano in the Rain - Elena Voss (classical/sad)
   Score: 1.30
   Reasons: mood match (+1.0); energy closeness (+0.30)

4. Storm Runner - Voltline (rock/intense)
   Score: 0.99
   Reasons: energy closeness (+0.99)

5. Neon Fiesta - DJ Solara (reggaeton/playful)
   Score: 0.98
   Reasons: energy closeness (+0.98)


============================================================
Profile: Adversarial: Punk Genre, Peaceful Mood  {'genre': 'punk', 'mood': 'peaceful', 'energy': 0.1, 'likes_acoustic': True}
============================================================
1. Northern Lights - Aurora Fields (folk/peaceful)
   Score: 2.35
   Reasons: mood match (+1.0); energy closeness (+0.85); acoustic bonus (+0.5)

2. Broken Amps - Rustbelt Kids (punk/angry)
   Score: 2.15
   Reasons: genre match (+2.0); energy closeness (+0.15)

3. Piano in the Rain - Elena Voss (classical/sad)
   Score: 1.40
   Reasons: energy closeness (+0.90); acoustic bonus (+0.5)

4. Spacewalk Thoughts - Orbit Bloom (ambient/chill)
   Score: 1.32
   Reasons: energy closeness (+0.82); acoustic bonus (+0.5)

5. Library Rain - Paper Lanterns (lofi/chill)
   Score: 1.25
   Reasons: energy closeness (+0.75); acoustic bonus (+0.5)
```

**Pairwise comparisons:**

- *High-Energy Pop vs. Deep Intense Rock*: the #1 pick flips completely (Sunrise City vs. Storm Runner), which makes sense — these are near-opposite listeners. But *Gym Hero* lands at #2 in **both** lists. That makes sense too once you look at the reasons: Gym Hero is high-energy and "intense," so it's a strong energy-driven runner-up for anyone whose target energy is around 0.9, regardless of whether they actually asked for "happy" or "intense" moods.
- *Chill Lofi vs. Punk-Genre/Peaceful-Mood*: both target very low-to-moderate energy plus an acoustic bonus, and they converge on largely the same quiet songs (Library Rain, Spacewalk Thoughts) even though one profile explicitly asked for genre "punk." This shows that when the energy gap is large enough, the actual audio content wins over the genre label — the opposite of what happened in the pop case above, where the genre label won even with a mood mismatch.
- *Energetic-but-Sad vs. Chill Lofi*: the internally-contradictory profile produces a confused list topped by two upbeat pop songs, while the internally-consistent Chill Lofi profile produces a clean top-2 that's obviously "right" (two actual lofi/chill tracks scoring near the max). The system works best when the user's own stated preferences agree with each other.

**What surprised me:** I expected the weight-shift experiment (halve genre, double energy — see README) to fix the Gym Hero vs. Rooftop Lights ordering, since I assumed genre was just "too strong." It didn't change the outcome, which showed me the actual bug is in *how* genre is compared (exact string match), not how much it's worth.

**Explaining it simply:** Gym Hero keeps showing up for people who just want "Happy Pop" because our system gives a big bonus just for being labeled "pop" — even though Gym Hero's own mood tag is "intense," not "happy." It's like a food app that boosts every dish with "chicken" in the name, including the extra-spicy buffalo wings, when what you actually asked for was mild honey-glazed chicken — same category, wrong flavor.

---

## 8. Future Work  

The clearest next step is to replace exact-string genre matching with some notion of genre *similarity* — a small genre-family map (e.g. "indie pop" partially overlapping with "pop") would fix the Gym Hero/Rooftop Lights problem directly, since the weight-shift experiment showed that reweighting alone can't fix it. I'd also want `UserProfile` to support more than one favorite genre/mood, or a fuller attribute vector instead of two categorical picks, so it can represent listeners with broader taste. Better handling of contradictory profiles would help too — even a simple check that warns "no songs closely match both your mood and energy target" would be more honest than silently returning a top-5 anyway. Finally, growing the catalog and adding a diversity rule (so the top-k isn't dominated by one artist or genre when scores are close) would make results feel less repetitive.

---

## 9. Personal Reflection  

> **Draft — personalize before submitting.** Rewrite this in your own words; it's a first pass based on what actually happened while building this.

Working through this made recommender systems feel a lot less like magic and a lot more like a spreadsheet with extra steps — a handful of numeric comparisons, added up and sorted. What stuck with me most was the weight-shift experiment: I expected that tuning the genre-vs-energy weights would resolve the Gym Hero/Rooftop Lights problem, and it didn't, because the actual issue was that genre was being compared with `==` instead of something that understood "indie pop" and "pop" are related. That's a small thing in an 18-song catalog, but it made me realize that in a real system with millions of songs and users, a similar mismatch between how categories are defined and how listeners actually think about them could explain a lot of the "why does it keep recommending this" frustration people have with real apps. It also made me more skeptical of ranked lists in general — this recommender never once said "I'm not sure" or "these don't really fit," even when I gave it a deliberately contradictory profile; it just quietly produced a confident-looking top 5 anyway.
