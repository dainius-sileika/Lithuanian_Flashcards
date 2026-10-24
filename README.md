# Lietuvių Flashcards

An illustrated Lithuanian Anki deck (A0 → A2+), every picture drawn as a page from a 1981 Lithuanian
civil-defence training album. Two subdecks (`Lietuvių Flashcards::A1`, `::A2`), picture cards, phrase
cards, cloze and sentence cards, human-recorded audio for the A1 core.

**Where is what:** [`INDEX.md`](INDEX.md) — the map of this working directory (every top-level item, where a
card's picture and audio are, how to build, record and verify, the Proton/git rules, the current release).

**Start here for the design:** `docs/DESIGN_SPEC_CURRENT.md` — the one authoritative statement of the design parameters
in force (image engine, lettering and emblem rules, card front/back, study order, versioning, ways of
working), sourced to the code and versioned (spec 3.0.0; `style/STYLE_LOCK.json` is its fingerprint,
`docs/HOW_TO_CHANGE_THE_LOOK.md` the procedure for touching the aesthetic). Once per clone:
`sh tools/install_hooks.sh`. `docs/SPEC_RECONCILIATION_2026-10-19.md` says where older documents disagree
with it. The owner's open decisions live on the Review Desk (`review_desk/`).

## Build

```bash
pip install genanki pillow openai
sh tools/install_hooks.sh                        # once per clone: pre-commit = style lock + layout + inventory
python3 build_study_order_v3.py                  # -> data/study_order.csv
APKG_VERSION=3.0 APKG_LEVELS=A1 python3 build_apkg.py     # -> Lietuviu_Flashcards_v3.0_A1.apkg
APKG_VERSION=3.0 APKG_LEVELS=A2 python3 build_apkg.py
sh tools/smoke_test.sh                           # every tool once
```
Run from the root. Generating or re-rolling pictures: the `gen.py` of each render batch
(`media/generation/out_deck_f62/gen.py`, `out_deck_a2/gen.py`, `out_deck_sent/gen.py`, `out_phrases_v3/gen.py`)
writes into `media/images/`; then `python3 code/qa_images.py media/images`, then a review page for the owner.
Nothing ships without his verdict.

## Map of the repository

The full map is **`INDEX.md`**; the complete inventory of every file is **`FILES.md`** (generated). In one
breath (layout of 2026-10-24, spec §13):

| top level | what it is |
|---|---|
| **Entry points (root)** | `build_apkg.py` (the package), `build_recorder.py` (recording sheet), `build_study_order_v3.py` (learning order); `recorder_A2.html` (the owner's recording sheet); the current release `.apkg` |
| `code/` | The pipeline modules: `card_frame.py` + `frame_crop.py` (standard bands, cropping), `go_generator.py` / `go_grammars.py` / `go_settings.py` / `deck_builder.py` / `verb_flashcards.py` / `situations.py` / `gen_phrases.py` / `historical.py` (the picture engine), `qa_images.py` (QA gate), `frame_preview.py` |
| `data/` | Every live data file: `cards_anki.csv` (A1 cards), `a2_wordlist.csv` (A2 list), `sentences/`, `master_wordlist.csv` + `card_notes.json` + `a2_staging.json` (staging), `context_notes.csv`, `study_order.csv`, `audio_source.tsv`, `recording_list.csv`, `key_maps/` (the key history), the list bookkeeping and the engine's tables |
| `media/` | **`images/<key>.png`** — the one current picture of every card; **`audio/<key>.mp3`** (+ `<key>_s.mp3`) — its audio; `images/_history/<old batch path>/` and `audio/_history/` — every other version; `audio/_inbox/` — recorder ZIPs; `generation/<batch>/` — each render batch's ledger, plan, QA sheets and `gen.py`. Pictures are not committed. |
| `docs/` | `DESIGN_SPEC_CURRENT.md` (versioned), `spec_history/`, `HOW_TO_CHANGE_THE_LOOK.md`, `VERSIONS.md` (deck ↔ spec ↔ style register), `RECORDING_GUIDE.md`, the plans, `decisions/`, the AnkiWeb description, the playbook, `CHANGELOG.md` |
| `reports/` | Build manifests and verify reports (`builds/`), frame-detection results, study-order audits, screenshot sets, the hand scan |
| `rounds/` | One dated folder per round of work (`2026-10-17_pilot_round2/`, `2026-10-19_fixes_round3/`, `2026-10-20_rename/`, `2026-10-24_deep_tidy/` …), each with its README; closed records |
| `tools/` | `check_layout.py`, `make_index.py` (→ `FILES.md`), `style_lock.py`, `spec_release.py`, `verify_apkg.py`, `rename_keys.py`, `keymap.py`, `ingest_takes.py`, `golden_set.py`, `build_situations.py`, `move_files.py`, `smoke_test.sh`, hooks |
| `review_desk/`, `sources/` | The owner's Review Desk sources; third-party word lists |
| `style/`, `anki/`, `fonts/`, `style_lab/` | Style lock + golden set; card CSS; Brygada 1918; the style experiments (kept as a record) |
| `_archive/`, `_TO_DELETE/` | Kept history (old code, docs, data, packages); junk for the owner to delete |
| caches | `_apkg_media/`, `_qa/`, `__pycache__/` — regenerate freely |

## License

**[CC BY-NC 4.0](LICENSE)** — free to use, share and adapt for non-commercial purposes, with attribution
and a link back. Applies to the artwork, wordlist, spec and code. The illustrations are AI-generated in a
house style; the copyright status of such images is unsettled and this license states the author's intent.

> "Lietuvių Flashcards" by Dainius Sileika, licensed under CC BY-NC 4.0.
> Source: https://github.com/dainius-sileika/Lithuanian_Flashcards
