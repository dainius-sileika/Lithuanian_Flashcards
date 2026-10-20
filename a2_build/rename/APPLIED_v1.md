# Rename v1 + proofreading return: what was applied (2026-10-20)

Executor: Opus, resuming after a container restart. Plans: `PLAN_rename_v1.md` (media method, §9–§12),
`a2_build/proofread/returned_plan_v1.{csv,md}`. Everything below was run and checked; the numbers are the
tools' own output.

## Commits (origin/main)

| commit | what |
|---|---|
| e4600f6 | `rename_keys.py`: `MEDIA_SUFFIX` covers `.edit_rawN` (raw `edit_inset.py` outputs in `_rerolled/`) |
| c780419 | untracked media pass on the Mac, log `media_log_key_map_v1_claude_2026-10-20.tsv` |
| tag `spec-v3.4.0` | annotated, on 02276fe (the commit that released spec 3.4.0), pushed from the Mac |
| 9905180 | proofreading return applied; `key_map_v2.csv` (five re-slugs); study order regenerated; `AUDIT_v3_2.txt`; proofreading export v2 |
| d118d03 | v2 media on the Mac, log `media_log_key_map_v2_claude_2026-10-20.tsv` |
| 9b8cc2b | recorder regenerated on the Mac; headless migration test; `RECORDING_GUIDE.md` |
| 9e746d2 | rc1 manifests renamed (`v3.0_A1_rc1.json`, `v3.0_A1_rc1.verify.json`) |
| a755db9 | v3.0 A1 rebuilt: manifest, verify report, `v3.0_A1_keys_rc2.tsv`, frame reports |
| (this commit) | AnkiWeb description recount, guide wording, this file |

## 1. Sync and tracked media

The Proton working copy went from 9d40d32 to origin/main by `fetch` + `reset --hard` (`core.logAllRefUpdates false`).
All 1,250 rows of `media_log_key_map_v1_tracked.tsv` exist under their new names in Proton, byte-identical
(size + sha1); no old name is left. (The lead's brief said 1,253 tracked media; the log and the 02276fe
message both say 1,250.) No "Edit conflict" file appeared; re-checks 30–60 s later showed no rollback. One
transient "not a git repository" right after the reset cleared on the next call.

## 2. Untracked media (Mac)

`rename_keys.py --apply-media out_phrases_v3/round2 out_phrases_v3 out_deck_f62 out_deck_a2 out_phrases_a2 out_deck_sent`
(the folders that exist on the Mac; there is no `_cloud_media`, `images_a2`, `out_phrases` or `images_sent` there):
**1,969 files renamed in place**, each sha1-checked: out_deck_a2 657 + `_rerolled` 136, out_deck_f62 520 +
`_rerolled` 122, out_deck_sent 55, out_phrases_a2 7, out_phrases_v3 231 + `_rerolled` 210, round2 14 +
`_rerolled` 17. Round 7's `out_phrases_v3/A2-0359.png` → `0092_labai_aciu.png`, and `_rerolled/A2-0359.r1…r8`
+ `.edit_raw3` → `0092_labai_aciu.*`. Re-check after 40 s: 1,969 of 1,969 present with the logged size, 0 old
names back. 17 files keep old names by design: the merged ids A2-1149, A2-1187 and 11 B1-deferred ids.
`--verify` on the Mac tree: **0 FAIL**. Every picture, phrase and sentence card has its image (1,462); the
971 without one are cloze cards (no picture by design).

Proton Drive sync could not be paused from the VM (PLAN §9 asks for it); the pass ran with sync live and
the checks above found nothing amiss.

## 3. Proofreading return

`a2_build/proofread/apply_returned_plan_v1.py` (dry run by default; idempotent): **74 field changes** in
`a2_wordlist.csv` (25 rows), `sentences.csv` (1), `id_map.csv` (4), `context_notes.csv` (1).
EDIT 11, KEEP_TARGET_NEW_SENTENCE 13, RETARGET 2, exactly as planned:
- 1006 *veikla* → **užsiėmimas**: gloss "activity; pastime (also: class, session)", užsiėmìmas, gen užsiėmimo, M;
- 2360 *draustis* → **apsidrausti**: "to take out insurance; to get insured (perf.)", apsidraũsti · apsidraũdžia · apsìdraudė;
- 0331 headword **Kelinta valanda?** (Kelintà valandà?); 2410 headword **Jau metus mokausi lietuvių kalbos**;
- 2392_rakinti pres3 **rakìna**, past3 **rakìno**;
- kirtis.info URLs in `check` as given in the .md; `notes` gets "owner proofread 2026-10-20 … : <action>".
No audio existed for any changed sentence or retargeted word (only 0514_amzius has a word take, *amžius*, unchanged).

**Deviation (not in the plan):** 0331's back-of-card usage note explained *Kuri valanda?* ("Literally 'which
hour?' … kuri dabar valanda?"). Left as it was, the A1 back would explain a form the card no longer shows, so
the note is withdrawn (`confidence` → `withdrawn`, text kept, reason appended). Usage notes on backs: 79 → 78.

**Re-slugs** (`key_map_v2.csv`, written by `amend_v2.py`; numbers kept; slugs by `rename_keys.slug` from the new content):

| v1 key | v2 key |
|---|---|
| 0331_kuri_valanda | 0331_kelinta_valanda |
| 1006_veikla | 1006_uzsiemimas |
| 2360_draustis | 2360_apsidrausti |
| 2410_metus_mokausi_lietuviu_kalbos | 2410_jau_metus_mokausi_lietuviu |
| 1543_ryte_as_geriu_kava | 1543_rytais_geriu_kava |

10 LIVE files rewritten (24 tokens); no tracked media for these keys; on the Mac 2 files renamed
(`out_phrases_a2/0331_…png`: a clock in the speech bubble, no lettering, fits *Kelinta valanda?*;
`out_deck_sent/1543_…png`). Aliases survive: `keymap` resolves A2-1193 → 0331_kuri_valanda → 0331_kelinta_valanda.
`rename_keys.py --verify` without `--map` now composes every `key_map_v*.csv`, and merged/deferred ids are
allowed from any map (an amendment map carries only its own rows). 0 FAIL with v1, v2 and composed.

**Dependency audit** (`a2_build/study_order/AUDIT_v3_2.txt`, `build_study_order_v3.py --report`):
**0 A1 cards needing an A2-only word**, before and after; 1,992 word uses; forward dependencies 7 → 6
(0748_skaicius now precedes 0514_amzius); 92 uses of words no card teaches (86 distinct). The regeneration moved
645 of 2,433 positions (1,788 unchanged, 432 by 1–2, 5 by more than 50). Key numbers did not change, so for
those cards the study position and the plate number now differ (accepted by the lead). The largest move:
**0331_kelinta_valanda 331 → 1069**: the builder ranks a phrase by its rarest word and *kelinta* is rarer than
*kuri*. *Kiek valandų?* (0366) still teaches the time question early.

**Proofreading export v2** (`export_v2.py`): `sentences_for_proofreading_v2.csv` + `sentences_lt_only_v2.txt`
+ `sentences_lt_en_v2.txt`, 1,255 rows, current keys. Checked against v1 through the key map: no row missing or
new, no text change outside the plan, all 26 plan rows changed. v1 files untouched.

## 4. Recorder

`build_recorder.py A2` on the Mac: **2,849 takes** (same as before the rename), IndexedDB `lt_recorder_A2_afb2ebe2`
(unchanged), KEY_MAP of 4,878 old take keys (v1 + v2 composed).

| | takes | status | word takes | sentence takes |
|---|---|---|---|---|
| A1 | 988 | 952 new · 20 replace-tts · 16 retake | 619 | 369 (334 example sentences + 35 sentence cards) |
| A2 | 1,861 | 1,788 new · 73 replace-tts | 1,194 | 667 (647 + 20) |

The 16 A1 re-takes are the ones already listed in the guide (colours, lūpos, mobilusis telefonas, rugsėjis,
čekis, two *Prašom* phrases), not caused by this pass.

Migration test (`recorder_migration_test_v2.py`, output `.txt`): headless Chromium 141 with a fake
microphone, nine clips seeded under old names. Result: 6 moved with their `said:` stamps and a `migrated:`
trail (incl. the chain A2-1193 → 0331_kelinta_valanda and the v1 name 1006_veikla); 1 conflict (old A2-0080_s
while 0514_amzius_s already existed) set aside as `superseded:A2-0080_s:<ms>`; 3 moved clips whose words had
changed set aside as superseded under the new key; 1 off-list clip kept. *Export all* returned all nine blobs,
under the new keys (`superseded/`, `off_list/` included), `manifest.tsv` with new keys. Nothing deleted.

## 5. A1 package

- rc1: `_archive/builds/Lietuviu_Flashcards_v3.0_A1_rc1.apkg` on the Mac (sha256 a390a735…, as in its manifest);
  manifests renamed `build_reports/builds/v3.0_A1_rc1.json`, `v3.0_A1_rc1.verify.json`. `v3.0_A1_keys.tsv` stays as rc1's list.
- `_apkg_media/` (old names) moved to `_TO_DELETE/_apkg_media_pre_rename_2026-10-20` (436 MB), then rebuilt.
- **`Lietuviu_Flashcards_v3.0_A1.apkg`** (Proton folder root, not committed): **147,602,124 bytes, sha256
  baf5ba41cd189e735655cfc822ad318a43993060b3625a4e09cd4e0ca292af25**; 1,191 notes, 1,427 media; spec 3.4.0,
  style 0885ded5e583, built from 9e746d2 (clean tree; no style-drift override).
- `verify_apkg.py --against …rc1.apkg --key-map key_map_v1.csv` (v2 picked up beside it): **0 FAIL**.
  1,186 GUIDs changed exactly as mapped, 0 unexpectedly, 5 new notes (dep37's additions to A1: keltis, muzika,
  tiesa, teisus, šviesti), 0 old notes missing. Field differences modulo the rename: 31 notes = 26 dep37
  rewordings + 5 proofreading corrections (0331, 0514, 0996, 1006, 1141); nothing else.
  Identity: 0 keys not NNNN_slug, 0 plates ≠ key number, 0 bad lt:: tags, 0 level tag ≠ subdeck, 0 picture/phrase/
  sentence notes without an image. 1,424 media references (567 sounds), 0 missing; all names ASCII; 140.8 MB.
- Anki import test (Anki 26.09.3 Python package on the Mac VM, as for rc1): 1,191 notes / 1,191 cards new,
  decks Lietuvių Flashcards::A1; five rendered cards (two picture, two cloze, one sentence) with every file resolved.
- A2 regression build (scratch path in the VM, not shipped or committed): 1,242 notes, 699 media, 90.3 MB, verify 0 FAIL,
  import OK.
- `build_reports/builds/v3.0_A1_keys_rc2.tsv`: per card due, key, plate, level, kind, pos, topic, note type, guid,
  image, audio, audio source. (rc1's list had no header and five columns; this one is wider.)
- Recount: **1,191 cards = 687 picture (420 base + 267 A2-list IMG) + 135 phrase + 334 cloze + 35 sentence;
  audio 547 human, 20 synthetic, 624 silent.** Written into `docs/ANKIWEB_DESCRIPTION_A1_v3.0.{md,html}`.

## Leftovers and things for the owner

1. **0331_kelinta_valanda now sits at study position 1,069** (was 331) after the regeneration. Move it back by hand
   in `study_order.csv` if it should stay early.
2. **0331 has no usage note now** (the old one described *Kuri valanda?*). Write a new one if wanted.
3. **1130_koseti (A1 picture card) ships `pres3 = "{{l"`, `past3 = "lt"`**: a wiki-template fragment, pre-existing,
   on the back of an A1 card. Not touched here: it needs sourced principal parts.
4. Plan items for the owner unchanged: 1975_prognoze, 2392_rakinti, 0514_amzius, 2309_karsciavimas (returned_plan_v1.md, end).
   Words no card teaches, as the plan reported: *intensyvus* (1514), *orų* (1975), *pagerinti* (2201, form check).
5. `restage_bubbles.csv` / `situations.py` still describe 0331's scene with the text "Kuri valanda?" (staging text
   for a re-render; the picture itself has no lettering). `stress_58_resolved.csv` keeps its *Kurì valandà?* row as
   the record of that resolution.
6. `recorder_A2.html` always carries old keys (its embedded KEY_MAP), so `--verify` will keep warning about it.
   That warning is expected.
7. `_TO_DELETE/_apkg_media_pre_rename_2026-10-20` (436 MB) can be deleted by the owner.
8. Before opening the new recorder, the owner should press **Export all** once in the old sheet as a safety copy.
   The tested migration should make this unnecessary, but it costs nothing.
9. AnkiWeb: the v3.0 A1 upload is a delete-and-reimport (all GUIDs changed once).
