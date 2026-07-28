# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

**Last updated: 2026-07-26 · audio settled; question words + A1 phrases ready to proof**

---

## → Do this first: `review_A1_priority.csv` — 57 rows

You asked for the **question words** fast and to **proof the A1 phrases** — both
are in this one small pack, ahead of the bigger queue.

- **Group 1 — question words (9).** `kas, kur, kada, kaip, kodėl, kiek, koks,
  kuris, kieno`. Eight already carry a sourced accent; only **kieno** needs one.
- **Group 2 — A1 phrases & sentences (48).** 16 formulas (*ačiū, prašom, sėkmės*),
  13 getting-by lines (*Kur yra tualetas?*), and 19 core sentence patterns
  (*Man reikia vandens*, *Man patinka šis miestas*). **8 single-word ones need an
  accent**; multi-word phrases are skipped.

Columns: `LT_ok_or_fix` (blank = mine is right), `accent_FILL`, `comment`.
`note_for_card` is mine — it records the grammar point each sentence teaches
(impersonal *man reikia* + genitive, negation taking the genitive, and so on).

**These 57 can be recorded as soon as you confirm them** — audio needs only the
words, not images.

## → Then, the rest of A1

**`review_A1.csv` — 312 rows** (the 57 above are a subset, so skip those).
**`review_A1_duplicates.csv` — 101 rows**, keep/drop.

---

## The plan, since you asked

**A1 = 427 existing cards + 409 queued = 836 words.** Getting there:

| step | what | status |
|------|------|--------|
| 1 | P-A: time, calendar, numbers, everyday nouns (97) | **verified + recorded**, images pending |
| 2 | **Question words + A1 phrases (57)** | ← *this pack* |
| 3 | Rest of A1 vocabulary — P-F verbs/nouns/adjectives (168), P-B function words (96) | `review_A1.csv` |
| 4 | Duplicate decisions (101) | `review_A1_duplicates.csv` |
| 5 | I generate P-A images, then the rest | not blocked on you |
| 6 | You record the remainder; I merge | after step 3 |

**Card types:** the question words, function words and sentences need the
**sentence/cloze note type**, which doesn't exist yet — I'm building it. Their
*words and audio* can land before it does; only the card layout waits.

---

## Audio: settled

**No trimming at all**, after three attempts proved gates eat phonemes — tail
gates removed word-final fricatives (*karvės* → *karvė*), the head gate shaved
plosive onsets (*dukra*). Measurement closed it: raw takes carry a median **and
max of 0.02 s** of leading silence, so gating could never help. Verified no raw
take has speech in its first 20 ms, so nothing was lost at capture.

The recorder now also has a **400 ms pre-roll** — mic goes live, prompt says
"wait", then "SPEAK NOW" — so future takes can't have this problem.

---

## Not blocked on you

- P-A scene phrases and image generation.
- Grammar forms for later phases; irregulars flagged, never guessed.
- The sentence/phrase note type.
