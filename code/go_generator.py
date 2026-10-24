#!/usr/bin/env python3
"""
Grazhdanskaya Oborona Generator  (GO-Gen)  —  files 1.7.1
=========================================================
Reusable engine for late-Soviet civil-defense INSTRUCTIONAL WALL CHART art.

Governing principle (the north star we JUDGE against): **deadpan civic
procedure** — a technical educational wall chart, not agitprop.

2026-10-17 pilot round 2 (rounds/2026-10-17_pilot_round2/RULES.md): three new rules.
     CONVERSATION_GAZE_RULE (situation=True, gaze="conversation") swaps the house
     gaze sentences of lead, GAZE_PAIR_RULE and suffix; ANATOMY_PROPS_RULE replaces
     ANATOMY_RULE on situation cards; PANEL_CONTINUITY_RULE is appended to EVERY
     card with insets, a motion strip or panels > 1 (deck-wide, owner's decision).
     New renders of inset cards are therefore no longer byte-identical to the
     shipped masters' prompts; the shipped pictures are not re-rendered by this.

2026-10-17: situation=True (bubble-free phrase cards, RESTAGE_PROPOSAL §2(f)):
     NO_TEXT_RULE_SITUATION + NO_BUBBLE_RULE replace NO_TEXT_RULE, and declared
     card_text never names the target. Only the rows of
     data/restage_bubbles.csv pass it; every other prompt is unchanged.

1.7.1: INSET_MEANING_RULE bakes the 1.7 guessability QA gate into the prompt
     itself — every inset must SUPPORT recognition of the subject; at worst it
     must stay attractive and on-theme; it must NEVER depict something mistakable
     for a different, neighbouring subject. Aim: fewer re-rolls (the gate was
     costing them — one card took 66 tries). Prompt otherwise unchanged.

1.6.1: single-glyph exception (decision Q2): glyph=True permits ONLY the one
     large letterform that IS the subject, keeps the red bars and every other
     text prohibition. Used by exactly three cards (letter/consonant/vowel).

1.6: hardening for the mass run. (a) OpenAI path now retries transient errors
     (rate limits, timeouts, 5xx) with exponential backoff — content-policy or
     auth errors still fail fast. (b) cards.csv schema carries lt_pron and
     gender so the Anki layer is fed in one pass. Prompts UNCHANGED — the
     locked 1.5.1 style renders byte-identically.

1.1: stripped the legacy supporting-label machinery from the app layer and
     from cards.csv (labels were for baked-in image text, dropped in 0.7). The
     engine keeps its optional text=True path for reuse in other projects.

1.0: styling locked. Engine unchanged from 0.9; the 1.0 change lives in the
     verb app — floating institutional main scene (context C) with an optional
     per-verb consequence inset (accent D). Nouns unchanged.

0.9 changes vs 0.8:
  - SYMBOLS: flag-only and OCCASIONAL. Intricate heraldry (Vytis, Columns of
    Gediminas, Vytis Cross, Šauliai) rendered as garble — same failure mode as
    text. Now: at most a small Lithuanian tricolor, only where it fits, and NOT
    on every card. No coats of arms or emblems.
  - light ANATOMY steer (five-finger hands, clean paws/feet) — reduces the
    extra-finger / distorted-paw rate (can't be eliminated; re-roll the rest)
  - period-correct black kirza-style work boots (black was standard issue;
    brown was the officer/long-service exception)

0.8: flat workers' caps; anatomical cutaways banned; verbs hard-capped at 2 insets.
0.7: text removed from the image; empty red bars; blue coveralls; cards.csv.

DUAL BACKEND — verbosity is inversely proportional to model competence:
  backend="openai" (default): gpt-image-2, quality "medium". Concept-forward.
  backend="zimage" (fallback): Z-Image-Turbo. Decomposed clause. Seeds recorded.

SETUP (keys live in YOUR environment, never in code or chat):
  OpenAI:  export OPENAI_API_KEY=sk-...   ; pip install openai
  Z-Image: export HF_TOKEN=hf_...         ; pip install gradio_client
"""
from __future__ import annotations
import os, re, sys, csv, time, shutil, argparse, hashlib, base64

# ===========================================================================
# CONCEPT-FORWARD encoding (backend="openai")
# ===========================================================================
# F6.2 house style (2026-10-11; F6.1 + spot-check 09 amendments). Hair wording
# corrected per owner 2026-10-11: curls are one option for older women, never a rule. Settled by the owner's blind surveys in
# style_lab/2026-10-10_06..08 (Fable analysis: 08_F6_roll/results/). Two leads that
# differ only in the composition sentence: vignette (objects, clothing, animals,
# persons, single-figure verbs) and full scene (places, buildings, crowds,
# workplace scenes). Each has a matching suffix appended at the very end, so the
# paper/gaze/inset finish is the last thing the model reads.
# Paper target (strict, style_lab/tools/papertone2.py): L* 85-88, b* 18-23.
CONCEPT_LEAD = "A printed page from a 1981 Lithuanian civil-defence training album, drawn and printed like the Soviet Grazhdanskaya Oborona wall charts of 1975-1985: dark-brown brush-and-ink outlines around every figure and object, dead-matte gouache fills with soft shading on every surface, four-colour offset with a faint coarse halftone, muted inks of dusty blue, olive, ochre, brick red and grey-brown on light aged cream paper with a faint yellow cast. The light paper is the background: the main subject is drawn directly on it, large and central, its surroundings sketched in around it and fading into the paper, leaving open margins; insets are small ruled boxes on the same paper, each a clearly different moment or detail. Flat even diagram lighting, a quiet nostalgic warmth. People are ordinary Lithuanians of 1981, anonymous types with correct natural proportions, each person a different individual: fair skin, ash-blond to light-brown hair, grey or blue-grey eyes, broad-cheeked oval faces, straight noses, calm closed mouths, austere and plainly handsome. Men side-parted or cropped, some moustached, working men in flat caps; women blond or light-brown-haired, the younger ones lean, with hair mostly straight, now and then faintly waved or neatly styled; older women in the usual range of everyday styles, plain, pinned back or set, occasionally curled, or under a cotton headscarf; clothes plain and loosely cut, in brown, olive, dusty blue, grey and dull red, chosen for the setting and occasion. Heads turn at varied natural angles: in a group most look at their task or at each other and one or two face the viewer, eyes just past the viewer's shoulder; of two main figures only one faces the viewer; a lone figure stands near-frontal, face turned only a little."
CONCEPT_LEAD_SCENE = "A printed page from a 1981 Lithuanian civil-defence training album, drawn and printed like the Soviet Grazhdanskaya Oborona wall charts of 1975-1985: dark-brown brush-and-ink outlines around every figure and object, dead-matte gouache fills with soft shading on every surface, four-colour offset with a faint coarse halftone, muted inks of dusty blue, olive, ochre, brick red and grey-brown on light aged cream paper with a faint yellow cast. The main scene fills its panel edge to edge as a complete, richly worked picture with its own sky, ground and background, the subject large and central in it, printed on the same light paper; insets are small ruled boxes beside or below it, each a clearly different moment or detail. Flat even diagram lighting, a quiet nostalgic warmth. People are ordinary Lithuanians of 1981, anonymous types with correct natural proportions, each person a different individual: fair skin, ash-blond to light-brown hair, grey or blue-grey eyes, broad-cheeked oval faces, straight noses, calm closed mouths, austere and plainly handsome. Men side-parted or cropped, some moustached, working men in flat caps; women blond or light-brown-haired, the younger ones lean, with hair mostly straight, now and then faintly waved or neatly styled; older women in the usual range of everyday styles, plain, pinned back or set, occasionally curled, or under a cotton headscarf; clothes plain and loosely cut, in brown, olive, dusty blue, grey and dull red, chosen for the setting and occasion. Heads turn at varied natural angles: in a group most look at their task or at each other and one or two face the viewer, eyes just past the viewer's shoulder; of two main figures only one faces the viewer; a lone figure stands near-frontal, face turned only a little."
STYLE_SUFFIX = 'Finish: dead-matte offset print on light aged cream paper with a faint yellow cast, brush-ink outlines, soft shading, correct proportions, flat tone on skin, hair, cloth and metal. One or two faces toward the viewer, eyes just past the shoulder; of two main figures only one. Every inset a clearly different moment, all in the same ruled frame. Diagram arrows and callouts in solid black ink.'
STYLE_SUFFIX_SCENE = 'Finish: a full, detailed scene in dead-matte offset print on light aged cream paper with a faint yellow cast, brush-ink outlines, soft shading, correct proportions, flat tone on skin, hair, cloth and metal. One or two faces toward the viewer, eyes just past the shoulder; of two main figures only one. Every inset a clearly different moment, all in the same ruled frame. Diagram arrows and callouts in solid black ink.'
LEADS = {"vignette": (CONCEPT_LEAD, STYLE_SUFFIX),
         "scene": (CONCEPT_LEAD_SCENE, STYLE_SUFFIX_SCENE)}

# The gpt-image-1.5 era lead (files 1.x, the 520 shipped masters). Kept for the
# record and for slicing old ledger prompts; not used for new renders.
LEGACY_CONCEPT_LEAD_1_5 = (
    "An illustration for a Lithuanian-language learning flashcard, in the style "
    "of a late Soviet instructional wall chart / civil-defense (Grazhdanskaya "
    "Oborona) training poster, circa 1975-1985. This is an educational technical "
    "wall chart, NOT propaganda and NOT a political poster: clean technical "
    "textbook illustration (between a botanical plate and an engineering manual), "
    "realistic proportions, clean outlines, muted printing colors, deadpan "
    "instructional calm, a structured grid layout with generous white space and "
    "an aged cream-paper offset-print feel. Where people appear they are "
    "ordinary Soviet-era Lithuanian people with neutral expressions and no "
    "heroic posing, in a period late-1970s setting."
)

# --- people & dress classes. F6.1 adds "formal" (church, weddings, occasions)
# and puts the red cross / pupils / smock into the professional class.
FIGURE_DRESS = {
    "worker": 'Any people who appear are working men and women in plain muted blue-grey work jackets and trousers, the men in flat cloth caps, with black kirza-style work boots.',
    "professional": 'Any people who appear are dressed for their profession and setting: a doctor or nurse in a white coat, with a small red cross on the medical kit or the clinic front; a teacher in a modest jacket or dress with pupils present at their desks; a shop assistant in a white smock; a uniformed officer in plain service uniform.',
    "civilian": 'Any people who appear are ordinary Lithuanian civilians in plain everyday clothes of 1981, dressed for the setting and the weather: shirts, cardigans, simple dresses and headscarves indoors and on the street; coats, caps and hats outdoors in cold weather.',
    "formal": 'Any people who appear are ordinary Lithuanians in their Sunday best for church, a wedding or a celebration: men in dark suits with a white shirt and tie, women in modest good dresses or skirts with a cardigan, a small hat or a fine headscarf, children neatly dressed.',
}
# guard against the model inventing a stray standing figure on object/place cards
NO_STRAY_FIGURE = ("Only include people the subject or scene actually calls for; "
                   "do not add an extra standing figure that is not needed.")

INSET_RULE = 'Include just 2 to 3 small supporting inset panels, all drawn in the same thin ruled frame on the same paper, each showing a clearly different moment, object or angle from the others and from the main picture. Keep them clean and uncluttered.'
# appended when a card supplies its own inset_note, so custom insets keep the
# same frame and stay distinct (F6 vestuves: one inset had an odd white frame)
INSET_FRAME_RULE = ("All insets are drawn in the same thin ruled frame on the "
                    "same paper, each showing a clearly different moment, object "
                    "or angle from the others and from the main picture.")
# F6.1: walking/running strips kept drawing the same foot forward twice
MOTION_STRIP_RULE = 'The motion strip shows one figure in three clearly different phases, left to right: first standing with both feet together and arms at the sides; second with the LEFT foot forward and the right arm swung forward; third with the RIGHT foot forward and the left arm swung forward. The three frames read as one continuous movement.'
# F6.1: ~20 % of F6 draws had a mechanical glitch (table in a doorway, a
# well-sweep with no well, a spoon behind its hook, a "dead" sleeping hare)
PLAUSIBILITY_RULE = 'Every object, tool and fixture is complete, attached and in working order: hanging things hang from a proper rack or hook, doorways and corridors stay clear and passable, furniture rests on the floor against a wall, tools are held in a usable grip, machines and vehicles are whole and correctly scaled to the people, and a resting animal is visibly alive and at ease, eyes closed and body relaxed.'
# F6.2 (2026-10-11, owner spot-check 09 + Fable): "this deck has a general
# highlight issue"; main picture must carry the word (gatve, mokykla, sokti read
# only through their insets); identical faces in groups; two main actors both
# looking at the camera.
MATTE_RULE = 'Every surface is dead-matte, as absorbent offset paper prints it: skin, hair, fabric, leather, metal, glass, water and polished wood carry flat ink tone and one soft shadow tone only.'
MAIN_MEANING_RULE = "The main picture alone makes this card's word obvious at a glance: the subject is the largest and most central element, shown in its most recognisable form and in the action that defines it, and the insets only add supporting detail."
DISTINCT_FACES_RULE = 'Every person in a group is a different individual, with a distinct face, age, build, hair and clothing colour.'
GAZE_PAIR_RULE = "Of two main figures, one faces the viewer with eyes resting just past the viewer's shoulder and the other looks at the task, at the first figure, or into the scene."
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


ARROW_RULE = 'Any arrow or callout, drawn in solid black ink, points only at the subject the card teaches or at the direction of its motion.'
# Spec 3.1.0 (owner 2026-10-19, "Yes, as drafted" — rounds/2026-10-19_fixes_round4/answers.md §4): the main actors move the way a
# page is read. Main figures only, never the background; new renders only (no card is re-rolled for it).
# Routing: direction_applies() below — on for motion-strip cards and stagings with a verb of motion; off for
# deck_builder.DIRECTION_FREE_ROWS (side/direction cards), two-panel situation_2 cards, and any staging that
# names a side itself in capitals (LEFT / RIGHT: the staging wins). QA: FIT_PROMPT "direction" (WARN only).
DIRECTION_RULE = "When the main figures walk, run, ride, drive or carry something from one place to another, they travel from the viewer's LEFT toward the RIGHT, the way a page is read; the place they are going to lies to the right of them. Figures who stand, sit or talk are not affected. This holds for the main figures only; people in the background go their own ways."
_MOTION_RE = re.compile(r"\b(walks?|walking|runs?|running|rides?|riding|drives?|driving|cycles|cycling|carrying|"
                        r"march(es|ing)?|hurr(ies|ying)|stroll(s|ing)?|jog(s|ging)?|travell?ing|"
                        r"cross(es|ing) (on|over|the|a)|heading (home|toward|towards|to|for|off|out))\b", re.I)
_SIDE_RE = re.compile(r"\b(LEFT|RIGHT)\b")          # capitals only: a staging that fixes sides itself


def direction_applies(text, motion_strip=False, panels=1):
    """True when DIRECTION_RULE is emitted for a card whose staging/subject is `text` (callers pass
    direction=False for deck_builder.DIRECTION_FREE_ROWS)."""
    if panels == 2 or _SIDE_RE.search(text or ""):
        return False
    return bool(motion_strip or _MOTION_RE.search(text or ""))


SETTING_GUARD = 'People stand inside the place: feet on its ground, scaled to its doors, furniture and vehicles, lit by the same flat light, with the setting continuing behind and between them. The setting stays behind and around the subject and never competes with it.'

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

# 1.7.1: the guessability gate, baked into the prompt so it holds at generation
# time instead of only at human QA. Applied whenever insets are present.
INSET_MEANING_RULE = (
    "Every inset must serve the meaning of THIS card: at best it should make the "
    "main subject easier to recognise; at the least it must stay attractive and "
    "on-theme. An inset must NEVER depict something that could be mistaken for a "
    "different, neighbouring subject, and must never compete with or pull "
    "attention away from what the card is teaching."
)

NO_CUTAWAY_RULE = (
    "Do NOT include internal anatomical cutaways or cross-sections of bodies — "
    "no organs, no digestive tracts, no bone interiors, no skin-layer diagrams, "
    "no udder or muscle interiors. Use external close-up details instead. "
    "(A simple sliced view of a fruit or plain object is fine.)"
)

ANATOMY_RULE = (
    "Render any human hands with clean, natural anatomy and exactly five "
    "fingers, and render animal paws, hooves and feet cleanly and correctly — "
    "no extra or malformed fingers or toes."
)

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

# 2026-10-18 historical places and figures (rounds/2026-10-17_historical/). Owner: "surroundings,
# but try faces as best you can". PRECEDENT_RULE carries a real Lithuanian thing or
# building by its features; LIKENESS_RULE, on listed cards only, asks for a named face
# at a named period. Both are additive segments: a card that passes neither renders
# exactly as before. Per-card values: historical.py (likeness_args.json).
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

# 0.9: flag-only, occasional. No intricate heraldry (it garbles like text did).
FLAG_RULE = (
    "If any national emblem is shown at all, use ONLY a small Lithuanian "
    "tricolor flag (a horizontal yellow band on top, green in the middle, red "
    "on the bottom), placed small and only where it fits naturally. Do NOT "
    "include coats of arms, the Vytis knight, the Columns of Gediminas, or any "
    "other heraldic emblem or badge. Do not put a flag on every card — many "
    "cards need no emblem at all."
)

# 1.7.4: flag variants for measurement cards (metric -> EU, imperial -> US+UK).
FLAG_RULE_EU = (
    "If any flags appear, use ONLY a small Lithuanian tricolor (yellow top, "
    "green middle, red bottom) together with a small European Union flag (a ring "
    "of twelve gold stars on a blue field), side by side. No coats of arms, no "
    "other emblems.")
FLAG_RULE_IMPERIAL = (
    "If any flags appear, use ONLY a small United States flag (stars and stripes) "
    "together with a small United Kingdom Union Jack, side by side. No coats of "
    "arms, no other national flags.")
# 2026-10-18: flag-first, no longer flag-only, on the routed cards only (FLAG_RULES["emblem"],
# deck_builder.FLAG_OVERRIDE). Owner: the Vytis is fine, the Cross of Vytis easier to draw and
# "leans patriotic". Heraldry garbled under gpt-image-1.5 (0.9); promote this text to the
# default FLAG_RULE only after the T4 (Cross) and T5 (Vytis) tests pass the owner's eye.
# Columns of Gediminas and every other badge stay out.
FLAG_RULE_EMBLEM = (
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
FLAG_RULES = {"eu": FLAG_RULE_EU, "imperial": FLAG_RULE_IMPERIAL, "emblem": FLAG_RULE_EMBLEM}

NO_TEXT_RULE = (
    "Render NO text, NO lettering, NO numbers, NO words, NO labels and NO "
    "captions anywhere in the image — no leader-line labels, no writing in any "
    "panel, on any flag, sign, or object, and none in the header or footer "
    "bands. Any area that would normally hold text must be left completely blank. "
    "This applies with full force inside speech bubbles and thought balloons: a "
    "bubble may contain a drawn picture or symbol, but never a written word, "
    "letter, or punctuation mark in any language."
)
# 2026-10-17 (RESTAGE_PROPOSAL §2(f)): the bubble-free "situation" cards. Used ONLY
# when generate(..., situation=True) — i.e. for the rows of data/restage_bubbles.csv
# (situations.py). Every other card keeps NO_TEXT_RULE above byte-for-byte. The
# situation variant drops the sentence that licensed pictures inside bubbles and adds
# one positive sentence: there are no bubbles at all.
NO_TEXT_RULE_SITUATION = (
    "Render NO text, NO lettering, NO numbers, NO words, NO labels and NO "
    "captions anywhere in the image — no leader-line labels, no writing in any "
    "panel, on any flag, sign, or object, and none in the header or footer "
    "bands. Any area that would normally hold text must be left completely blank."
)
NO_BUBBLE_RULE = ("No speech bubbles, thought bubbles or floating symbols of any kind; "
                  "meaning is carried by people, gestures, objects and setting.")
GLYPH_RULE = (
    "The ONLY lettering permitted is the one single large letter that is "
    "itself the subject of this card, drawn once as a bold display letterform. "
    "Render NO other text, lettering, numbers, words, labels or captions "
    "anywhere else in the image, and none in the header or footer bands."
)
def _exact_text_rule(spec, exclude=""):
    """1.7.7 text exception. A few cards are unteachable without a little
    lettering (unit marks on a ruler, ABC/123 on a blackboard, a price, a
    masthead, the vowel set). This permits EXACTLY the specified lettering and
    nothing else — the no-text rule still governs the rest of the card.

    1.9.0: the spec must be UNCONDITIONAL. Phrasing like "a question mark only
    if the phrase is a question" was silently ignored by the model, which drew
    the mark on all nine non-question cards. The caller decides; the prompt only
    ever states what to draw. The exclusion clause is also carried here — it
    previously reached the labelled branch only, so cards using a text exception
    had nothing stopping the target word from being written into the art."""
    segs = ["TEXT EXCEPTION for this card: the only lettering permitted "
            f"anywhere in the image is {spec} Draw it cleanly and correctly "
            "spelled in the muted period print style, large enough to read. "
            "Render NO other text, lettering, numbers, words, labels or "
            "captions anywhere else in the image — no leader-line labels, no "
            "writing on any other object, sign or flag — and none in the "
            "header or footer bands."]
    if exclude:
        segs.append(f"Absolutely never write the word \"{exclude}\", any part "
                    "of it, its translation, or any other Lithuanian or English "
                    "word anywhere in the image. Speech bubbles must stay free "
                    "of words in every language.")
    return " ".join(segs)


BARS_RULE = 'Frame the card with a plain solid deep, dark brick-red horizontal band across the very top and another across the very bottom, plus a thin band of the same dark red around the whole card. These bands are blank design elements and must contain no text whatsoever. Keep ALL illustration content — every figure, object, and inset panel — fully inside the inner frame; nothing may overlap, touch, or extend across the red header or footer bands.'


def _label_clause(labels, exclude=""):
    segs = []
    if labels:
        words = labels if isinstance(labels, str) else ", ".join(labels)
        segs.append("Annotate with thin leader lines labeling ONLY these "
                    f"supporting Lithuanian words, spelled exactly as given, and "
                    f"NO other text at all: {words}.")
    if exclude:
        segs.append(f"Never write the target word \"{exclude}\" or its "
                    "translation anywhere.")
    return " ".join(segs)


def _prompt_openai(subject, scene="", labels=None, exclude="", insets=True,
                   inset_note="", text=False, people="worker", extra="",
                   glyph=False, flag="lt", exact_text="", composition="vignette",
                   staging="", setting="", motion_strip=False, situation=False,
                   gaze="default", panels=1, precedent="", likeness="", direction=None):
    """F6.1 assembly order (production_spec_F6_1.json): lead, subject, per-card
    staging, class scene, setting, dress, inset rules, plausibility, arrows,
    text rules, bars, flag, anatomy, extra, suffix."""
    lead, suffix = LEADS.get(composition, LEADS["vignette"])
    conversation = bool(situation and gaze == "conversation")
    if conversation:
        lead, suffix = _conversation_lead(lead, suffix)
    segs = [lead, f"Subject: {subject}."]
    if staging:
        segs.append(staging)
    if scene:
        segs.append(scene)
    if setting:
        segs.append(setting)
        segs.append(SETTING_GUARD)
    if precedent:
        segs.append(PRECEDENT_RULE.format(description=precedent))
    if likeness:
        segs.append(likeness)          # already formatted LIKENESS_RULE text, one per figure
    segs.append(MAIN_MEANING_RULE)
    segs.append(FIGURE_DRESS.get(people, FIGURE_DRESS["worker"]))
    segs.append(DISTINCT_FACES_RULE)
    segs.append(CONVERSATION_GAZE_RULE if conversation else GAZE_PAIR_RULE)
    segs.append(NO_STRAY_FIGURE)
    if insets:
        segs.append(inset_note if inset_note else INSET_RULE)
        if inset_note:
            segs.append(INSET_FRAME_RULE)
        if motion_strip:
            segs.append(MOTION_STRIP_RULE)
        segs.append(INSET_MEANING_RULE)
        segs.append(NO_CUTAWAY_RULE)
    segs.append(PLAUSIBILITY_RULE)
    if insets or motion_strip or panels > 1:
        segs.append(PANEL_CONTINUITY_RULE)
    segs.append(MATTE_RULE)
    segs.append(ARROW_RULE)
    if direction is None:
        direction = direction_applies(f"{subject} {staging}", motion_strip, panels)
    if direction:
        segs.append(DIRECTION_RULE)
    if glyph:
        segs.append(GLYPH_RULE)
        segs.append(BARS_RULE)
    elif situation and exact_text:
        # declared object lettering (a sign, a clock face, a ticket) on a
        # bubble-free situation card; the target is never named (no exclude)
        segs.append(_exact_text_rule(exact_text))
        segs.append(NO_BUBBLE_RULE)
        segs.append(BARS_RULE)
    elif situation:
        segs.append(NO_TEXT_RULE_SITUATION)
        segs.append(NO_BUBBLE_RULE)
        segs.append(BARS_RULE)
    elif exact_text:
        segs.append(_exact_text_rule(exact_text, exclude))
        segs.append(BARS_RULE)
    elif text:
        lc = _label_clause(labels, exclude)
        if lc:
            segs.append(lc)
    else:
        # Wordless cards deliberately do NOT name the target word: naming a
        # forbidden thing primes it, and NO_TEXT_RULE already bans all lettering.
        # `exclude` therefore only reaches the branches that permit some text.
        segs.append(NO_TEXT_RULE)
        segs.append(BARS_RULE)
    segs.append(FLAG_RULES.get(flag, FLAG_RULE))
    segs.append(ANATOMY_PROPS_RULE if situation else ANATOMY_RULE)
    if extra:
        segs.append(extra)
    segs.append(suffix)
    return " ".join(segs)


# ===========================================================================
# DECOMPOSED encoding (backend="zimage") — text-incapable fallback
# ===========================================================================
_Z_LEAD_IN = ("1970s Soviet civil defense grazhdanskaya oborona instructional "
              "wall chart illustration of {SUBJECT}")
_Z_STYLE = (
    "clean technical textbook illustration with confident black outlines and "
    "flat matte shading, deadpan instructional calm, ordinary worker figures in "
    "plain muted blue-grey coveralls, soft flat cloth caps and black work boots, "
    "muted institutional palette of cream, blue-grey, olive, grey and brown, "
    "four-color offset print feel with faint halftone dots and aged paper "
    "texture, matte finish")
_Z_NEGATIVE = ("no readable text, no lettering, no captions, no watermark, no "
               "coats of arms or heraldic emblems, no anatomical cutaways, no "
               "glossy oil painting, no vibrant saturated color")
DEFAULT_OVERLAYS = ["a circular zoom-in detail inset"]
MOTION_ARROW = "a single bold directional arrow showing the direction of travel"


def _prompt_zimage(subject, scene="", overlays=None, extra=""):
    if overlays is None:
        overlays = DEFAULT_OVERLAYS
    parts = [_Z_LEAD_IN.format(SUBJECT=subject)]
    if scene:
        parts.append(scene)
    if overlays:
        parts.append("with diagrammatic overlays: " + ", ".join(overlays))
    parts.append(_Z_STYLE)
    if extra:
        parts.append(extra)
    parts.append(_Z_NEGATIVE)
    return ", ".join(parts)


def build_prompt(subject, scene="", labels=None, exclude="", insets=True,
                 inset_note="", text=False, people="worker", overlays=None,
                 glyph=False,
                 extra="", backend="openai", flag="lt", exact_text="",
                 composition="vignette", staging="", setting="",
                 motion_strip=False, situation=False, gaze="default", panels=1,
                 precedent="", likeness="", direction=None):
    if backend == "openai":
        return _prompt_openai(subject, scene, labels, exclude, insets,
                              inset_note, text, people, extra, glyph=glyph,
                              flag=flag, exact_text=exact_text,
                              composition=composition, staging=staging,
                              setting=setting, motion_strip=motion_strip,
                              situation=situation, gaze=gaze, panels=panels,
                              precedent=precedent, likeness=likeness,
                              direction=direction)
    return _prompt_zimage(subject, scene, overlays, extra)


OPENAI_SIZES = {"1:1": "1024x1024", "3:4": "1024x1536", "4:3": "1536x1024"}
# The engine's "4:3" has always meant the 1536x1024 landscape master (which is
# really 3:2). The Space offers that exact size, so the fallback now matches the
# masters pixel-for-pixel instead of silently producing portrait (2026-10-10).
ZIMAGE_RES   = {"1:1": "1024x1024 ( 1:1 )", "3:4": "864x1152 ( 3:4 )",
                "4:3": "1536x1024 ( 3:2 )"}

# Override per run with GO_IMAGE_MODEL. Default switched 2026-10-10 from
# gpt-image-1.5 (removed from the API 2026-12-01) to gpt-image-2 after a 10-card
# style probe the owner approved (_proto/gpt-image-2/compare_sheet.jpg). The 520
# shipped masters were drawn by gpt-image-1.5; new cards come from gpt-image-2.
# 2026-10-11: production model is Sunburst (owner blind spot-check 09: 19/30
# wins, 7/10 on scenes, fewer glitches, paper on target; 3.3x cheaper). One
# model for the whole deck. gpt-image-2 remains the fallback via GO_IMAGE_MODEL.
OPENAI_MODEL = os.environ.get("GO_IMAGE_MODEL", "gpt-image-2.5-sunburst")
OPENAI_QUALITY = "medium"
ZIMAGE_SPACE = "mcp-tools/Z-Image-Turbo"
ZIMAGE_STEPS = 8


# --- ledger provenance (spec 3.0.0, 2026-10-19) --------------------------------------
# Every render records the design-spec version and the style hash in force when it was drawn,
# so a picture can always be matched to the exact look that produced it (docs/DESIGN_SPEC_CURRENT.md
# §11, tools/style_lock.py). Computed once per process from the live code; never fatal.
LEDGER_BASE_COLUMNS = ["key", "subject", "seed", "backend", "size", "file", "prompt"]
LEDGER_STAMP_COLUMNS = ["spec_version", "style_hash"]
LEDGER_COLUMNS = LEDGER_BASE_COLUMNS + LEDGER_STAMP_COLUMNS
_STAMP = None


def style_stamp():
    """(spec_version, style_hash_short) of the live code, or ("", "") if the lock tooling is absent."""
    global _STAMP
    if _STAMP is None:
        try:
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # code/ -> the working directory
            tools = os.path.join(root, "tools")
            if tools not in sys.path:
                sys.path.insert(0, tools)
            import style_lock
            live = style_lock.fingerprint(style_lock.extract())
            _STAMP = (style_lock.spec_version(), live["style_hash_short"])
        except Exception as e:          # a render must never fail on provenance
            print(f"WARNING: style stamp unavailable ({type(e).__name__}: {e}); ledger rows get empty stamps")
            _STAMP = ("", "")
    return _STAMP


class _LedgerWriter:
    """csv.writer that appends spec_version and style_hash to any row of the seven base fields."""
    def __init__(self, raw):
        self.raw = raw

    def writerow(self, row):
        row = list(row)
        if len(row) == len(LEDGER_BASE_COLUMNS):
            row += list(style_stamp())
        return self.raw.writerow(row)

    def writerows(self, rows):
        for r in rows:
            self.writerow(r)


def _migrate_ledger(path):
    """Add the stamp columns to a pre-3.0.0 ledger header, padding old rows with empty cells.
    Existing columns and values are untouched; a ledger that already has them is left alone."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0][:len(LEDGER_BASE_COLUMNS)] != LEDGER_BASE_COLUMNS:
        return                                    # not a GO ledger; leave it
    if all(c in rows[0] for c in LEDGER_STAMP_COLUMNS):
        return
    rows[0] = rows[0] + [c for c in LEDGER_STAMP_COLUMNS if c not in rows[0]]
    width = len(rows[0])
    tmp = path + ".migrating"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r + [""] * (width - len(r)) if len(r) < width else r)
    os.replace(tmp, path)


class GOGenerator:
    def __init__(self, backend="openai", ratio="4:3", quality=OPENAI_QUALITY,
                 steps=ZIMAGE_STEPS, verbose=True):
        self.backend = backend
        self.ratio = ratio
        self.quality = quality
        self.steps = steps
        self.verbose = verbose
        if backend == "openai":
            from openai import OpenAI
            _key = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".openai_key.txt")
            if not os.environ.get("OPENAI_API_KEY") and os.path.exists(_key):
                os.environ["OPENAI_API_KEY"] = open(_key).read().strip()
            if not os.environ.get("OPENAI_API_KEY") and verbose:
                print("WARNING: no OPENAI_API_KEY in environment. See SETUP.")
            self._client = OpenAI()
            self.size = OPENAI_SIZES.get(ratio, "1536x1024")
        elif backend == "zimage":
            from gradio_client import Client
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            if token:
                import inspect
                params = inspect.signature(Client.__init__).parameters
                kw = "token" if "token" in params else "hf_token"
                self._client = Client(ZIMAGE_SPACE, **{kw: token})
            else:
                if verbose:
                    print("WARNING: no HF_TOKEN — anonymous quota throttles fast.")
                self._client = Client(ZIMAGE_SPACE)
            self.size = ZIMAGE_RES.get(ratio, "1536x1024 ( 3:2 )")
        else:
            raise ValueError(f"unknown backend: {backend}")

    def _gen_openai(self, prompt, dest, tries=5, wait=20):
        """Retry transient failures (rate limit / timeout / 5xx) with
        exponential backoff; anything else (auth, content policy) fails fast."""
        for i in range(tries):
            try:
                resp = self._client.images.generate(
                    model=OPENAI_MODEL, prompt=prompt, size=self.size,
                    quality=self.quality, n=1)
                with open(dest, "wb") as fh:
                    fh.write(base64.b64decode(resp.data[0].b64_json))
                return None
            except Exception as e:
                name = type(e).__name__
                transient = (any(k in name for k in
                                 ("RateLimit", "Timeout", "APIConnection",
                                  "InternalServer", "APIStatus"))
                             or any(c in str(e) for c in ("429", "500", "502",
                                                          "503", "504")))
                if transient and i < tries - 1:
                    delay = wait * (2 ** i)
                    if self.verbose:
                        print(f"   transient {name}, retrying in {delay}s "
                              f"({i+1}/{tries})")
                    time.sleep(delay)
                else:
                    raise

    def _gen_zimage(self, prompt, dest, tries=6, wait=45):
        from gradio_client.exceptions import AppError
        for i in range(tries):
            try:
                result, seed_msg = self._client.predict(
                    prompt=prompt, resolution=self.size, steps=self.steps,
                    random_seed=True, api_name="/generate")
                shutil.copy(result, dest)
                return "".join(c for c in str(seed_msg) if c.isdigit())
            except AppError as e:
                if "quota" in str(e).lower() and i < tries - 1:
                    if self.verbose:
                        print(f"   quota hit, waiting {wait}s ({i+1}/{tries})")
                    time.sleep(wait)
                else:
                    raise
        raise RuntimeError("retries exhausted")

    def generate(self, subject, scene="", labels=None, exclude="", insets=True,
                 inset_note="", text=False, people="worker", overlays=None,
                 glyph=False,
                 extra="", out_dir=".", filename=None, flag="lt", exact_text="",
                 composition="vignette", staging="", setting="",
                 motion_strip=False, situation=False, gaze="default", panels=1,
                 precedent="", likeness="", direction=None):
        prompt = build_prompt(subject, scene=scene, labels=labels,
                              exclude=exclude, insets=insets, inset_note=inset_note,
                              text=text, people=people, overlays=overlays,
                              glyph=glyph, extra=extra, backend=self.backend,
                              flag=flag, exact_text=exact_text,
                              composition=composition, staging=staging,
                              setting=setting, motion_strip=motion_strip,
                              situation=situation, gaze=gaze, panels=panels,
                              precedent=precedent, likeness=likeness,
                              direction=direction)
        os.makedirs(out_dir, exist_ok=True)
        if filename is None:
            filename = "go_" + hashlib.md5(subject.encode()).hexdigest()[:8] + ".png"
        dest = os.path.join(out_dir, filename)
        seed = (self._gen_openai(prompt, dest) if self.backend == "openai"
                else self._gen_zimage(prompt, dest))
        if self.verbose:
            print(f"OK  {filename}  seed={seed or 'n/a'}")
        return dest, seed, prompt

    @property
    def engine_tag(self):
        """Backend plus model, for the ledger's backend column, so each card
        records which model drew it (1.5 masters vs gpt-image-2 additions)."""
        return f"openai/{OPENAI_MODEL}" if self.backend == "openai" else self.backend

    @staticmethod
    def open_ledger(path):
        """Append-mode ledger. Columns: key, subject, seed, backend, size, file, prompt, and since
        spec 3.0.0 (2026-10-19) spec_version and style_hash, filled in by the writer for every row
        that carries the seven base fields (callers are unchanged). A ledger made before 3.0.0 is
        migrated once: the two columns are added to its header and left empty on the old rows."""
        new = not os.path.exists(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not new:
            _migrate_ledger(path)
        f = open(path, "a", newline="", encoding="utf-8")
        w = _LedgerWriter(csv.writer(f))
        if new:
            w.raw.writerow(LEDGER_COLUMNS)
        return f, w

    @staticmethod
    def open_cards(path):
        new = not os.path.exists(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        f = open(path, "a", newline="", encoding="utf-8")
        w = csv.writer(f)
        if new:
            w.writerow(["key", "lithuanian", "english", "lt_pron", "gender",
                        "number", "category", "image_file"])
        return f, w


def _cli():
    p = argparse.ArgumentParser(description="Grazhdanskaya Oborona Generator")
    p.add_argument("subject")
    p.add_argument("--backend", default="openai", choices=["openai", "zimage"])
    p.add_argument("--scene", default="")
    p.add_argument("--ratio", default="4:3")
    p.add_argument("--text", action="store_true", help="bake text (default off)")
    p.add_argument("--out", default="./go_out")
    a = p.parse_args()
    gen = GOGenerator(backend=a.backend, ratio=a.ratio)
    dest, seed, prompt = gen.generate(a.subject, scene=a.scene, text=a.text,
                                      out_dir=a.out)
    f, w = GOGenerator.open_ledger(os.path.join(a.out, "ledger.csv"))
    w.writerow(["cli", a.subject, seed, gen.engine_tag, gen.size,
                os.path.basename(dest), prompt]); f.close()
    print(f"\nsaved -> {dest}")


if __name__ == "__main__":
    _cli()
