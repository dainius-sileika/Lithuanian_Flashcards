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
python3 build_study_order_v3.py                  # -> study_order.csv (v2 kept as history)
APKG_VERSION=3.0 APKG_LEVELS=A1 python3 build_apkg.py     # -> Lietuviu_Flashcards_v3.0_A1.apkg
APKG_VERSION=3.0 APKG_LEVELS=A2 python3 build_apkg.py
```
Generating or re-rolling pictures: the `gen.py` of each render batch (`media/generation/out_deck_f62/gen.py`,
`out_deck_a2/gen.py`, `out_deck_sent/gen.py`, `out_phrases_v3/gen.py`) writes into `media/images/`; then
`python3 qa_images.py media/images`, then a review page for the owner. Nothing ships without his verdict.

## Map of the repository

The full map is **`INDEX.md`**. In one breath (layout of 2026-10-24, spec §13):

| top level | what it is |
|---|---|
| **Pipeline code (root)** | `build_apkg.py` (the package), `build_recorder.py` (recording sheet), `build_study_order_v3.py` (learning order), `card_frame.py` + `frame_crop.py` (standard bands, cropping), `go_generator.py` / `go_grammars.py` / `go_settings.py` / `deck_builder.py` / `verb_flashcards.py` / `situations.py` / `gen_phrases.py` / `historical.py` (the picture engine), `qa_images.py` (QA gate), `frame_preview.py` |
| **Live data (root)** | `cards_anki.csv` (A1 cards), `master_wordlist.csv` + `card_notes.json`, `study_order.csv`, `audio_source.tsv`, `wordlist_a2_pending.csv`, `recorder_A2.html` (the owner's recording sheet) |
| `media/` | **`images/<key>.png`** — the one current picture of every card; **`audio/<key>.mp3`** (+ `<key>_s.mp3`) — its audio; `images/_history/<old batch path>/` and `audio/_history/` — every other version; `generation/<batch>/` — each render batch's ledger, plan, QA sheets and `gen.py`. Pictures are not committed. |
| `a2_build/` | The A2 list (`a2_wordlist.csv`), sentences, usage notes, key maps (`rename/`), recording list and guide, review rounds, plans, the 2026-10-24 move table (`tidy/`) |
| `docs/` | `DESIGN_SPEC_CURRENT.md` (versioned), `spec_history/`, `HOW_TO_CHANGE_THE_LOOK.md`, `VERSIONS.md` (deck ↔ spec ↔ style register), `CHANGELOG.md`, the AnkiWeb description, the playbook |
| `style/`, `tools/`, `anki/`, `fonts/` | Style lock + golden set; `check_layout.py`, `style_lock.py`, `spec_release.py`, `verify_apkg.py`, `rename_keys.py`, `keymap.py`, `ingest_takes.py`, hooks; card CSS; Brygada 1918 |
| `build_reports/`, `review_desk/` | Build manifests and verify reports; the owner's Review Desk sources |
| `a2_rebase/`, `sources/`, `style_lab/` | A2 queue rebase; frequency/lexicon sources; the style experiments (kept as a record) |
| `_archive/`, `_TO_DELETE/` | Kept history (old code, docs, packages); junk for the owner to delete |
| caches | `_apkg_media/`, `_qa/`, `__pycache__/` — regenerate freely |

## License

**[CC BY-NC 4.0](LICENSE)** — free to use, share and adapt for non-commercial purposes, with attribution
and a link back. Applies to the artwork, wordlist, spec and code. The illustrations are AI-generated in a
house style; the copyright status of such images is unsettled and this license states the author's intent.

> "Lietuvių Flashcards" by Dainius Sileika, licensed under CC BY-NC 4.0.
> Source: https://github.com/dainius-sileika/Lithuanian_Flashcards
