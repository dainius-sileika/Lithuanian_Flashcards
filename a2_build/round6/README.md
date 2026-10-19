# Round 6 fixes (2026-10-19): executor log

Source: the owner on **Round 5 Fixes**, A2-0359 *Labai ačiū*: "Final panel should be a man leaving the hospital, not entering it".
The round-5 inset said "walking out through the hospital's front doors onto the steps, seen from behind". The engine drew a man
seen from behind going UP the steps to the doors, which reads as arriving. Round 5's extra QA asked a leading question ("is the
second the man leaving?") and passed it.

| card | done | file history |
|---|---|---|
| A2-0359 | Whole re-roll (spec 3.1.0 working rule). Main scene and inset 1 unchanged; inset 2 restaged (`a2_build/src/apply_round6.py`): the same man, coat, scarf, a brown bag in his RIGHT hand, coming DOWN the steps TOWARD the viewer, the glass doors BEHIND him. Try 1 failed QA GAZE (he looked straight out at the viewer); try 2 lowers his eyes to the steps. **Try 2 is the card.** | round 5 -> `out_phrases_v3/_rerolled/A2-0359.r6.png`; try 1 -> `.r7.png`; try 2 = `out_phrases_v3/A2-0359.png` |

Render: `a2_build/round6/gen_0359.py` (GOGenerator.generate on `gen_phrases.build_situation_call`, the production path; old
picture moved to `_rerolled/` first). That call writes no ledger row, so `ledger_r6.py` appended both prompts (spec 3.1.0,
style ae72a30c53bd) to `out_phrases_v3/ledger.csv`. Prompt check: `situations.py` changes for A2-0359 only.

## QA
- `qa_round6_try1.csv`: try 1 **FAIL** (GAZE: the man in the lower inset looks toward the viewer).
- `qa_round6.csv` (`qa_images.py --limbs`): try 2 **PASS**, blind guess "visit a patient in the hospital".
- `qa_round6_extra.csv` (`qa_r6_extra.py`): unchanged LIMBS_PROMPT (ok) and a BLIND question about the lower inset only:
  - try 2: moving away from the building, down the steps, faces the viewer, doors behind him, reads as **leaving**, not looking at the viewer;
  - round 5 (control): up the steps, doors in front of him, reads as **entering**.

Spend (project rates): 2 renders ≈ $0.03; 6 QA calls ≈ $0.03.

## Review page
**Round 6 Fixes**: https://claude.ai/artifact/VDVfrUATNXedrbHPVa6aFw (private; capabilities db + user; db `round6`, notes
`round6_meta/general`; empty after publish). Rebuild: `python3 a2_build/round6/build_page.py` (media in `page/media/`, not committed).

## Sync note
The Proton Drive folder rolled back three edited text files (`apply_round6.py`, `situations.py`, `restage_bubbles.csv`) to an
earlier save without leaving a conflict copy, and it also rewrote `.git/refs/heads/main` from old copies (conflict copies
moved to `.git/_sync_conflicts/`). The commits of this session were therefore made from a clone outside the synced tree
and pushed from there.
