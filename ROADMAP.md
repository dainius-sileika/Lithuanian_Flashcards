# Roadmap — from the 520-card base to A2

**Target: CEFR A2 Lithuanian.** This document is the plan of record: what the deck
covers now, what A2 additionally requires, how we get there, and the non-vocabulary
work that has to land alongside it.

Companion file: **`wordlist_a2_pending.csv`** — the actual queue of words, phrases
and grammar items, one row per proposed card, phased and deduplicated against the
existing deck.

---

## 1. Where we are

520 cards, complete and QA'd through five owner rounds, each with an illustration,
audio and a stress-accented headword.

The base is a *Fluent Forever 625*-style concrete vocabulary: things you can
photograph. Coverage by type:

| type | count |
|------|------:|
| nouns | 362 |
| verbs | 86 |
| adjectives | 74 |
| pronouns | 8 |

**This is roughly an A1 concrete core — and it has a specific, systematic hole.**
An audit of the wordlist found the deck contains **zero** of the following:

- numbers (no *vienas, du, dešimt, šimtas*)
- days, months, seasons, or clock/calendar words (no *diena, savaitė, metai, valanda*)
- question words (no *kas, kur, kada, kaip, kodėl, kiek*)
- prepositions (no *į, iš, su, ant, prie, be, po*)
- conjunctions (no *ir, bet, arba, nes, kad, jei*)
- adverbs (no *labai, dažnai, visada, niekada, jau, dar, tik*)
- possessives (no *mano, tavo, jo, jos, mūsų*)
- core modal verbs (no *būti, turėti, galėti, norėti, reikėti*)
- greetings and everyday formulas (no *labas, ačiū, prašau, atsiprašau*)

Also missing at the concrete level: *vardas, telefonas, parduotuvė, oras,
pusryčiai/pietūs/vakarienė, rytas/vakaras/naktis*.

That absence is not an oversight in the original list — it is a direct consequence
of the method. The picture rule ("no text in the art; infer the word from the image
alone") works beautifully for *šuo* and badly for *nes*.

## 2. What A2 actually requires

A2 is not "more nouns". It is the level at which a learner handles routine
exchanges: describing the past and future, asking and answering, expressing need
and preference, and getting through shops, travel, appointments and small talk.

Practically that means roughly **1,000–1,500 known lemmas**, of which the deck
supplies ~520 — but more importantly it means **function words, phrases and
grammar**, which is exactly the hole above.

**So the honest conclusion: reaching A2 requires a second card type.** The image
card cannot teach *although* or *+genitive*. This is the same conclusion Fluent
Forever reaches — pictures for concrete vocabulary, then **sentence/cloze cards**
for grammar and abstractions.

## 3. Phased plan

`wordlist_a2_pending.csv` holds **402 proposed rows** (376 net new; 26 flagged as
already covered and awaiting a drop decision). Projected finished deck: **~900 cards.**

| phase | what | rows | card type | engine work |
|-------|------|-----:|-----------|-------------|
| **A** | A1 completion — time, calendar, numbers, missing everyday nouns | 107 | image | numbers need a `TEXT_EXCEPTION` (render the digit); calendar/season staging |
| **B** | Function words — question words, prepositions, conjunctions, adverbs, possessives, modal verbs | 101 | **sentence** | new note type + template; no image required |
| **C** | A2 topical vocabulary — travel, health, work & school, shopping, home, feelings, technology, weather, society | 139 | image | existing engine, no changes |
| **D** | Phrases & formulas — greetings, politeness, getting by | 39 | **phrase** | audio-first card; text front, no illustration |
| **E** | Grammar patterns — the 7 cases, tenses, reflexives, comparatives, agreement | 16 | **pattern** | reference-card template with worked examples |

### Sequencing

1. **Phase A first.** It is picturable, uses the engine exactly as it stands, and
   removes the most embarrassing gaps (a learner cannot count or say "Monday").
2. **Phase C next**, for the same reason — pure content, no new machinery.
3. **Phase B and D require the new card types.** Build the sentence/phrase note
   type once, then both phases are data entry.
4. **Phase E last** — it is reference material, most useful once the learner has
   enough vocabulary to apply it.

### Per-phase definition of done

- Lithuanian target verified by a native speaker (every row currently says
  `LT proposed — verify`).
- Stress accent sourced (Wiktionary → kirtis.info), validated by the stress-strip
  rule, never invented.
- Grammar forms filled: genitive for nouns, principal parts for verbs, feminine
  for adjectives.
- Audio generated.
- Images generated and QA'd against the guessability gate (Phases A, C).
- `build_recorder.py` re-run so the recorder stays in step.
- Changelog entry + version bump.

## 4. Engine work required

**New note type: sentence/cloze cards** (Phases B, D). Front = a short Lithuanian
sentence with the target word blanked; back = the full sentence, the word, its
gloss and audio. Needs: a template, a `sentences` column in the data, and a build
path in `build_apkg.py`. This is the single biggest technical item on the roadmap.

**`TEXT_EXCEPTION` for numerals** (Phase A) — the mechanism already exists (used
for `m`, `cm`, `in`, `ABC/123`, `A E I O U`); numbers just need rows added.

**Calendar and season staging** (Phase A) — days and months are near-impossible to
disambiguate visually. Likely approach: a calendar page with the day/month
position marked, using the text exception for the numeral only.

**Pattern cards** (Phase E) — a reference layout: the rule, a worked example, and
a small paradigm table, in the house style.

## 5. Non-vocabulary work

Independent of A2, these are outstanding:

1. **Human audio.** The current audio is Azure neural; its Lithuanian word stress
   is unreliable, and no cloud engine (Azure, Google, ElevenLabs) accepts phoneme
   overrides for `lt-LT` — this was tested and confirmed. `recorder.html` is built
   and current, ready for a native speaker (or the owner) to record one clip per
   card. **This is the highest-value single improvement to the deck.**
2. **Native verification of the rule-derived forms.** Glosses and verb principal
   parts are owner-confirmed; the bulk noun genitives and adjective feminines are
   rule-derived and still want a spot-check.
3. **Pre-1.7.1 image backlog.** ~105 of the earliest cards (#1–231) had their
   insets generated under the old "worker" dress default, before the civilian rule.
   They are serviceable but stylistically inconsistent with the rest.
4. **Weak cards.** #440 dėvėti (wear) still reads closer to "protective gear".
5. **Distribution.** The `.apkg` is ~170 MB, too large to attach automatically to a
   GitHub Release. Options: a phone-sized build (downscaled images, ~40–50 MB), or
   manual upload each release. AnkiWeb listing text lives in
   `ANKIWEB_DESCRIPTION.md`.
6. **Card direction.** Every card is currently recognition-only
   (image → word). Production practice (EN → LT, or typed answer) would need a
   second template — worth deciding before the deck grows to 900.

## 6. Open decisions

- **Drop or keep the 26 flagged duplicates** in `wordlist_a2_pending.csv`
  (`status = review-duplicate`). Some are genuine collisions; a few are arguably
  distinct senses (*sąskaita* = restaurant bill vs bank account; *kaina* = price
  vs cost).
- **Sentence cards: whose sentences?** Fluent Forever recommends personal,
  memorable sentences over generic ones. Generic can be authored quickly;
  personal ones are better learning but need the owner to write them.
- **Numbers: how far?** The list stops at *milijonas* with ordinals to *penktas*.
  A2 arguably needs ordinals to ~20 for dates.
- **Do phrases need images?** Currently specified as text+audio. A GO-style
  illustration for *"Kiek kainuoja?"* is possible but expensive and may add little.

## 7. Milestones

| milestone | deck size | gate |
|-----------|----------:|------|
| **M1** — Phase A generated and QA'd | ~625 | numbers/calendar legible |
| **M2** — Phase C generated and QA'd | ~765 | guessability gate passes |
| **M3** — sentence note type shipped; Phase B + D loaded | ~905 | cloze cards render with audio on desktop + mobile |
| **M4** — Phase E pattern cards | ~920 | — |
| **M5** — human audio replaces synthesized | ~920 | full re-record, deck rebuild |
| **A2 release** | ~920 | native verification complete; version 2.0 |
