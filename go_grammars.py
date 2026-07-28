#!/usr/bin/env python3
"""
GO visual grammars (files 1.7.1) — the executable design bible.

1.7.1: noun-inset population follows the verb principle. People in noun insets
  default to CIVILIAN (ordinary everyday figures), not coverall workers; workers
  appear only where the inset setting is genuinely a work setting — the Materials
  class (workshop/industrial samples) by category default, and specific
  tool/industry rows via deck_builder people overrides. The class inset prose no
  longer hard-codes "worker": it names a neutral "person"/"people" and lets the
  engine dress class (FIGURE_DRESS) decide. Existing per-row people overrides in
  deck_builder.NOUN_STAGING still win.

1.7: population follows the place — Location people default civilian; place cards
  show characteristic occupants; person grammar "role" not "working role";
  SCENE_TAIL exposed as a constant for per-row main overrides.

1.6: two new classes close the coverage gaps found in the code audit.
  - "attribute" (adjectives + Color clusters): the phrase itself IS the
    composition (a marked side-by-side contrast, or a same-color object
    cluster); NO supporting insets — the second object plays the inset's role.
  - "chart" (the 11 category-multi words): calm specimen chart of exemplars;
    NO insets — the exemplars are the insets, structurally.
  route() resolves a wordlist row (flags + type + category) to its class, so
  the deck builder never guesses.

Instead of prose ("animals should have a profile and a habitat inset"), the
visual language of the deck is encoded as DATA: each semantic class states its
main composition and its supporting insets. The noun app reads this to build
category-appropriate cards, so a building, a tool, a fish, and a coat each get
their own idiom — while the frozen house-style (palette, print feel, red bars,
no text, flag-only) stays constant across all of them.

This is the model-independent core: if the renderer ever changes (gpt-image-2,
or anything after), the grammar survives — only the prompt phrasing adapts.
"""

# category (from master_wordlist.csv) -> semantic class
CAT2CLASS = {
    "Animal": "creature",
    "Food": "food",
    "Beverages": "beverage",
    "Location": "place",
    "Transportation": "vehicle",
    "Clothing": "garment",
    "Body": "body_part",
    "Home": "object",
    "Electronics": "object",
    "Misc": "object",
    "Math": "object",
    "Art": "object",
    "Nature": "nature",
    "Materials": "material",
    "People": "person",
    "Job": "person",
    "Color": "attribute",       # object-cluster cards; phrase carries the scene
    "Adjectives": "attribute",  # marked-contrast cards
}
DEFAULT_CLASS = "object"

# classes whose composition is complete in itself — no supporting insets
NO_INSET_CLASSES = {"attribute", "chart", "question", "sequence"}

# category -> dress class for any people on the card.
# 1.7: population follows the place — Location cards default to civilians
# (schools, banks, clubs are civilian spaces); industrial locations override
# back to worker per-row via deck_builder.NOUN_STAGING.
# 1.7.1: the baseline human is now a CIVILIAN, not a worker. Coveralls appear
# only where the setting is a work setting: Materials (workshop/industrial
# samples) by category, and specific tool/industry rows via deck_builder
# people overrides. Job stays professional; People/Location stay civilian.
PEOPLE_CLASS = {"Job": "professional", "People": "civilian",
                "Location": "civilian", "Materials": "worker"}
DEFAULT_PEOPLE = "civilian"

# each class: a main-composition imperative + 2-3 supporting inset ideas.
# 'it' / 'them' refers to the Subject the engine names just before the scene.
NOUN_GRAMMARS = {
    "creature": {
        "main": "Draw it in full-body side profile for clear identification.",
        # 1.7.1: neutral "a person" — dress class decides (civilian by default,
        # worker only for livestock/farm rows via deck_builder overrides).
        "insets": ["a close-up of its head",
                   "a close-up of a foot, paw, or hoof",
                   "a civic scene of a person tending or handling it"]},
    "food": {
        "main": "Draw it whole, with a cut or sliced view beside it.",
        "insets": ["a close-up of a characteristic detail",
                   "a plain canteen scene of people with the food"]},
    "beverage": {
        "main": "Draw it in its serving glass or cup.",
        "insets": ["its source container — a jug, bottle, or pot",
                   "a person drinking it in a canteen or rest area"]},
    "place": {
        # 1.7: occupants ARE the disambiguating signal for places — a school
        # reads as a school because of children, a hospital because of white
        # coats. Populate accordingly.
        "main": ("Draw it from the front as a clear architectural elevation, "
                 "with the people who characteristically use it visible at or "
                 "around it, dressed for that place."),
        "insets": ["a detail of the entrance or a characteristic feature",
                   "a glimpse of the people who characteristically use it, "
                   "inside or at the entrance, doing what one does there"]},
    "vehicle": {
        "main": "Draw it in clear static side profile.",
        "insets": ["a close-up of a key part — a wheel, the engine, or a fitting",
                   "the vehicle in use, driven or loaded by ordinary people"]},
    "garment": {
        "main": "Draw it clearly, laid flat or worn by a plain figure.",
        "insets": ["a close-up of a detail such as a pocket, collar, or fastening",
                   "a person wearing it"]},
    "body_part": {
        "main": "Draw it clearly on a simplified figure, external view only.",
        "insets": ["a clean external close-up",
                   "the part shown in ordinary use"]},
    "object": {
        "main": "Draw it clearly and centered for identification.",
        "insets": ["a close-up of a working detail",
                   "a person using it in a plain civic setting"]},
    "nature": {
        "main": "Draw it clearly in its natural form.",
        "insets": ["a close-up detail such as a leaf, root, or surface",
                   "the feature set within a wider Lithuanian landscape"]},
    "material": {
        "main": "Draw it as a sample piece, clearly revealing its surface.",
        "insets": ["a close-up of the texture",
                   "an everyday object made from it"]},
    "person": {
        # 1.7: "role", not "working role" — a patient, a fan, or a brother has
        # a typical role that is not a trade. Insets follow the role.
        "main": "Draw them in their typical role, dress, and setting.",
        "insets": ["an object characteristic of them in that role",
                   "a plain civic scene of them in their usual role"]},
    # 1.6 — the phrase IS the composition; no insets for these two.
    "attribute": {
        "main": ("Stage the scene exactly as the subject describes, as ONE "
                 "single composed scene. If the description marks a target "
                 "with an arrow, render exactly one bold clear arrow "
                 "indicating it and nothing else."),
        "insets": []},

    # 1.9 — QUESTION grammar. Question words are unpicturable one at a time, but
    # uniform as a set: the SAME civic enquiry scene every card, with only the
    # thing being asked about changing inside the speech bubble. The learner
    # reads the bubble, not the scene, so the scene must never vary.
    "question": {
        "main": ("Compose the card as a calm civic enquiry: one plain figure on "
                 "the LEFT turns to a second figure behind a plain information "
                 "counter on the RIGHT and asks a question. A single large clean "
                 "speech bubble rises from the asking figure and fills the upper "
                 "half of the card. The bubble is the subject of the card — draw "
                 "it large, bold-outlined and uncluttered. Inside the bubble, and "
                 "nowhere else, place one bold question mark together with the "
                 "pictogram described. Keep the two figures small, plain and "
                 "identical in every card of this set."),
        "insets": []},

    # 1.9 — SEQUENCE grammar. A phrase or sentence is a chain of events, so it
    # is staged the way the manual stages a procedure: numbered panels read left
    # to right, each one step, joined by arrows. Same frame every time.
    "sequence": {
        "main": ("Compose the card as a civil-defence procedure strip: a single "
                 "horizontal row of equally sized bordered panels, read LEFT to "
                 "RIGHT, each panel showing exactly one step of the action, with "
                 "a bold arrow between consecutive panels. Number the panels in "
                 "small plain circles in their upper-left corners. Every panel "
                 "shares the same border weight, background and figure scale. No "
                 "panel may contain more than one action."),
        "insets": []},
    "chart": {
        "main": ("Compose the card as a calm specimen chart: arrange the "
                 "named items in an even row or grid, each drawn small, "
                 "clean and complete in its own right, with no single item "
                 "dominating the card."),
        "insets": []},
}


# the frozen framing clause appended to every main composition (1.7: exposed
# as a constant so deck_builder per-row main overrides keep the house framing)
SCENE_TAIL = (" Keep the subject large and dominant in the foreground, "
              "floating cleanly on the cream paper on a simple background.")


def class_for(category: str) -> str:
    return CAT2CLASS.get(category, DEFAULT_CLASS)


def route(category: str, wtype: str = "N", flags: str = "") -> str:
    """Resolve a wordlist row to its semantic class. Flag-level routing wins
    (category-multi), then word type, then the category map. Verbs are handled
    by the verb treatment, not a noun grammar."""
    f = flags or ""
    if "categoryC" in f:
        return "chart"
    # 1.9 — the two new uniform-set grammars
    if wtype == "Q" or category == "Question words" or "question" in f:
        return "question"
    if wtype in ("PHRASE", "SENTENCE") or "sequence" in f:
        return "sequence"
    if wtype == "A":
        return "attribute"
    return class_for(category)


def compose_class(cls: str, category: str = ""):
    """Return (scene, inset_note, semantic_class, people, insets) for a
    semantic class. The engine supplies the Subject and the frozen
    house-style; this only sets the class-specific composition."""
    g = NOUN_GRAMMARS[cls]
    scene = g["main"] + SCENE_TAIL
    insets = cls not in NO_INSET_CLASSES
    inset_note = ("Include 2 to 3 small supporting insets: "
                  + "; ".join(g["insets"]) + ".") if insets else ""
    people = PEOPLE_CLASS.get(category, DEFAULT_PEOPLE)
    return scene, inset_note, cls, people, insets


def compose_noun(category: str):
    """Back-compatible category entry point; see compose_class()."""
    return compose_class(class_for(category), category)
