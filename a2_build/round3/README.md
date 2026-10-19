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

Masked edits (13, `edit_regions.json`): A2-0359, A2-0377 (round2), A2-0917 (3rd try: fingers only), A2-0925, A2-1162 (door
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

## 3. Historical A5 roll-out (test passed)

Owner verdicts on the Historical Test: 012 Lituanica (with faces), 097 Adamkus + Vytis, A2-1297 Sports Hall and A2-1769
Freedom Statue passed — the test renders were copied into production (`historical_copyin.txt`; the shipped pictures are in
`_rerolled/`, ledger rows "HISTTEST"). 123_autorius: "Keep original" — the shipped picture stays, its pre-test note is back in
`card_notes.json` and 123 is no longer `active` in `likeness_args.json`. 035 teismas: "use the flag" — re-rolled with a large
tricolour behind the bench and no other emblem.

**Emblem routing:** `deck_builder.FLAG_OVERRIDE` now carries `emblem` for 97 only (35 removed); every other card keeps the
flag-only `FLAG_RULE`. `FLAG_RULE_EMBLEM` stays registered, not promoted.

**Rendered (25):** A1 — 035, 048 (1939 Kaunas Clinics), 055 (Bank of Lithuania hall), 106/107 (State Stadium), 138 (the 1939
basketball team; precedent + Lubinas as the tall centre), and the owner's "All three" likenesses 113 (Basanavičius), 122
(Čiurlionis, with a Karalių pasaka-like canvas) and A2-0782 (Gustaitis, ANBO-type drawing). A2 places — every A2 row of
`settings_rows.csv` except the three B1 cards (A2-0654, A2-1347, A2-1370): 0085, 0645, 0649, 0652, 0653, 0656, 0658, 0812,
1260, 1282, 1293, 1360, 1747 and the optional 0667, 1326, 1357 (staging written from the planner's partial lines;
settings rows added for 138, 0667, 1326, 1357). A2-0792 writer: "leave the old card" — untouched. Not in this roll-out:
112, 029 (optional, not chosen) and A2-1917 (pilot likeness card; separate).

Staging written from `historical/implementation/staging_rows.csv` (old values in `old_staging_historical.json`). Prompt
check: all 1,178 A1/A2 production prompts rebuilt before and after — exactly the 26 intended keys change (25 renders + 123
back to its shipped note).

Face words for 113, 122, A2-0782 and 138 come from the planner's `likeness_cards.csv`; the executor could not view the
portraits this round, so they stay marked UNVERIFIED in `likeness_args.json`.

QA (`qa_historical.csv`, `--limbs`, 29 cards incl. the 4 copied-in test renders): **0 FAIL**, 11 WARN (guess wording:
"airplane" for plane/engineer, "courtroom", "Lithuania" for 097), 18 PASS; no LIMBS/PROPS/HANDS finding. Lettering read back
on 0653, 0658, 1260, 1282, 1297 is the card_text each declares.

Ledger note: `out_deck_f62/gen.py` keeps its own local ledger (`~/f62_work`) while `edit_inset.py` uses `~/a2_work/f62_*`;
the two had drifted (each copy-back dropped the other's rows). They were merged (superset, nothing deleted) and both local
copies now match the folder.
