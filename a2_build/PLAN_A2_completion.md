# PLAN — finishing A2 (for the executor agent; written by Fable, 2026-10-12)

You are an executor with no memory of this project. Everything you need is in this file and the
files it names. Do the tasks in order; each has a goal, exact commands, acceptance checks and what
to hand back. Judgement calls (what a card should show, what a word means) are already made and
sit in the data files — do not re-decide them; if a step cannot proceed, stop and report.

## Status 2026-10-12 (executor) — tasks 0–7 done, task 8 waits on the owner
- [x] 1 A1 Redo round: 65 re-rolled + 3 once more (138, 290, 318); QA 0 FAIL. 290/318 still miss (prompt-vs-staging conflict, see out_deck_f62/README.md). Page `out_deck_f62/review_pub/rerolls_2026-10-12/`.
- [x] 2 A2: 49 missing + 8 changed-prompt re-rolls (6 planned + A2-1314, A2-1379); 625/625, ledger current.
- [x] 3 A2 QA: 377 PASS · 245 WARN · 3 FAIL (false positives); 3 real FAILs fixed in one round.
- [x] 4 Phrases: 154 in `out_phrases_a2/` (question-word rows not re-rendered); QA 75 PASS · 74 WARN · 5 FAIL — all five drawn as the bubble spec asks (a "?" or a "0"), not re-rolled.
- [x] 5 Sentences: `out_deck_sent/gen.py` (new), 55 rendered + S-0024 re-rolled (mushroom-cloud blackboard); QA 0 FAIL.
- [x] 6 `Lietuviu_Flashcards_v2.0_A1.apkg` (1077 notes, 140.5 MB), `…_A2.apkg` (1208 notes, 94.4 MB); refs resolve, media ASCII, GUIDs stable across two builds.
- [x] 7 Review pages built (not published): rerolls_2026-10-12, pictures_2026-10-12/part1–3, phrases, sentences.
- Spent: 338 images ≈ $4.56 + QA ≈ 900 inspections ≈ $9.

## 0. Ground rules (owner's, absolute)
- **Never overwrite or delete** an old file, image, audio or .apkg. New versions go beside the old (new folder, `_vN` suffix); generators already move superseded renders into `_rerolled/`. Text files under git may be edited in place.
- **Don't commit, don't push.** The main session commits. Say which files changed.
- Work on the Mac through the device shell: project root `"$HOME/mnt/51 Lithuanian Language & Culture/51.04 Lithuanian Flashcard Project"` (quote it). Python: `$HOME/venv/bin/python` or `python3`. Each shell call dies at 180 s: run generators as `timeout 178 python -u <gen> <launch-window-s> <workers>` and repeat the call until it prints `remaining 0`. Launch window ≈ 15 s, workers 10–40 (Tier-1 OpenAI: 5 images/min → workers 4; check `gen_log.jsonl` timings).
- Logs: generators append to `~/a2_work/` (outside the Proton-synced tree) and copy in once per call. After every run: `find . -name "*Edit conflict*"` — if Proton made conflict copies, list them for the main session (don't delete; `git status` must stay clean of them before a commit).
- Costs: Sunburst medium ≈ **$0.0135 per image**; QA (gpt-5.6-luna) ≈ $0.01 per image. Key: `.openai_key.txt` (read by the scripts). If a call returns 429 "no credits", stop and report the remaining count.
- Don't touch `style_lab/`, `images/` (1.5 masters), `out_deck/`, `audio/`.

## 1. Re-roll the A1 Redo cards (65 keys)
Goal: redraw the 60 cards the owner marked Redo in `out_deck_f62/review_pub/owner_review_2026-10-11.json`, plus 5 Fable fixes (084, 088, 097, 387, 378 — staging already in `card_notes.json`). The staging and declared lettering are done: `card_notes.json` (notes) and `master_wordlist.csv` (`card_text` for 022, 134, 280, 336, 338, 339, 344, 464). `deck_builder.py` now honours a staging line's own `Insets:` list.
1. Keys: `python3 -c "import json;print(','.join(v['key'] for v in json.load(open('out_deck_f62/review_pub/owner_review_2026-10-11.json')) if v['verdict']=='redo'))"` → 60 keys; add `084_tevai,088_brolis,097_prezidentas,387_mokytis,378_zudyti`.
2. Dry-run three prompts and read them: `python3 deck_builder.py --dry-run --only 134_doleris` (expect the ONE DOLLAR exact-text clause), `--only 121_kareivis` (interwar uniform), `--only 300_miskas` (no people in main picture). If a prompt contradicts its staging, report; don't edit staging.
3. `REROLL=<65 keys> timeout 178 python -u out_deck_f62/gen.py 15 10` — repeat until `remaining 0`. Old renders move to `out_deck_f62/_rerolled/`; ledger appends.
4. QA: `QA_WORKERS=20 timeout 176 python -u qa_images.py out_deck_f62 --budget 150 --csv out_deck_f62/qa_f62_rerolls.csv` (cache skips unchanged cards; expect ~65 fresh). Re-roll any FAIL once more (same REROLL command with the failing keys); report persistent FAILs.
Accept: 65 new PNGs dated today; QA PASS or WARN; no edit-conflict files. Budget ≈ 70–80 images ≈ $1.1.
Hand back: list of re-rolled keys + QA table; the review page (task 7).

## 2. Finish the 49 missing A2 pictures and apply the staging fixes
Goal: all 625 IMG rows of `a2_build/a2_wordlist.csv` rendered in `out_deck_a2/`.
1. Rebuild the list first (staging/lettering edited today): `python3 a2_build/src/build_a2.py` → expect `rows 1709`, `warnings 0`. Then refresh the plan: `python3 out_deck_a2/gen.py 0 0 --plan`.
2. `timeout 178 python -u out_deck_a2/gen.py 100 40` → renders the 49 missing (list in `out_deck_a2/README.md`).
3. Re-roll the renderer's flags, whose staging/card_text changed today: `REROLL=A2-0865,A2-0813,A2-0255,A2-1769,A2-0071,A2-0067 timeout 178 python -u out_deck_a2/gen.py 15 10`. Also re-roll the 31 cardinal cards A2-0041…A2-0071 only if their `plan.json` prompt changed (the adapter used to rewrite their card_text; the source now carries digits — compare `plan.json["card_text_rewrites"]`, expect it empty; if the prompts are byte-identical to the rendered ones, skip).
Accept: `ls out_deck_a2/*.png | wc -l` = 625; ledger last row per key current. Budget ≈ 55–90 images ≈ $1.2.

## 3. QA all A2 pictures, re-roll failures
`QA_WORKERS=20 timeout 176 python -u qa_images.py out_deck_a2 --budget 150 --csv out_deck_a2/qa_a2.csv` — ~12 calls for 625. Rules: no undeclared lettering; declared `card_text` present; guessability. Re-roll FAILs: `REROLL=<keys> timeout 178 python -u out_deck_a2/gen.py 15 10`, QA again (`--recheck` not needed; the cache is by file hash). Two rounds maximum; report what still fails with the QA reason — those become owner decisions, not more rolls.
Accept: `qa_a2.csv` complete, FAIL ≤ 2 %. Budget: QA $6 + re-rolls (~10 %, 60 images) $0.8.

## 4. Phrase cards → `out_phrases_a2/`
Goal: picture cards for the 154 PHRASE rows (+ the 10 question-word rows, whose A1 bubbles exist in `out_phrases/` and are reused).
`A2_LIST=a2_build/a2_wordlist.csv PHRASES_OUT=out_phrases_a2 GO_WORKERS=20 timeout 178 python3 gen_phrases.py 60 100` — repeat until done; bubbles come from `bubbles.py` (A2 entries merged from `a2_build/src/bubbles_a2.py`; every PHRASE row has one — verify: `python3 -c "..."` as in `a2_build/README.md` or just check the generator's skip count is 0). Then `QA_WORKERS=20 timeout 176 python -u qa_images.py out_phrases_a2 --budget 150 --csv out_phrases_a2/qa_phrases.csv`; a lone question mark is permitted on question cards only. Re-roll FAILs by deleting nothing: move the PNG to `out_phrases_a2/_rerolled/` and re-run the generator (it renders what is missing).
Accept: 154 PNGs; QA FAIL ≤ 2 %. Budget ≈ 170 images ≈ $2.3 + QA $1.6.

## 5. Sentence-card pictures (55) → `out_deck_sent/`
Goal: one picture per row of `a2_build/sentences/sentences.csv` (keys S-0001…S-0055), staging in `a2_build/sentences/staging.json`, declared lettering in the `card_text` column (3 rows). No renderer exists yet: **copy `out_deck_a2/gen.py` to `out_deck_sent/gen.py`** (new folder; OUT = "out_deck_sent") and feed it rows built from sentences.csv: `id`→key, `subject_phrase_EN` = the English sentence (column `en`), staging line = `staging.json["notes"][id]`, category `Sakiniai`, route IMG, `card_text` from the CSV, class via `a2_adapter.build_call_a2` (the staging starts with "Main picture:", so it replaces the composition clause; dress class civilian; `people` as the staging says). The front of these cards carries a Lithuanian cloze under the picture (built by `build_apkg.py` from `sentences.csv`), so the picture must show the whole proposition — that is what the staging lines do. Print two prompts with `--plan` and read them before rendering. Then QA as above (`qa_images.py out_deck_sent`).
Accept: 55 PNGs, QA PASS/WARN. Budget ≈ 60 images ≈ $0.8.

## 6. Packages (versioned, split for the 250 MB AnkiWeb cap)
Goal: `Lietuviu_Flashcards_v2.0_A1.apkg` and `Lietuviu_Flashcards_v2.0_A2.apkg`, never overwriting `Lietuviu_Flashcards.apkg`.
1. Small code change in `build_apkg.py`: add `APKG_LEVELS` (env, default `A1,A2`) — build only the listed subdecks into the package (filter `DECKS` before `genanki.Package`) and default `APKG_OUT` to `Lietuviu_Flashcards_v{APKG_VERSION}_{levels}.apkg` when one level is given. Both packages keep the same model ids and deck ids, so Anki merges them under one parent deck "Lietuvių Flashcards". Keep `versioned_out()` (suffix -1, -2 if the name exists).
2. `python3 build_study_order_v2.py` (refreshes `study_order.csv`; sentence cards slot after their words; v1 generator superseded 2026-10-17).
3. `APKG_LEVELS=A1 python3 build_apkg.py` and `APKG_LEVELS=A2 python3 build_apkg.py`. Defaults already read A1 images from `out_deck_f62` (fallback `images/`), A2 from `out_deck_a2,out_phrases_a2`, sentences from `out_deck_sent`, A2 audio from `audio_a2/` (empty until the owner records — fine).
4. Verify each package: unzip to a temp dir; `sqlite3 collection.anki2 "select count(*) from notes"`; counts per model (`models` JSON in `col`); every `src="…"`/`[sound:…]` in note fields exists in the `media` map; all media names ASCII; sizes < 250 MB each (if A1 > 250 MB, set `IMG_WIDTH=900`); build twice → identical GUID sets (`select guid from notes`). The cloud test did exactly this (see `a2_build/CLOUD_ROUND_2026-10-11.md` §6); a verifier snippet is in that section's description.
Accept: two .apkg files, both < 250 MB, all references resolve, note counts: A1 ≈ 428 picture + ~640 A2-list rows tagged A1 (cloze/picture) + 35 sentences; A2 ≈ the rest; GUIDs stable.

## 7. Review pages (publish ≤ 255 files per publish)
- **A1 re-rolls:** `python3 out_deck_f62/build_review_pub.py` with the 65 re-rolled keys, showing the new picture, the OLD one from `_rerolled/`, and the owner's note from `owner_review_2026-10-11.json` beside each (read the script's options; if it has no "note" column, add one — the JSON has `key`, `note`, `verdict`). Output under `out_deck_f62/review_pub/rerolls_2026-10-12/`.
- **A2 pictures:** `python3 out_deck_a2/build_review_a2.py` → `out_deck_a2/review_pub/part1`, `part2` (rebuilt after QA; media per part ≤ 255 files — split into part3 if needed).
- **Phrase + sentence cards:** same builder with `out_phrases_a2` and `out_deck_sent` as sources (add a `--src` option if missing) → `out_deck_a2/review_pub/phrases/`, `…/sentences/`.
Hand back to the main session: the folder paths and file counts; it publishes them as artifacts.

## 8. Owner-input tasks (do not start; list them in your report)
- **Audio**: the owner records with `recorder_A2.html` (regenerate with `python3 build_recorder.py A2` if the list changed; takes are keyed `<id>`, `<id>_s`, `S-####`). When ZIPs arrive: convert to `audio_a2/<key>.mp3` (`ffmpeg -i in.webm -codec:a libmp3lame -q:a 4 out.mp3`), update `audio_source.tsv` (human), rebuild the A2 package. Also re-record `265_lupa` (now lūpos).
- **Study order**: owner to confirm `study_order.csv` (first 40 positions listed in `a2_build/CLOUD_ROUND_2026-10-11.md`).
- **Sentence cards batches 2–3** (to ~150): after the owner sees batch 1.
- **Owner review verdicts** on the pages of task 7 → next re-roll list.

## Budget summary
A1 re-rolls ~$1.1 · A2 finish + flags ~$1.2 · A2 QA + re-rolls ~$7 · phrases ~$4 · sentences ~$1 · ≈ **$14–15 total**.

## Files you may edit
`build_apkg.py` (task 6), `out_deck_sent/gen.py` (new, task 5), review builders (task 7), `out_deck_a2/README.md` + `out_deck_f62/README.md` (status notes), `a2_build/PLAN_A2_completion.md` (tick tasks). Everything else: report, don't edit.
