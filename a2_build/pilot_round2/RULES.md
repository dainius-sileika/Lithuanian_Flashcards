# Rule changes for pilot round 2 — exact text (Fable, 2026-10-17; for the executor)

Scope rule, same as on 2026-10-17: these changes fire only when `generate(..., situation=True)`, i.e. for the rows of `restage_bubbles.csv`. Every other card's prompt stays byte-identical. Each block below says **NEW** (add) or **REPLACES** (and quotes the text it replaces). Nothing here has been applied; `go_generator.py`, `go_grammars.py`, `gen_phrases.py`, `qa_images.py` and the data are untouched in this commit.

---

## (a) CONVERSATION_GAZE — go_generator.py

### a1. NEW constants (place directly after `GAZE_PAIR_RULE`, line 126)

```python
# 2026-10-17 pilot round 2 (owner): "all the conversation cards need to have the actors
# looking at each other when they speak, unlike the other, single-panel, cards." Five of
# the twelve two-panel pilot cards and two single scenes failed on a face turned to the
# viewer. The prompt asked for it three times (lead, GAZE_PAIR_RULE, suffix). For
# situation cards whose staging has a speaker (gaze == "conversation") all three are
# swapped for this rule; non-speaking situation cards (a man patting his pockets, a
# woman at a calendar, galvoti) keep the house gaze.
CONVERSATION_GAZE_RULE = (
    "This is a spoken moment. The person who speaks and the person spoken to look at "
    "each other, eyes on each other's face, heads turned toward one another; where the "
    "staging has the speaker look or point at a thing (a clock, a shelf, the rain), the "
    "listener looks at the speaker or at that thing. Nobody in the picture looks at the "
    "viewer or toward the camera; no face is turned to the front with eyes past the "
    "viewer's shoulder. Bystanders look at their own task or at the speakers. A person "
    "on a telephone looks at the receiver or into the middle distance, never at the "
    "viewer. In a two-panel picture this holds in both panels."
)
# the two gaze sentences of the house style that CONVERSATION_GAZE_RULE replaces; the
# asserts below fail loudly if a later edit of the lead or suffix changes their wording
_HOUSE_GAZE_LEAD = ("Heads turn at varied natural angles: in a group most look at their task "
                    "or at each other and one or two face the viewer, eyes just past the "
                    "viewer's shoulder; of two main figures only one faces the viewer; a lone "
                    "figure stands near-frontal, face turned only a little.")
_HOUSE_GAZE_SUFFIX = ("One or two faces toward the viewer, eyes just past the shoulder; of two "
                      "main figures only one. ")
_CONVERSATION_GAZE_LEAD = ("Heads turn toward each other: the people who speak look at one "
                           "another, the rest at their task; nobody looks at the viewer.")
_CONVERSATION_GAZE_SUFFIX = "The speakers look at each other; no face toward the viewer. "
for _lead in (CONCEPT_LEAD, CONCEPT_LEAD_SCENE):
    assert _HOUSE_GAZE_LEAD in _lead, "house gaze sentence moved in the lead; update _HOUSE_GAZE_LEAD"
for _suf in (STYLE_SUFFIX, STYLE_SUFFIX_SCENE):
    assert _HOUSE_GAZE_SUFFIX in _suf, "house gaze sentence moved in the suffix; update _HOUSE_GAZE_SUFFIX"


def _conversation_lead(lead, suffix):
    """The house lead and suffix with their gaze sentences swapped for the conversation
    ones. Used only when situation=True and gaze == "conversation"."""
    return (lead.replace(_HOUSE_GAZE_LEAD, _CONVERSATION_GAZE_LEAD),
            suffix.replace(_HOUSE_GAZE_SUFFIX, _CONVERSATION_GAZE_SUFFIX))
```

### a2. REPLACES the signature of `_prompt_openai` (line 246–249)

replaces
```python
def _prompt_openai(subject, scene="", labels=None, exclude="", insets=True,
                   inset_note="", text=False, people="worker", extra="",
                   glyph=False, flag="lt", exact_text="", composition="vignette",
                   staging="", setting="", motion_strip=False, situation=False):
```
with
```python
def _prompt_openai(subject, scene="", labels=None, exclude="", insets=True,
                   inset_note="", text=False, people="worker", extra="",
                   glyph=False, flag="lt", exact_text="", composition="vignette",
                   staging="", setting="", motion_strip=False, situation=False,
                   gaze="default", panels=1):
```
(`gaze` is `"default"` or `"conversation"`; `panels` is 1 or 2. Both are threaded through `build_prompt()` and `GOGenerator.generate()` with the same defaults, exactly as `situation` was on 2026-10-17.)

### a3. REPLACES the lead/suffix selection and the gaze line inside `_prompt_openai`

replaces (line 253)
```python
    lead, suffix = LEADS.get(composition, LEADS["vignette"])
```
with
```python
    lead, suffix = LEADS.get(composition, LEADS["vignette"])
    conversation = bool(situation and gaze == "conversation")
    if conversation:
        lead, suffix = _conversation_lead(lead, suffix)
```
and replaces (line 265)
```python
    segs.append(GAZE_PAIR_RULE)
```
with
```python
    segs.append(CONVERSATION_GAZE_RULE if conversation else GAZE_PAIR_RULE)
```

Behaviour kept: `situation=False` → unchanged prompt. `situation=True, gaze="default"` → the 2026-10-17 situation prompt, unchanged (question words kas/kur/kada/koks/kuris, 374 galvoti). `situation=True, gaze="conversation"` → the three house gaze sentences become the conversation ones.

---

## (b) PANEL_CONTINUITY — go_generator.py (constant, every multi-panel card) + go_grammars.py

Owner, 2026-10-17 review notes: "all panel cards needs a coherency check to make sure the mise-en-scene between panels remains consistent." This is therefore a **standing rule for the whole deck**, not a situation-only rule: it fires on every card that has two or more panels, a strip, or insets — which is nearly every card. It is the one change here that touches prompts outside the situation set; the owner has confirmed it. The rule exempts insets that show a different place, object or detail, so the house inset style (each inset "a clearly different moment or detail") is untouched; it binds only where a panel or inset repeats the scene.

### b1. NEW constant in go_generator.py (after `SETTING_GUARD`, line 128)

```python
# 2026-10-17 pilot round 2 — owner: "all panel cards needs a coherency check to make sure
# the mise-en-scene between panels remains consistent." 0897 (a man moved behind his
# companion between panels), 0898 (a door that exists only in the right panel), 0383 (a
# suitcase in different hands across insets). Appended to EVERY card with more than one
# panel, a strip, or insets; it binds only where a panel or inset repeats the same scene.
PANEL_CONTINUITY_RULE = (
    "Wherever the card shows the same scene more than once - in two or more panels, in a "
    "strip, or in an inset that repeats the main scene - every repetition is the same "
    "place seen from a consistent viewpoint: the same people in the same clothes and the "
    "same relative positions (left stays left, nobody steps in front of or behind another, "
    "nobody enters or leaves), the same walls, doors, windows, furniture, counters, signs "
    "and street fixtures in the same places, and every object held by the same person "
    "unless the staging says it is handed over, and then both hands are on it. Only the "
    "moment changes: gesture, expression, the step of the action. An inset that shows a "
    "different place, object or close-up detail is not a repetition and is free."
)
```

### b2. REPLACES the plausibility line inside `_prompt_openai` (line 275)

replaces
```python
    segs.append(PLAUSIBILITY_RULE)
```
with
```python
    segs.append(PLAUSIBILITY_RULE)
    if insets or motion_strip or panels > 1:
        segs.append(PANEL_CONTINUITY_RULE)
```
(`panels` is the new kwarg from a2; gen_phrases passes 2 for `situation_2` and 3 for `sequence`.) Consequence stated plainly: every future render of an inset card carries one more sentence, so the "prompts byte-identical to the shipped masters" line in the module docstring is no longer true for new renders. The 1387 shipped pictures are not re-rendered by this; see d6 for checking them.

### b3. REPLACES the `situation_2` grammar in go_grammars.py (lines 221–229)

replaces
```python
    "situation_2": {
        "main": ("Compose the card as exactly TWO equal bordered panels side by "
                 "side, read LEFT to RIGHT, sharing one border weight, background "
                 "and figure scale. THE SAME TWO PEOPLE appear in both panels, "
                 "identically dressed and at the same scale, so the pair reads as "
                 "one exchange: the LEFT panel shows the first act, the RIGHT panel "
                 "shows the answer as a plain visible action or object. Both panels "
                 "are equally large and legible. No speech bubble in either panel."),
        "insets": []},
```
with
```python
    "situation_2": {
        "main": ("Compose the card as exactly TWO equal bordered panels side by "
                 "side, read LEFT to RIGHT, sharing one border weight, background "
                 "and figure scale. THE SAME TWO PEOPLE appear in both panels, "
                 "identically dressed, at the same scale and in the same places, so "
                 "the pair reads as one exchange seen from one spot: the LEFT panel "
                 "shows the first act, the RIGHT panel shows the answer as a plain "
                 "visible action or object. Both panels are equally large and "
                 "legible. No speech bubble in either panel."),
        "insets": []},
```

### b4. gen_phrases.py `build_situation_call()` — one addition to `kw = dict(...)`

```python
              gaze=s.get("gaze", "conversation"),
              panels=(2 if fmt == "situation_2" else 3 if fmt == "sequence" else 1),
```

---

## (c) ANATOMY / PROPS — go_generator.py

### c1. NEW constant (after `ANATOMY_RULE`, line 151)

```python
# 2026-10-17 pilot round 2: 0895 (the mother's waving hand on the brother's arm), 0383
# (a suitcase nobody's hand is actually on), 0900 (a shopkeeper fused into his counter),
# 0114 (the wrong hand). ANATOMY_RULE only counted fingers. Used in place of it on
# situation cards; every other card keeps ANATOMY_RULE byte-for-byte.
ANATOMY_PROPS_RULE = (
    "Render every human hand with clean natural anatomy and exactly five fingers. Every "
    "arm and hand belongs to one body and is drawn joined to that body's shoulder: no "
    "hand floats, no arm crosses from one person onto another, and when two people stand "
    "close each one's arms stay on their own side. When the staging names a right or left "
    "hand, that hand and no other performs the action, drawn on the correct side of the "
    "body as the viewer sees it. An object a person is said to carry, hold or hand over is "
    "visibly in that person's grip, fingers closed round the handle or the object, its "
    "weight on that hand. People stand beside, behind or in front of furniture, counters, "
    "rails and vehicles, never inside or merged with them: a person behind a counter is "
    "cut off by its top edge and nothing else; a seated person sits on the seat. Faces are "
    "whole and each face is its own."
)
```

### c2. REPLACES the anatomy line inside `_prompt_openai` (line 305)

replaces
```python
    segs.append(ANATOMY_RULE)
```
with
```python
    segs.append(ANATOMY_PROPS_RULE if situation else ANATOMY_RULE)
```

### c3. Handedness lives in the staging line

The rule can only honour a hand the staging names. From round 2 on, a staging line names the hand whenever the owner's verdict or the gesture depends on it (0114: "her RIGHT hand"; 0360: "her right hand to her chest"; 0882: "brush in her right hand … waving her left"). `restage_round2.csv` does this for the 14. For the remaining ~133 cards the executor adds a hand only where a gesture is one-handed and the side matters (holding out coins, pointing, a handshake: right hand).

---

## (d) QA checks — qa_images.py

### d1. REPLACES `FIT_PROMPT` (lines 121–135)

replaces the whole `FIT_PROMPT = """…"""` block with
```python
FIT_PROMPT = """You are inspecting an illustration from a language-learning flashcard deck.
Its English caption is: {caption}
The detail meant to make the situation unmistakable is: {cue}
{conversation_line}
Answer ONLY about what is visible. Return strict JSON:
  "fit":        "yes" | "nearly" | "no" — with the caption, does the picture show
                the moment this phrase is said?
  "cue_visible": true | false — is the detail above clearly visible?
  "stray_acts": array of gestures or symbols in the picture that belong to a
                DIFFERENT phrase and that this caption does not call for
                (a handshake, a wave, a raised palm, a bowed head, a thumb-up,
                a pointing finger, a hand on the chest). [] if none.
  "speakers":   for a picture in which someone speaks or is spoken to: an object
                {{"look_at_each_other": true|false,
                  "anyone_at_viewer": true|false,
                  "note": "who looks where, one line"}};
                null if nobody in the picture is speaking to anyone.
  "panels":     for a two-panel picture only: an object
                {{"same_people": true|false,
                  "same_positions": true|false,   (left stays left, nobody moved in front of or behind another)
                  "same_background": true|false,  (same walls, doors, windows, furniture, signs in both)
                  "props_consistent": true|false, (objects held by the same person in both, unless handed over)
                  "right_answers_left": true|false,
                  "note": "what differs, one line"}};
                null for a single scene.
  "limbs_ok":   true | false — every arm and hand is attached to the right body
                (no hand on another person's arm, no floating or shared limb).
                If false, say which in "limbs_note".
  "limbs_note": one line, or "".
  "props_ok":   true | false — every object the caption or cue says is carried or
                held is visibly in that person's grip; no figure is merged into
                furniture, a counter or a vehicle. If false, say which in "props_note".
  "props_note": one line, or "".
"""
CONVERSATION_LINE = ("In this picture someone speaks to someone else; the deck's rule is that "
                     "they look at each other and nobody looks at the viewer.")
```
(The old `two_panels_ok` key is superseded by `panels`. Braces are doubled because the string is `.format()`-ed.)

### d2. REPLACES the fit call in `describe_situation()` (line 176)

replaces
```python
    seen["fit"] = _ask(client, path, FIT_PROMPT.format(caption=cap, cue=srow.get("cue") or "(none given)"))
```
with
```python
    seen["fit"] = _ask(client, path, FIT_PROMPT.format(
        caption=cap, cue=srow.get("cue") or "(none given)",
        conversation_line=(CONVERSATION_LINE if srow.get("gaze", "conversation") == "conversation" else "")))
```

### d3. REPLACES the tail of `judge_situation()` (lines 210–214)

replaces
```python
    for a in fit.get("stray_acts") or []:
        warns.append(f"stray act: {a}")
    if fit.get("two_panels_ok") is False and srow.get("format") == "situation_2":
        warns.append("two panels: people/scale/answer do not match")
    return fails, warns
```
with
```python
    for a in fit.get("stray_acts") or []:
        warns.append(f"stray act: {a}")
    # 2026-10-17 pilot round 2 — the four owner-flagged defect classes. Each was a
    # re-roll in the owner's hands, so each is a hard FAIL here, not a WARN; the vision
    # model's own uncertainty is carried in the note.
    conv = srow.get("gaze", "conversation") == "conversation"
    sp = fit.get("speakers")
    if conv:
        if not sp:
            warns.append("gaze: model saw nobody speaking on a conversation card")
        elif sp.get("anyone_at_viewer") is True:
            fails.append(f"GAZE: a speaker looks at the viewer ({sp.get('note', '')})")
        elif sp.get("look_at_each_other") is False:
            fails.append(f"GAZE: speakers do not look at each other ({sp.get('note', '')})")
    pn = fit.get("panels") or {}
    if srow.get("format") == "situation_2":
        if not pn:
            warns.append("panels: model did not report on the two panels")
        else:
            bad = [k for k in ("same_people", "same_positions", "same_background", "props_consistent")
                   if pn.get(k) is False]
            if bad:
                fails.append(f"CONTINUITY: {', '.join(bad)} ({pn.get('note', '')})")
            if pn.get("right_answers_left") is False:
                warns.append(f"two panels: right does not answer left ({pn.get('note', '')})")
    if fit.get("limbs_ok") is False:
        fails.append(f"LIMBS: {fit.get('limbs_note') or 'a limb is on the wrong body'}")
    if fit.get("props_ok") is False:
        fails.append(f"PROPS: {fit.get('props_note') or 'a carried object is not held / figure merged into furniture'}")
    return fails, warns
```

### d4. Deck-wide coherence check — REPLACES the `"problems"` entry of the base `PROMPT` (lines 79–82)

Every card, not only situation cards: the base cold-read gains a coherence question, so `judge()` can fail any inset or panel card whose repeated scene drifts.

replaces
```python
  "problems":   array of short strings describing anything visually wrong:
                garbled or nonsense lettering, malformed hands or faces, duplicated
                or fused limbs, incoherent objects, elements that contradict each
                other, or anything a careful reviewer would call an error. [] if none.
"""
```
with
```python
  "problems":   array of short strings describing anything visually wrong:
                garbled or nonsense lettering, malformed hands or faces, duplicated
                or fused limbs, incoherent objects, elements that contradict each
                other, or anything a careful reviewer would call an error. [] if none.
  "coherence":  for a picture with two or more panels, a strip, or an inset that
                repeats the main scene: {"applies": true, "consistent": true|false,
                "note": "what differs between the repetitions, one line"} — people,
                clothes, positions (left/right, front/behind), fixtures and held
                objects must match; only gesture, expression or step may change.
                {"applies": false} when no scene is repeated (insets that show a
                different object, place or close-up do not count).
"""
```
and in `judge()`, before `for p in seen.get("problems", []) or []:` (line 389), add
```python
    coh = seen.get("coherence") or {}
    if coh.get("applies") and coh.get("consistent") is False:
        fails.append(f"CONTINUITY: {coh.get('note') or 'repeated scene differs between panels/insets'}")
```
`SIT_PROMPT` is built from `PROMPT`, so situation cards inherit the key; `judge_situation()` calls `judge()`, so they inherit the fail too. The two-panel-specific `panels` block in d3 stays (it also checks that the right panel answers the left).

### d5. Cache key

Append `":r2"` to the situation cache key so round-2 reads are not served from round-1 cache entries (which lack the new keys): in `main()` both occurrences of `(":sit" if … else "")` become `(":sit:r2" if … else "")`. The base cache is keyed by file hash only, so the shipped 1387 cards keep their old entries until run with `--recheck`; a retro coherence pass over the shipped deck is a separate decision for the owner (at the pilot's rate, ≈ $0.01 a card, so ≈ $15 for the whole deck; it finds existing inset drift, it does not fix it).

### d6. `situation_row()` carries `gaze`

`situations.py` (generated) gets a `gaze` key — see (f). `situation_row()` needs no change: it returns the whole dict.

---

## (f) situations.py — via restage_bubbles.csv and build_situations.py

`situations.py` is generated; do not edit it by hand. Two changes:

1. **New CSV column `gaze`** in `a2_build/restage_bubbles.csv`, values `conversation` | `default` | empty. `a2_build/pilot_round2/restage_round2.csv` has the column filled for the 14 redraws; its 14 rows are **appended** to `restage_bubbles.csv` (the build takes the last "yes" row per gloss, so they supersede round 1 without deleting history).
2. **build_situations.py**: add to the `entry` dict
   ```python
             "gaze": (r.get("gaze") or "").strip() or _default_gaze(r),
   ```
   with
   ```python
   def _default_gaze(r):
       """Empty gaze column: phrase, exchange and sentence rows are spoken moments;
       question-word pictures and 374 galvoti are not, unless the column says so."""
       src = r["source_file"]
       if "QUESTION_BUBBLE" in src or "NOUN_STAGING" in src:
           return "default"
       return "conversation"
   ```
   and `"gaze"` added to the docstring's key list. Round-1 question-word rows that do show a spoken exchange get an explicit `conversation` in round 2 (0113, 0114, 0117); the rest (0108, 0110, 0111, 0112, 0115, 0116, 374) stay `default` and are not redrawn.

---

## Order for the executor

1. (f) CSV column + build_situations.py; append `restage_round2.csv`; regenerate `situations.py`; `python3 -c "import situations"`.
2. (a), (b1), (b2), (c) in go_generator.py; (b3) in go_grammars.py; (b4) in gen_phrases.py. Dry-run three prompts (0360, 0383, 0113) and read them: the word "viewer" must appear only inside the conversation rule's negations; `PANEL_CONTINUITY_RULE` on all three (0360 has two panels, 0383 and 0113 have insets); two insets only on 0113. Also dry-run one ordinary noun card and confirm its prompt differs from the shipped ledger by exactly the one `PANEL_CONTINUITY_RULE` sentence and nothing else.
3. (d) in qa_images.py; run it on the untouched round-1 folder first with `--recheck` into a scratch cache to see the false-positive rate of the five new checks (gaze, panels, limbs, props, coherence) before spending on renders.
4. Render the 14 into `out_phrases_v3/round2/` (never over round 1); QA; owner review page.
