# Hand-scan fixes (A3, 2026-10-18)

The 40 cards of `build_reports/hand_scan/fix_plan.csv`. Review page **Hand Fixes** (private artifact,
db collection `handfix`, general notes `handfix_meta/general`): https://claude.ai/artifact/7nzsZ88kikZj9XftaSbauH

## What was done
- **32 masked edits** with `a2_build/additions_round2/edit_inset.py`, regions and per-card instructions in
  `edit_regions.json` (`GO_EDIT_REGIONS=a2_build/hand_fixes/edit_regions.json`). Every A1 key resolves to
  `out_deck_f62/<key>.png` (the build's first hit), not `images/*.webp` as the plan assumed, so the A1 edits
  are PNG edits; the tool's `.webp` round-trip exists but was not needed.
- **4 re-rolls** with the plan's staging sentence: 291_upe and 403_myleti (`card_notes.json`, `out_deck_f62/gen.py`),
  A2-0209 and A2-0679 (`a2_staging.json`, `out_deck_a2/gen.py`).
- **Not fixed, original kept (3):** 512_jis and A2-1433 (three edits each erased the hand or glove instead of
  repainting it), A2-1252 (the edit endpoint's safety filter refused the shower card). Owner's call: OK as is or re-roll.
- 035_teismas is left to the historical re-roll (A5).
- `before.json` names the picture each fix replaced; every superseded file is in `<dir>/_rerolled/`.
  `restore_before.py` puts the original back before a fresh edit; `edit_log.txt` lists every edit call.

## Tool changes (edit_inset.py, qa_images.py)
- `dir` per entry incl. `out_deck_f62` and `images` (ledgers `f62_` / `images_` in ~/a2_work, seeded from the folder's
  ledger first so the copy-back never shortens it); `.webp`/`.jpg` masters are edited as RGB and written back in their format.
- `instruction`: a free sentence for the masked area. `prefill: "blur"`: for removals, the masked pixels go up blurred
  (the endpoint redraws whatever shape it can see). The repaint is colour-matched to a 24 px ring around the mask
  (a grey box showed on flat shirts). `background="opaque"` and a refusal of empty/transparent fills (whole-inset
  masks came back black or blank; use a mask over the hands instead).
- `qa_images.py --limbs`: a caption-blind limbs/props/hands call for non-situation cards (LIMBS/PROPS = FAIL, HANDS = WARN).

## QA (`qa_handfix.csv`, with --limbs)
39 checked (035 not touched): 22 PASS, 13 WARN (guess wording), 4 FAIL, all four CONTINUITY notes on insets that show
other people by design (271, 388, 400, A2-1333); no LIMBS, PROPS or HANDS finding on any fixed card.

## Rebuild the page
`python3 a2_build/hand_fixes/make_pairs.py` (media) then `python3 a2_build/hand_fixes/build_page.py <repo> <out>`;
template `a2_build/review_template/template_review.html` (the Additions Round 2 template, generalised: image pairs,
close-up, optional judging questions).
