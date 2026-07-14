# VERSIONS — Lietuvių 625 deck

**Current: files 1.7.1 / wordlist 2.3** (working files in this folder root).

| version | what | where |
|---------|------|-------|
| **1.7.1** (current) | noun-inset dress follows setting (civilian default; Materials + tool/industry = worker); inset-meaning gate baked into the prompt | root: `go_grammars.py`, `go_generator.py`, `deck_builder.py`; `files_1_7_1_DIFF.md`; `GO_STYLE_SPEC_files_1_7_1.md` |
| 1.7 | guessability pass: QA gate, NOUN_STAGING (22 rows), OVERRIDE_CLASS reroutes, wordlist 2.3 (22 phrases) | `deprecated/code_1.7/`; `files_1_7_DIFF.md` (corrected record) |
| 1.6.1 | 8 open design decisions implemented; glyph exception; wordlist 2.2 | `deprecated/code_1.6.1/`, `deprecated/spec_1.6.1/`, `deprecated/wordlist_2.2/` |
| ≤1.6 | full narrative history (0.1 → 1.6) | "File batches ledger" in `GO_STYLE_SPEC_files_1_7_1.md` |

## Current working files (root)
- `go_generator.py` — the GO engine (style/palette/overlays/generation). Backend: OpenAI gpt-image-1.5.
- `go_grammars.py` — per-category visual grammars (the executable design bible).
- `deck_builder.py` — production runner; reads `master_wordlist.csv`.
- `driver.py` — parallel batch/reroll runner (merges into `out_deck/`).
- `verb_flashcards.py`, `noun_flashcards.py` — verb production staging / noun demo.
- `master_wordlist.csv` — wordlist 2.3 (429 generable rows).
- `GO_STYLE_SPEC_files_1_7_1.md` — canonical spec + changelog.
- `files_1_7_DIFF.md`, `files_1_7_1_DIFF.md` — per-release sign-off diffs.
- `out_deck/` — generated card PNGs + `ledger.csv` + `cards.csv` (190 cards done, #1–231 except #227).
- `out_par/` — transient per-card working dirs (safe to ignore).
- `deprecated/` — frozen older versions (see `deprecated/README.md`).

## Generation status
- **COMPLETE: 429 / 429 eligible cards generated** (out_deck), all QA'd.
- Full forward run done under 1.7.1 / wordlist 2.4: Home, Electronics, Body,
  Nature, Materials, Misc (incl. 3 glyph cards via the single-glyph exception),
  Verbs (#363–445), Adjectives (#446–507).
- #227 raidė now generated (glyph exception renders a clean letterform).
- Known weak spots (inherent concept difficulty, flagged not re-rolled):
  #350 priebalsis / #351 balsis (consonant/vowel glyphs read as "a letter";
  #351's "A" collides with #227 letter); #440 dėvėti (wear) reads closer to
  "protective gear". All rely partly on the Anki text field.
- Still pending (separate pass): re-roll the ~105 pre-1.7.1 original cards
  (#1–231) whose insets were made under the old worker default → civilian.

## QA round 2 (files 1.7.2 / wordlist 2.5)
- Owner QA of the full generated deck produced 34 card corrections, all re-rolled
  and re-QA'd (pass). Engine: `deck_builder` gains `VERB_INSET` (per-verb custom
  insets, like NOUN_STAGING inset_note). Backups: `deck_builder.py.bak172`,
  `master_wordlist.csv.bak24`.
- Fixed: body clarity (262 hair, 271 back clothed, 272 toe, 278 shoulder clothed,
  282 knee, 287 skin+mosquito, 288 body+doctor); nature (303 wind arrows, 306
  valley, 314 beach); 358 injury; verbs (366/367 arrows, 369 fly insets, 371 go,
  372 stop, 373 follow, 383 buy, 401 sit, 404 pass-by, 430 feed, 433 clean, 434
  find, 435 fall, 440 wear); adjectives (446 long, 454/455 slow/fast, 471 quiet,
  473 sad, 474/475 beautiful/ugly, 478 kind, 499 dirty).
- Not changed: #299 žemė (note "insert bleeding" unclear — awaiting clarification).

## Wordlist
- Current: **2.5** (`master_wordlist.csv`). Backups: 2.4 `.bak24`, 2.3 `.bak23`.
  2.5 = 2.4 + 10 phrase rewrites from round-2 QA (314, 446, 454, 455, 471, 473,
  474, 475, 478, 499). 2.4 = 2.3 + (#232 ceiling, #238 yard).
