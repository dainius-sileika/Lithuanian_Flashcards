# PLAN — the deep tidy of the working directory (2026-10-24, afternoon)

Owner, 2026-10-24: "We're on git, yes? Set it up if not — then go do a deeper tidy, for complete coherency; make a
total index." (Git: GitHub `dainius-sileika/Lithuanian_Flashcards`, branch `main`, was already set up.)

Planner and executor: Fable (sub-agent). The morning tidy (`rounds/2026-10-24_tidy/`) gave the media one home.
This one gives everything else one. Record of what was run: `APPLIED.md`. Rules: `move_rules.csv`; the expanded
move table, one row per file with its sha1: `moves.csv` (1,274 rows, written on the Mac before anything moved);
the logs: `move_log_*.tsv`; the text rewriter for path mentions: `path_map.py`.

## 1. What was wrong

- The root held ~20 Python modules and 6 live data files next to the three programs one actually runs, the
  recorder and the release — "too many path literals; risky" was the morning's reason to leave them.
- `a2_build/` was a grab bag: the A2 list and the other live data, 20 review-round folders, plans, audits, the
  sentence cards, the key maps, the recorder's script, one-shot scripts, the audio inbox, two tidies' records.
- Reports sat in `build_reports/` and `a2_build/study_order/`; one round (`a2_rebase/`) sat at the top level by
  itself; two tables the engine reads sat in `style_lab/research/` (a folder kept as a record).
- Names: `study_order/` the folder beside `study_order.csv` the file; `round3` … `round7`, `rollout_round2`,
  `pilot_round2`, `review_2026-10-17`, `tidy` — all rounds, none dated the same way.
- No complete inventory existed; `INDEX.md` named the top level only.

## 2. The design (spec §13)

```
<root>      build_apkg.py  build_recorder.py  build_study_order_v3.py   recorder_A2.html   Lietuviu_Flashcards_v3.0_A1.apkg
            README.md  INDEX.md  FILES.md  LICENSE  .gitignore   (secrets)   _apkg_media/ _qa/ __pycache__/ (caches)
code/       the 12 pipeline modules (Python only)
data/       every live data file (+ data/sentences/, data/key_maps/)
media/      images/  audio/ (+ _inbox/)  generation/           unchanged from the morning, plus the inbox
docs/       spec + spec_history/, VERSIONS, HOW_TO, PLAYBOOK, RECORDING_GUIDE, the plans, decisions/, AnkiWeb, CHANGELOG
reports/    builds/, frame_*.csv, study_order/, hand_scan/, the screenshot sets          (was build_reports/ + audits)
rounds/     YYYY-MM-DD_<name>/ — one dated folder per round of work, 26 of them         (was a2_build/<round>, a2_rebase/)
tools/      maintenance tools, hooks, make_index + index_descriptions.csv, smoke_test.sh
review_desk/  sources/  anki/  fonts/  style/  style_lab/   as before
_archive/   retired code, docs, data, packages        _TO_DELETE/<reason>/   junk for the owner
a2_build/audio/inbox/README.md                        a forwarding stub for today's recording session only
```

Why this and not something else:

- **`code/` as a folder on `sys.path`, not a package with relative imports.** Every module is imported by bare
  name from a dozen places (`import go_generator as g` in the gen drivers, `style_lock.extract()`, `qa_images`,
  `deck_builder`…). Putting `code/` on `sys.path` in the three entry points, the tools and the drivers keeps every
  import line as it was; a package (`from lt_deck import …`) would have touched them all for no gain. The modules
  find the working directory as the parent of their own folder (`_ROOT`) and read `data/` from there, so they no
  longer depend on the current directory; the entry points still run from the root (their root-relative literals
  are documented as such).
- **The three entry points stay at the root as the real programs**, not thin wrappers: `build_apkg.py` is imported
  as a module by `build_recorder.py`, `tools/rename_keys.py` and the move tools, and the style lock reads its source
  by path; a wrapper would have had to re-export everything. The brief allowed either.
- **`data/` flat**, with only `sentences/` and `key_maps/` as sub-folders. Twenty-odd files are readable at a glance;
  a `data/study_order/` beside `data/study_order.csv` is exactly the near-duplicate the brief forbids, so
  `retier_v3.csv`, `retag_A1.csv`, `recording_order_v3.csv` sit flat. Generated files (`study_order.csv`,
  `recording_list.csv`, `recording_order_v3.csv`) stay in `data/` and are marked *generated* in `FILES.md`:
  they are what the build reads, and a reader looks for them with the other data.
- **`rounds/`, not `reviews/`.** `review_desk/` is live and `reviews/` beside it would be the near-duplicate the
  brief warns about; and not every folder is a review (the cloud round, the audio backfill, the two tidies, the
  rename). "Round" is the word the project has used throughout. Dated `YYYY-MM-DD_<name>` by first commit;
  `round3` → `2026-10-19_fixes_round3` (the READMEs call them "Round 3 fixes"). Each round's one-shot data patch
  (`apply_round3.py` …, `fix_backs_data.py`) moved from `a2_build/src/` into its round, so a round folder is
  self-contained: plan, QA, patch, log, page.
- **`_archive/` keeps its underscore** (the brief's example said `archive/`). The underscore convention — `_archive`,
  `_TO_DELETE`, `_history`, `_inbox`, `_apkg_media`, `_qa` = not part of the live tree — is consistent and useful,
  and renaming `_archive/` would have moved ~800 untracked raw recordings and backups for a cosmetic gain: a risky
  move with a small gain, so not made.
- **The A2-list builder's modules** (`a2_build/src/*.py` minus the live `build_situations.py` and the round
  patches) went to `_archive/deprecated/a2_src_2026-10/`, next to their driver `build_a2.py`, which was already
  retired there on 2026-10-19. The brief suggested `code/`; they are not imported by anything live
  (checked: no live import of `additions`, `lettering`, `official_overrides`, `queue_overrides`, `staging_*`,
  `examples_*`, `bubbles_a2`), so they are history, not code.
- **Live tables out of history folders**: `likeness_args.json` (read by `historical.py`) left
  `a2_build/historical/implementation/`; `settings_assignments.csv` and `location_bank.json` (read by
  `go_settings.py`) left `style_lab/research/`. `rename_keys.LIVE_IN_HISTORY` shrank accordingly. The key maps
  (`key_map_v1.csv`, `key_map_v2.csv`, `topic_map_v1.csv`) are live data read by `tools/keymap.py` and the build, so
  they are `data/key_maps/`; the rename round's plan, logs and tests stay a round.
- **The inbox** moved to `media/audio/_inbox/` (all audio things under `media/audio/`: current takes, `_history/`,
  `_inbox/`). Because the owner may drop a ZIP today, the old path keeps a forwarding note,
  `tools/ingest_takes.py --inbox` reads both folders, and `tools/check_layout.py` points at a ZIP found in the old
  one. The stub is the one impurity at the top level; `INDEX.md` says so and when to remove it.
- **Records keep the paths of their time.** The round folders, ledgers, QA sheets, manifests and the dated rows of
  `VERSIONS.md` and the spec changelog are not rewritten (the morning's rule for keys, spec §12, extended to
  paths). Live code and live documents are rewritten — by `path_map.py`, derived from the move rules, so a
  comment that named `a2_build/pilot_round2/RULES.md` now names `rounds/2026-10-17_pilot_round2/RULES.md`.
  `code/situations.py` is regenerated by `tools/build_situations.py` (only its two header lines change — the
  generator is deterministic, which is itself a check).
- **The total index** is two files. `INDEX.md` stays the 5-minute map. `FILES.md` is generated by
  `tools/make_index.py` from `git ls-files` and the hand-kept `tools/index_descriptions.csv` (one row per file or
  per family; status live / generated / history / cache / secret / source; purpose; who reads and writes it);
  key-named media families are one row with a count; untracked folders are counted, not listed
  (`--untracked`, on the Mac). The pre-commit hook runs `make_index.py --check`: a tracked file without a row, or
  a stale `FILES.md`, refuses the commit. Both files are copied to the claude.ai Project by the lead.
- **The style lock** records each item's `source` file (`go_generator.py` → `code/go_generator.py`) but the style
  hash is computed from item names and values only, so moving the modules cannot change it; `style_lock.py check`
  stayed green through the move with the 3.4.1 lock, and the spec release (3.4.2, patch) rewrites the lock with the
  new `source` paths and the same hash `0885ded5e583`.

## 3. Steps

1. **Inventory**: `git ls-files` by folder; every intra-project import; every path literal in live code
   (`build_apkg.py`, `build_recorder.py`, `build_study_order_v3.py`, the modules, `tools/*.py`, the gen drivers,
   `review_desk/build.py`); the first-commit date of every round folder; the untracked files on the Mac.
2. **Rules → plan** (`tools/move_files.py plan`, on the Mac against the Proton folder): 1,274 rows — 447 tracked,
   827 untracked (the pictures the round pages showed, work folders, `.DS_Store` → `_TO_DELETE/junk_2026-10-24/`).
   Committed first (stage 0) so the plan exists before anything moves.
3. **Stage 1, in the cloud clone**: `apply --tracked` (447 `git mv`); the code for the new paths (sys.path, `_ROOT`
   anchors, data literals, `check_layout.py` rewritten, `rename_keys.py` lists, `keymap.py`, `golden_set.py`,
   `ingest_takes.py --inbox`, `build_recorder.py` output overrides, `review_desk/build.py` made relative,
   `style_lock.py` sources); `path_map.py` over live code and live documents; `code/situations.py` regenerated;
   `.gitignore`; `INDEX.md` rewritten; `tools/make_index.py` + `index_descriptions.csv` + `FILES.md`; the hook;
   `tools/smoke_test.sh` written and green; commit, push.
4. **Stage 2, on the Mac**: Proton `fetch` + `reset --hard` (brings the tracked moves); `apply --untracked`
   (os.rename, sha1 before/after); empty old folders removed; `verify` (1,274 rows); conflict copies under `.git/`
   to `.git/_sync_conflicts/`; re-check after 30–60 s.
5. **Verify**: A1 and A2 rebuilt to scratch on the Mac; `verify_apkg` against rc4 (sha256 42e8456a…) and against
   the morning's `A2_post_tidy.apkg`: 0 field differences, same GUIDs, media identical by sha256; the smoke test
   green on the Mac (recorder regenerated equals the live sheet, `SHEET_ID A2_afb2ebe2` and `migrateKeys` kept);
   `path_map.py --check` over live code and docs finds nothing.
6. **Spec release** 3.4.2 (patch) through `tools/spec_release.py --no-commit`, committed with the required trailer;
   the lock rewritten with the new `source` paths, style hash unchanged.
7. `FILES.md --untracked` recounted on the Mac; `APPLIED.md`; commit, push, Proton synced and re-checked.

## 4. Not moved, and why

- `anki/`, `fonts/`, `style/`, `style_lab/`, `review_desk/`, `sources/`: already one thing each, named in the spec
  and the lock's `source` fields; moving `anki/` into `code/` would have changed lock sources for no clarity.
- `_archive/` → `archive/`: see §2 (800 untracked raw recordings; the underscore convention is the better rule).
- `recorder_A2.html`: the owner is recording; same name, same place, same IndexedDB `lt_recorder_A2_afb2ebe2`.
  Regenerated once (its hint text now names `docs/RECORDING_GUIDE.md`); the KEY_MAP and migration code are the same.
- The release package `Lietuviu_Flashcards_v3.0_A1.apkg`: untouched, re-hashed after.
- Round folders' own scripts (`edit_inset.py`, `restore_before.py`, the `build_page.py`s) still name the folders of
  their time: they are records, used only when the owner asks for a masked edit — fix their paths then.
- `data/wordlist_a2_pending.csv`: the 2026-09 queue is still read by `build_recorder.py`, `qa_images.py` and
  `gen_phrases.py`, so it is live data, not archive.
- `media/generation/<batch>/` names: the historical batch names stay (every ledger and QA sheet names them).
- `docs/CHANGELOG.md`, `docs/VERSIONS.md` rows, the spec changelog, `docs/SPEC_RECONCILIATION_2026-10-19.md`,
  `anki/templates.md`: dated records; their path mentions are of their time.
