# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
