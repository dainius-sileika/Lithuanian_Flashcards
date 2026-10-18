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

## Step 2: the ten unverified usage notes — owner: "Approve all as written"

The ten rows in `a2_build/context_notes.csv` marked `unverified` now carry `owner-approved`
(their source notes keep what was and was not read, plus the approval). `build_apkg.py`
`USAGE_CONFIDENCE` accepts `owner-approved`, so all 80 notes go on the backs. The leading repeat of
the English gloss was dropped as in 5ec1a76 (e.g. "Of course — the neutral agreement word" →
"The neutral agreement word"); literal meanings and alternative glosses stay.
`a2_build/context_notes_unverified.csv` is retired (its rows live in context_notes.csv).

## Step 3: roll-out of the restaged bubble cards

Data before rendering (`restage_bubbles.csv`, `situations.py` regenerated):
- `gaze` = `default` on 27 rows where nobody speaks to anyone (signs, clocks, lone figures, the
  three-panel water card, the clothing floors, the loudspeaker): they keep the house gaze, as the
  round-2 rule says for non-speaking cards. The other 106 take the conversation gaze by default.
- Handedness (RULES §c3): only the three handshakes are named (both RIGHT hands: 0891, 0363, 1197).
  Pointing and the rest are left as staged.
- Prompts are built exactly as for pilot round 2 (`gen.py` → `build_situation_call`): a card whose
  staging lists no insets gets no inset sentence and no PANEL_CONTINUITY sentence, and the model
  still draws the house insets (as on 0352/0377, which passed). The QA coherence check runs on all.
