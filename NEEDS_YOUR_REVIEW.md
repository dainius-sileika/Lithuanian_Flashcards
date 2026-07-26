# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

**Last updated: 2026-07-25 · A1 push — 312 rows to verify, then record**

---

## → Goal: finish A1 today, then record

**A1 = 427 existing cards + 409 queued rows = 836 words.** Audio is gated on the
*word list*, not on images — so recording can happen before the new A1 pictures
are generated.

### 1. `review_A1.csv` — 312 rows *(the critical path)*

The A1 rows of P-B (function words), P-F (vocabulary) and P-G (phrases), sorted
by phase then category. Same three columns as the P-A pack:

- **`LT_ok_or_fix`** — blank = my Lithuanian is right; type a correction if not.
- **`accent_FILL`** — **39 rows** need a kirtis.info lookup (phrases skipped).
- **`form_ok_or_fix`** — **66 rows** flagged; 129 are rule-derived and just need a
  skim. Verbs need *3sg · past* (e.g. `dirba / dirbo`) — I don't guess those.

### 2. `review_A1_duplicates.csv` — 101 rows

Mark `KEEP_or_DROP`. These collide with the existing 520; `collides_with` says how.
Fast, and it decides the true A1 size.

### 3. Then I merge, and you record

`recorder_A1.html` is **already built and current** — 524 A1 words right now,
rising to ~836 once the 312 are confirmed and merged. Run
`python3 build_recorder.py A1` any time to refresh it.

---

## Recording notes, for when you get there

**The recorder now prompts the full paradigm.** Each card shows a dashed box with
everything to say: the headword, then the genitive (nouns), the principal parts
(verbs) or the feminine (adjectives) — e.g. `dìrbti · 3sg dìrba · past dìrbo`.
Read them one clear breath apart; **one clip per card**, so nothing changes in
the merge pipeline. Of the 524 A1 cards currently loaded, 489 prompt more than
one form.

- **Headwords carry stress marks; the other forms don't.** We only sourced
  accents for headwords, and accenting every inflected form would be a large
  separate job. For recording it doesn't matter — you know how to say *namo*, and
  **your recording becomes the authority** for that form's stress.
- **836 words with paradigms is ~2.5 hours** with retakes. The recorder saves to
  the browser continuously, so stop and resume freely; a partial export merges
  fine and un-recorded cards keep their synthesized audio until you finish.
- Quiet room, consistent mic distance, natural citation form.
- Export the ZIP and hand it back; I normalise, trim, convert and rebuild.

---

## Not blocked on you

- Authoring P-A scene phrases and generating those 97 images (validation batch first).
- Grammar forms for later phases; irregulars flagged, never guessed.
- The sentence/phrase note type, which unblocks P-B, P-D, P-E and P-G as *cards*
  (their words can still be recorded today).
