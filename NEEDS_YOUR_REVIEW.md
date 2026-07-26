# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

**Last updated: 2026-07-25 · P-A verified and merged**

---

## → Nothing is blocked on you this minute

**P-A is verified and merged** — 97/97 accents (all passed the strip-back gate),
62 grammar forms, every row now reads *owner-confirmed*. I'm authoring the scene
phrases and generating that phase now; I'll come back with a small validation
batch (a numeral, a day, a month, a plain noun) before spending on all 97, because
the `card_text` lettering machinery is new and I want it proven on four cards
rather than ninety-seven.

## → Next for you, whenever convenient

**1. Duplicate decisions — `wordlist_a2_pending.csv`, filter `status = review-duplicate`.**
139 rows collide with the existing 520. Most should be dropped; a few are arguably
distinct senses (*sąskaita* = restaurant bill vs bank account). Mark keep/drop.
Quick, and it shrinks every phase downstream.

**2. `accents_todo_kirtis.csv` — 185 words left** (down from 195; the 10 in P-A are
done). **43 are A1.** The next review pack (P-C) will draw from this list, so
doing the A1 ones first stays efficient.

## Coming back to you next

**`review_P-C.csv`** — 122 rows, A2 topical vocabulary (travel, health, work,
shopping, home, feelings, technology, society). Same three-column format. I'll
produce it once P-A images are through QA.

---

## Not blocked on you

- Rule-deriving grammar forms for the remaining phases; irregulars get flagged,
  never guessed.
- Authoring subject phrases per phase, after that phase's words are confirmed.
- Building the sentence/phrase note type, which unblocks P-B, P-D, P-E and P-G.

---

## The loop, for reference

For each phase: **I produce a review pack → you correct it → I author the scene
phrases, generate, QA, and merge** (with audio, level tags and a rebuilt
recorder). Order: **P-A → P-C → P-F** (in three chunks), with
**P-B / P-D / P-E / P-G** following once the sentence note type exists.
