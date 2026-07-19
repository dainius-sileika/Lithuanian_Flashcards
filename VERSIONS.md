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

## Audio + importable deck (files 1.7.6)
- **Audio:** all 519 words voiced with Azure neural **lt-LT-LeonasNeural** (male);
  one mp3 per card key in `audio/` (committed, ~6 MB).
- **Importable Anki deck:** `build_apkg.py` (genanki) bundles cards + images +
  audio + GO theme → `Lietuviu_Flashcards.apkg` (519 cards, ~126 MB) — distributed
  via GitHub **Release** (too big for the repo). README documents download + local
  build.
- TODO (in progress): stress-accented pronunciation column + finish the 88
  irregular noun genitives (native-quality pass).

## Grammatical forms + tidy (files 1.7.5)
- **`cards_anki.csv`** — clean, deduplicated Anki data (519 rows) with new fields:
  `gen_sg` (noun genitive → declension), `pres3`/`past3` (verb principal parts,
  accented), `fem` (adjective feminine). 85 verb triples + 61 adj feminines
  authored; 274 regular noun genitives rule-based; **88 tricky noun genitives
  (-is/-uo/irregular) left blank** + all forms flagged VERIFY (accents/irregulars
  need a native pass). Anki template + `.forms` CSS updated to show them.
- Recommendation implemented per grammar advice: verbs = inf·3sg·past, nouns =
  nom·gen·gender, adjectives = masc·fem.
- Folder tidied: working `*.bak*` → `deprecated/backups/`; scratch (out_fix,
  out_sample, qa_crop, stale logs) → `_scratch/` (gitignored).
- TODO: full headword accents on nouns; audio (Azure TTS — needs key); build the
  importable `.apkg`.

## Abstract cards + Anki theme (files 1.7.4 / wordlist 2.7)
- **All 88 abstract/"unfinished" words + 2 new feed verbs generated** — deck is
  now **519/519**. Engine: `go_generator` flag variants (EU flag for metric,
  US+UK for imperial); `deck_builder` ABSTRACT_ATTR routing (self-contained
  scenes → attribute class), per-card inset toggle, FLAG_OVERRIDE map. Backups:
  `deck_builder.py.bak173`, `go_generator.py.bak173`, `master_wordlist.csv.bak26`.
- Wordlist 2.7: 88 subject phrases + Lithuanian target words (machine-translated,
  **flagged "verify"** in notes) + rows 528 šerti / 529 lesinti. Two shared words
  by design: dangus (heaven≈sky), garsus (famous≈loud).
- Owner-specified GO cards done: money=Litai, newspaper=Lietuvos Aidas,
  magazine=Naujoji Romuva, hell=devil-Stalin, God=Creation of Adam, heaven=pearly
  gates, drug/murder/sex per spec, EU/US-UK measure flags, pray=Catholic+Orthodox.
- Fixes after QA: heaven/hell no arrow, God arrow→God, sex-act bar+lock insets,
  355 no=red X (not +), 154 gun=hunting-lodge (moderation).
- **Anki theme** added: `anki/go_theme.css` + `anki/templates.md` (cream paper,
  red bars, gender chips, verb-forms line). Draft doc: `DRAFT_unfinished_cards.md`.
- TODO: populate verb forms (inf/3sg/past); audio (TTS); push 1.7.3+1.7.4 to
  GitHub; full owner QA of the 90 new cards.

## QA round 3 (files 1.7.3 / wordlist 2.6)
- Owner full-deck review → 29 more card fixes, re-rolled + re-QA'd (28 clean).
  Engine unchanged; NOUN_STAGING round-3 block + VERB_STAGING/VERB_INSET edits +
  10 adjective phrase rewrites (wordlist 2.6). Backups: `deck_builder.py.bak1721`,
  `master_wordlist.csv.bak25`.
- Fixed: 186/187 (pig/cow insets), 194 (oil, no bad flag), 204 (family dinner),
  215/216 (civilian woman), 246 (different clock times), 258 (head insets), 259
  (neck, less cartoony), 272 (toe), 279 (heart, less cartoony), 283 (sweat + sun),
  301 (sky), 371 (solid wall), 386 (shoot insets), 410 (pyjama wake), 426 (timber
  frame), 430 (feed child only), 433 (brush scrub), 446 (fish+ruler), 447/456
  (arrow targets), 448/449 (basketball height), 450/451 (two-sided width arrows),
  478 (helping old lady — NOTE: still drew a stray arrow, minor), 490/491
  (tight/loose suits).
- TODO next: draft the 88 unfinished/abstract cards for review; add ŠERTI /
  LĘSINTI cards; Anki back-side CSS theme.

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
