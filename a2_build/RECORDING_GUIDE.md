# Recording guide (one page)

*Executor, 2026-10-19; counts updated 2026-10-20 after the key rename and the proofreading return. The sheet: `recorder_A2.html` at the repo root. Its list: `a2_build/recording_list.csv`. Both come from `python3 build_recorder.py A2`.*

## What is on the sheet
The sheet lists every take that the current deck still needs: **2,849 takes**. The A1 subdeck comes first, then A2, each in study order (`study_order.csv`, study order v3; same order as `a2_build/study_order/recording_order_v3.csv`).

| | takes | of which |
|---|---|---|
| **A1** (takes 1–988) | **988** | 952 new · 20 replace the synthetic voice · 16 re-takes |
| **A2** (takes 989–2,849) | **1,861** | 1,788 new · 73 replace the synthetic voice |
| kinds | | 1,813 words · 981 example sentences (`<key>_s`) · 55 sentence cards |

By kind: **A1** 619 word takes · 334 example sentences · 35 sentence cards (369 sentence takes in all);
**A2** 1,194 word takes · 647 example sentences · 20 sentence cards (667 sentence takes).
Every take is named by its card key (`NNNN_slug`, spec §12); the number on the take is the card's plate number.

These takes are not on the sheet:
- the 415 base-deck cards and 150 A2-list cards whose July takes still match the card;
- the 31 B1-deferred rows and the 4 merged-away keys.

**Re-takes (16, all A1; a red "re-take" badge shows the old words):**
- The words are now wrong, so the old take has been withdrawn and the card is silent until you re-record it:
  - 1124_lupos *lūpos* (was *lūpa*);
  - 1082_mobilusis_telefonas *mobilusis telefonas · mobiliojo telefono* (the old genitive was wrong);
  - 0836_rugsejis *rugsėjis · rugsėjo* (was *rugsėjio*);
  - 0923_cekis *čekis* (was *kvitas*);
  - 0521_prasom_pakartoti *Prašom pakartoti*;
  - 0565_prasom_uzrasyti *Prašom užrašyti*.
- The ten colours (0617_raudonas … 0626_pilkas) said the genitive (*raudonas · raudono*). The card now shows the feminine (*raudonas · raudona*). The old takes are correct Lithuanian and stay in the deck until you replace them.

The other wording changes were never recorded, so they appear as ordinary new takes in their new wording: 0203_prasom_kalbeti_leciau *Prašom kalbėti lėčiau*, 1029_prasom_sestis *Prašom sėstis*, 2136_ar_galite_ka_nors *…parekomenduoti?*, 1653_pakartoti_s, 1112_sestis_s.

The proofreading return of 2026-10-20 changed 26 sentences or headwords (`a2_build/proofread/returned_plan_v1.md`); none of them had been recorded, so they are ordinary new takes in the corrected wording (e.g. 0331_kelinta_valanda *Kelinta valanda?*, 1006_uzsiemimas *užsiėmimas*, 2360_apsidrausti *apsidrausti*, 2392_rakinti_s *Kai rakino duris, atėjo kaimynas.*).

**Takes recorded under the old card names** (`A2-0348`, `001_suo`, `S-0001` …, and the five keys re-slugged on 2026-10-20) are not lost: when you click *Enable microphone & start*, the regenerated sheet moves each stored clip to its new key together with the words it was recorded for, and says how many it carried over. A clip whose words have since changed is set aside (in *Export all*, folder `superseded/`); nothing is deleted. Tested headless on 2026-10-20 (`a2_build/rename/recorder_migration_test_v2.txt`). Still: press **Export all** once in the old sheet before opening the new one, as a safety copy.

## How to record
1. **On the Mac**, open this file in **Chrome**: `~/Library/CloudStorage/ProtonDrive-…/50-59 Languages & Learning Method/51 Lithuanian Language & Culture/51.04 Lithuanian Flashcard Project/recorder_A2.html`. You can double-click it in Finder and choose *Open With → Google Chrome*. Use the same browser every time, because your takes are kept in that browser's storage. Safari and Firefox are untested for local files.
2. Click **Enable microphone & start**. The sheet jumps to the first take that has not been recorded yet.
3. Read everything in the dashed box: the headword, then its forms, one breath apart. The *italic* line under the word is the stressed form; say it that way. For sentences, read the sentence once, naturally.
4. Press **Space** to start. Wait for "SPEAK NOW" (0.4 s), speak, then press **Space** again. With auto-advance on, the sheet moves to the next take. **P** plays the take back; **←/→** move between takes.

**Phone:** opening the file on a phone does not work, because the microphone and the stored takes need a web address. Record on the Mac.

**Session size:** about **100 takes**, roughly 30 minutes at ~15 s a take. The A1 share is about 4 hours in all, so about 10 sessions. Stop when your voice tires; the sheet resumes where you left off.

## After each session: Export new
- Click **⬇ Export new takes**. You get one ZIP with only the takes recorded since the last export (`lt_A2_takes_<date>_batch.zip`). Batches add up; a re-recorded take goes out again in the next batch.
- **Put the ZIP in** `a2_build/audio/inbox/` in the project folder. ZIPs there are not committed to git. Then tell the executor: "audio batch in the inbox".
- **Export all** is the safety copy. It holds every take in the browser, plus older clips the sheet has set aside (`superseded/`, `off_list/`). Use it once at the end, or before clearing the browser.

## What happens next (executor)
1. The executor converts each clip to the `dest` path in `recording_list.csv` (`audio/` for the 520-word base, `audio_a2/` for the rest) and writes the key's row in `audio_source.tsv`, including what was said.
2. When the sheet is regenerated, recorded takes drop off it. The browser storage name stays fixed (`lt_recorder_A2_afb2ebe2`), so regenerating never loses a take.
3. If a card's words change later, its stored take is set aside, not deleted, and the card comes back as a re-take.
