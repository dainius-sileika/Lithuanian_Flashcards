# Recording guide (one page)

*Executor, 2026-10-19. The sheet: `recorder_A2.html` at the repo root. Its list: `a2_build/recording_list.csv`. Both come from `python3 build_recorder.py A2`.*

## What is on the sheet
The sheet lists every take that the current deck still needs: **2,849 takes**. The A1 subdeck comes first, then A2, each in study order (`study_order.csv`, study order v3; same order as `a2_build/study_order/recording_order_v3.csv`).

| | takes | of which |
|---|---|---|
| **A1** (takes 1–980) | **980** | 945 new · 19 replace the synthetic voice · 16 re-takes |
| **A2** (takes 981–2,849) | **1,869** | 1,795 new · 74 replace the synthetic voice |
| kinds | | 1,813 words · 981 example sentences (`<id>_s`) · 55 sentence cards (`S-####`) |

These takes are not on the sheet:
- the 415 base-deck cards and 150 A2-list cards whose July takes still match the card;
- the 31 B1-deferred rows and the 4 merged-away keys.

**Re-takes (16, all A1; a red "re-take" badge shows the old words):**
- The words are now wrong, so the old take has been withdrawn and the card is silent until you re-record it:
  - 265 *lūpos* (was *lūpa*);
  - 249 *mobilusis telefonas · mobiliojo telefono* (the old genitive was wrong);
  - 0836_rugsejis *rugsėjis · rugsėjo* (was *rugsėjio*);
  - 0923_cekis *čekis* (was *kvitas*);
  - 0521_prasom_pakartoti *Prašom pakartoti*;
  - 0565_prasom_uzrasyti *Prašom užrašyti*.
- The ten colours (069–078) said the genitive (*raudonas · raudono*). The card now shows the feminine (*raudonas · raudona*). The old takes are correct Lithuanian and stay in the deck until you replace them.

The other wording changes were never recorded, so they appear as ordinary new takes in their new wording: 0203_prasom_kalbeti_leciau *Prašom kalbėti lėčiau*, 1029_prasom_sestis *Prašom sėstis*, 2136_ar_galite_ka_nors *…parekomenduoti?*, 1653_pakartoti_s, 1112_sestis_s.

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
