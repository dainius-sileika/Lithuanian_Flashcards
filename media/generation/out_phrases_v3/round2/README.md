# out_phrases_v3/round2 — pilot round 2 renders (2026-10-17/18)

The 14 redraws of `a2_build/pilot_round2/redraw_list.csv`, drawn under the round-2 rules
(conversation gaze, panel continuity, anatomy/props; commit f6548b8) from the restaged rows
(commit 5fd5f2f) by `V3_OUT=out_phrases_v3/round2 ONLY=... python out_phrases_v3/gen.py`
(gpt-image-2.5-sunburst, medium, 1536x1024). Round 1 in `out_phrases_v3/` is untouched.
The other ~133 restaged bubble cards are NOT rendered: they wait for the owner's round-2 verdict.

Renders paid: 22 = 14 first passes + 8 re-rolls (hard QA FAIL only, at most two per card;
every earlier version is in `_rerolled/<key>.r<n>.png`; last ledger row per key = current).

## QA (`qa_round2.csv`, qa_images.py with the round-2 checks, gpt-5.6-luna)

| key | rolls | status | finding |
|---|---|---|---|
| A2-0113 kodėl | 2 | WARN | r1 FAILed CONTINUITY (the board inset is a different moment, as staged) + neighbour "how"; r2: neighbour "what kind of" (slight) |
| A2-0114 kiek | 3 | FAIL | neighbour test reads "how much does it cost (phrase)" on all three rolls (as in round 1); r1 also GAZE (seller looks at the scale) |
| A2-0352 Labas vakaras | 1 | WARN | neighbour "Nice to meet you" (slight); stray act: handshake (now staged) |
| A2-0360 Nėra už ką | 1 | WARN | stray act: hand on chest (staged) |
| A2-0362 Atleiskite | 2 | WARN | r1 FAIL neighbour "Excuse me, please…" (clear); r2 slight |
| A2-0377 Kiek kainuoja? | 1 | PASS | |
| A2-0383 Ar galite man padėti? | 1 | WARN | neighbour "Could you help me, please?" (slight) |
| A2-0881 Atsiprašau | 3 | FAIL | GAZE on all three: the staging bows the boy's head, so the speakers never meet eyes |
| A2-0882 Nieko tokio | 1 | WARN | stray act: boy's raised palms (staged) |
| A2-0895 Geros kelionės | 3 | FAIL | neighbour test reads "Goodbye" (clear) on all three rolls |
| A2-0897 Kas tas žmogus? | 1 | WARN | stray act: thumb over the shoulder |
| A2-0898 Kur yra tualetas? | 1 | WARN | stray act: pointing finger (staged) |
| A2-0900 Nekalbu lietuviškai | 1 | PASS | |
| A2-0928 Kiek kainuoja bilietas? | 1 | PASS | |

No bubble, lettering, limb, prop or two-panel continuity failure on any current picture.
The three remaining FAILs are staging-level (two neighbour pairs, one staging that
contradicts the gaze rule), not render faults; they go to the owner as they are.

QA images are sent as 1152x768 JPEG (q85) by `~/a2_work/qa_fast.py` (the VM's upload link
ran at ~5 KB/s); the reads, prompts, judging and cache keys are qa_images.py's own.
