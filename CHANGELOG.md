# Changelog

All notable changes to **Lietuvių Flashcards** are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/); the project uses
`files X.Y.Z / wordlist N.M` versioning (art engine / vocabulary data).
`VERSIONS.md` holds the long-form production notes behind each entry.

## [Unreleased] — planning

### Added
- **CEFR levels on every card.** `cards_anki.csv` and the wordlist carry a `level`
  column, and the deck now builds as **subdecks** `Lietuvių Flashcards::A1` and
  `::A2` with matching `A1`/`A2` tags. Studying the parent deck studies all of it;
  a subdeck studies one level. Existing 520 auto-assigned 427 A1 / 93 A2.
- **`card_text` wordlist column** — text exceptions are now data, not code. Any
  row can name exactly what lettering its card may carry (a day name on a calendar,
  a numeral, a unit mark); everything else stays wordless. This is what makes
  undepictable-but-teachable cards (days, months, numbers) generable.
- **`ROADMAP.md`** — the plan of record for reaching CEFR **A2**, including a gap
  audit which found the deck contains *no* numbers, calendar words, question words,
  prepositions, conjunctions, adverbs, possessives or modal verbs — a systematic
  consequence of the picture-only method rather than an oversight.
- **Accent pass on the A2 queue.** 634 of 829 single-word rows (76%) now carry a
  stress-marked form, sourced — never guessed — from the existing deck, English
  Wiktionary (wikitext `head=` and rendered headword) and Lithuanian Wiktionary,
  each accepted only if stripping its marks exactly reproduces the headword.
  102 rows also captured IPA. The 195 words no source covers are listed in
  **`accents_todo_kirtis.csv`** for manual lookup; 8 rows where a source returned
  an unstressed form were moved there rather than left looking complete.
- **`wordlist_a2_pending.csv`** — the A2 queue: **984 proposed rows** (845 net new)
  across seven phases, each marked `level` (A1/A2) and `image_possible`, with
  A1 *and* A2 phrases and model sentences. 722 rows can go straight through the
  existing image engine. Every Lithuanian target is marked `LT proposed — verify`.

## [1.8.0] — 2026-07-26 — human audio

### Added
- **Human audio for A1.** 524 owner-recorded clips replace the synthesized voice
  on **all 427 A1 cards** (of 520 total); the remaining 97 clips belong to queued P-A rows
  and wait for their images. Each clip reads the **full paradigm** — headword,
  then genitive (nouns), 3sg + past (verbs) or feminine (adjectives) — so the
  audio now teaches the stress *shift* between forms, which a written accent on
  the lemma cannot.
- Processing: gently silence-gated (−55 dB, requiring 0.15 s of true silence, so
  soft onsets survive) with **150 ms of lead-in and 300 ms of tail padding** kept
  on every clip, then EBU R128 loudness-normalised to −16 LUFS, mono 24 kHz
  64 kbps MP3. 12.3 MB for 524 clips. An earlier pass trimmed too tightly and
  clipped the edges of words; all clips were reprocessed from the raw takes.
- **`audio_source.tsv`** records per-card provenance (human vs azure-neural), so
  the deck description can stay honest while the changeover is partial.

### Fixed
- **Six wrong noun genitives**, caught by the owner while recording:
  `sultys→sulčių`, `durys→durų`, `grindys→grindų`, `petys→peties`,
  `smegenys→smegenų`, `naktis→nakties`. All six were rule-derived in 1.7.5 and
  the rule misfired on plural-only and i-stem nouns (it had produced *sultio*,
  *durio*, *nakčio*). A follow-up audit of all 50 `-is`/`-ys` genitives and every
  i-stem noun in the deck found **no further cases** — the true i-stems were
  hand-authored and correct.

### Changed
- **Deck images downscaled to 1024 px** (JPEG q85, progressive). AnkiWeb caps a
  shared deck at 250 MB; measurement showed resolution dominates format — full
  size WebP would still reach ~308 MB at the projected 1365 cards, whereas
  1024 px JPEG lands ~179 MB and keeps universal client compatibility. The deck
  drops from **170 MB to 78 MB**, and 1024 px is still larger than a card ever
  displays.

### Note
- `071_melynas` was silent on the first take (9.2 s at RMS 4 — the mic dropped);
  re-recorded the same day via a single-word recorder page. **All 427 A1 deck
  cards now carry human audio.**

## [1.7.8] — 2026-07-24

### Added
- **`recorder.html`** — a self-contained offline browser recorder for capturing
  human audio (one clip per card key, resumable via IndexedDB, exports a zip that
  drops straight into `audio/`). `build_recorder.py` now reads `cards_anki.csv`
  directly rather than a one-off snapshot, so the recorder cannot drift out of
  step with the deck; re-run it after any wordlist change.

### Fixed
- **334 metras / 335 centimetras / 337 colis** now actually carry their unit
  marks (`m` + `100 cm`, `1 cm`, `1 in`). The text exceptions were written in
  1.7.7 but the three rows were omitted from the generation batch, so the old
  wordless art was still shipping.
- **507 šviesus / 506 tamsus** — the marking arrow no longer points off the edge
  of the card. Arrows now sit inside the marked half and point down into it, and
  the pair was re-rolled together so both halves stay symmetric.
- **350 priebalsis** — now renders the consonant row `B C D F G`, matching the
  vowel card. Its wordlist phrase still demanded "one single large letter B on a
  stand", which kept overriding the new rule and colliding with 227 raidė.

### Changed
- **362 raštas** re-pointed from *pattern* to **writing / script**, its primary
  sense (Wiktionary: writing system · literacy · writing/text/document ·
  handwriting · pattern). The gloss had been machine-matched to the last sense,
  which is also why the art kept drawing knitting. Card is now a hand writing on
  a page, with manuscript and typewriter insets, using a text exception that
  permits generic handwriting.

### Verified
- Owner confirmed the 530 lydyti principal parts (`lýdo` / `lýdė`) and the
  1.7.4 abstract-word glosses. All `verify` flags cleared from the wordlist.

## [1.7.7] — 2026-07-24

### Added
- **Adjective ruleset.** Adjectives previously had no rule of their own.
  - `ADJ_PAIR` / `ADJ_PAIR_BASE`: all 30 opposite pairs now share ONE base scene
    drawn identically for both cards, with only the marking arrow moving to the
    other pole. `ADJ_MARK` pins the arrowhead onto the marked side, forbids it
    pointing away, and keeps it inside the card frame.
  - Adjectives now get **insets** (the attribute class is inset-free by
    default): two per card showing the *same quality* in other everyday objects,
    so the quality rather than the object reads as the target.
  - Pair rows override the row's subject phrase with the quality itself, so an
    old phrase cannot contradict the new staging.
  - Owner-specified staging: clean/dirty = two boys; deep/shallow = pool ends;
    male/female = a teacher pointing at a lavatory pictogram; dark/light = the
    same room lit and unlit.
- **`TEXT_EXCEPTION`** (`go_generator._exact_text_rule`) — permits exactly the
  named lettering on cards that cannot teach their word wordlessly, and nothing
  else: unit marks, `ABC`/`123`, the `5 Lt.` price tag, the *NAUJOJI ROMUVA*
  masthead, and the vowel set. 351 balsis left `GLYPH_ROWS` as part of this.
- **New card 530 lydyti** (transitive *to melt*, a foundry pour) beside
  398 tirpti (intransitive).

### Fixed
- 58 cards re-rolled from owner QA round 4: pronouns 510–516 (the arrow marks
  the referent, never the speaker), 46, 51, 102, 103, 109, 110, 138, 149, 151,
  154, 156, 157, 160, 188, 189, 198, 199, 224, 252, 265, 285, 298, 301, 333,
  340, 343, 344, 345, 346, 351, 352, 354, 356, 361, 362, 363, 374, 403, 421,
  466, 477, 478, 479.
- **Duplicate `NOUN_STAGING` keys** (149/154/301) meant older entries silently
  overrode newer staging — stale duplicates removed.
- **Ignored inset specs**: ten rows carried an `inset_note` while routed to an
  inset-free class, so their insets were silently dropped.
- **103 žmogus** tripped the image-safety filter ("the general human form" read
  as a nude study); restaged as an explicitly clothed civic-handbook figure.

## [1.7.6] — 2026-07-19

### Added
- **Audio** for every card — Azure neural `lt-LT-LeonasNeural`, one mp3 per key.
- **Importable deck**: `build_apkg.py` (genanki) bundles cards + images + audio
  + theme into `Lietuviu_Flashcards.apkg`, distributed via GitHub Releases.
- **Stress-accented pronunciation** for all headwords, sourced from Wiktionary
  and [kirtis.info](https://kirtis.info) — never generated. Each accent is
  accepted only if stripping its marks exactly reproduces the plain headword, so
  a wrong-word match is impossible.

### Fixed
- Deck images transcoded to **JPEG** for the `.apkg` (some Anki clients don't
  render WebP inside cards); the repo keeps the compact WebP set.
- The `<img>` tag now lives in the note field rather than being built from a
  filename in the template, so Anki's *Check Media* sees the images as used.
- **Stable note GUIDs** (`guid_for(key)`) — re-importing an updated deck now
  updates cards in place instead of duplicating them, preserving study history.

## [1.7.5] — 2026-07-19

### Added
- `cards_anki.csv`: the clean, deduplicated Anki dataset, with grammar forms —
  `gen_sg` (noun genitive, showing declension), `pres3`/`past3` (verb principal
  parts), `fem` (adjective feminine).

## [1.7.4] — 2026-07-18

### Added
- The 88 abstract/"unfinished" words plus the two feed verbs (šerti, lesinti),
  completing the deck. Flag variants (EU / US+UK) for the measurement cards.
- Anki theme: `anki/go_theme.css` + `anki/templates.md`.

## [1.7.1 – 1.7.3] — 2026-07-14 … 07-18

### Changed
- Noun-inset dress follows the setting (civilian by default; worker only where
  work belongs) and the inset-meaning gate went into the prompt.
- Three rounds of owner QA (~85 cards) covering guessability, arrows, insets
  and moderation reframings.

## [1.7] — 2026-07-14

### Added
- The guessability pass: the QA gate ("if you didn't know the word, could you
  infer it from the main image alone?"), `NOUN_STAGING`, and class reroutes.

## [0.1 – 1.6] — 2026-07

Initial engine, house style and vocabulary build-out. See the "File batches
ledger" in `GO_STYLE_SPEC_files_1_7_1.md` for the full narrative history.
