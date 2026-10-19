# Lietuvių Flashcards

An illustrated Lithuanian Anki deck (A0 → A2+), every picture drawn as a page from a 1981 Lithuanian
civil-defence training album. Two subdecks (`Lietuvių Flashcards::A1`, `::A2`), picture cards, phrase
cards, cloze and sentence cards, human-recorded audio for the A1 core.

**Start here:** `docs/DESIGN_SPEC_CURRENT.md` — the one authoritative statement of the design parameters
in force (image engine, lettering and emblem rules, card front/back, study order, versioning, ways of
working), sourced to the code. `docs/SPEC_RECONCILIATION_2026-10-19.md` says where older documents disagree
with it. The owner's open decisions live on the Review Desk (`review_desk/`).

## Build

```bash
pip install genanki pillow openai
python3 build_study_order_v2.py                  # -> study_order.csv
APKG_LEVELS=A1 python3 build_apkg.py             # -> Lietuviu_Flashcards_v2.1_A1.apkg (APKG_VERSION to bump)
APKG_LEVELS=A2 python3 build_apkg.py
```
Generating or re-rolling pictures: the `gen.py` in each image folder (`out_deck_f62/gen.py`,
`out_deck_a2/gen.py`, `out_deck_sent/gen.py`, `out_phrases_v3/gen.py`), then `python3 qa_images.py <folder>`,
then a review page for the owner. Nothing ships without his verdict.

## Map of the repository

| top level | what it is |
|---|---|
| **Pipeline code (root)** | `build_apkg.py` (the package), `card_frame.py` + `frame_crop.py` (standard bands, caption, section labels, cropping), `build_study_order_v2.py` (learning order), `go_generator.py` (prompt engine and rules), `go_grammars.py` (per-category grammars), `deck_builder.py` + `verb_flashcards.py` (A1 staging, used by the gen scripts), `situations.py` (generated bubble-free phrase staging), `gen_phrases.py`, `go_settings.py` (real places), `historical.py` (precedents/likenesses), `qa_images.py` (QA gate), `frame_preview.py` (screenshots), `build_recorder.py` (recording sheets) |
| **Data (root)** | `cards_anki.csv` (A1 cards), `master_wordlist.csv` + `card_notes.json` (A1 wordlist and staging), `study_order.csv`, `wordlist_a2_pending.csv` (A2 queue), `audio_source.tsv`, `accents_todo_kirtis.csv` (open stress item), `recorder_A2.html` (the owner's recording sheet) |
| `a2_build/` | The A2 list and everything built around it: `a2_wordlist.csv`, `id_map.csv`, `merged_keys.csv`, `deferred_B1.csv`, `context_notes.csv` (usage lines), `restage_bubbles.csv`, `sentences/`, `study_order/`, `historical/`, `src/` (list builders and apply scripts), one folder per review round (`pilot_round2/`, `rollout*/`, `hand_fixes/`, `round3/` …) with its page builder, and the plans (`A1_WRAPUP.md` is current) |
| `a2_rebase/` | The 2026-10-10 rebase of the A2 queue against the official lists; `a2_build/src/build_a2.py` reads it |
| `sources/` | Frequency and lexicon sources (PERLSI 3000, VU A1/A2); PDFs not committed |
| **Images by stage** | `images/` 1.x WebP masters (A1 fallback) · `out_deck_f62/` F6.2 A1 renders (current) · `out_deck_a2/` A2 pictures · `out_phrases_v3/` (+ `round2/`) bubble-free phrase and situation renders · `out_deck_sent/` sentence pictures · `out_phrases_a2/` the few remaining A2 phrase pictures. Each holds its `gen.py`, `ledger.csv` (every prompt), `plan.json`, QA csv and `_rerolled/` (previous versions, `<key>.r<n>.png`). PNGs are not committed. |
| `audio/` | A1 mp3 (human-recorded core, Azure elsewhere); `audio_a2/` appears when the owner records |
| `fonts/` | Brygada 1918 shipped as media; `_superseded/` the retired pair |
| `anki/` | Card CSS (`go_theme.css`, `frame_standard.css`, `back_proposed.css`) and `templates.md` (v2.0 reference) |
| `review_desk/` | The owner's Review Desk SOP, items and builder |
| `build_reports/` | Build-time reports (frame flags, hand-scan results, previews used in reviews) |
| `style_lab/` | The style experiments that settled F6.2 (dated folders with NOTES and analyses) and `research/` (location bank and settings assignments read by `go_settings.py`) |
| `docs/` | `DESIGN_SPEC_CURRENT.md`, `SPEC_RECONCILIATION_2026-10-19.md`, `PLAYBOOK_flashcard_language_system.md` (method, reusable) |
| `_archive/` | Kept history: `deprecated/` (1.6/1.7 code, specs, raw recording masters), `docs/` (superseded GO_STYLE_SPEC, ROADMAP, NEEDS_YOUR_REVIEW), `code/` (driver, build_review, bubbles), `review_packs/`, `out_deck_1.5/` (ledger of the 1.x masters), `recent_versions/` (the bubble pictures replaced on 2026-10-18) |
| `_TO_DELETE/` | Everything judged an orphan on 2026-10-19, with `MANIFEST.csv` (path, size, category, reason). The owner deletes it; git-ignored. |
| `_apkg_media/`, `_qa/`, `__pycache__/` | Caches (transcoded media, QA results); regenerate freely |
| root | `CHANGELOG.md`, `VERSIONS.md` (release history), `ANKIWEB_DESCRIPTION.md`, `LICENSE` (CC BY-NC 4.0), the current `Lietuviu_Flashcards_v2.1_*.apkg` (not committed) |

## License

**[CC BY-NC 4.0](LICENSE)** — free to use, share and adapt for non-commercial purposes, with attribution
and a link back. Applies to the artwork, wordlist, spec and code. The illustrations are AI-generated in a
house style; the copyright status of such images is unsettled and this license states the author's intent.

> "Lietuvių Flashcards" by Dainius Sileika, licensed under CC BY-NC 4.0.
> Source: https://github.com/dainius-sileika/Lithuanian_Flashcards
