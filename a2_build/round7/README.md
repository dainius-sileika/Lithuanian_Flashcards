# Round 7 fixes (2026-10-20): executor log

Source: the owner on **Round 6 Fixes**, A2-0359 *Labai ačiū*: "Can't be flowers in the first insert, because the flowers
come after his release; redo". The round-6 picture had a vase with a bouquet on the bedside table in inset 1 (the man as a
patient some days earlier); the round-6 inset-1 text named no objects, so the engine carried the main scene's flowers in.

| card | done | file history |
|---|---|---|
| A2-0359 | Whole re-roll (spec 3.1.0 working rule). Main scene and inset 2 unchanged word for word; inset 1 restaged (`a2_build/src/apply_round7.py`, the only text change, logged in `data_applied.csv`): "...sitting up in a hospital bed **with plain white sheets**, the same nurse **in her white coat and cap** standing beside the bed **with the dark clipboard in both hands, a small bare bedside table holding only a glass of water and a folded white towel, plain pale green walls (this moment is before his discharge: the flowers appear only in the main scene)**". **Try 1 passed every check and is the card.** | round 6 -> `out_phrases_v3/_rerolled/A2-0359.r8.png`; try 1 = `out_phrases_v3/A2-0359.png` |

Render: `a2_build/round7/gen_0359.py` (GOGenerator.generate on `gen_phrases.build_situation_call`, the production path,
medium quality, 1536x1024; old picture moved to `_rerolled/` first; `PHRASES_OUT` points at the Proton Drive
`out_phrases_v3`, since images are not in git). That call writes no ledger row, so `ledger_r7.py` appended the prompt
(spec 3.3.0, style ae72a30c53bd) to `out_phrases_v3/ledger.csv`. Prompt check: `situations.py` changes for A2-0359 only
(inset-1 text and the `render` marker); DIRECTION_RULE does not route on for this staging (it names RIGHT in capitals), as in round 6.

Note: a first launch of `gen_0359.py` in the background was stopped by the VM shell before it wrote a file (it had already
moved the round-6 picture to `.r8`); the render was then run in the foreground. Whether that stopped launch reached the API
is unknown; it produced no image and has no ledger row.

## QA
- `qa_round7.csv` (`qa_images.py --limbs`): try 1 **PASS**, no fails or warnings, blind guess "hospital", fit yes.
- `qa_round7_extra.csv` (`qa_r7_extra.py`): unchanged LIMBS_PROMPT (ok) and three BLIND questions that never say what any
  panel should show:
  - `panels_blind`: every object in the main scene and in EACH inset, with a flower flag asked of all panels alike.
    Try 1 upper-right inset (bed): bed, pillow, blanket, sheet, striped pyjamas, nurse, cap, black clipboard, bedside
    table, drinking glass, glass of water, "closed book or notepad" (the folded towel); **flowers false**. Flowers only
    in the main scene. Round 6 control: "vase", "bouquet" on the bedside table, **flowers true** (the check sees the defect).
  - `main_blind`: a bouquet passed from the man in the brown coat to the nurse, giver_hands **both**.
  - `inset2_blind` (round 6's blind question, located by content): lower-right, down the steps, faces the viewer, doors
    behind him, reads as **leaving**, not looking at the viewer.
- By eye: inset 1 has no flowers, petals or patterned fabric. In the main scene one of his hands is clearly seen at the
  stems and the nurse's hand meets it; his second hand is under the paper wrap (the staging asks for the wrap covering his
  fingers). The blind check reads both hands; Round 6's main scene, which the owner did not flag, is the same.

Spend (project rates): 1 render ≈ $0.015 (+ the stopped launch, at most another ≈ $0.015); about 10 QA calls ≈ $0.05.

## Review page
**Round 7 Fixes**: https://claude.ai/artifact/Jd2n1Nmk3p7Zr8K9bEyiqQ (private; capabilities db + user; db `round7`, notes
`round7_meta/general`; empty after publish). Rebuild: `PHRASES_OUT=<project>/out_phrases_v3 python3 a2_build/round7/build_page.py`
(media in `page/media/`, not committed). The new picture spans the page width with the Round 6 picture below it and a
close-up of inset 1 (Round 6 | new).

## Sync note
As in round 6, the commits were made from a clone outside the synced tree (`~/work/repo` in the Mac VM) and pushed from
there; the Proton Drive folder was then reset to origin/main. The .apkg was not rebuilt.
