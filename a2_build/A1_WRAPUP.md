# A1 wrap-up — what remains before the A1 subdeck is finished and released

Planner, 2026-10-18. Owner's goal: "wrap up A1, then A2". The A1 subdeck today: 1,164 cards in `study_order.csv` (the 520-card base, the A2-list rows tagged A1 — including the 62 survival items retagged on 2026-10-17 — and 35 sentence cards), packaged as `Lietuviu_Flashcards_v2.1_A1.apkg` with the standard bands and the new backs. Tags: **owner** (only he can do or decide it), **executor** (runs renders, edits, builds), **planner** (writes the staging or plan). Costs are the project's own rates ($0.0135 a render, ≈ $0.02–0.04 an edit, QA ≈ $0.07 a card); "0" means no API spend.

Rule in force throughout (NEEDS_YOUR_REVIEW.md): generate → `qa_images.py` → review page → owner confirms → push. Nothing below ships without the owner's verdict on a review page.

## A. Pictures

| # | item | who | what exactly | cost |
|---|------|-----|--------------|------|
| A1 | **Roll-out verdicts** on the 133 bubble-free situation cards (Roll-out Review page, review desk item `rollout`) | owner | Mark OK/Redo. 48 of the 133 are A1-level phrase cards (greetings, thanks, please, survival formulas). Until this is answered the 201 superseded bubble pictures cannot be deleted and the 19 QA fails cannot be re-rolled with confidence. | 0 |
| A2 | **Roll-out round 2**: re-roll the QA failures per `a2_build/rollout_round2/restage.csv` (15 cards; 11 are A1-level) plus the 6 continuity-only fails by the same pattern | executor | After A1. Two decisions inside it are the owner's: merge *Sudie* into *Viso gero*; merge *atsargiai* (1149) with *Atsargiai!* (0385). | ≈ $0.80 with QA |
| A3 | **Hand-scan fixes**: `build_reports/hand_scan/fix_plan.csv` — 40 cards (3 glitches, 37 minor); 21 are A1 masters | executor | 35 masked edits, 4 re-rolls, 1 covered by A4. The edit tool needs a `dir` for `images/*.webp` and a PNG round-trip; that is a small code change in `a2_build/additions_round2/edit_inset.py`. Purely corrective: no owner decision, but the before/after go on a review page. | ≈ $1.50–2.00 |
| A4 | **Historical places and figures, six-render test** (`a2_build/historical/implementation/test_plan.csv`): T1 plane, T2 author, T3 basketball, T4 court + Cross of Vytis, T5 president = Adamkus + Vytis, T6 Freedom Statue | executor, then **owner** judges | Requires first: merge `location_bank_additions.json`, add `PRECEDENT_RULE` / `LIKENESS_RULE` / `FLAG_RULES["emblem"]` to `go_generator.py` (exact text in `RULES_precedent_likeness.md`), the `precedent=`/`likeness=` arguments, and `FLAG_OVERRIDE` routing. The owner checks: word still guessable; API refusal on T5; Vytis garble. | ≈ $0.15 |
| A5 | **Historical places on the A1 cards** (after A4 passes): 035 teismas, 048 ligoninė (Clinics), 055 bankas, 106/107 stadium, 012 lėktuvas (Lituanica + faces), 097 prezidentas (Adamkus), 123 autorius (Žemaitė, Binkis), optional 113, 122, 138, 112 | executor; **owner** decides 138 (team → basketball?) and the optional likenesses | Staging in `staging_rows.csv`; settings rows only reach A1 cards whose note does not start "Main picture:" (so 106/107 by the bank, 035/048/055 by the staging). | ≈ $0.60–0.90 with re-rolls and QA (A1 share) |
| A6 | **Additions round 2 leftovers**: the 338 pėda redraw and A2-1898/1899 pins are done; check the Additions Round 2 review page verdicts (db `adds2`) and act on any Redo | owner, then executor | 1898 mama and 1899 tėtis are A1-level. | ≈ $0.10 |
| A7 | **Delete the superseded bubble pictures** (`out_phrases/_superseded/` 53 A1 files) once A1 is passed | executor | Keeps the repo and the media folder honest; nothing in the build points at them. | 0 |
| A8 | **Final A1 picture QA sweep**: `qa_images.py` over every A1 image path the build resolves (f62 → images fallback, out_phrases_v3, out_deck_sent) with the round-2 checks, zero hard FAIL as the gate | executor | Catches a stale transcode or a re-roll that never ran QA. | ≈ $25 at $0.07 × ~370 picture cards if run cold; the cache cuts it to the changed files, ≈ $3 |

## B. Data checks

| # | item | who | what exactly | cost |
|---|------|-----|--------------|------|
| B1 | **Genders**: 94 rows of `cards_anki.csv` have an empty `gender` — verbs and adjectives legitimately, but the executor must prove no noun is among them (one script line); the 2026-10-10 gender review (63 rows) was decided, no change needed | executor | 0 |
| B2 | **Rule-derived forms on the A1-tagged A2-list rows**: the 2026-10-17 backs fixes corrected 118 + 5 genitives and the feminines; re-run the same kirtis.info check on every A1-tagged A2-list row whose `check` column still says "rule-derived" (gen_sg, fem) and list what is still unverified | executor | 0 (kirtis.info is free; Wiktionary rate-limits the cloud IP) |
| B3 | **Stress marks**: `accents_todo_kirtis.csv` has 1 `FILL_ME` left; the 9 unmarked A1 prons were fixed on 2026-10-17; confirm every A1-tagged row has a `pron` with a mark (script) | executor | 0 |
| B4 | **Glosses**: the 355 A2-list rows whose English field carries editorial notes (BACKS_AUDIT §1.7) — split display gloss from note for the A1-tagged ones first (the `english_alt`/`notes` columns exist) | planner proposes the split, **owner** skims it | 0 |
| B5 | **Usage notes**: 80 on the backs, 10 owner-approved as written; nothing left here unless the owner wants notes on more cards | — | 0 |
| B6 | **Study order**: adopted 2026-10-17 (v2); add the 10 PIN_AFTER pairs from `a2_build/additions_round2/order_adjacency.csv` (done in data on 2026-10-18? — the executor confirms the pins are in `build_study_order_v2.py` and rebuilds `study_order.csv`); **owner** confirms the first 40 positions once more after the retag | executor, owner | 0 |

## C. Backs, frame and typography

| # | item | who | what exactly | cost |
|---|------|-----|--------------|------|
| C1 | **Lithuanian section labels**: apply `a2_build/section_labels/section_labels_lt.csv` to `card_frame.SECTIONS` and the `::before` text (`{n} skyrius ·`); two choices are the owner's (XVIII *pagalbiniai žodžiai*; XVI *sąvokos* or *idėjos*) | owner decides, executor applies | 0 |
| C2 | **Backs default** (thumbnail redesign, Brygada 1918) is adopted; remaining check: the six phone screenshots in `build_reports/backs_default_2026-10-18/` were made at 390 px — add one AnkiDroid and one desktop Anki screenshot of a real import (fonts embedded, night mode, "do not invert images" noted in the description) | executor | 0 |
| C3 | **Frame flags**: `build_reports/frame_flags.csv` lists 10 of 1,387 pictures whose drawn bands the cropper could not trim cleanly; fix by crop parameter or re-roll | executor | ≈ $0.15 |
| C4 | **Plate numbering** (BACKS_AUDIT §1.10): A1 "1", A2 "0001", sentences "S 0001" — unify or leave; decision pending since 2026-10-17 | **owner** | 0 |

## D. Audio (owner task, parked on the review desk as `t-audio`)

| # | item | who | what exactly | cost |
|---|------|-----|--------------|------|
| D1 | **Record the A1-level takes**: `recorder_A2.html` lists the A1-tagged A2-list rows and the 35 A1 sentences in study order (`a2_build/recording_list.csv`, 2,694 takes in all; the A1 share is roughly the first 640 rows + the sentences); plus the re-take of `265_lupa` (now *lūpos*) and the four *Prašom + infinitive* phrases whose wording changed on 2026-10-17 | **owner** | his time: ≈ 3–4 hours of recording for the A1 share at ~15 s a take |
| D2 | **Ingest**: ZIP → `audio_a2/<key>.mp3` (ffmpeg, `-q:a 4`), `audio_source.tsv` updated, loudness check against the 674 existing A1 files | executor | 0 |
| D3 | **Decision**: ship A1 v2.2 without the new audio (the 520 base cards have audio; the A1-tagged additions would be silent) or wait for D1 | **owner** | 0 |

## E. The v2.2 build and import test

| # | item | who | what exactly | cost |
|---|------|-----|--------------|------|
| E1 | `APKG_VERSION=2.2 APKG_LEVELS=A1 python3 build_apkg.py` after A–D land; `build_study_order_v2.py` first | executor | 0 |
| E2 | **Verify** as in PLAN_A2_completion §6: note count, every `src=`/`[sound:]` in the media map, ASCII media names, < 250 MB, GUIDs identical across two builds | executor | 0 |
| E3 | **Import test on a clean profile**: desktop Anki and AnkiDroid; because the note types changed (usage field, backs, frame) this release is a **delete-and-reimport** for existing users — write that into the release note | executor runs, **owner** looks at 20 cards on his phone | 0 |
| E4 | **Changelog + VERSIONS**: entry for 2.2 (standard bands, Brygada backs, usage notes, bubble-free situations, Lithuanian section labels, study order v2, emblem rule if adopted) | planner | 0 |

## F. The AnkiWeb release

| # | item | who | what exactly | cost |
|---|------|-----|--------------|------|
| F1 | **Description**: `ANKIWEB_DESCRIPTION.md` still says "520 core words"; rewrite for the A1 subdeck (count, picture/cloze/phrase/sentence mix, audio coverage, the 1981 free-Lithuania frame, delete-and-reimport note, licence) | planner drafts, **owner** approves the text | 0 |
| F2 | **Licence and credits**: LICENSE in repo; the description must state the image licence and that pictures are AI-generated in a house style; public-domain works (Čiurlionis) and any named likeness (Adamkus, Darius, Girėnas, Žemaitė, Binkis) listed in the credits if A5 ships them | **owner** decides the wording about living persons | 0 |
| F3 | **Upload** the A1 package under the owner's AnkiWeb account; keep the v2.0 share or replace it (decision) | **owner** | 0 |
| F4 | **Tag the repo** `v2.2-A1`, archive the package in `anki/` or a release asset | executor | 0 |

### Order
A1 → (A2, A3, A4 in parallel) → A5 → B1–B3, C1, C3 → A6–A8 → D (or D3 = ship without) → E → F. The owner's critical path is: roll-out verdicts (A1), four small decisions (A2 merges, C1 words, C4 numbering, D3 audio), the six-render verdict (A4), and the recording (D1).

### Rough total API spend to finish A1: ≈ $7–9 (with the cold QA sweep) or ≈ $4–5 (cached).

---

# A2 — the shorter list after A1

1. **Phrase additions**: render the 69 PHRASE-route benchmark cards from `a2_build/phrase_additions/staging.csv` (65 after the two duplicate merges; three further merges are the owner's call), QA, review page. executor + owner. ≈ $2.50.
2. **Cloze additions**: the ~100 CLOZE-route benchmark rows (A2-1863…1982) need their example sentences checked once more against kirtis (stress) and the `english` gloss split (B4 pattern). executor. 0.
3. **Historical places on the A2 cards** (20 rows of `settings_rows.csv` plus the Freedom Statue swap), after A4; the three deferred B1 cards wait. executor. ≈ $1.
4. **Roll-out round 2, A2 share** (4 cards) and the remaining continuity fails. executor. ≈ $0.30.
5. **Hand-scan pass 2**: the 426 changed keys deferred from the first scan (`build_reports/hand_scan/changed_all.txt`), scanned with the same brief; fixes by the same plan pattern. executor (scan is model time, ≈ $3), then edits.
6. **Sentence cards batches 2–3** (to ~150): design exists; staging is planner work after the owner has seen batch 1 in use. planner + executor. ≈ $1.50.
7. **Audio for A2**: the rest of `recording_list.csv` (≈ 2,000 takes). owner; ≈ 8–10 hours.
8. **B1 pack** (`a2_build/deferred_B1.csv`, 31 rows) stays out of A2.
9. **Build `v2.2_A2.apkg`**, same verification, same delete-and-reimport note; update the description for two packages under one parent deck. executor, owner.
