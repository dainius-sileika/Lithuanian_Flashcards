# out_deck_a2 — A2 picture cards, first renders (2026-10-11)

Every `route = IMG` row of `a2_build/a2_wordlist.csv` drawn by the production prompt
path on the production model, into `out_deck_a2/<id>.png` — the folder
`build_apkg.find_a2_image` already searches (`A2_IMAGE_DIRS`). Nothing in `a2_build/`,
`master_wordlist.csv` or `cards_anki.csv` was touched.

**Status: 576 of 625 rendered, then the OpenAI account ran out of credits
(HTTP 429 "You have no credits remaining") — 49 cards, the whole QA pass and the
phrase cards are waiting on a top-up.** Everything is resumable; see *To finish*.

| | |
|---|---|
| Model | `gpt-image-2.5-sunburst`, quality `medium`, 1536×1024 |
| Planned | 625 IMG rows (0 skipped; every row has a subject phrase, 369 have a staging line) |
| Rendered | **576** (`ledger.csv` 576 rows, `gen_log.jsonl` 576 renders, 0 re-rolls yet) |
| Not rendered (49) | A2-0101 desertas, 0222 suvenyras, 0252 namų darbai, 0286 skalbiniai, 0309 tingus, 0425 išlipti, 0466 griauti, 0472 pripildyti, 0479 rišti, 0571 kartus, 0606 nagas, 0637 virvė, 0647 krautuvėlė, 0656 sporto salė, 0674 koldūnas, 0677 šoninė, 0695 riešutas, 0703 slyva, 0714 auliniai batai, 0716 saga, 0722 tramvajus, 0728 sėdynė, 0738 pieva, 0744 pelkė, 0750 krūmas, 0751 ąžuolas, 0752 pušis, 0753 beržas, 0755 avis, 0756 ožka, 0758 antis, 0759 žąsis, 0760 triušis, 0761 lapė, 0763 lokys, 0764 elnias, 0765 voverė, 0767 varlė, 0768 gyvatė, 0769 vabzdys, 0771 drugelis, 0772 voras, 0773 skruzdėlė, 0774 gandras, 0775 pelėda, 0782 inžinierius, 0789 statybininkas, 0796 lenta, 0866 moneta |
| Cost so far | 576 × $0.0135 ≈ **$7.78** |
| Render time | median 35 s, p90 58 s |
| Content-safety | 2 first-try rejections (A2-0478 atrakinti "key in a front-door lock", A2-0813 paroda), both passed on automatic retry |
| QA | **not run** (gpt-5.6-luna is on the same account). `qa_images.py` is ready for it: the A2 list is now its first metadata source, so each row's `card_text` is the declared lettering |
| Paper | 576 measured (`paper_tone_strict.json`): vignette cards (514) median L* 86.5 / b* 19.3 — on target (85–88 / 18–23); the 62 full-scene cards read 74.5 (scene fill, estimator limitation as before). Bright: A2-0013 naktis 92.5 (a night card whose paper is the margin), A2-0052, A2-1785 |

## How the A2 rows go through the A1 pipeline — `a2_adapter.py`

`a2_adapter.build_call_a2(row, staging)` is the A2 twin of `deck_builder.build_call`
(a thin adapter, not a parallel prompt builder; the prompt itself still comes from
`go_generator.build_prompt`). What it decides:

- **Class** (insets, dress, vignette-vs-scene): the A2 categories are mapped onto
  `go_grammars.CAT2CLASS`; the catch-all `Nouns` (211 rows) is split by keyword into
  place / person / food / garment / creature / object. Result: object 205, verb 84,
  food 70, attribute 68, place 66, nature 44, person 37, garment 28, vehicle 11,
  body_part 8, creature 3, beverage 1.
- **Verbs**: all 84 carry a staging line, so they get `VERB_INSET_DEFAULT` (F6.2) and
  no `VERB_STAGING` entry is needed.
- **Adjectives / ordinals** (type A): `deck_builder.adj_inset_note`. **Cardinals**
  (type NUM): routed `attribute` with a "same number of things" inset rule.
- **Staging lines** that begin `Main picture:` replace the class composition clause,
  exactly as `deck_builder` does for `card_notes.json`.
- **card_text** → `exact_text`, `exclude` = target, flag `lt`, no bank Setting line
  (`settings_assignments.csv` knows only A1 keys).
- **One rewrite, recorded in `plan.json["card_text_rewrites"]`:** the 31 cardinal
  numerals A2-0041…0071 declare `the numeral for "zero"` etc. — the quoted string is
  the *English word*, which the exact-text rule would have lettered onto the card and
  QA would then have required. The adapter sends `the numeral "0" … "1 000 000"
  written once, very large` instead. **For the A2 builder:** please change those 31
  `card_text` values at source (`a2_build/src/lettering.py`) to the digit strings, or
  QA rule 3 will flag every numeral card as "declared text missing".

## What I saw on the contact sheets (23 sheets, `_sheets/`; QA still to come)

The set is strong — the F6.2 look holds on A2 subjects, lettering came out legibly
where declared (Pr An Tr Kt Pn Št Sk strips, 1981 calendar heads, prices in Lt/ct,
`Gedimino pr. 9, Vilnius`, `Kaunas 100 km`, `Katedra`, `Antakalnis`, `Herkus Mantas`,
`Matematika 5`, `Lietuvių–anglų`, `LIETUVOS RESPUBLIKA`, `Sveikinimai iš Nidos!`,
`200 g`, `1 l`, `−10°`, scoreboards). Things for the owner's eye and for re-rolls once
credits are back:

- **A2-0865 centas** — the coin shows "1", the declared text is "10 ct"; one inset coin
  looks like a euro. Re-roll.
- **A2-0255 diplomas** — American graduation gown and mortarboard, not a 1981
  Lithuanian diploma scene; a staging line is needed (builder).
- **A2-0813 paroda** (safety retry) — includes a cow being judged (agricultural
  exhibition); defensible but odd beside the gallery. Re-roll.
- **A2-1769 paminklas** — a Soviet-looking statue-and-plaque composition; no state
  symbol, but worth a look.
- **A2-0071 milijonas** — numeral drawn on a dark night-sky panel; style outlier.
- **A2-0067 aštuoniasdešimt** — the "80" is small, the coins dominate.
- **A2-0084 adresas / A2-1401 vokas** — handwriting legible but tiny; QA will tell.
- **Compass set A2-1786…1789** — one rose with the arrow on the named point: reads well.
- No Soviet state symbols, no coats of arms, no Vytis seen. Sheen is matte throughout;
  a few glass/metal objects (A2-1262 bottle, A2-1367 glass, A2-0319 batteries) keep a
  small printed highlight, as on the A1 set.

## Files

- `a2_adapter.py` — the row → kwargs adapter (`python out_deck_a2/a2_adapter.py A2-0042` prints a prompt)
- `gen.py` — the resumable renderer (`timeout 178 python -u out_deck_a2/gen.py 100 40`; `REROLL=A2-0865,… ` to redo, superseded renders go to `_rerolled/`)
- `plan.json` — the 625 frozen prompts, class, composition, exact_text, `card_text_rewrites`
- `ledger.csv` — deck_builder columns; `cards.csv` — Anki fields; `gen_log.jsonl` — seconds + usage
- `paper_tone_strict.json`, `_sheets/` (24 contact sheets + `make_sheets.py`)
- `review_pub/part1/` (A2-0010…A2-1240, 367 cards, 318 rendered, media 34 MB) and `review_pub/part2/` (A2-1241…, 258 cards, media 28 MB): publishable owner pages, same design as the F6.2 ones (artifact `db`, collection `review_a2`, localStorage fallback). Rebuild with `build_review_a2.py` after the remaining renders and QA.
- `*.png` — gitignored (`out_deck_a2/*.png`)

## To finish (once the account has credits), in order

1. `timeout 178 python -u out_deck_a2/gen.py 100 40` — one call renders the 49 missing cards.
2. `QA_WORKERS=20 timeout 176 python -u qa_images.py out_deck_a2 --budget 150 --csv out_deck_a2/qa_a2.csv` — about 12 calls for 625 images; re-roll FAILs with `REROLL=`.
3. Phrase cards: `A2_LIST=a2_build/a2_wordlist.csv PHRASES_OUT=out_phrases_a2 GO_WORKERS=20 timeout 178 python3 gen_phrases.py 60 100` (166 rows: 140 UTTER, 14 EXCH, 12 question-word cards whose A1 bubbles already exist in `out_phrases/`), then `qa_images.py out_phrases_a2`.
4. `python out_deck_a2/build_review_a2.py` and publish the two parts.

Append-only logs live in `~/a2_work/` (outside Proton) and are copied in once per call, as for the F6.2 run; no edit-conflict copies appeared this time.
