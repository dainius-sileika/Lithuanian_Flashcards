# Plan: finish A1 (then A2)

*Lead, 2026-11-03. Owner (verbatim): "All A1 recordings are done. Process them, and then re-orient our plan so that
finishing A1 is the priority, A2 we'll work on after, so make the plan." This plan supersedes the A1 parts of
`docs/A1_WRAPUP.md` (a log of 2026-10-18 that is now mostly done) and parks `docs/PLAN_A2_completion.md` until A1
ships. Live status of every owner question: the Review Desk (https://claude.ai/artifact/R3AF86rbem8AQxpNkdqPSd).*

## What "A1 finished" means

1. Every A1 card has its final Lithuanian: natural (owner's standard, `docs/LESSONS_LEARNED.md`), every displayed
   form stress-marked from a source or by the owner, no card needing a word only A2 teaches.
2. Every A1 card has the owner's voice: no synthetic voice, no silent card, no take whose words differ from the card.
3. Every A1 picture card has an approved picture; the pictures pass the QA gate.
4. A1 package `Lietuviu_Flashcards_v3.0_A1.apkg` (rc5 or later) is built, verified, import-tested, checked by the
   owner on his phone, and uploaded to AnkiWeb with an approved description.

## Where A1 stands (2026-11-03, after audio batch 3)

- **1,192 A1 cards** (A1 block 0001–1191 + the new phrase card 2434 *Ką daryti?*). Study order v3, audit 0 A1→A2
  dependencies (`reports/study_order/AUDIT_v3_4.txt`).
- **Language:** proofreading pass (owner's 25 corrections), naturalness + politeness review (75 changes applied
  2026-10-28, `rounds/2026-10-28_naturalness/APPLIED_v1.md`), one more owner fix on 2026-11-03 (*Autobusas greitai
  atvažiuos*).
- **Stress:** 949 forms sourced (spec 3.5.0); still unmarked until the owner supplies them: A1 rows of
  `rounds/2026-10-28_stress_forms/OWNER_SHEET_v1.csv` (90 A1 / 263 A2) and
  `rounds/2026-10-28_naturalness/OWNER_STRESS_v1.csv` (7).
- **Audio:** batches 1–3 ingested. Batch 3 (2026-11-03): 499 of 501 takes shipped (471 A1, 28 A2), loudness
  median −19.2 LUFS, true peak ≤ −1.51 dBTP, 0 mixed takes; page https://claude.ai/artifact/L9Q2KDUNwW4bRkihSp2Eib
  (`audio_b3`; 133 flagged first, mostly a stop click kept inside the 250 ms guard). Record:
  `rounds/2026-11-03_audio_b3/`.
- **A1 takes left: 3.**
  - `0263_tik` *tìk*: failed the self-check twice ("no speech found"). Say it a little longer, wait half a second
    before Space.
  - `0650_greitai_s` *Autobusas greitai atvažiuos.*: the new word order; the take in batch 3 had the old order and
    was set aside, not shipped.
  - `2434_ka_daryti` *Ką daryti?*: not on the sheet until its picture exists (2.3).
  - Plus whatever the owner decides for the **19 clipped July takes** (1.3).
- **A2 takes left: 1,835** (1,771 new, 64 replacing the synthetic voice). Parked.
- **Pictures:** all shipped A1 picture cards have pictures except the new phrase card *Ką daryti?* (2434).
  Round 7 (0092 *Labai ačiū*) awaits the owner's verdict. 0856 keeps its "1 Lt" picture as an anachronism; the
  sentence says *eurą* (owner 2026-11-03: prices in sentences are euro, litas may stay in pictures as an
  anachronism; the euro has its own A1 cards, 0262 *euras* and 0585 *centas*).
- **Last package:** rc4 (2026-10-20, sha256 42e8456a…), built before the rename-era data changes of 10-28; it is
  out of date.

## The plan, in order

### Phase 1: owner items (only he can do these; all on the Review Desk)
| # | item | why it blocks A1 |
|---|---|---|
| 1.1 | **Record the remaining A1 takes**: 0263 *tìk*, 0650 sentence, then 2434 once its picture exists (list above) | done = "every card has his voice" |
| 1.2 | **Stress sheets**: the 90 A1 rows of `OWNER_SHEET_v1.csv` + the 7 of `OWNER_STRESS_v1.csv`; save as `…_returned.csv` | displayed forms without marks |
| 1.3 | **19 clipped July takes** (recording stopped while the word was sounding; batch 2 page, "July" section): decide re-record (recommended for the A1 ones) | audible defect |
| 1.4 | **Round 7** verdict (0092 *Labai ačiū*) | open picture |
| 1.5 | **Audio pages** (batches 1–3): optional listening; unanswered = processed ships. **Limiter**: default "no" (new takes ~2 dB quieter than July) unless he says otherwise | loudness consistency |
| 1.6 | **AnkiWeb description**: sign or "the author", title, tags, replace the v2.0 share, licence | release text |
| 1.7 | **Duplicate sentences policy**: 34 old pairs share a sentence (`rounds/2026-10-28_naturalness/SECOND_CHECK.md`). Lead's proposal: phrase-card + cloze-card pairs are a deliberate pattern; only true duplicates within one kind get fixed (e.g. 0043/0103 *Atsiprašau*) | consistency |

### Phase 2: executor work (Opus), as soon as the inputs exist
| # | item | input | notes |
|---|---|---|---|
| 2.1 | Ingest each new recording batch (same tool chain), regenerate the recorder | his ZIPs in `media/audio/_inbox/` | `tools/ingest_takes.py`, processing in the cloud |
| 2.2 | Apply the returned stress sheets | 1.2 | record "owner 2026-11-xx" as the source |
| 2.3 | Picture for **2434 *Ką daryti?*** (resigned "what can you do"): situation staging → render → QA (blind questions) → review page → owner verdict | — | ≈ $0.10 |
| 2.4 | Fix the true duplicate sentences (after 1.7) | 1.7 | dependency audit after |
| 2.5 | **Build checks** that make the lessons enforceable: one `{…}` gap per cloze sentence; no identical sentence on two cards of the same kind; every displayed form stressed or on the owner list; template residue; A1 dependency audit = 0 | — | add to `build_apkg.py` or `tools/smoke_test.sh` |
| 2.6 | **Final A1 picture QA sweep** with the round-2 checks (cache keeps cost ≈ $3) | — | gate: zero hard FAIL |
| 2.7 | **Freeze the study order in code.** `build_study_order_v3.py` no longer reproduces the committed `data/study_order.csv` (a re-run reorders 1,952 rows; found 2026-11-03, reverted). Make it read the frozen order (keys = order) and only refresh text columns; then regenerate the stale `data/recording_order_v3.csv` (still says 0857 *litą*) and check the diff is text only | — | do not run the old script before this; lessons "Keys, versions, releases" |

### Phase 3: release
| # | item | who |
|---|---|---|
| 3.1 | Build **A1 rc5** (`APKG_VERSION=3.0 APKG_LEVELS=A1 python3 build_apkg.py`), move rc4 to `_archive/builds/…_rc4.apkg` first; `verify_apkg` against rc4 with the key maps; Anki import test; recount `docs/ANKIWEB_DESCRIPTION_A1_v3.0.*` | executor |
| 3.2 | Regenerate the showcase PDF from rc5 (`tools/build_showcase.py`) | executor |
| 3.3 | Owner imports rc5 on his phone, looks at ~20 cards | owner |
| 3.4 | Owner uploads to AnkiWeb; lead adds the `docs/VERSIONS.md` row and tags the release from the Mac | owner, lead |

Card IDs stay unlocked until A1 **and** A2 are signed off (spec 3.3.0): the description already warns that an
update before the lock may need a re-import.

## After A1: A2 (parked until A1 ships)
1. A2 audio: ~1,863 takes (the sheet continues after A1).
2. Hand-scan pass 2 over the pictures changed since 10-19; historical A2 places; sentence batches 2–3.
3. A2 naturalness is already reviewed (packets B and C); the 263 A2 stress forms on the owner sheet.
4. A2 build, description, upload; then the **key lock** (A1 + A2 signed off).
