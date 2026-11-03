# Recording guide (one page)

*Executor, 2026-10-19; counts updated 2026-11-03 after audio batch 3. The sheet: `recorder_A2.html` at the repo root. Its list: `data/recording_list.csv`. Both come from `python3 build_recorder.py A2`.*

## What is on the sheet
The sheet lists every take that the current deck still needs: **1,837 takes** (3 Nov 2026, after audio batches 1–3; the sheet started at 2,849). The A1 subdeck comes first, then A2, each in study order (`study_order.csv`, study order v3; same order as `data/recording_order_v3.csv`).

| | takes | of which |
|---|---|---|
| **A1** (takes 1–2) | **2** | 0263_tik *tìk* (failed the safety check twice: say it a touch longer) · 0650_greitai_s re-take |
| **A2** (takes 3–1,837) | **1,835** | 1,771 new · 64 replace the synthetic voice |
| kinds | | 1,169 words · 648 example sentences (`<key>_s`) · 20 sentence cards |

By kind: **A2** 1,168 word takes · 647 example sentences · 20 sentence cards.
Every take is named by its card key (`NNNN_slug`, spec §12); the number on the take is the card's plate number.

These takes are not on the sheet:
- every take already in the deck in your voice with the card's current words (batches 1–3 and the July takes);
- 2434_ka_daryti *Ką daryti?*: an A1 phrase card without a picture yet; it joins the sheet once its picture exists;
- the 31 B1-deferred rows and the 4 merged-away keys.

**Re-take (1, A1; a red "re-take" badge shows the old words):** 0650_greitai_s *Autobusas greitai atvažiuos.* (owner,
2026-11-03: *greitai* before the verb = soon; the batch 3 take said *Autobusas atvažiuos greitai.* and was not shipped).
The re-takes of the earlier rounds (lūpos, mobilusis telefonas, rugsėjis, čekis, the ten colours, the 20 of the
naturalness round) were all recorded in batches 2–3 and are in the deck.

(2026-10-20) The other wording changes had not been recorded, so they went on the sheet as ordinary new takes in their new wording (all recorded since): 0203_prasom_kalbeti_leciau *Prašom kalbėti lėčiau*, 1029_prasom_sestis *Prašom sėstis*, 2136_ar_galite_ka_nors *…parekomenduoti?*, 1653_pakartoti_s, 1112_sestis_s.

The proofreading return of 2026-10-20 changed 26 sentences or headwords (`rounds/2026-10-20_proofread/returned_plan_v1.md`); none of them had been recorded, so they went on the sheet as ordinary new takes in the corrected wording (e.g. 0331_kelinta_valanda *Kelinta valanda?*, 1006_uzsiemimas *užsiėmimas*, 2360_apsidrausti *apsidrausti*, 2392_rakinti_s *Kai rakino duris, atėjo kaimynas.*).

**Takes recorded under the old card names** (the A2-list ids, the three-digit base keys and the sentence ids of before the rename, and the five keys re-slugged on 2026-10-20; all listed in `data/key_maps/key_map_v*.csv`) are not lost: when you click *Enable microphone & start*, the regenerated sheet moves each stored clip to its new key together with the words it was recorded for, and says how many it carried over. A clip whose words have since changed is set aside (in *Export all*, folder `superseded/`); nothing is deleted. Tested headless on 2026-10-20 (`rounds/2026-10-20_rename/recorder_migration_test_v2.txt`). Still: press **Export all** once in the old sheet before opening the new one, as a safety copy.

## How to record
1. **On the Mac**, open this file in **Chrome**: `~/Library/CloudStorage/ProtonDrive-…/50-59 Languages & Learning Method/51 Lithuanian Language & Culture/51.04 Lithuanian Flashcard Project/recorder_A2.html`. You can double-click it in Finder and choose *Open With → Google Chrome*. Use the same browser every time, because your takes are kept in that browser's storage. Safari and Firefox are untested for local files.
2. Click **Enable microphone & start**. The sheet jumps to the first take that has not been recorded yet.
3. Read everything in the dashed box: the headword, then its forms, one breath apart. The *italic* line under the word is the stressed form; say it that way. For sentences, read the sentence once, naturally.
4. Press **Space** to start. Wait for "SPEAK NOW" (0.4 s), speak, wait about half a second, then press **Space** again (the stop key's click is cut away only when it comes at least a quarter of a second after your last sound; in batch 3, 111 takes kept it). With auto-advance on, the sheet moves to the next take. **P** plays the take back; **←/→** move between takes.

**Phone:** opening the file on a phone does not work, because the microphone and the stored takes need a web address. Record on the Mac.

**Session size:** about **100 takes**, roughly 30 minutes at ~15 s a take. The A1 share is about 4 hours in all, so about 10 sessions. Stop when your voice tires; the sheet resumes where you left off.

## After each session: Export new
- Click **⬇ Export new takes**. You get one ZIP with only the takes recorded since the last export (`lt_A2_takes_<date>_batch.zip`). Batches add up; a re-recorded take goes out again in the next batch.
- **Put the ZIP in** `media/audio/_inbox/` in the project folder (since the deep tidy of 2026-10-24; a ZIP dropped in the old `a2_build/audio/inbox/` is still found). ZIPs there are not committed to git. Then tell the executor: "audio batch in the inbox".
- **Export all** is the safety copy. It holds every take in the browser, plus older clips the sheet has set aside (`superseded/`, `off_list/`). Use it once at the end, or before clearing the browser.

## What happens next (executor)
1. The executor first builds a listening page (each take as recorded and as processed) for you. Then `python3 tools/ingest_takes.py --inbox` removes the key clicks at both ends (never closer than 250 ms to your voice; anything doubtful is kept and flagged for you to listen to), brings the volume to the July takes, and writes each clip to the `dest` path in `data/recording_list.csv` (`media/audio/<key>.mp3` for every card since the tidy of 2026-10-24; before that `audio/` for the 520-word base and `audio_a2/` for the rest) and writes the key's row in `audio_source.tsv`, including what was said. A take it replaces moves to `media/audio/_history/`. Your original clips and the ZIP are kept in `_archive/takes/<zip>/`.
2. When the sheet is regenerated, recorded takes drop off it. The browser storage name stays fixed (`lt_recorder_A2_afb2ebe2`), so regenerating never loses a take.
3. If a card's words change later, its stored take is set aside, not deleted, and the card comes back as a re-take.
