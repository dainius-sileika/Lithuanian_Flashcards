# Staging for the 69 PHRASE-route benchmark additions (A2-1863…2045)

Plan only (2026-10-18). Source rows: `a2_build/a2_wordlist.csv`, route PHRASE, category Functions (the 69 of the 183 benchmark additions that take a picture; the rest are cloze or the 14 IMG cards already rendered). None of these has a staging line yet, which is why the roll-out left them unrendered.

`staging.csv` is in `restage_bubbles.csv`'s columns so `build_situations.py` can take it as a second input (or the rows can be appended): the same situation grammar (no bubbles, no lettering unless declared in `card_text`, hands named where a gesture depends on them, insets kept and named so PANEL_CONTINUITY has nothing to bind), `gaze` = `conversation` wherever someone speaks to someone, `default` for the lone figures and the two-panel pairs that are not one conversation (1997, 2003, 2044, 2000, 1897).

Decisions for the owner:
- **Duplicates**: A2-1944 = A2-1995 (same phrase) and A2-1958 = A2-1991 (same meaning) — merge, render one of each.
- **Merge candidates**: A2-2007 with A2-0917 (one coffee / I would like coffee), A2-2012 with A2-0964 (recommend), A2-2020 with A2-0374 if QA reads the cupped ear as "Could you repeat?".
- **Declared lettering**: A2-2002 needs a house number in `card_text` (e.g. the numeral "7") — the only new lettering in the set.
- **Pairs staged as one scene in two moments** (same place, same people): 1987/1989 (tea offered / declined), 1993/1994 (may I / go ahead), 2008/2009 (anything else / that's all), 1984/2034 (can I help / just looking). They are separate cards; PANEL_CONTINUITY does not apply across cards, but the shared scene helps the learner.
- **Gestures to deconflict** across the old set: the farewell hand signs of 0355/0356/0893 against 2019 (two-finger salute) and 2018 (two mirrored hands); the hand-on-chest of 0367/0910 against 2022 (standing, name card). The `confusables` column says which stagings to check.

Cost: 65 renders (after merges) with up to two re-rolls ≈ $1.80–2.60, QA ≈ $0.30.
