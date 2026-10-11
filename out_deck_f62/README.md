# out_deck_f62 — the F6.2 / Sunburst re-render (2026-10-11)

Every eligible deck card drawn again by the production path
(`deck_builder.build_call` → `go_generator.build_prompt`) on the production model.
`out_deck/` (the shipped 1.5 masters) is untouched; nothing here is in the `.apkg`
until the owner confirms the review page and the main session swaps the folders.

| | |
|---|---|
| Model | `gpt-image-2.5-sunburst`, quality `medium`, 1536×1024 (one model for the whole deck) |
| Cards | **521** = all of `deck_builder.eligible` (520 shipped cards + new 531 *batonas*); 0 skipped |
| Renders paid for | **545** = 521 first passes + 24 re-rolls (19 cards once, 5 twice) |
| Cost | ≈ **$7.36** at the owner's $0.0135/image (545 × 0.0135); QA calls on top (gpt-5.6-luna, 545 inspections) |
| Render time | median 41 s, p90 72 s, max 122 s per image (439 logged; ~100 log lines lost to a Proton edit-conflict, see below) |
| Content-safety rejections | 3 first-try rejections (217 vonia, 357 skausmas, 400 sprogti), all passed on automatic retry; 0 cards blocked |

## QA (`qa_images.py`, gpt-5.6-luna) — `qa_f62.csv`

Final state after re-rolls: **324 PASS · 196 WARN · 1 FAIL** (99.8 % pass the hard gate).

- **First pass: 4 FAIL / 521** (0.8 %): 032 viešbutis (taxi roof sign "TAXI"), 134 doleris (banknote text),
  159 žaidimas (letters on playing cards), 227 raidė (its own letter "A" read three times — a QA
  false positive on the glyph card, now exempted; see *code changes*).
- **Still failing: 134 doleris.** A dollar bill carries lettering by definition; two re-rolls gave
  "THE UNITED STATES OF AMERICA / ONE DOLLAR" and then "ONE". The first render also put a
  Vytis-type horseman on a litas note (FLAG_RULE breach); the current one is clean apart from "ONE".
  Owner decision needed: declare `card_text` for the bill (e.g. `"ONE DOLLAR"`), or accept the leak,
  or restage without a readable note.
- **Declared lettering (14 cards, the new rule 3 in QA):** every quoted string in `card_text` came
  out exactly on the first pass — 050 "80 ct", 110 "ABC" + "2 + 3 = 5", 151 "NAUJOJI ROMUVA",
  160 "5 Lt.", 334 "m"/"100 cm", 335 "cm", 337 "in", 350 "B C D F G", 351 "A E I O U",
  383 "2 Lt 40 ct", 385 "1 Lt 20 ct", 484/485 "150 Lt"/"2 Lt". (160 shows its tag twice; 362 raštas
  has no quoted string and reads as illegible running hand, as specified.)
- **WARN:** 186 of the 196 are cold-read synonyms (carp/fish, pigeon/bird, pub/bar, "pay" for
  buy/sell…), harmless. The other 10 carry a reviewer note: pseudo-text on newspaper/computer
  screens (123, 152, 250, 253 — illegible squiggle, as on the 1.5 masters), awkward clasped hands
  (139, 140), the mousetrap panel on 378, the bottle inset on 451, "sequence skips E" on 350
  (correct: those are the consonants), and the illegible script on 362 (intended).

## Re-rolls (24 renders, 19 cards) — old versions kept in `_rerolled/`

| Card | Why | Result |
|---|---|---|
| 032 viešbutis | QA: "TAXI" on the cab | fixed (cab stays, no sign) |
| 134 doleris | QA: banknote text + Vytis on litas note | ×1 — still "ONE" (see above) |
| 159 žaidimas | QA: letter "A" on cards | fixed |
| 288 kūnas | QA note: doctor with three arms | fixed |
| 336 kilogramas | scale level with a weight on one pan | ×2 — now apples vs weight, balanced |
| 378 žudyti | mousetrap in the fly-swatting strip | ×2 — mousetrap persists; it is the prompt's "result" panel, not a render fault |
| 148 taika | rifle in an inset of a peace card | now a rifle with a flower in the barrel; acceptable |
| 505 lengvas | feather pan drawn LOWER than the anvil | fixed |
| 312 oras | lung cut-away inset | persists — it is NOUN_STAGING 312's own inset note ("a pair of lungs"); staging, not render |
| 387 mokytis | glowing-brain inset | persists — same, staging-level |
| 416 pralaimėti | main picture was the winner breasting the tape | now the loser in front with the arrow; the winner still visible behind |
| 427 mokyti | blackboard showed a mushroom-cloud lesson, gas mask on desk | now a smoke/pollution diagram; acceptable |
| 513 ji / 517 jie | civil-defence lecture / bunker scene swallowing the pronoun | 513 fixed (map lesson); 517 still a shelter scene but the arrow sits on the group |
| 138 komanda | eleven near-identical faces | more varied; still a team in matching kit |
| 054 kosmosas | Sputnik-type satellite (Soviet emblem by association) | Sputnik again; the staging says "satellite" |
| 084 tėvai, 088 brolis, 097 prezidentas | both main figures face the viewer | ×2 each, pattern persists on every roll — the pair staging ("a man and a woman side by side", two podiums) overrides GAZE_PAIR_RULE; a staging line is needed, not another roll |

## Things I looked at by eye (27 contact sheets, `_sheets/`) and did NOT re-roll

- **Sheen:** skin, hair and cloth are matte throughout. Metal and glass keep a small printed
  highlight on a few object cards (224 raktas, 236 telefonas, 175 alus, 176 sultys, 330 auksas,
  327 deimantas) — the same borderline the F6.2 check accepted (batai, obuolys). No face or
  hair highlight found.
- **Same default face across neighbouring cards:** 251–254 (computer cards) and 258–260
  (head/neck/face) use one and the same young man. Not a per-card fault; worth a word in the
  leads if it bothers you.
- **Anachronisms inherent to the wordlist:** 249 mobilusis telefonas (brick handset, 1983+),
  253 nešiojamasis kompiuteris (luggable). 145 technologija shows a rocket; 147 karas a tank.
- **Civil-defence flavour** leaks into pronoun/teaching cards (427, 513, 517) because the lead
  names the GO album; kept where the arrow still carries the word.
- **Setting integration** is good: Trakai on 017/318, Kernavė mounds on 319, the TV tower on 125,
  koplytstulpiai on 008/034, Laisvės alėja-type street on 027, EU flag on metric cards.
- No Soviet state symbols, no coats of arms, no Vytis except the first 134 roll (replaced).

## Paper (`style_lab/tools/papertone2.py`, strict estimate) — `paper_tone_strict.json`

All 521 measured. **Vignette cards (491): median L\* 87.5 / b\* 19.0** — inside the target
85–88 / 18–23 (IQR of the whole set L\* 84.5–88.5, b\* 17.4–20.4). The 30 full-scene cards
read L\* 79.5 / b\* 17.0 because the estimator measures scene fill, not paper (the F6.2 check noted
the same); their margins are the normal cream. Two vignettes read bright (345 svoris 92.5,
346 krastas 91.5), none dark.

## Review page

`out_deck_f62/review/index.html` (468 KB) + `review/media/` (1 041 JPEGs, 31 MB, 480 px wide):
one row per card, 1.5 master left, F6.2 render right, word, gloss, QA badge, cold read,
lettering read-back, tags (re-rolled, lettering declared, LT setting, full scene), filters by
status/category, and per-card **OK / Redo** buttons with a note field (localStorage) and a
"copy Redo list" button. Opens straight from disk.

## Files

- `gen.py` — the resumable renderer (`timeout 178 python -u out_deck_f62/gen.py 100 40`; `REROLL=key,…` to redo)
- `plan.json` — the 521 frozen prompts with composition / setting / exact_text per card
- `ledger.csv` — 545 rows, deck_builder columns (`key, subject, seed, backend, size, file, prompt`); last row per key is the current picture
- `cards.csv` — Anki fields for the 521 cards (same columns deck_builder writes)
- `gen_log.jsonl` — per-render seconds and token usage (439 of 545; the rest lost to a Proton conflict)
- `qa_f62.csv` — QA verdicts; `paper_tone_strict.json` — paper readings
- `_rerolled/` — superseded renders (`<key>.rN.png`); `_sheets/` — contact sheets + `make_sheets.py`
- `review/` — the owner page; `build_review_f62.py` rebuilds it
- `*.png` — the 521 renders (gitignored, like `out_deck/*.png`)

## Code changes outside this folder (uncommitted; main session to commit)

- `deck_builder.py` — **verbs now pass `card_text`** (`exact_text` + `exclude`) in `build_call`.
  The verb branch dropped them, so 383 pirkti / 385 parduoti would have rendered wordless
  despite their new price tags.
- `qa_images.py` — rule 3: every quoted string in `card_text` must appear in the read-back
  (whitespace/case-insensitive, diacritics and numerals exact) → FAIL "declared text
  garbled/missing"; `+ =` added to the bare-numeral regex; glyph rows (`deck_builder.GLYPH_ROWS`)
  may show their own single letter; `QA_WORKERS` env (default 8); cache saved every 10 images
  and `--budget` is now a hard stop (the old run waited on in-flight futures past the shell cap).
- `.gitignore` — `out_deck_f62/*.png`, `out_deck_f62/review/media/`, `out_deck_f62/_sheets/`.

## Proton note

Appending to `ledger.csv` / `gen_log.jsonl` inside the synced folder during a 40-thread run made
Proton Drive fork six "(# Edit conflict …)" copies and lock the files with `EDEADLK` for ~20 min.
`gen.py` now appends to `~/f62_work/` (outside Proton) and copies in once per call; the conflict
copies were merged and removed. Keep append-only logs out of the synced tree.
