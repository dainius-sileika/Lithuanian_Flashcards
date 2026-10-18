# Roll-out (2026-10-18) — owner passed pilot round 2

## Step 1: the six redraws (owner verdicts, 2026-10-18)

All six were masked edits with `a2_build/additions_round2/edit_inset.py` (extended: a region entry
may now name its folder, carry its own staging text, and use the conversation lead). Only the
masked area changes; the previous PNG is in `<folder>/_rerolled/<key>.r<n>.png`, the raw edit
beside it. Regions and clauses: `edit_regions.json`.

| key | owner note | what was repainted | QA (`qa_redraws.csv`) |
|---|---|---|---|
| A2-0352 Labas vakaras | "Man in the doorway has feet inside the door frame" | the host's legs and shoes, the threshold | WARN: neighbour "Nice to meet you" (slight), handshake (staged) — as before |
| A2-0377 Kiek kainuoja? | "Purse panels have an extra finger" | the purse hand in the main picture + the purse inset | PASS |
| A2-0895 Geros kelionės | "Hand holding child's hand is weird" | the mother's and boy's clasped hands | FAIL: neighbour "Goodbye" (clear) — the same staging-level read as all three round-2 rolls; the hands themselves pass the limb check. Not re-rolled: a re-roll cannot change the neighbour read |
| A2-1894 | "Woman's hand in main panel is strange" | both of the woman's hands (on the door, on the bags) | PASS |
| A2-1911 | "Gerbil cage shows AI anomalies" | the cage, wheel and house (all inside the cage now), the hamster, the girl's fingers | PASS |
| A2-1915 | "two kings … one must be a queen, on the left, and then a king, on the right" | the painting on the wall + the upper inset: a Čiurlionis-style fairy tale, a queen (left, blue) and a king (right, red) over the glowing globe; `a2_staging.json` line updated | PASS |

Cost: 6 edits.
