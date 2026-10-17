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

## (b) PANEL_CONTINUITY — go_generator.py (constant) + go_grammars.py (grammar text)

### b1. NEW constant in go_generator.py (after `SETTING_GUARD`, line 128)

```python
# 2026-10-17 pilot round 2: 0897 (a man moved behind his companion between panels) and
# 0898 (a door that exists only in the right panel). The two-panel grammar fixed people,
# dress and scale but not position, setting or props. Appended by gen_phrases for
# format situation_2 (panels == 2).
PANEL_CONTINUITY_RULE = (
    "Both panels are the same place seen from the same viewpoint at the same distance: "
    "the same people stand in the same relative positions, left stays left and right "
    "stays right, nobody steps in front of or behind another person between panels, "
    "and nobody enters or leaves. The same walls, doors, windows, furniture, counter, "
    "signs and street fixtures appear in both panels in the same places; anything "
    "visible in one panel is visible in the other. Every object a person holds in the "
    "left panel is held by the same person in the right panel unless the staging says "
    "it is handed over, and then both hands are on it. Only the gesture and expression "
    "change."
)
```

### b2. REPLACES the `situation_2` grammar in go_grammars.py (lines 221–229)

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
(only "and in the same places" and "seen from one spot" are added; the continuity detail lives in `PANEL_CONTINUITY_RULE` so the grammar stays short.)

### b3. gen_phrases.py `build_situation_call()` — two one-line additions

after `main = NOUN_GRAMMARS[fmt]["main"] + SCENE_TAIL` (line 83), add
```python
        if fmt == "situation_2":
            main += " " + PANEL_CONTINUITY_RULE
```
and in the `kw = dict(...)` add
```python
              gaze=s.get("gaze", "conversation"), panels=(2 if fmt == "situation_2" else 1),
```
with `from go_generator import GOGenerator, PANEL_CONTINUITY_RULE` at the top.

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

### d4. Cache key

Append `":r2"` to the situation cache key so round-2 reads are not served from round-1 cache entries (which lack the new keys): in `main()` both occurrences of `(":sit" if … else "")` become `(":sit:r2" if … else "")`.

### d5. `situation_row()` carries `gaze`

`situations.py` (generated) gets a `gaze` key — see (f). `situation_row()` needs no change: it returns the whole dict.

---

## (e) Optional: stop the lead from priming insets on single scenes — go_generator.py

Not in the owner's list; it is the mechanism behind 0383's extra "panels" and the README observation that most single scenes grew 2–3 insets. If adopted, apply only when `situation and not insets`:

```python
_INSET_LEAD = ("; insets are small ruled boxes on the same paper, each a clearly different "
               "moment or detail")
_INSET_SUFFIX = " Every inset a clearly different moment, all in the same ruled frame."
_INSET_MEANING_TAIL = ", and the insets only add supporting detail"
NO_INSET_RULE = ("One picture only: no inset panels, no second moment, no small boxed "
                 "details, no sequence. The whole card is this one scene.")
```
and in `_prompt_openai`, when `situation and not insets`: strip `_INSET_LEAD` from `lead`, `_INSET_SUFFIX` from `suffix`, `_INSET_MEANING_TAIL` from the `MAIN_MEANING_RULE` segment, and append `NO_INSET_RULE` after the scene. Owner's call: 0113 wants insets by design and gets them (`insets=True`), so this only affects cards staged as one scene. I recommend adopting it in round 2 so that the 11 single-scene redraws test it.

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
2. (a), (b1), (c) in go_generator.py; (b2) in go_grammars.py; (b3) in gen_phrases.py. Dry-run three prompts (0360, 0383, 0113) and read them: the word "viewer" must appear only inside the conversation rule's negations; `PANEL_CONTINUITY_RULE` only on 0360; two insets only on 0113.
3. (d) in qa_images.py; run it on the untouched round-1 folder first with `--recheck` into a scratch cache to see the false-positive rate of the four new checks before spending on renders.
4. Render the 14 into `out_phrases_v3/round2/` (never over round 1); QA; owner review page.
