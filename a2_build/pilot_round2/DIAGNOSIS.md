# Pilot round 1 — diagnosis (Fable, 2026-10-17)

Source: the owner's per-card verdicts on the 34-card bubble-free pilot (`out_phrases_v3/`), read against the prompts in `out_phrases_v3/ledger.csv`, `go_generator.py`, `go_grammars.py`, `gen_phrases.py` and `qa_images.py`.

## Tally

| set | cards | clean | not clean |
|---|---|---|---|
| two-panel (situation_2) | 12 | 6 (0896, 0903, 0905, 0906, 0907, 0909) | 6 (0360, 0882, 0897, 0898, 0900, 0928) |
| single scene, phrases | 12 | 7 (0348, 0349, 0350, 0351, 0358, 0887; 0352 passed with a request) | 5 (0362, 0377, 0383, 0881, 0895) |
| question words + galvoti | 10 | 8 | 2 (0113, 0114) |

Of the six two-panel misses, **five** are gaze or continuity (0360, 0897, 0898, 0900, 0928) and **one** is staging (0882: the scuffed book does not read). The task brief said "six failed on gaze or continuity"; the count is five plus one. Either way the stop rule in `PILOT_24.md` ("three or more failures in one set means the set's staging rule is wrong, not the render") is met for the two-panel set, so the fix is a rule change, not re-rolls.

## What the prompt actually says (why the rule is at fault)

Every pilot prompt carries **three** sentences asking for a face toward the viewer:

1. `CONCEPT_LEAD` (first thing read): "…of two main figures only one faces the viewer; a lone figure stands near-frontal…"
2. `GAZE_PAIR_RULE` (mid-prompt): "Of two main figures, one faces the viewer with eyes resting just past the viewer's shoulder and the other looks at the task, at the first figure, or into the scene."
3. `STYLE_SUFFIX` (the last thing read): "One or two faces toward the viewer, eyes just past the shoulder; of two main figures only one."

For a conversation card this is an instruction to draw exactly the defect the owner saw in 0360, 0377, 0897, 0900 and 0928. The model obeyed the prompt. No staging line can override a rule stated three times, last of all at the end of the prompt. (The owner's review of the review-desk pilot phrased the general note the same way: "all the conversation cards need the actors looking at each other when they speak, unlike the other, single-panel cards.")

The two-panel grammar (`go_grammars.py` → `situation_2`) asks for "THE SAME TWO PEOPLE … identically dressed and at the same scale" and says nothing about **relative position**, **background and fixtures**, or **props**. 0897 (the blue man moved behind the brown one) and 0898 (the toilet door exists only in the right panel) are exactly the two gaps.

`ANATOMY_RULE` speaks only of finger count. Nothing in the prompt says a hand must belong to the right body (0895), that a carried object must be visibly in the carrier's hand (0383), or that a figure may not merge with furniture (0900 "in" the counter; `PLAUSIBILITY_RULE` covers furniture, not people).

0383's "second panel / last panel" is the same continuity failure in another guise: the single scene grew insets (as most single scenes do — `out_phrases_v3/README.md` noted it), and the insets repeated the main scene with the suitcase in different hands. The owner keeps insets ("our concurrent goal is beauty/aesthetic interest, and the panels add to this criterion") and makes coherency a standing rule for every multi-panel card: "all panel cards needs a coherency check to make sure the mise-en-scene between panels remains consistent." So the fix for 0383 is not fewer insets but PANEL_CONTINUITY applied to insets that repeat the scene, plus a staging line that says what each inset shows.

## Attribution per card

| key | failure in the owner's words (short) | cause | fix |
|---|---|---|---|
| A2-0360 | he shouldn't be looking at us | **rule** (gaze ×3) | CONVERSATION_GAZE |
| A2-0377 | woman looking at us, not at the seller | **rule** (gaze) | CONVERSATION_GAZE |
| A2-0928 | actors must look at each other | **rule** (gaze) | CONVERSATION_GAZE |
| A2-0897 | man in blue suddenly behind; should look at the brown man | **rule** (continuity + gaze) | PANEL_CONTINUITY + CONVERSATION_GAZE |
| A2-0898 | no bathroom in panel 1, there is in panel 2 | **rule** (continuity) | PANEL_CONTINUITY; staging names the door in both panels |
| A2-0900 | man "in" the counter; must look at the woman | **rule** (figure/furniture + gaze) | ANATOMY_PROPS + CONVERSATION_GAZE |
| A2-0895 | mother's waving hand has the brother's arm | **rule** (limb ownership) | ANATOMY_PROPS; staging assigns each arm |
| A2-0383 | hands not carrying the suitcase; man not carrying it in the last panel | **rule** (held props; insets repeating the scene incoherently) | ANATOMY_PROPS; PANEL_CONTINUITY on insets; staging names the insets |
| A2-0114 | hand should be her right | **staging** (silent on handedness) + rule (c) | staging names the hand; ANATOMY_PROPS honours it |
| A2-0882 | book isn't clear; use a dented car or paints and easel | **staging** | new scene (paints and easel) |
| A2-0881 | better a child that's done something wrong | **staging** | new scene (boy, football, broken pane) |
| A2-0362 | should look like he just bumped into the woman | **staging** | new scene (bump on the trolleybus) |
| A2-0113 | main panel + two insets, owner's design | **staging** | new scene as designed |
| A2-0352 | an extended hand would make it clearer (accepted) | **staging** (addition) | hand added |

Rule-caused: 8 cards (0360, 0377, 0928, 0897, 0898, 0900, 0895, 0383). Staging-caused: 6 cards (0114, 0882, 0881, 0362, 0113, 0352). Every staging-caused card is also redrawn under the new rules, so round 2 tests both at once.

## What is not a problem

- No bubble, no floating symbol, no lettering leak in any of the 34 (QA and owner agree). The bubble-free grammar itself holds.
- Greetings as pictures: all five passed. The owner's remaining concern (they "could pass for their neighbour") is answered on the back, not in the picture — see `context_notes.csv`.
- 0115 koks: accepted "with text to help" — no redraw.
