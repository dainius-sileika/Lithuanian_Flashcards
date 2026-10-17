# Pilot round 2 — what this folder is (for the owner)

**Diagnosis.** Of the 12 two-panel cards, 6 did not pass: 5 on gaze or continuity (0360, 0897, 0898, 0900, 0928), 1 on staging (0882). That trips the stop rule, and the cause is in the prompt, not the renders: every pilot prompt asks three times for a face turned toward the viewer (the house-style lead, GAZE_PAIR_RULE, and the suffix, which is the last thing the model reads). The two-panel grammar fixed people, dress and scale but never position, background or props. Nothing in the prompt says a hand belongs to one body or that a carried case must be in someone's grip. Full attribution per card: `DIAGNOSIS.md`.

**Four rule changes** (`RULES.md`, paste-ready, nothing applied yet):
- CONVERSATION_GAZE: on any card where someone speaks, the speakers look at each other and nobody looks at the viewer; the three house gaze sentences are swapped for it. Non-speaking situation cards keep the house gaze.
- PANEL_CONTINUITY: same place, same viewpoint, same positions, same fixtures, props held by the same person in both panels; only gesture and expression change.
- ANATOMY/PROPS: every arm on its own body, the named hand does the action, carried objects visibly gripped, nobody merged into furniture.
- QA: `qa_images.py` asks the four matching questions (speakers' gaze, panel continuity, limb ownership, held props) and fails a card on any of them.

**14 redraws** (`redraw_list.csv`, `restage_round2.csv`): 0113 as you designed it (rain, chalkboard, diagram); 0881 a boy with a football and a broken pane; 0882 the paints and easel; 0362 the bump on the trolleybus; 0352 with the extended hand; and fixes for 0114, 0360, 0377, 0383, 0895, 0897, 0898, 0900, 0928. Hands are named wherever the gesture depends on them.

**Context notes** (`context_notes.csv`, `CONTEXT_NOTES.md`): 32 one-line notes for the greeting, thanks, please and apology sets, each with a source URL; 28 verified against a read source, 3 medium, 1 unverified. vlkk.lt blocked this session; the main source is the "Kalbos etiketas" chapter of the *Kompiuterinis lietuvių kalbos žinynas* (2004). They go on the back under the gloss in a new `usage` field — a schema change, but one that rides on the delete-and-reimport you have already accepted. Two notes correct a deck gloss (dėkui; iki pasimatymo).

**The remaining ~133 bubble cards.** My view agrees with the proposal: render only these 14 under the new rules, run QA, and roll out after you pass them. Reason: the gaze rule changes the first and last sentence of every conversation prompt, and the QA gate gains four hard fails whose false-positive rate is unknown; 14 cards (≈ $0.40 with re-rolls) measure both before 133 cards (≈ $2.50) depend on them. One addition: the executor should run the new QA on the untouched round-1 folder first, so you see what it would have caught and what it flags wrongly, at no render cost.
