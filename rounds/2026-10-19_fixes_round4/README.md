# Round 4 fixes (2026-10-19) — executor log

Plan: `plan.csv` + `answers.md` (planner, commit 7e2da4b). Pictures are not committed (`.gitignore`); every replaced
picture is in `<dir>/_rerolled/`. Data changes: `a2_build/src/apply_round4.py` (idempotent; log `data_applied.csv`,
replaced values `old_staging.json`). Prompt check: all 1,465 production prompts rebuilt before and after — exactly the
22 intended keys change (5 restores whose staging/setting reverted, 6 re-rolls/edits with new A1/A2 staging, 11 restage rows).

## Restores (5) — `restore_r4.py`, `restore_log.txt`
097 (r4 back; the Adamkus/Vytis render -> r5), 106 (r2), 107 (r1), A2-1326 (r1), A2-0085 (r1). Staging notes back to their
pre-roll-out text; `settings_assignments.csv` 106 -> vilnius_vingis, 107 -> place-less, A2-1326 and A2-0085 rows removed
(no row before 52fabca); `settings_rows.csv` rows marked REVERTED; 097 out of `likeness_args.json` `active`.
`deck_builder.FLAG_OVERRIDE {97: "emblem"}` untouched: the emblem allowance is dormant (no shipped card shows a Vytis).
A2-0085 restored on the planner's recommendation (owner: "if it's for the location, then fine").

## Re-rolls (11)
f62: 055 (grille below face height), 413 (bouquet, rings on a cushion); a2: A2-0660 (heading right); v3 restage rows
(appended, `situations.py` regenerated): 0359 (flowers), 1162 (frame behind him), 1167 (normal door, host inside), 1172
(Sartai races, flat chop), 1184, 1185 (broken plate), 2010 (thumb side), 2022 (hands off the table).
Each passed on the first roll. 413's third inset came out as a hand close-up (the staging asked for a wedding car): one
masked edit replaced it with the car.

**A2-2010, deviation from the plan:** the planner's sentence put the driver's thumb "on the kerb side (nearest the
viewer)". A right hand turned palm-up and reaching back to the rear right door has its thumb toward the back of the car,
on the side away from the kerb (thumb = fingers × palm-normal). The row says that instead; QA reads the hand as a right hand.

## Masked edits (10) — `edit_regions.json`, `edit_log.txt`, `edit_inset.py`
083 (owner option 2: the joined hands cropped from the main picture into inset 3, then one seam-ring edit), 0925 (hand in
the cuff), 1431 (foot into shoe, no hand), 2002 (right hand palm out; left hand fenced off), 2026 (banknotes through the
round opening), 2029, S-0051 (boy blowing out five candles), 1191 (VELNIO NUOTAKA poster, also in the small inset),
1360 (MILŽINO PAUNKSMĖ playbill), 0649 (post box inset; no exterior).
`edit_inset.py` gained three small options: a `ring` region (a border band), `exact_text` (the card's declared lettering
replaces the no-text sentence in the edit prompt) and `prefill: file:<path>`; edit ledger rows now carry the spec stamp.
Large whole-inset masks with the blur pre-fill came back empty (flat) — 2026, 2029, S-0051, 0649 were redone without it.

**A2-2029, deviation:** the side-window view the plan asked for failed QA twice (NEIGHBOUR: reads as "On the right",
clear margin; round 3 passed). The round-3 inset (the taxi at the kerb) was put back and only the arm out of the front
window was removed: no hand from the front window, and the arrival cue stays.
**S-0051:** the first two edits drew four candles; the third has five (visual count). The QA model's own counts were
inconsistent (5/4, then 6/7) and are not relied on.

## QA
`qa_round4.csv` (`qa_images.py --limbs`, 26 cards): **0 FAIL**, 12 WARN, 14 PASS; no LIMBS/PROPS/HANDS finding.
Declared lettering read back exactly: VELNIO NUOTAKA, MILŽINO PAUNKSMĖ, 7. WARNs are guess wording (holding hands, sports,
scarf, wedding, theater, tailor, mail delivery, independence), stray acts (a wave, pointing, blowing out candles) and
pseudo-marks on the taxi's chequer band (2029, unchanged area).
`qa_round4_extra.csv` (`qa_r4_extra.py`): the unchanged LIMBS_PROMPT on all 14 situation cards — all limbs/props/hands ok;
2010 right hand; 0660 left-to-right; 055 face clear, bars ok; 413 no hand close-up; 2002 palm out, natural; 1162 frame behind;
1167 door normal, host clear; 2029 no hand out of a window.

## Spec 3.0.1 (tag `spec-v3.0.1`)
`go_grammars.py` joined the style lock (six new items, no prompt changed); spec §2 describes the emblem allowance as
dormant and adds the poster/sign rule; §3 drops 097 from the likeness list. The direction-of-movement rule was not added
(owner's decision, `answers.md` §4).

## Review page and spend
**Round 4 Fixes** — https://claude.ai/artifact/MKfmPoGgWjMLmBMzEqpfnQ (private; db `round4`, notes `round4_meta/general`;
both empty after publish). 26 cards + the planner's four answers. Rebuild: `python3 a2_build/round4/build_page.py`
(media in `page/media/`, not committed).

Spend (project rates; the edit price is unverified): 11 renders ≈ $0.15; 24 edit calls (15 kept, 9 returned empty
fills) ≈ $0.50–1.00; ≈ 80 QA calls ≈ $0.30–0.60. Total ≈ $1.0–1.8.
