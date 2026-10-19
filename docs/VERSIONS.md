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
| v2.1 (A1 + A2) | 2026-10-17 → 2026-10-19 | 3.0.0 (de facto state frozen 2026-10-19) | `9253f93aaa33` (first lock, 2026-10-19) | `e9eca5d` bands · `8822576` full-res build · `87308f0` state locked | standard bands (`card_frame.py`, `frame_crop.py`), proposed backs with thumbnail (2026-10-18), Brygada 1918, `usage` field (schema change → delete-and-reimport), bubble-free situation cards, Lithuanian section labels, one plate sequence, study order v2, emblem scope (Vytis on 097 only; dormant since spec 3.0.1 — 097 restored in round 4). Scratch builds only; not released |
| v3.0 (A1) | 2026-10-19 | 3.2.0 (study order v3) | `ae72a30c53bd` | `4ddbfe8` | **major release** (owner 2026-10-19; was planned as v2.2): delete-and-reimport, keys and GUIDs unchanged and frozen from now on. `Lietuviu_Flashcards_v3.0_A1.apkg`, 1,186 notes / 1,186 cards (levels after the v3 re-tier), 1,424 media files (566 audio), 140.4 MB, sha256 `a390a735…`, media hash `545f12af…`. Study order v3; 150 July owner takes of A2-list cards now shipped (moved to `audio_a2/`), 265 and 249 silent until re-recorded (withdrawn takes); A2-0359 round-6 picture. Manifest `build_reports/builds/v3.0_A1.json`; verification and import test `build_reports/builds/v3.0_A1.verify.json` (`tools/verify_apkg.py`: refs all in the media map, ASCII names, GUIDs identical for the 1,145 keys shared with v2.1, import into a fresh collection with anki 26.09.3: 1,186 notes / 1,186 cards, 5 cards rendered with every file resolved) |

Engine tags before the first package (`legacy-0.1 … legacy-1.7.1`, `v1.7.2`, `v1.7.4`) mark prompt-engine
states, not decks; their story is `_archive/docs/GO_STYLE_SPEC.md` ("File batches ledger") and the root
`VERSIONS.md` (production notes 0.1 → 1.9.2, superseded 2026-10-19).

## Spec releases
| spec | date | tag | note |
|---|---|---|---|
| 3.0.0 | 2026-10-19 | `spec-v3.0.0` | first versioned release of `docs/DESIGN_SPEC_CURRENT.md`; style lock, golden set, build manifest, ledger stamps introduced |
| 3.0.1 | 2026-10-19 | `spec-v3.0.1` | patch, style `65c086a17684` (105 items): `go_grammars.py` (SCENE_TAIL, compose_class, category grammars) added to the lock as six new items — no look change, every prompt identical; §2 emblem allowance described as dormant (097 restored in round 4, no shipped Vytis); §2 poster/sign rule (real period Lithuanian work, declared `card_text`, QA read-back, no blank posters) |
| 3.1.0 | 2026-10-19 | `spec-v3.1.0` | minor, style `ae72a30c53bd` (106 items): `DIRECTION_RULE` added (main figures travel left to right; main actors only, not background; off for `deck_builder.DIRECTION_FREE_ROWS`, `situation_2` and LEFT/RIGHT-named stagings; new renders only — no card re-rolled for it), `FIT_PROMPT` direction question (WARN only); working rule: fix by whole re-roll, not masked edits, unless the owner asks for an edit. **Erratum:** 3.0.1 added a rule (posters/signs) and by §11 should have been a minor release; it is recorded here and not renumbered |
