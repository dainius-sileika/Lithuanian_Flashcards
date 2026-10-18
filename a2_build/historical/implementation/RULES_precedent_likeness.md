# Precedent, likeness and emblem rules — exact text for go_generator.py

Plan only (2026-10-18). Nothing applied. Owner decisions of 2026-10-17 behind this text: places "adopt all"; faces "surroundings, but try faces as best you can"; president = Adamkus, "use the likeness of Adamkus when he was serving as president", anachronisms OK; "vytis is fine, although the vytis cross might be easier to draw, and leans patriotic, which I like"; tram stays; hospital → 1939 Kaunas Clinics and Maironis bronze → 1928 Freedom Statue approved.

Everything below is additive except the FLAG_RULE wording. The 520 shipped A1 masters and the A2 renders that do not pass `precedent=`, `likeness=` or `flag="emblem"` render byte-identically.

## 1. New constants (place after `ANATOMY_PROPS_RULE`, before `FLAG_RULE`)

```python
# 2026-10-18 historical places and figures (a2_build/historical/). Owner: "surroundings,
# but try faces as best you can". PRECEDENT_RULE carries a real Lithuanian thing or
# building by its features; LIKENESS_RULE, on listed cards only, asks for a named face
# at a named period. Both are additive segments: a card that passes neither renders
# exactly as before.
PRECEDENT_RULE = (
    "This card quietly evokes a real Lithuanian precedent: {description}. It is carried "
    "by features alone - the shape and materials of the building, the cut and colour of "
    "period dress, the livery, struts and engine of an aircraft, the kit of a team - and "
    "never by lettering, a name, a plaque or a badge. The precedent sits inside the album's "
    "1981 world and is drawn in the same flat matte ink as everything around it; it "
    "supports the card's word and does not replace it."
)

LIKENESS_RULE = (
    "The {role} is drawn in the likeness of {name} as {pronoun} looked in {period}: "
    "{features}. Carry the likeness in the face, hair, build and bearing, printed flat in "
    "the album style at the same scale as the other figures - a recognisable person "
    "drawn by the same anonymous hand, not a portrait. No name, caption, plaque or "
    "lettering identifies the person anywhere in the picture."
)
```

Per-card values live in the staging tables (`a2_build/historical/implementation/likeness_cards.csv`), not in code; the executor formats `LIKENESS_RULE` once per figure and joins them with a space when a card has two (012, A2-1917, 123).

## 2. Assembly (inside `_prompt_openai`)

New keyword arguments `precedent=""` and `likeness=""` (both default empty; `generate()` and `build_prompt()` pass them through like `staging`). Insert after the setting block and before `MAIN_MEANING_RULE`, so the precedent sits with the scene and the likeness just before the dress rule it refines:

```python
    if setting:
        segs.append(setting)
        segs.append(SETTING_GUARD)
    if precedent:
        segs.append(PRECEDENT_RULE.format(description=precedent))
    if likeness:
        segs.append(likeness)          # already formatted LIKENESS_RULE text, one per figure
    segs.append(MAIN_MEANING_RULE)
```

The lead's "anonymous types of 1981" sentence stays as it is: on a likeness card it governs every face *except* the named one, which is what the owner asked for. If the test (test_plan.csv) shows the lead wins and the face comes out generic, the fallback is to append the likeness sentence a second time at the very end, after `suffix` — the position the model reads last — rather than to edit the lead.

## 3. Emblems: the Vytis and the Cross of Vytis (replaces the flag-only wording)

### 3a. Replacement text of `FLAG_RULE` (the owner's rule change, stated once)

```python
# 2026-10-18: flag-first, no longer flag-only. Owner: the Vytis is fine, the Cross of
# Vytis easier to draw and "leans patriotic". Heraldry garbled under gpt-image-1.5
# (0.9); gpt-image-2.5 is to be tested on T4/T5 before any card beyond the listed ones
# carries an emblem. Columns of Gediminas and every other badge stay out.
FLAG_RULE = (
    "If any national emblem is shown at all, prefer a small Lithuanian tricolor flag "
    "(a horizontal yellow band on top, green in the middle, red on the bottom), placed "
    "small and only where it fits naturally. Where the scene itself calls for a state "
    "emblem - a courtroom wall, a parliament chamber, a podium, a uniform, a public "
    "building - it may carry the Cross of Vytis, a plain double-barred cross drawn once "
    "as one clean simple shape, or, only where a wall or banner gives it room, the "
    "Vytis: a white armoured knight on a white rearing horse, sword raised in his right "
    "hand and a shield on his left arm, on a plain red field, drawn large, clean and "
    "simple with no fine detail. Never more than one emblem in a picture; do NOT include "
    "the Columns of Gediminas or any other heraldic badge. Do not put a flag or emblem "
    "on every card - many cards need none at all."
)
```

### 3b. Recommended executable form (what the executor should actually do)

Do **not** swap the default `FLAG_RULE` yet. Add the text above as `FLAG_RULE_EMBLEM`, register it as `FLAG_RULES["emblem"]`, and route only the listed cards through it (`deck_builder.FLAG_OVERRIDE[n] = "emblem"` for A1 numbers 035, 097, 112; the A2 adapter passes `flag="emblem"` for A2-1347 and A2-1370 when the B1 pack ships). Reason: the 0.9 note records heraldry garbling as a fact of the previous model, and `qa_images.py` has no check for a malformed knight. After T4 (Cross) and T5 (Vytis) pass QA and the owner's eye, promote the text to the default `FLAG_RULE` and record it in GO_STYLE_SPEC.md's changelog as:

> files 2.2 — EMBLEMS: flag-first, not flag-only. The Cross of Vytis (plain double-barred cross) and, where a wall gives it room, the Vytis are allowed once per picture on cards whose scene calls for a state emblem (owner 2026-10-17). Columns of Gediminas and other badges remain out. Tested on 035 teismas and 097 prezidentas before roll-out.

The zimage fallback's `_Z_NEGATIVE` ("no coats of arms or heraldic emblems") is left as it is: that backend garbles heraldry by construction.

## 4. Ledger provenance

`feasibility.md` §2 asks that a card carrying a real person be recorded. The executor adds a `likeness` column to the card ledger rows of the listed cards (person, period), so a later contributor knows the card carries a named face. `cards.csv` schema is unchanged.
