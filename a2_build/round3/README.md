# Round 3 fixes (2026-10-19) — owner verdicts on Roll-out, Phrase Additions, Hand Fixes, Historical Test

Executor log. Pictures are not committed (see .gitignore); every superseded picture is in `<dir>/_rerolled/`.
Edit regions: `edit_regions.json` (`GO_EDIT_REGIONS=a2_build/round3/edit_regions.json`); edit calls: `edit_log.txt`;
originals put back: `restore_log.txt`; staging before this round: `old_staging_cards.json`, `old_staging_situations.json`.

## 1. Hand Fixes verdicts

**Originals restored (8)** — owner "Original is better / OK": 174_vynas, 388_sokti, 456_karstas, 472_laimingas,
A2-0473, A2-0568, A2-1411, A2-1817 (`hand_fixes/restore_before.py`; the rejected edit moved to `_rerolled/<key>.r<n>.png`).

**Redos (8).** Where the hand-scan edit had already failed, a full re-roll with a staging tweak that keeps hands out of trouble:

| key | owner note | done |
|---|---|---|
| 083_tevas | "father's hands are too huge in insert 3" | masked edit of inset 3 only (the inset-1 fix the owner kept stays): the father's hand in natural proportion |
| 271_nugara | "redo is garbled" | re-roll; note added: the hand-on-back inset replaced by a man bending to lift a crate by its handles |
| 413_tuoktis | "Both are corrupted" | re-roll; one ring hand meets one flat hand; the hand close-up inset replaced by rings in an open box |
| 459_vesus | (redo) | re-roll; note added: the man holds a mug in both hands, legs uncrossed |
| A2-0660 | "both mangled" | re-roll; no clasped hands: the child holds the handbag strap; inset 2 = shoes at the kerb line; signal shows only green |
| A2-1309 | "No hanging medal" | re-roll; nobody hangs a medal: the medal is already worn; insets medal close, medal in a case, podium |
| A2-1416 | "Both are mangled" | re-roll; the dance-hold inset replaced by two dancers with hands on their own hips |
| A2-1431 | "Not a mirror image" | re-roll; no mirror anywhere (main and hat inset) |

512_jis, A2-1433, A2-1252: marked OK by the owner, originals kept.

## 2. Anatomy fixes from the Roll-out and Phrase Additions pages

Masked edits (14, `edit_regions.json`): A2-0359, A2-0377 (round2), A2-0917 (3rd try: fingers only), A2-0925, A2-1162 (door
jamb added), A2-1167, A2-1184 (the third hand at the mouth removed, mouth open), A2-1185 (stray hand removed), S-0051 (2nd try:
toy only, no hands), A2-1934, A2-2002, A2-2022, A2-2026 (3rd try, no blur pre-fill). Failed edits were put back
(`restore_log.txt`) before the next try, so no edit was stacked on a failed one.

Re-rolls with a staging tweak (`restage_bubbles.csv`, `situations.py` regenerated; old lines in `old_staging_situations.json`):
- A2-0888: the edit could not add the young woman's glass; re-rolled twice, now four people, four glasses.
- A2-0894: two edits erased the hand into a grey box; re-roll: the customer holds the loaf against his chest, string bag on his arm.
- A2-0895 (round2): the edit had already failed in the roll-out; re-roll: no clasped hands, the boy waves a paper tricolour.
- A2-2010: owner's fixed staging: the driver sits in the FRONT LEFT seat behind the wheel and reaches back to the open rear door.
Skipped as instructed: A2-1187 and A2-1991 (merges).

QA (`qa_items12.csv`, `qa_images.py --limbs`, 33 cards): 19 PASS, 7 WARN, 7 FAIL. **No LIMBS, PROPS or HANDS finding.**
The 7 FAILs are the known staging-level reads, not anatomy: GAZE on 0359 (deep bow) and 1934 (man doubled over), NEIGHBOUR
on 2022 ("My name is…") and 0894 ("Goodbye", restage proposed in rollout_round2), CONTINUITY on insets that show the scene
from further off (0894, 0895, 1184, 1416).
