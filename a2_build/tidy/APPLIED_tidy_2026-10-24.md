# Tidy of 2026-10-24: what was applied

Executor: Fable (sub-agent). Plan: `PLAN_tidy_2026-10-24.md`. Move table: `moves_2026-10-24.csv` (3,239 rows:
old path, new path, kind, tracked, bytes, sha1). The numbers below are the tools' own output.

## Commits (origin/main)

| commit | what |
|---|---|
| `f6b756b` | the layout: 1,243 tracked moves (`git mv`, log `move_log_tracked_cloud-clone_2026-10-24.tsv`), code and docs for the new paths, spec 3.4.1 (tag `spec-v3.4.1`), `INDEX.md`, `tools/check_layout.py`, hook |
| (this commit) | the recorder and `recording_list.csv` regenerated for the new audio home, the Mac move log, the verify reports, this file |

## 1. Inventory and the plan (Mac, before anything moved)

`tidy_moves.py plan`: every file under `out_phrases_v3/round2`, `out_phrases_v3`, `out_deck_f62`, `out_deck_a2`,
`out_phrases_a2`, `out_deck_sent`, `images`, `audio`, `audio_a2` and the root candidates; the current picture of
every card computed with `build_apkg.find_image` / `find_a2_image` in the build's own order:
**1,452 current pictures** (the pre-tidy A2 build reports the same 1,452 crops), 1,055 other pictures, 668 current
takes, 6 superseded takes, 44 generation records, 7 root items, 7 junk files. No audio clash (no key had a file in the
folder the build did not read), so merging `audio/` and `audio_a2/` changes nothing.

The 32 top-level pictures the build did not use: 22 lost the first hit to another batch (e.g. `out_phrases_v3/0065_kiek_kainuoja.png`
to `round2/`, `out_deck_sent/0104_kiek_kainuoja_duona.png` to `out_phrases_v3/`); **10 belong to cards that have no
picture route** (cloze question words `0138_kieno`, `0150_kaip`, `0204_kur`, `0215_kas`, `0217_kuris`, `0238_koks`,
`0274_kodel` (round 1 and round 2), `0347_kiek` (both rounds), `0428_kada`, and `1334_nuostabus`) — they are in
`media/images/_history/<batch>/` and could become picture cards if the owner ever wants them; nothing about the deck changed.
14 pictures are named by merged/deferred ids (`A2-1149`, `A2-1187`, 11 `A2-xxxx` in `out_deck_a2`) or by no key (`yes_no.png`): history.

## 2. Baselines

- A1: the release `Lietuviu_Flashcards_v3.0_A1.apkg` (rc4, sha256 `42e8456a…`), unchanged throughout (re-hashed after).
- A2: `~/work/scratch_tidy/A2_pre_tidy.apkg` built from `48acf92` before any move (1,242 notes, 699 media,
  media hash `3349e034…`; manifest `verify/A2_pre_tidy.json`).

## 3. Moves

- **Tracked, in the cloud clone** (`apply --tracked`, `git mv`, sha1 before and after): 1,243 files —
  520 WebP masters → `media/images/_history/images/`, 668 takes → `media/audio/`, 6 → `media/audio/_history/`,
  44 records → `media/generation/<batch>/`, 5 root files (`CHANGELOG.md` → `docs/`; `VERSIONS.md`,
  `ANKIWEB_DESCRIPTION.md` → `_archive/docs/`; `build_study_order_v2.py` → `_archive/deprecated/`;
  `accents_todo_kirtis.csv` → `_archive/data/`). Five of them (the four `gen.py` drivers and `a2_adapter.py`) were
  edited for the new paths in the same commit; `verify` accepts them because they match git at the new path.
- **Proton** brought to `f6b756b` by `fetch` + `reset --hard` (deletion had to be enabled for the session: without
  it git cannot unlink the files it updates; nothing was deleted by hand except the then-empty old folders, see
  below). Clean tree, no `Edit conflict` file; one stale `index.lock` from the first attempt moved to
  `.git/_sync_conflicts/`.
- **Untracked, on the Mac in place** (`apply --untracked`, `os.rename`, sha1 before and after, 44 s):
  **1,996 files** — 1,452 current pictures → `media/images/`, 535 → `media/images/_history/<batch>/…` (the other 520 history
  pictures are the tracked WebP masters, moved by git),
  2 packages → `_archive/builds/`, 7 junk → `_TO_DELETE/junk_2026-10-24/`. Log `move_log_untracked_mac_2026-10-24.tsv`.
- `tidy_moves.py verify` on the Mac: **3,239 ok, 0 missing, 0 old paths still present, 0 wrong.** The emptied
  folders `out_deck_a2/`, `out_deck_f62/`, `out_deck_sent/`, `out_phrases_a2/`, `out_phrases_v3/` (and their empty
  `_rerolled/`, `review_pub/`, `__pycache__/`) were removed (`find -type d -empty -delete`); `images/`, `audio/`,
  `audio_a2/` were emptied by git.

## 4. Verification

- **A1 rebuilt** to `~/work/scratch_tidy/A1_post_tidy.apkg` from the new layout: 1,191 notes, 1,427 media, media hash
  `4777a602…` = rc4's. `verify_apkg.py --against Lietuviu_Flashcards_v3.0_A1.apkg --key-map key_map_v1.csv`:
  **ok; 0 field differences; GUIDs 1,191 in both, 0 changed, 0 new, 0 missing;** refs 1,424 (567 sounds), 0 missing;
  identity 0/0/0/0/0; 140.8 MB. Media inside the two zips compared name by name and sha256: **1,427 = 1,427, identical.**
  (`verify/A1_post_tidy.verify.json`, `verify/A1_post_tidy.json`.)
- **A2 rebuilt** to `A2_post_tidy.apkg`: 1,242 notes, 699 media, media hash `3349e034…` = the pre-tidy build's.
  Against `A2_pre_tidy.apkg`: **ok; 0 field differences; GUIDs 1,242 / 0 / 0 / 0;** refs 696 (101 sounds); media
  **699 = 699, identical.** (`verify/A2_post_tidy.verify.json`, `verify/A2_post_tidy.json`.)
- `tools/style_lock.py check`: OK, style `0885ded5e583`, spec 3.4.1 (no drift override anywhere).
- `tools/check_layout.py --strict`: OK on the Mac and in the clone.
- `tools/rename_keys.py --verify` on the Mac: every data file NNNN_slug; media under the new names: image 1,462, audio 668
  (the 971 without a picture are cloze cards); the expected WARN for `recorder_A2.html`; **one FAIL that predates
  this work:** `review_desk/items.json` carries 6 old names (`531_batonas`, `A2-0359`, `A2-0782`, `A2-1191`,
  `A2-1297`, `A2-1360`) in the prose of two Review Desk items, since commit `1ffa840` (2026-10-20). Not touched here —
  it is the owner's open-items file; the lead may add the current keys.
- `tools/golden_set.py --status`: all 28 golden keys resolve to `media/images/<key>.png` (each came from the batch
  whose ledger describes it).
- Stale paths: a grep of live code and docs for `out_deck_*`, `out_phrases*`, `audio_a2`, `images/`, `audio/` finds
  only history notes, the batch names used as names, and `anki/templates.md` (superseded 2026-10-19, kept as is).
- The release package: sha256 `42e8456aeef1989d417fef4ca16a9ca54661b6fc615bd229ac7e6504eaf2bb31`, unchanged.

## 5. Recorder

`build_recorder.py A2` on the Mac: 2,849 takes (A1 988: new 952, replace-tts 20, retake 16; A2 1,861: new 1,788,
replace-tts 73), IndexedDB `lt_recorder_A2_afb2ebe2` (`SHEET_ID`), KEY_MAP of 4,878 old take keys and the migration code
unchanged. Diff against the previous page: **one line differs, the `WORDS` data line**, and in it only the `dest` of
each take (`audio/…`, `audio_a2/…` → `media/audio/…`). `recording_list.csv`: 2,849 rows, only the `dest` column changed.
`tools/ingest_takes.py` takes the dest from this list; `a2_build/RECORDING_GUIDE.md` says so.

## 6. Left for the owner

1. `_TO_DELETE/junk_2026-10-24/`: six `.DS_Store` files and one `__pycache__` from the old batch folders. Delete.
2. `_TO_DELETE/_apkg_media_pre_rename_2026-10-20/` (436 MB) and `_TO_DELETE/rc3_transfer/` were already waiting.
3. The 10 unused pictures of cloze cards (§1) sit in `media/images/_history/`; a picture route for any of them is a
   content decision, not a tidy.
4. `review_desk/items.json` old names (§4).
5. `edit_inset.py` and `restore_before.py` (round tools) still name the old folders; fix when next used.
6. The tag `spec-v3.4.1` is pushed with this commit (the first push of the tag was cut off by the proxy).
