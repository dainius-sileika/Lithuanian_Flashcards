# VERSIONS — deck ↔ spec ↔ style register

One row per package version. From spec 3.0.0 on, every build writes its row's facts into
`build_reports/builds/<package>.json` (date, commit, spec version, style hash, counts, media hash) and
into the deck description inside the `.apkg`; copy them here when a package is released. The style hash
is the short form of `style/STYLE_LOCK.json` → `style_hash` (`python3 tools/style_lock.py show`).
Spec versions are tagged `spec-vX.Y.Z`; frozen copies live in `docs/spec_history/`. Rows before 3.0.0
are reconstructed from git and carry no style hash (there was no lock).

| deck version | date | spec version | style hash | commit | notes |
|---|---|---|---|---|---|
| v1.7.6-beta | 2026-07-19 | files 1.7.6 (`_archive/docs/GO_STYLE_SPEC.md`) | — | `87e5a68` (tag `v1.7.6-beta`) | first importable `.apkg`: 519 cards, gpt-image-1.5 masters, Azure audio, drawn red frame, `anki/go_theme.css` |
| v1.7.8 | 2026-07-24 | files 1.7.8 / wordlist 2.9 | — | `322ff6b` (tag `v1.7.8`) | QA round 5, text exceptions on the measure cards, CHANGELOG published |
| v1.8.0 | 2026-07-26 | files 1.8.0 | — | `d0611f6` (tag `v1.8.0`) | human-recorded A1 audio, genitive corrections, deck 78 MB |
| v1.9.2 | 2026-07-28 | files 1.9.2 / wordlist 2.9 | — | `aca77ed` | 520-card beta: question and sequence grammars, gender symbols on the back, 581 recordings cleaned; last 1.x |
| v2.0 (A1 + A2 split) | 2026-10-12 | F6.2 house style (`style_lab/2026-10-10_08_F6_roll/results/production_spec_F6_1.json`, spot-check 09; no single spec document) | — | `0228c67` | engine → gpt-image-2.5-sunburst; A1 re-rendered in F6.2 (`out_deck_f62`), all A2 pictures, bubble phrase cards, 55 sentence pictures; one package per level; drawn frame, v2.0 templates |
| v2.1 (A1 + A2) | 2026-10-17 → 2026-10-19 | 3.0.0 (de facto state frozen 2026-10-19) | `9253f93aaa33` (first lock, 2026-10-19) | `e9eca5d` bands · `8822576` full-res build · `87308f0` state locked | standard bands (`card_frame.py`, `frame_crop.py`), proposed backs with thumbnail (2026-10-18), Brygada 1918, `usage` field (schema change → delete-and-reimport), bubble-free situation cards, Lithuanian section labels, one plate sequence, study order v2, emblem scope (Vytis on 097 only). Scratch builds only; not released |
| v2.2 (A1) | planned | 3.0.0 or later | lock at build time | — | the next A1 release (`a2_build/A1_WRAPUP.md` §E): release now, audio later; the build manifest and this row are filled by `build_apkg.py` |

Engine tags before the first package (`legacy-0.1 … legacy-1.7.1`, `v1.7.2`, `v1.7.4`) mark prompt-engine
states, not decks; their story is `_archive/docs/GO_STYLE_SPEC.md` ("File batches ledger") and the root
`VERSIONS.md` (production notes 0.1 → 1.9.2, superseded 2026-10-19).

## Spec releases
| spec | date | tag | note |
|---|---|---|---|
| 3.0.0 | 2026-10-19 | `spec-v3.0.0` | first versioned release of `docs/DESIGN_SPEC_CURRENT.md`; style lock, golden set, build manifest, ledger stamps introduced |
