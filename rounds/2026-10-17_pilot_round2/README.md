# Pilot round 2 — what this folder is (for the owner)

**Diagnosis.** Of the 12 two-panel cards, 6 did not pass: 5 on gaze or continuity (0360, 0897, 0898, 0900, 0928), 1 on staging (0882). That trips the stop rule, and the cause is in the prompt, not the renders: every pilot prompt asks three times for a face turned toward the viewer (the house-style lead, GAZE_PAIR_RULE, and the suffix — the last thing the model reads). The two-panel grammar fixed people, dress and scale but never position, background or props. Nothing in the prompt says a hand belongs to one body or that a carried case must be in someone's grip. Per-card attribution: `DIAGNOSIS.md`.

**Four rule changes** (`RULES.md`, paste-ready; nothing applied yet):
- CONVERSATION_GAZE: where someone speaks, the speakers look at each other and nobody looks at the viewer; the three house gaze sentences are swapped for it. Non-speaking cards keep the house gaze.
- PANEL_CONTINUITY — a standing rule for the whole deck, as you asked: every card with panels, a strip or insets gets it; it binds wherever a scene is repeated and leaves insets that show a different detail free. Insets stay.
- ANATOMY/PROPS: every arm on its own body, the named hand does the action, carried objects visibly gripped, nobody merged into furniture.
- QA: `qa_images.py` asks the matching questions — speakers' gaze, panel/inset coherence (every card), limb ownership, held props — and fails a card on any of them.

**14 redraws** (`redraw_list.csv`, `restage_round2.csv`): 0113 as you designed it; 0881 a boy, a football, a broken pane; 0882 the paints and easel; 0362 the bump on the trolleybus; 0352 with the extended hand; fixes for 0114, 0360, 0377, 0383, 0895, 0897, 0898, 0900, 0928. Hands are named wherever the gesture depends on them.

**Context notes — now, as you chose** (`context_notes.csv`, `CONTEXT_NOTES.md`): 80 one-line notes covering every phrase whose meaning hinges on register or a near-synonym, 28 with a tu/jūs variant; 54 verified against a read source, 16 medium, 10 flagged unverified for you to confirm or cut. vlkk.lt blocked this session; the main source is the "Kalbos etiketas" chapter of the *Kompiuterinis lietuvių kalbos žinynas* (2004). They go on the back under the gloss in a new `usage` field. One finding needs your decision: the reference calls *Pakartokite, prašau* and three other imperative-plus-prašau cards a calque.

**The remaining ~133 bubble cards.** Render only these 14 under the new rules, run QA, roll out after you pass them. The gaze rule rewrites the first and last sentence of every conversation prompt and the continuity rule now touches every card; 14 renders (≈ $0.40) measure both before 133 (≈ $2.50) depend on them. First, run the new QA on the untouched round-1 folder — no render cost — to see what it catches and what it flags wrongly.
