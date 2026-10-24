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

### Renders and QA

133 cards rendered into `out_phrases_v3/` (gpt-image-2.5-sunburst, medium, 1536×1024), then QA'd with
the round-2 checks (`qa_rollout.csv` there; reads sent as 1152×768 JPEG by `~/a2_work/qa_fast.py`).
Every hard FAIL was re-rolled, at most twice: 42 after the first pass, 25 after the second; 200
renders in all. Every version is kept in `out_phrases_v3/_rerolled/<key>.r<n>.png` (r1 = first
render). Where an earlier roll scored better than the last one (fewer hard fails, then fewer warnings),
it was put back as the current picture and the last roll moved to `_rerolled/` — 7 cards, logged in
`out_phrases_v3/picks.jsonl` (for those, the last ledger row is not the current picture).

Result: **83 PASS · 31 WARN · 19 FAIL**. The 19 FAILs after two re-rolls:

| key | Lithuanian | failing check |
|---|---|---|
| A2-0357 | Prašau | neighbour |
| A2-0359 | Labai ačiū | gaze |
| A2-0375 | Prašom kalbėti lėčiau | symbol/arrow |
| A2-0894 | Geros dienos | neighbour |
| A2-0919 | Man reikia vandens | symbol/arrow |
| A2-0955 | Kur reikia persėsti? | neighbour |
| A2-0957 | Kaip nuvykti į…? | continuity |
| A2-0959 | Eikite tiesiai | continuity |
| A2-1148 | aišku | neighbour |
| A2-1149 | atsargiai | continuity |
| A2-1150 | gaila | gaze |
| A2-1165 | Su šventėmis! | neighbour |
| A2-1167 | Užeikite! | continuity |
| A2-1171 | alio | gaze |
| A2-1179 | dėmesio | continuity, symbol/arrow |
| A2-1184 | Negali būti! | continuity |
| A2-1187 | Sudie | neighbour |
| A2-1191 | šiaip sau | symbol/arrow |
| A2-1197 | susipažinti | neighbour |

Most of these are staging-level and repeat on all three rolls: the neighbour pairs (Prašau/Here you are,
Have a nice day/Goodbye, Sudie/Viso gero, Happy holidays/Merry Christmas, Where do I change/Which
platform, Get acquainted/Nice to meet you); stagings that ask for the forbidden mark itself (1179
"loudspeaker with sound lines", 0375 "slow patting motion", 0919's three-step strip draws arrows);
and staged downward looks that the gaze rule reads as "not looking at each other" (0359 deep bow,
1150, 1149, 1171). The continuity fails are mostly insets drawn as a later moment of the same scene.

### Old bubble pictures

All 167 situation keys now resolve to `out_phrases_v3` (round2 first) in `build_apkg.py`
(A1, A2 and sentence image paths). The 201 bubble pictures they replace moved to
`out_phrases/_superseded/` (53), `out_phrases_a2/_superseded/` (147) and
`out_deck_f62/_superseded/374_galvoti.png`; list in `superseded_moved.txt`. Bubble pictures with no
replacement stay where they were (A2-0899/0901/0902/0904 merged or not rendered; 0384, 1153, 1193).
The 69 PHRASE-route benchmark additions were not rendered (no staging yet).

Spend (estimate from the project's per-image rate, $0.0135 a render; edits unverified at ≈ $0.02–0.04):
200 renders ≈ $2.70, 6 edits ≈ $0.15, QA 582 calls on gpt-5.6-luna (824k in / 219k out tokens) ≈ $0.43.

## Review page

**Roll-out Review** — https://claude.ai/artifact/6AMcXu3Zmc734iCZnx85gK (db `rollout`, `rollout_meta/general`; empty at publish). Source in `page/`.
