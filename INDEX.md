# INDEX — where everything is

*A map of this working directory for someone who knows nothing about it. Five minutes to read; every line
links to a deeper document. Kept current by `tools/check_layout.py` (spec §13); the complete, generated
inventory of every file is **`FILES.md`** (`tools/make_index.py`). Layout of 2026-10-24 (deep tidy; the
morning tidy of the same day gathered the pictures into `media/`).*

**The project:** an illustrated Lithuanian Anki deck, A0 → A2+, every picture drawn as a page from a 1981
civil-defence training album. Two subdecks (A1, A2), picture / phrase / cloze / sentence cards, human audio.
Owner: Dainius Sileika. The design is stated in **`docs/DESIGN_SPEC_CURRENT.md`** — read that second.
**Then read `docs/LESSONS_LEARNED.md`** — what our mistakes taught us; add to it the day something goes wrong, and give its short list to every agent.

## 1. The top level

One rule: the root holds the programs you run and the things you ship; everything else has a named home.

| item | what it is |
|---|---|
| `build_apkg.py` | **Builds the package.** Reads `data/`, `media/images/`, `media/audio/`, `anki/`, `fonts/`; writes `Lietuviu_Flashcards_v<ver>_<level>.apkg` and a manifest in `reports/builds/`. §4 below. |
| `build_recorder.py` | **Makes the owner's recording sheet** `recorder_A2.html` (and `data/recording_list.csv`) from what the build still needs. §5. |
| `build_study_order_v3.py` | Generates `data/study_order.csv` (the order new cards are learned). Spec §8. |
| `recorder_A2.html` | The owner's recording sheet (a self-contained web page; its takes live in the browser). Regenerated, never hand-edited. **Stays at the root under this name.** |
| `Lietuviu_Flashcards_v3.0_A1.apkg` | **The current release** (A1, rc4). §12. Not committed; older packages are in `_archive/builds/`. |
| `README.md`, `INDEX.md`, `FILES.md`, `LICENSE` | Front page (GitHub), this map, the complete inventory (generated), CC BY-NC 4.0. |
| `code/` | **The pipeline modules**, imported by the three entry points, the tools and the `gen.py` drivers: `card_frame.py` + `frame_crop.py` (the standard-bands frame, cropping), `frame_preview.py` (screenshots), `go_generator.py` / `go_grammars.py` / `go_settings.py` / `deck_builder.py` / `verb_flashcards.py` / `situations.py` (generated) / `gen_phrases.py` / `historical.py` (the picture engine), `qa_images.py` (the QA gate: `python3 code/qa_images.py media/images`). Python only. |
| `data/` | **Every live data file.** `cards_anki.csv` (the 521 A1 base cards), `master_wordlist.csv` + `card_notes.json` (the A1 wordlist and staging), `a2_wordlist.csv` + `a2_staging.json` (the A2 list), `sentences/` (the 55 sentence cards), `context_notes.csv` (usage lines on the backs), `restage_bubbles.csv` (situation staging → `code/situations.py`), `study_order.csv` (generated), `audio_source.tsv` (who made each take), `recording_list.csv` (generated, the recorder's take list), `merged_keys.csv`, `deferred_B1.csv`, `id_map.csv`, `retier_v3.csv`, `retag_A1.csv`, `key_maps/` (**the key history**, §8, + `topic_map_v1.csv`), `likeness_args.json`, `location_bank.json`, `settings_assignments.csv`, `recorder_A2_afb2ebe2_script.json`, `wordlist_a2_pending.csv` (the 2026-09 queue). No code. |
| `media/` | **All card media.** `images/<key>.png` the one current picture of every card, `audio/<key>.mp3` its audio, `_history/` beside each, `audio/_inbox/` where the owner drops recorder ZIPs, `generation/<batch>/` each render batch's ledger, plan, QA sheets and `gen.py`. §2 and §3. |
| `docs/` | The design spec (`DESIGN_SPEC_CURRENT.md`) and its frozen history (`spec_history/`), `VERSIONS.md` (deck ↔ spec ↔ style register), `HOW_TO_CHANGE_THE_LOOK.md`, `PLAYBOOK_flashcard_language_system.md`, `RECORDING_GUIDE.md`, the plans (`A1_WRAPUP.md`, `PLAN_A2_completion.md`), `decisions/` (dated owner decisions and superseded proposals the code still cites), the AnkiWeb description, `CHANGELOG.md` (pre-3.0), `SPEC_RECONCILIATION_2026-10-19.md`. §6. |
| `reports/` | What the tools report: `builds/` (build manifests, verify reports, per-card lists of every package), `frame_bands.csv` + `frame_flags.csv` (frame detection of the last build), `study_order/` (the order audits), `hand_scan/`, the backs / type / labels screenshot sets, `frame_preview/`. |
| `rounds/` | **One dated folder per round of work** (`YYYY-MM-DD_<name>/`), each with its README: the A2 re-base (10-10), the cloud round (10-11), the A1 redo (10-12), the review pages, pilot round 2, additions, benchmark, backs audit, historical places (10-17), hand fixes, phrase additions, roll-outs, section labels, data checks (10-18), fixes rounds 3–7, dep37, the audio backfill (10-19/20), the proofreading round-trip and the key rename (10-20), the two tidies (10-24), the stress marks on the backs' forms (10-28). Everything in them is a closed record; the pictures their pages showed stay on the Mac. |
| `tools/` | Maintenance tools: `check_layout.py` (this layout), `make_index.py` + `index_descriptions.csv` (→ `FILES.md`), `style_lock.py`, `spec_release.py`, `golden_set.py`, `verify_apkg.py`, `apkg_keys_list.py`, `rename_keys.py`, `keymap.py`, `ingest_takes.py`, `build_situations.py`, `move_files.py`, `smoke_test.sh` (runs them all), `hooks/pre-commit` + `install_hooks.sh`. |
| `review_desk/` | The owner's Review Desk: `items.json` (open decisions), `build.py`, `template.html`, `README.md` (the SOP). §7. |
| `sources/` | Third-party word lists: PERLSI 3000 frequency, the VU A1/A2 lexicon, subtitle lemma frequencies (the PDFs are not committed). |
| `anki/` | Card CSS (`go_theme.css`, `frame_standard.css`, `back_proposed.css`) and `templates.md` (superseded notes). |
| `fonts/` | Brygada 1918 (shipped inside the package as media); `_superseded/` the retired pair; `review/` preview fonts (not committed). |
| `style/` | `STYLE_LOCK.json` (the fingerprint of the look) and `golden/` (28 reference pictures with their prompts). §6. |
| `style_lab/` | The style experiments that settled the F6.2 look (dated folders with notes); kept as a record (owner). |
| `_archive/` | Kept history: `deprecated/` (old code, specs, the retired A2-list builder), `docs/` (superseded documents), `data/` (closed records), `code/`, `review_packs/`, `builds/` (old packages, not committed), `recent_versions/` (the bubble pictures replaced on 2026-10-18), `takes/` (leftover clips of each ingested ZIP). |
| `_TO_DELETE/` | Things judged junk, sorted by reason (`MANIFEST.csv`; `junk_2026-10-24/` = `.DS_Store` files and stray `__pycache__`). **The owner deletes; nobody else.** Gitignored. |
| `a2_build/` | **A forwarding stub only**: `audio/inbox/README.md` says the inbox moved to `media/audio/_inbox/`. Remove after the current recording session. |
| `_apkg_media/`, `_qa/`, `__pycache__/` | Caches: transcoded card pictures for the package (keyed by source hash), QA results, Python bytecode. Safe to delete; regenerate on the next run. Gitignored. |
| `.azure_key.txt`, `.openai_key.txt`, `.github_token`, `.huggingface_token` | **Secrets.** Gitignored, read from the root by the scripts, never shared, never moved, never printed. |

Underscore = not part of the live tree (`_archive`, `_TO_DELETE`, `_history`, `_inbox`, the caches).

## 2. Where card X's picture and audio are

Every card has one key, `NNNN_slug` (e.g. `0027_suo`; spec §12). Then:

- its picture is **`media/images/0027_suo.png`** (or `.webp`/`.jpg`) — one folder, one file per key, nothing else to search;
- its audio is **`media/audio/0027_suo.mp3`**; a cloze card's example sentence is `media/audio/<key>_s.mp3`;
- the package shows a cropped copy, `_apkg_media/0027_suo_sf2.jpg`, made by the build (cache; rebuilt when the source changes).

If a key has no file in `media/images/`, the card has no picture (cloze cards by design). `build_apkg.py` reads
exactly these two folders (`IMAGE_DIR`, `AUDIO_DIR`); so do the recorder, the ingest tool and the QA gate.
Its words, forms and English are in `data/cards_anki.csv` (A1 base), `data/a2_wordlist.csv` (A2 list) or
`data/sentences/sentences.csv`; its learning position in `data/study_order.csv`.

## 3. Where the history is

Nothing is ever deleted or overwritten; everything that is not current sits beside the current files:

- **`media/images/_history/<old batch path>/`** — every picture the deck does not show: renders another batch
  outranked (`out_deck_f62/0027_suo.png`), every re-roll (`<batch>/_rerolled/<key>.r<n>.png`), the 1.x WebP masters
  (`images/<key>.webp`), pictures no card uses. The batch names are the historical folders
  (`out_deck_f62` = the F6.2 A1 re-render, `out_deck_a2` = A2 pictures, `out_deck_sent` = sentence pictures,
  `out_phrases_v3` and `round2` = bubble-free phrase cards, `out_phrases_a2` = the bubble-era A2 phrases).
- **`media/audio/_history/`** — replaced takes.
- **`media/generation/<batch>/`** — the text records of every render batch: `ledger.csv` (every prompt ever sent;
  last row per key = that batch's current render), `plan.json`, `cards.csv`, `gen_log.jsonl`, the QA sheets, a
  README, and the batch's `gen.py` driver (which writes new pictures straight into `media/images/`, see §4).
- **`rounds/<date>_<name>/`** — what each round of work did and decided, with its QA sheets and applied patches.
- **`rounds/2026-10-24_tidy/moves_2026-10-24.csv`** and **`rounds/2026-10-24_deep_tidy/moves.csv`** say where
  every file came from (§14); `tools/keymap.py` turns any old card name into the current key (§8). `_archive/`
  holds retired code, documents and packages. Ledgers, QA sheets and round records keep the names and paths of
  their time (spec §12, §13); only live code and live documents are rewritten when something moves.

## 4. How to build a package

```bash
pip install genanki pillow            # once
sh tools/install_hooks.sh             # once per clone (pre-commit: style lock + layout + inventory)
APKG_VERSION=3.0 APKG_LEVELS=A1 python3 build_apkg.py     # -> Lietuviu_Flashcards_v3.0_A1.apkg (never overwrites: -1, -2…)
APKG_VERSION=3.0 APKG_LEVELS=A2 python3 build_apkg.py     # -> the A2 package
python3 tools/verify_apkg.py NEW.apkg --against OLD.apkg --key-map data/key_maps/key_map_v1.csv   # prove what changed
sh tools/smoke_test.sh                # every tool once; green before any commit that touches layout or tooling
```
Run everything from the root. The build refuses to run if the code has drifted from `style/STYLE_LOCK.json`
(spec §11) and warns if the layout drifted from this index. Each build writes `reports/builds/<package>.json`
(spec version, style hash, commit, counts, media hash) and the deck description inside the package. Release =
copy the row into `docs/VERSIONS.md`. Full procedure for a change of look: `docs/HOW_TO_CHANGE_THE_LOOK.md`.

**New or re-rolled pictures:** `python3 media/generation/<batch>/gen.py …` (each driver's docstring has the
exact calls; `REROLL=key1,key2` moves the old picture to `_history/<batch>/_rerolled/`), then
`python3 code/qa_images.py media/images`, then a review page for the owner. Nothing ships without his verdict.
Pictures cost money (OpenAI); the drivers read `.openai_key.txt` from the root.

## 5. How to record and ingest audio

1. The owner opens `recorder_A2.html` (Chrome on the Mac) and records; the guide is `docs/RECORDING_GUIDE.md`.
   Takes live in the browser's IndexedDB `lt_recorder_A2_afb2ebe2`, which survives regeneration of the page.
2. He clicks **Export new takes** and drops the ZIP into `media/audio/_inbox/` (a ZIP dropped in the old
   `a2_build/audio/inbox/` is found too).
3. `python3 tools/ingest_takes.py --inbox` converts each clip with ffmpeg to the `dest` in
   `data/recording_list.csv` (`media/audio/<key>.mp3`), moves any take it replaces to `media/audio/_history/`,
   and appends the key's row to `data/audio_source.tsv`. Leftover clips go to `_archive/takes/<zip>/`.
4. `python3 build_recorder.py A2` regenerates the sheet without the recorded takes (keeps the IndexedDB name and
   the key-migration code). Then rebuild the package (§4).

## 6. Design spec, version register, style lock, golden set

- **`docs/DESIGN_SPEC_CURRENT.md`** — the authoritative design, `**Spec version X.Y.Z**` in its header; frozen
  copies in `docs/spec_history/`, tags `spec-vX.Y.Z`. Change the prose, then `python3 tools/spec_release.py --bump
  major|minor|patch --note "…"` (bump rules in spec §11).
- **`docs/VERSIONS.md`** — deck ↔ spec ↔ style register, one row per package. `docs/CHANGELOG.md` is the older log.
- **`style/STYLE_LOCK.json`** — hash of every look-defining constant; `python3 tools/style_lock.py check` must be
  green before any commit or build. `docs/HOW_TO_CHANGE_THE_LOOK.md` is the procedure.
- **`style/golden/`** — the reference pictures (`manifest.csv`, `<key>.jpg`, `<key>.prompt.txt`), refreshed by
  `tools/golden_set.py`.
- `docs/PLAYBOOK_flashcard_language_system.md` — the method, reusable for another language.
- `docs/SPEC_RECONCILIATION_2026-10-19.md` — where older documents disagreed with the spec when it was frozen.
- `docs/decisions/` — dated owner decisions (`PRASOM_SWITCH_2026-10-18.md`, `merges_2026-10-19.md`) and the
  proposals the spec absorbed (`RESTAGE_PROPOSAL_2026-10-17.md`, `PILOT_24_2026-10-17.md`).

## 7. The Review Desk

The owner decides on one page: https://claude.ai/artifact/R3AF86rbem8AQxpNkdqPSd. Its sources are
`review_desk/items.json` (open items), `review_desk/template.html` and `review_desk/build.py` (run from
`review_desk/`); answers are stored in the page's database (collection `answers`). SOP: `review_desk/README.md`.
Older review pages: the round folders in `rounds/`.

## 8. Old card names and the key maps

Cards were renamed once, on 2026-10-20 (spec §12). `data/key_maps/key_map_v1.csv` and `key_map_v2.csv` are the
only link from the old names (`001_suo`, `A2-0348`, `S-0001`, `265_lupos`) to the current keys; append-only.
`tools/keymap.py` (`canonical`, `aliases`, `lookup`) resolves them; ledgers, QA sheets and reports keep the
names a card had when they were written. The rename itself (plan, dry-runs, logs, the recorder migration test)
is `rounds/2026-10-20_rename/`.

## 9. Secrets

`.azure_key.txt`, `.openai_key.txt`, `.github_token`, `.huggingface_token` at the root. Gitignored, read by the
scripts from the root; never commit, copy, print or move them.

## 10. Tracked and gitignored

- **Tracked (in GitHub, `dainius-sileika/Lithuanian_Flashcards`, branch `main`):** all code, all data and
  documents, the audio (`media/audio/`), the 1.x WebP masters (`media/images/_history/images/`), the fonts, the
  golden set, the generation records (`media/generation/`), the build manifests, the round records.
- **Only on the owner's Mac (gitignored, see `.gitignore`):** the card pictures (`media/images/*.png` and the rest
  of `_history/`, ~5.6 GB), the packages (`*.apkg`), the caches, the pictures the round pages showed
  (`rounds/*/page/media/`), `recorder_A2.html`'s takes (in Chrome), the secrets, `_TO_DELETE/`, raw recordings
  under `_archive/deprecated/recordings_raw/`, the source PDFs. Pictures are distributed through GitHub Releases /
  AnkiWeb, not through git. `FILES.md` counts these folders.

## 11. Proton Drive and git

The working directory is a Proton Drive folder on the owner's Mac. Proton is flaky: it rolls files and `.git`
back, creates `… (# Edit conflict …)` copies, once renamed `.git/index` to `index 2`. Rules that have held:
- commit from a clone **outside** Proton (`~/work/repo` in the Mac VM, or a cloud clone), push to GitHub;
- bring Proton up to date with `git config core.logAllRefUpdates false`, then
  `git fetch origin main && git reset --hard FETCH_HEAD` (the credential helper reads `.github_token`);
- move any `Edit conflict` file and orphan copies under `.git/` into `.git/_sync_conflicts/`;
- re-check 30–60 s later that nothing rolled back;
- untracked files (the pictures) can only be moved in place on the Mac, with a per-file sha1 log, the way
  `tools/rename_keys.py --apply-media` and `tools/move_files.py` do it;
- append-only logs are written outside Proton (`~/a2_work`) and copied in, because Proton locks files that are
  appended to while it syncs.

## 12. The current release

`Lietuviu_Flashcards_v3.0_A1.apkg` (rc4, 2026-10-20) at the root: 147,602,124 bytes, sha256
`42e8456aeef1989d417fef4ca16a9ca54661b6fc615bd229ac7e6504eaf2bb31`; 1,191 notes, 1,427 media files, spec 3.4.0,
style `0885ded5e583`. Manifest `reports/builds/v3.0_A1.json`, verify report `v3.0_A1.verify.json`, per-card
list `v3.0_A1_keys_rc4.tsv`. Release candidates rc1–rc3 and the v2.1 packages: `_archive/builds/`. The A2
package is not released yet (`docs/PLAN_A2_completion.md`). AnkiWeb text: `docs/ANKIWEB_DESCRIPTION_A1_v3.0.md`.

## 13. Keeping it tidy

Three guards, all in the pre-commit hook (`sh tools/install_hooks.sh` once per clone):
- `python3 tools/style_lock.py check` — the look has not drifted from the spec;
- `python3 tools/check_layout.py --strict` — a tracked file in the wrong place (root, `code/`, `data/`, `media/`,
  a round folder not dated), an old folder coming back, or a top-level item this index does not name, refuses the
  commit; `build_apkg.py` prints the warnings at the start of every build;
- `python3 tools/make_index.py --check` — every tracked file has a line in `tools/index_descriptions.csv` and
  `FILES.md` is current; a new file needs its row (or falls under a family rule) in the same commit.
The rules are spec §13. **A new top-level item means a new line in §1, same commit.** `sh tools/smoke_test.sh`
runs every tool once.

## 14. What moved on 2026-10-24

**Morning:** pictures from six batch folders into `media/images/` (+ `_history/`), audio from two folders into
`media/audio/`, batch records into `media/generation/`. Plan `rounds/2026-10-24_tidy/PLAN_tidy_2026-10-24.md`,
move table `moves_2026-10-24.csv` (3,239 files), result `APPLIED_tidy_2026-10-24.md`.

**Afternoon (this layout):** the ~20 modules and 6 data files left the root for `code/` and `data/`; `a2_build/`
(live data, review rounds, plans, audits and tools all mixed) was dissolved into `data/`, `rounds/`, `docs/`,
`reports/`, `sources/`, `tools/` and `_archive/`; `build_reports/` became `reports/`, `a2_rebase/` a round; the
audio inbox moved to `media/audio/_inbox/`. Plan `rounds/2026-10-24_deep_tidy/PLAN.md`, move table `moves.csv`
(1,274 files, old path → new path, sha1), result `APPLIED.md` (both packages rebuilt and verified identical in
content against the release and the morning build). The cards, keys and GUIDs did not change.
