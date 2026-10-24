# INDEX — where everything is

*A map of this working directory for someone who knows nothing about it. Five minutes to read; every line
links to a deeper document. Kept current by `tools/check_layout.py` (spec §13). Written 2026-10-24, when the
pictures were gathered from six batch folders into one.*

**The project:** an illustrated Lithuanian Anki deck, A0 → A2+, every picture drawn as a page from a 1981
civil-defence training album. Two subdecks (A1, A2), picture / phrase / cloze / sentence cards, human audio.
Owner: Dainius Sileika. The design is stated in **`docs/DESIGN_SPEC_CURRENT.md`** — read that second.

## 1. The top level

| item | what it is |
|---|---|
| `build_apkg.py` | **Builds the package.** Reads the card lists, `media/images/`, `media/audio/`, writes `Lietuviu_Flashcards_v<ver>_<level>.apkg` and a manifest in `build_reports/builds/`. §4 below. |
| `build_recorder.py` | **Makes the owner's recording sheet** `recorder_A2.html` from what the build emits. §5. |
| `build_study_order_v3.py` | Generates `study_order.csv` (the order new cards are learned). Spec §8. |
| `recorder_A2.html` | The owner's recording sheet (a self-contained web page; its takes live in the browser). Regenerated, never hand-edited. **Stays at the root under this name.** |
| `Lietuviu_Flashcards_v3.0_A1.apkg` | **The current release** (A1, rc4). §12. Not committed; older packages are in `_archive/builds/`. |
| `README.md`, `LICENSE`, `INDEX.md` | Front page (GitHub), CC BY-NC 4.0, this map. |
| `cards_anki.csv` | **Live data:** the 521 A1 base cards (key, Lithuanian, English, gender, forms, pron, level…). |
| `master_wordlist.csv`, `card_notes.json` | Live data: the A1 wordlist (Fluent Forever 625 + additions) and the staging notes the pictures were drawn from. |
| `study_order.csv` | Live data: key → learning position, 1…2433, made by `build_study_order_v3.py`. |
| `audio_source.tsv` | Live data: for every audio file, who made it (`human`, `azure-neural`, `superseded`), its path and what was said. The recorder and the ingest tool read it. |
| `wordlist_a2_pending.csv` | Live data: the A2 queue the recorder and QA still read (the A2 list itself is `a2_build/a2_wordlist.csv`). |
| `card_frame.py`, `frame_crop.py`, `frame_preview.py` | Card front/back templates, the standard-bands frame, cropping of the drawn frame, screenshot previews. |
| `go_generator.py`, `go_grammars.py`, `go_settings.py`, `deck_builder.py`, `verb_flashcards.py`, `situations.py`, `gen_phrases.py`, `historical.py` | The picture engine: prompt rules, per-category grammars, real places, A1 staging, bubble-free phrase staging, historical precedents. Imported by the `gen.py` drivers under `media/generation/`. |
| `qa_images.py` | The QA gate for pictures (`python3 qa_images.py media/images`). Spec §5. |
| `media/` | **All card media.** §2 and §3. |
| `docs/` | The design spec and its history, the version register, how to change the look, the AnkiWeb description, the changelog, the method playbook. §6. |
| `a2_build/` | Everything built around the A2 list: `a2_wordlist.csv`, `sentences/sentences.csv`, `context_notes.csv` (usage lines on the backs), `id_map.csv`, `merged_keys.csv`, `deferred_B1.csv`, `recording_list.csv` (the recorder's take list), `RECORDING_GUIDE.md`, `rename/` (the key maps, §8), `tidy/` (the 2026-10-24 move table, §14), `study_order/` (audits), `src/` (list builders), one folder per review round (`round3/` … `round7/`, `rollout*/`, `pilot_round2/`, `hand_fixes/`…), the plans (`A1_WRAPUP.md`, `PLAN_A2_completion.md`), `audio/inbox/` (where the owner drops exported takes). |
| `rounds/` | **Being created (deep tidy of 2026-10-24):** one dated folder per round of work; plan and move table in `rounds/2026-10-24_deep_tidy/`. This index is rewritten for the new layout in the same tidy. |
| `tools/` | `check_layout.py` (this layout), `style_lock.py`, `spec_release.py`, `golden_set.py`, `verify_apkg.py`, `apkg_keys_list.py`, `rename_keys.py`, `keymap.py`, `ingest_takes.py`, `hooks/pre-commit` + `install_hooks.sh`. |
| `anki/` | Card CSS (`go_theme.css`, `frame_standard.css`, `back_proposed.css`) and `templates.md`. |
| `fonts/` | Brygada 1918 (shipped inside the package as media); `_superseded/` the retired pair; `review/` preview fonts. |
| `style/` | `STYLE_LOCK.json` (the fingerprint of the look) and `golden/` (28 reference pictures with their prompts). §6. |
| `build_reports/` | Build manifests and verify reports (`builds/`), frame-crop flags, hand-scan results, previews. |
| `review_desk/` | The owner's Review Desk: `items.json` (open decisions), `build.py`, `template.html`, `README.md` (the SOP). §7. |
| `a2_rebase/` | The 2026-10-10 rebase of the A2 queue against the official lists (`README.md` has the source URLs). |
| `sources/` | Frequency and lexicon sources (PERLSI 3000, VU A1/A2); the PDFs are not committed. |
| `style_lab/` | The style experiments that settled the F6.2 look (dated folders with notes); kept as a record (owner). `research/` is still read by `go_settings.py`. |
| `_archive/` | Kept history: `deprecated/` (old code and specs), `docs/` (superseded GO_STYLE_SPEC, ROADMAP, the pre-3.0 VERSIONS.md and AnkiWeb text), `builds/` (old packages and release candidates), `data/`, `code/`, `review_packs/`, `recent_versions/` (the bubble pictures replaced on 2026-10-18); `takes/` appears at the first audio ingest (leftover clips of each recorder ZIP). |
| `_TO_DELETE/` | Things judged junk, sorted by reason (`MANIFEST.csv`; `junk_2026-10-24/` = `.DS_Store` and a stray `__pycache__`). **The owner deletes; nobody else.** Gitignored. |
| `_apkg_media/`, `_qa/`, `__pycache__/` | Caches: transcoded card pictures for the package (keyed by source hash), QA results, Python bytecode. Safe to delete; regenerate on the next run. Gitignored. |
| `.azure_key.txt`, `.openai_key.txt`, `.github_token`, `.huggingface_token` | **Secrets.** Gitignored, read from the root by the scripts, never shared, never moved, never printed. |

## 2. Where card X's picture and audio are

Every card has one key, `NNNN_slug` (e.g. `0027_suo`; spec §12). Then:

- its picture is **`media/images/0027_suo.png`** (or `.webp`/`.jpg`) — one folder, one file per key, nothing else to search;
- its audio is **`media/audio/0027_suo.mp3`**; a cloze card's example sentence is `media/audio/<key>_s.mp3`;
- the package shows a cropped copy, `_apkg_media/0027_suo_sf2.jpg`, made by the build (cache; rebuilt when the source changes).

If a key has no file in `media/images/`, the card has no picture (cloze cards by design). `build_apkg.py` reads
exactly these two folders (`IMAGE_DIR`, `AUDIO_DIR`); so do the recorder, the ingest tool and the QA gate.

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
- `a2_build/tidy/moves_2026-10-24.csv` says where every file came from (§14); `tools/keymap.py` turns any old
  card name into the current key (§8). `_archive/` holds retired code, documents and packages.

## 4. How to build a package

```bash
pip install genanki pillow            # once
sh tools/install_hooks.sh             # once per clone (pre-commit: style lock + layout)
APKG_VERSION=3.0 APKG_LEVELS=A1 python3 build_apkg.py     # -> Lietuviu_Flashcards_v3.0_A1.apkg (never overwrites: -1, -2…)
APKG_VERSION=3.0 APKG_LEVELS=A2 python3 build_apkg.py     # -> the A2 package
python3 tools/verify_apkg.py NEW.apkg --against OLD.apkg --key-map a2_build/rename/key_map_v1.csv   # prove what changed
```
The build refuses to run if the code has drifted from `style/STYLE_LOCK.json` (spec §11) and warns if the
layout drifted from this index. Each build writes `build_reports/builds/<package>.json` (spec version, style
hash, commit, counts, media hash) and the deck description inside the package. Release = copy the row into
`docs/VERSIONS.md`. Full procedure for a change of look: `docs/HOW_TO_CHANGE_THE_LOOK.md`.

**New or re-rolled pictures:** `python3 media/generation/<batch>/gen.py …` (each driver's docstring has the
exact calls; `REROLL=key1,key2` moves the old picture to `_history/<batch>/_rerolled/`), then
`python3 qa_images.py media/images`, then a review page for the owner. Nothing ships without his verdict.
Pictures cost money (OpenAI); the drivers read `.openai_key.txt` from the root.

## 5. How to record and ingest audio

1. The owner opens `recorder_A2.html` (Chrome on the Mac) and records; the guide is `a2_build/RECORDING_GUIDE.md`.
   Takes live in the browser's IndexedDB `lt_recorder_A2_afb2ebe2`, which survives regeneration of the page.
2. He clicks **Export new takes** and drops the ZIP into `a2_build/audio/inbox/`.
3. `python3 tools/ingest_takes.py a2_build/audio/inbox/<zip>` converts each clip with ffmpeg to the `dest` in
   `a2_build/recording_list.csv` (`media/audio/<key>.mp3`), moves any take it replaces to `media/audio/_history/`,
   and appends the key's row to `audio_source.tsv`. Leftover clips go to `_archive/takes/<zip>/`.
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
- `docs/SPEC_RECONCILIATION_2026-10-19.md` — where older documents disagree with the spec.

## 7. The Review Desk

The owner decides on one page: https://claude.ai/artifact/R3AF86rbem8AQxpNkdqPSd. Its sources are
`review_desk/items.json` (open items), `review_desk/template.html` and `review_desk/build.py`; answers are stored in
the page's database (collection `answers`). SOP: `review_desk/README.md`. Older review pages: the round folders in
`a2_build/` and `build_reports/`.

## 8. Old card names and the key maps

Cards were renamed once, on 2026-10-20 (spec §12). `a2_build/rename/key_map_v1.csv` and `key_map_v2.csv` are the
only link from the old names (`001_suo`, `A2-0348`, `S-0001`, `265_lupos`) to the current keys; append-only.
`tools/keymap.py` (`canonical`, `aliases`, `lookup`) resolves them; ledgers, QA sheets and reports keep the
names a card had when they were written. `a2_build/rename/APPLIED_v1.md` is the record of the rename.

## 9. Secrets

`.azure_key.txt`, `.openai_key.txt`, `.github_token`, `.huggingface_token` at the root. Gitignored, read by the
scripts from the root; never commit, copy, print or move them.

## 10. Tracked and gitignored

- **Tracked (in GitHub, `dainius-sileika/Lithuanian_Flashcards`, branch `main`):** all code, all data and
  documents, the audio (`media/audio/`), the 1.x WebP masters (`media/images/_history/images/`), the fonts, the
  golden set, the generation records (`media/generation/`), the build manifests.
- **Only on the owner's Mac (gitignored, see `.gitignore`):** the card pictures (`media/images/*.png` and the rest
  of `_history/`, ~5.6 GB), the packages (`*.apkg`), the caches, `recorder_A2.html`'s takes (in Chrome), the
  secrets, `_TO_DELETE/`, raw recordings under `_archive/deprecated/recordings_raw/`, the source PDFs.
  Pictures are distributed through GitHub Releases / AnkiWeb, not through git.

## 11. Proton Drive and git

The working directory is a Proton Drive folder on the owner's Mac. Proton is flaky: it rolls files and `.git`
back, creates `… (# Edit conflict …)` copies, once renamed `.git/index` to `index 2`. Rules that have held:
- commit from a clone **outside** Proton (`~/work/repo` in the Mac VM, or a cloud clone), push to GitHub;
- bring Proton up to date with `git config core.logAllRefUpdates false`, then
  `git fetch origin main && git reset --hard FETCH_HEAD` (the credential helper reads `.github_token`);
- move any `Edit conflict` file and orphan copies under `.git/` into `.git/_sync_conflicts/`;
- re-check 30–60 s later that nothing rolled back;
- untracked files (the pictures) can only be moved in place on the Mac, with a per-file sha1 log, the way
  `tools/rename_keys.py --apply-media` and `a2_build/tidy/tidy_moves.py` do it;
- append-only logs are written outside Proton (`~/a2_work`) and copied in, because Proton locks files that are
  appended to while it syncs.

## 12. The current release

`Lietuviu_Flashcards_v3.0_A1.apkg` (rc4, 2026-10-20) at the root: 147,602,124 bytes, sha256
`42e8456aeef1989d417fef4ca16a9ca54661b6fc615bd229ac7e6504eaf2bb31`; 1,191 notes, 1,427 media files, spec 3.4.0,
style `0885ded5e583`. Manifest `build_reports/builds/v3.0_A1.json`, verify report `v3.0_A1.verify.json`, per-card
list `v3.0_A1_keys_rc4.tsv`. Release candidates rc1–rc3 and the v2.1 packages: `_archive/builds/`. The A2
package is not released yet (`a2_build/PLAN_A2_completion.md`). AnkiWeb text: `docs/ANKIWEB_DESCRIPTION_A1_v3.0.md`.

## 13. Keeping it tidy

`python3 tools/check_layout.py` warns about a file at the root or in `media/` that the layout does not expect, a
picture under `media/generation/`, two current pictures for one key, an old media folder coming back, and a
top-level item this index does not name. The pre-commit hook runs it with `--strict` (a tracked file in the
wrong place, or an unnamed top-level folder, refuses the commit); `build_apkg.py` prints the warnings at the
start of every build. The rules are spec §13. **A new top-level item means a new line in §1, same commit.**

## 14. What moved on 2026-10-24

Before: pictures in `images/`, `out_deck_f62/`, `out_deck_a2/`, `out_deck_sent/`, `out_phrases_v3/` (+`round2/`),
`out_phrases_a2/`, resolved first-hit by the build; audio in `audio/` and `audio_a2/`; old packages and superseded
documents at the root. After: §1–§3. Plan `a2_build/tidy/PLAN_tidy_2026-10-24.md`, move table
`a2_build/tidy/moves_2026-10-24.csv` (3,239 files, old path → new path, sha1), logs `move_log_*.tsv`, result
`a2_build/tidy/APPLIED_tidy_2026-10-24.md` (both packages rebuilt and verified identical in content against the
release). The cards, keys and GUIDs did not change.
