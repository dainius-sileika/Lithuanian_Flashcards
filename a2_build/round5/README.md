# Round 5 fixes (2026-10-19) — executor log

Source: the owner's verdicts on **Round 4 Fixes**. Working rule from this round on (owner: "this patching of images isn't
working"): **fix by whole re-roll, not masked edits, unless the owner asks for an edit.** No masked edit was made.
Pictures are not committed (`.gitignore`); every replaced picture is in `<dir>/_rerolled/`.
Data: `a2_build/src/apply_round5.py` (idempotent; log `data_applied.csv`, replaced values `old_staging.json`).
Prompt check: all 1,465 production prompts rebuilt before and after — exactly the 8 intended keys change
(A1 083, 413; A2 0085, 0660; situations 0359, 0925, 1167, 2002).

| card | done | file history |
|---|---|---|
| 083_tevas | re-roll; inset 3 staged as the whole family on a bench before the house (no hand close-up) | round-4 composite -> `_rerolled/083_tevas.r9.png` |
| 413_tuoktis | the FIRST round-3 staging (ledger row 3: groom slides the ring on, her hand flat and still) put back; three whole re-rolls; **try 1 picked** (cleanest hands; insets ring box / signing / grain as staged). Try 3 drew a hand close-up inset again. `pick_413.py` | round-4 = r5, tries = r6 (picked, copied back), r7, r8 |
| A2-0085 | Kaunas station rows reinstated (`settings_assignments.csv` row back, `settings_rows.csv` REVERTED mark lifted); round-3 note with the clerk's hands on her own counter, ticket and change out through the slot; re-roll | restored r1 -> `_rerolled/A2-0085.r3.png` |
| A2-0359 | re-roll with the round-4 main scene described as rendered + new insets (the man earlier as a patient in bed; leaving through the front doors). The main scene came out close to round 4 (same layout); both are on the page | r5 |
| A2-0660 | **restore** of the round-3 picture (`_rerolled/A2-0660.r5.png`, written 2026-10-18 23:59, the one the owner judged "faces and hands are good" on Round 3 Fixes and saw as the left picture on Round 4 Fixes); note back to its round-3 text. `restore_r5.py` | round-4 re-roll -> r6 |
| A2-0925 | re-roll with the planner's fallback staging (both arms in the sleeves, buttoning with the right hand; cap in the left hand instead of "hidden inside the lapel"). Try 1 failed QA GAZE (both looked at the clock); try 2 has them look at each other | r3, r4 |
| A2-1167 | round-4 main staging + the first version's insets (hanging her coat; tea at the table). Try 1 failed QA CONTINUITY (coat vs jumper); try 2 names the red jumper under the coat | r5, r6 |
| A2-1431 | whole re-roll, same staging (inset 1 = a foot sliding into a shoe; no shoehorn) | r4 |
| A2-2002 | re-roll; right hand palm turned out, index finger up at the plate, left hand on the gate; "7" reads back | r3 |
| A2-2010 | re-roll, same staging (driver front-left, right hand palm up) | r3 |

## QA
`qa_round5.csv` (`qa_images.py --limbs`, 10 cards): **0 FAIL**, 3 WARN (413 guessed "wedding", 1431 "tailor", 0925 stray
acts: pointing finger, hand on chest), 7 PASS. Before the second tries: 2 FAIL (0925 GAZE, 1167 CONTINUITY), each fixed by one
extra re-roll. `qa_round5_extra.csv` (`qa_r5_extra.py`, unchanged LIMBS_PROMPT + specific asks): limbs/props/hands ok on all
five situation cards and on all three 413 tries; 083 inset 3 = family, no hand close-up; 0085 hands on her side, not through
the glass; 1431 no shoehorn, hand ok, nothing outside the frame; 2002 palm out, natural, left ok; 2010 right hand, seats whole;
0359 insets = patient in bed / leaving the hospital; 1167 door normal, host clear.

Spend (project rates): 13 renders ≈ $0.18; ≈ 30 QA calls ≈ $0.10–0.25.
