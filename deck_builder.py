#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deck builder (files 1.7.1) — the wordlist-driven production runner.

1.7.1: tool/industry worker rows. With go_grammars 1.7.1 making CIVILIAN the
default noun-inset dress, the few rows whose insets genuinely belong to workers
are pinned back to "worker" here via a per-row people override: #21 variklis
(engine), #195 tepalas (machine oil), #245 įrankis (tool). Editable seed list —
extend as later tool/industrial rows are reviewed. Materials cards get worker
dress by category (go_grammars.PEOPLE_CLASS), so they need no per-row entry.

1.7 (the guessability pass, owner QA of cards 1-127): NOUN_STAGING gives
nouns the same per-row staging verbs already had (main-clause override,
dress class, card-specific insets); OVERRIDE_CLASS re-routes 51/56/101 to
attribute, 52 to chart, 53 to nature; population follows the place
(go_grammars 1.7: Location defaults to civilians, place cards show their
characteristic occupants, person cards say "role" not "working role").
QA gate added to the spec: the target word must be inferable from the main
image alone, and insets must support it — not vote for a neighbouring word.

1.6.1: the 8 open design decisions are IN (see GO_STYLE_SPEC ledger). PENDING
is now empty; glyph rows 227/350/351 generate via the engine's single-glyph
exception; rows 137 (wedding) and 379 (die: gravestone) are phrase-complete
and routed "attribute"; superseded color duplicates 518-527 are excluded by
the wordlist itself (depictable=superseded).

This is the file Cowork drives. It reads master_wordlist.csv and generates the
whole picture deck (or any slice of it) through the frozen GO pipeline:

  nouns        -> go_grammars visual grammars (per category)
  adjectives   -> "attribute" class: marked-contrast scene, no insets
  category-C   -> "chart" class: specimen chart, no insets
  verbs        -> context C default / D accent, staged per-verb (VERB_STAGING)

Fixes carried from the 1.5.1 audit:
  - collision-proof keys: {row#}_{ascii-slug} (eiti x2, sokti x2, peda x2,
    vyras x2, zeme x2, senas x2 would otherwise overwrite each other)
  - card numbers come from the wordlist '#' column (no BASE_NUMBER)
  - cards.csv now carries lt_pron + gender for the Anki layer
  - --only for the QA re-roll pass; --category for block-by-block production
  - rows pending a design decision are SKIPPED by default (see PENDING)

Run:
  export OPENAI_API_KEY=sk-...
  python deck_builder.py --dry-run                 # plan + prompts, no API
  python deck_builder.py --trial 6                 # first 6 eligible rows
  python deck_builder.py --category Animal         # one category block
  python deck_builder.py --only 001_suo,113_gydytojas   # re-roll pass
  python deck_builder.py                           # the full deck
"""
from __future__ import annotations
import os, csv, sys, argparse, unicodedata

from go_generator import GOGenerator
from go_grammars import route, compose_class, SCENE_TAIL
from verb_flashcards import scene_for, inset_for

WORDLIST = "master_wordlist.csv"
OUT_DIR = "./out_deck"
RATIO = "4:3"

# ---------------------------------------------------------------------------
# Rows awaiting an owner design decision (see STAGING_files_2_1.md §5).
# Generating them would burn credits on cards that may change. Override with
# --include-pending once decided, or delete entries here.
# ---------------------------------------------------------------------------
PENDING = {}   # all design questions resolved at 1.6.1

# rows whose composition is complete in the phrase itself (no class grammar,
# no motion insets): wedding scene, gravestone; 1.7 adds guessability
# re-routes — 51 šalis (map, phrase-complete), 56 vieta (pointing hand on
# map), 101 vaikas (age-row + arrow), 52 pastatas (specimen chart of
# building types), 53 žemė (soil is nature, not architecture).
OVERRIDE_CLASS = {137: "attribute", 379: "attribute",
                  227: "attribute", 350: "attribute", 351: "attribute",
                  51: "attribute", 56: "attribute", 101: "attribute",
                  52: "chart", 53: "nature"}

# ---------------------------------------------------------------------------
# 1.7 — per-row noun staging (the guessability pass, Dainius QA of cards
# 1-127). Same idea as VERB_STAGING but for nouns: row# -> overrides applied
# AFTER compose_class. Keys: "main" (replaces the class main clause; the
# frozen SCENE_TAIL framing is re-appended), "people" (dress class),
# "inset_note" (replaces the class inset menu with card-specific insets).
# Insets must SUPPORT the target word or at least not vote for a wrong one.
# ---------------------------------------------------------------------------
NOUN_STAGING = {
    # sparnas: creature grammar forces a full-body bird; the word is WING.
    9: {"main": ("Draw the single outstretched wing alone, detached and "
                 "diagram-like, its feather groups clearly drawn."),
        "inset_note": ("Include 2 small supporting insets: a bird in flight "
                       "with both wings spread; a close-up of the feather "
                       "structure.")},
    # bilietas: a blank slip is unguessable — tell the ticket's story.
    22: {"people": "civilian",
         "inset_note": ("Include 3 small supporting insets telling one "
                        "sequence: a conductor handing the ticket to a "
                        "passenger; the conductor punching the ticket; the "
                        "passenger boarding the train, ticket in hand.")},
    # miestas: no basement workers — city is streets, crowds, traffic.
    24: {"inset_note": ("Include 2 small supporting insets: a rooftop "
                        "skyline of the city; a busy pedestrian crossing "
                        "with civilians and cars.")},
    32: {"inset_note": ("Include 2 to 3 small supporting insets: a tidy "
                        "hotel room with two made-up beds ready for guests; "
                        "the reception desk with a wall rack of room keys; "
                        "a guest's suitcase.")},
    # ūkis: the one Location row that genuinely belongs to workers.
    34: {"people": "worker"},
    35: {"inset_note": ("Include 2 to 3 small supporting insets: a close-up "
                        "of the wooden gavel; the courthouse facade; the "
                        "scales of justice.")},
    36: {"inset_note": ("Include 2 to 3 small supporting insets: a classroom "
                        "with a woman teacher at a chalkboard and children "
                        "at desks; children playing in the schoolyard.")},
    # miestelis: two straight rolls made the church the subject (church-door
    # and church-interior insets voting "bažnyčia"); force town-life insets.
    39: {"inset_note": ("Include 2 small supporting insets: a row of low "
                        "wooden houses along a dirt road; a small wooden "
                        "kiosk with a queue of townspeople.")},
    40: {"inset_note": ("Include 2 small supporting insets: a lecture hall "
                        "with rows of young adult students; a library "
                        "reading room.")},
    41: {"inset_note": ("Include 2 small supporting insets: the club "
                        "entrance at night with young people arriving; a "
                        "record player with musical notes in the air.")},
    43: {"inset_note": ("Include 2 to 3 small supporting insets: a "
                        "children's playground with a slide and swings; a "
                        "bench under a tree; a flowerbed.")},
    48: {"people": "professional",
         "inset_note": ("Include 2 to 3 small supporting insets: a "
                        "white-coated doctor and nurse at a patient's "
                        "bedside; a nurse pushing a wheelchair; a plain red "
                        "cross on a white circle.")},
    55: {"inset_note": ("Include 2 to 3 small supporting insets: a teller "
                        "counting banknotes at a counter window; a neat "
                        "stack of banknotes and coins; a strongbox safe.")},
    # vyras/žmona (married): the rings carry the meaning.
    93: {"inset_note": ("Include 2 small supporting insets: a close-up of "
                        "the couple's clasped hands with wedding rings; the "
                        "couple exchanging rings before a registry "
                        "official.")},
    94: {"inset_note": ("Include 2 small supporting insets: a close-up of "
                        "the couple's clasped hands with wedding rings; the "
                        "couple exchanging rings before a registry "
                        "official.")},
    # prezidentas: the person-grammar "characteristic object" inset keeps
    # pulling a judge's gavel (twice in a row) — force state-leader insets.
    97: {"inset_note": ("Include 2 small supporting insets: the president "
                        "signing a document at a large desk with the "
                        "tricolor on a stand behind; the president waving "
                        "to a crowd from a podium draped with the "
                        "tricolor.")},
    # sirgalius: insets must be SPORT, not markets.
    107: {"inset_note": ("Include 2 small supporting insets: the football "
                         "match seen from the stands; a waved knitted scarf "
                         "and a small plain two-colour pennant.")},
    # pacientas: the person-grammar "role" clause still needs forcing here —
    # patients REST and RECEIVE care. Dress professional so carers get
    # white coats; the main clause dresses the patients themselves.
    114: {"main": ("Draw them as patients at rest in neighbouring hospital "
                   "beds, in plain pyjamas or hospital gowns with blankets "
                   "over them — resting and receiving care, not working."),
          "people": "professional",
          "inset_note": ("Include 2 to 3 small supporting insets: a bedside "
                         "table with medicine bottles and a thermometer; a "
                         "white-coated doctor checking a patient's pulse; a "
                         "patient carried on a stretcher toward an "
                         "ambulance.")},
    # vestuvės: wedding guests are not coverall workers (moved from
    # the 1.6.1 special case in build_call).
    137: {"people": "civilian"},
    # tepalas: machine oil filed under Food — the food-class canteen inset
    # votes "cooking oil" (aliejus is the very next card). Machine-only.
    # 1.7.1: tool/industry — carers here are mechanics, so dress worker.
    195: {"people": "worker",
          "inset_note": ("Include 2 small supporting insets: a close-up of "
                         "the oil can's spout releasing a single drop onto "
                         "gear teeth; a mechanic's hand wiping an oily "
                         "machine part with a rag.")},
    # gėrimas: chart card kept sprouting a standing worker pair as a fourth
    # "exemplar" (twice in a row) — exclude people explicitly.
    179: {"main": ("Compose the card as a calm specimen chart of the drinks "
                   "only: the named drinks arranged in an even row, each "
                   "drawn clean and complete. No people anywhere on the "
                   "card.")},
    # maistas: same chart-card people intrusion as 179 — a worker pair took
    # the fourth grid cell. Foods only.
    208: {"main": ("Compose the card as a calm specimen chart of the foods "
                   "only: the named foods arranged in an even grid, each "
                   "drawn clean and complete. No people anywhere on the "
                   "card.")},
    # 1.7.1 tool/industry worker rows: with civilian now the noun-inset
    # default, these few belong to workers. Any figure is a mechanic/fitter in
    # coveralls, not a civilian. Extend this group as later tools are reviewed.
    21:  {"people": "worker"},   # variklis (engine)
    245: {"people": "worker"},   # įrankis (tool)
    # 1.7.1 QA fixes (from the 1.7.1 validation sample):
    # lubos: the phrase's "hanging lamp" made the LAMP the subject and every
    # inset voted lamp/light. Force the ceiling plane as subject; architectural
    # insets only, no lamp. (Paired with wordlist 2.4 phrase rewrite.)
    232: {"main": ("Draw the room's ceiling itself as the clear subject, seen "
                   "from below at a slight angle so the flat plastered ceiling "
                   "plane, its cornice moulding, and the corners where the walls "
                   "meet it are all visible; one bold arrow points up at the "
                   "ceiling surface. A hanging lamp, if shown at all, is tiny and "
                   "incidental — never the subject."),
          "inset_note": ("Include 2 to 3 small supporting insets: a close-up of "
                         "the decorative cornice moulding running along the top "
                         "of a wall; the upper corner of a room where two walls "
                         "meet the ceiling; a wide view of a room interior with "
                         "the ceiling prominent overhead.")},
    # padanga: the vehicle grammar's "wheel, the engine, or a fitting" inset
    # produced an engine-bay panel voting "engine". Pin tire-only insets.
    19:  {"inset_note": ("Include 2 to 3 small supporting insets: a close-up of "
                         "the tire's tread pattern; a stack of several road "
                         "tires; a person fitting or changing a tire onto a car "
                         "wheel.")},
    # kiemas: "yard with a fence" made the GATE the subject and the insets were
    # all gate latches -> blind-reads as "gate". Force the enclosed yard SPACE
    # and its everyday use; yard-life insets, never a gate latch.
    238: {"main": ("Draw the enclosed household yard itself as the subject, seen "
                   "from inside the fence: the open swept ground behind the house "
                   "is the dominant space, with everyday yard things in it — a "
                   "stacked woodpile, a wooden bench, a clothesline with laundry, "
                   "a few chickens. The house wall and a low fence only frame the "
                   "yard; a gate is NOT the subject and need not appear."),
          "inset_note": ("Include 2 to 3 small supporting insets: a corner of the "
                         "yard with a stacked woodpile and an axe in a chopping "
                         "block; laundry drying on a line strung across the yard; "
                         "a person sweeping the yard ground with a besom broom.")},
    # kunas: generic "body" tripped output moderation ("sexual") — likely a nude.
    # Force a clothed, clinical whole-body anatomy-chart figure.
    288: {"main": ("Draw a whole-body anatomy lesson: a person standing front-on "
                   "in a plain modest grey full-body jumpsuit that covers the "
                   "torso and limbs, while a doctor in a white coat stands beside "
                   "them pointing at different parts of the body (head, arm, "
                   "torso, leg) as on a teaching chart. Modest, non-sexual, "
                   "clinical."),
          "people": "professional",
          "inset_note": ("Include 2 supporting insets: the doctor pointing at "
                         "the jumpsuited figure's arm; the same figure shown from "
                         "the back.")},
    # ---- 1.7.2 QA round 2: body-part clarity fixes ----
    # plaukai: was reading as "comb". Make HAIR the subject; comb incidental.
    262: {"main": ("Draw a clear study of a person's HAIR itself — a head shown "
                   "so the hair (its length, texture and the way it is combed) "
                   "fills the focus. A comb may appear small and incidental but "
                   "the hair is unmistakably the subject, not the comb."),
          "inset_note": ("Include 2 small supporting insets: a close-up of the "
                         "hair strands and parting; a person at a mirror smoothing "
                         "their hair with a hand.")},
    # nugara: bare back -> clothed back.
    271: {"main": ("Draw a person's BACK, seen from behind, CLOTHED in an "
                   "ordinary shirt or blouse; one bold arrow points to the middle "
                   "of the back. No bare skin."),
          "inset_note": ("Include 2 small supporting insets: a clothed figure "
                         "from behind with the whole back indicated; a hand "
                         "pressed to the small of a clothed back.")},
    # kojos pirstas: "ghost foot" -> a solid, correctly drawn foot.
    272: {"main": ("Draw one clean, solid, correctly-proportioned bare foot in "
                   "side-and-top view with all five toes clearly separated; one "
                   "bold arrow points specifically at the big TOE. Natural "
                   "anatomy, no missing or faded parts."),
          "inset_note": ("Include 2 small supporting insets: a close-up of the "
                         "toes; a foot in an open sandal with the toes visible.")},
    # petys: was a bare real back -> shoulder on a clothed/jumpsuit figure.
    278: {"main": ("Draw the SHOULDER on a CLOTHED figure (plain shirt or grey "
                   "jumpsuit), the join of arm and torso clearly shown from the "
                   "front-side; one bold arrow points at the shoulder. No bare "
                   "skin."),
          "people": "professional"},
    # kelis: was strange / low detail -> a clear knee.
    282: {"main": ("Draw a clear, well-detailed study of a bent KNEE on a "
                   "trousered leg, side view, the kneecap and the bend of the "
                   "joint clearly rendered; one bold arrow points at the knee."),
          "inset_note": ("Include 2 small supporting insets: a close-up of the "
                         "kneecap; a person kneeling on one knee.")},
    # oda: replace the odd saw inset with a mosquito biting skin.
    287: {"inset_note": ("Include 2 to 3 small supporting insets: a close-up "
                         "cross-section of skin layers; a mosquito biting and "
                         "piercing a patch of bare skin; a hand feeling the skin "
                         "of a forearm.")},
    # vejas: wind arrows must blow the SAME way the trees and scarf bend.
    303: {"main": ("Draw trees and grass bent hard to the RIGHT by strong WIND, "
                   "a scarf streaming to the RIGHT; the wind-direction arrows and "
                   "all the dashed motion lines point to the RIGHT, the SAME way "
                   "everything is bending — never against it."),
          "inset_note": ("Include 2 small supporting insets: a flag streaming "
                         "straight out in the wind; leaves blown along the "
                         "ground — all in the same rightward direction.")},
    # slenis: read as "river". Foreground the VALLEY landform itself.
    306: {"main": ("Draw a broad VALLEY as a landform: two hillsides or ridges "
                   "sloping down on the left and right to meet at a low green "
                   "valley floor between them, seen from an elevated viewpoint "
                   "looking along the valley. Any stream is small and incidental; "
                   "the bowl-shaped valley between the hills is the subject."),
          "inset_note": ("Include 2 small supporting insets: a cross-section "
                         "diagram of a V-shaped valley between two hills; a wide "
                         "grassy valley floor with grazing meadows.")},
    # suzalojimas: sling alone read as "break". Show varied wounds/injuries.
    358: {"inset_note": ("Include 3 small supporting insets showing DIFFERENT "
                         "kinds of injury so the general idea reads: a grazed "
                         "bandaged knee; a bruised arm; a sticking-plaster over a "
                         "small cut on a hand.")},
    # spyna: output-moderation false-positive ("illicit") on the plain padlock.
    # Steer hard to benign hardware — no picking, no forcing, no hands on it.
    235: {"main": ("Draw a single ordinary closed brass padlock resting beside "
                   "its own key on a plain surface, as a calm hardware-catalogue "
                   "illustration — the shackle is shut and intact."),
          "inset_note": ("Include 2 small supporting insets: a clean close-up of "
                         "the keyhole and the shut shackle; the padlock hung on a "
                         "simple wooden gate hasp, closed.")},
}

# rows generated with the engine's single-glyph exception (decision Q2)
GLYPH_ROWS = {227, 350, 351}

# ---------------------------------------------------------------------------
# Per-verb staging: row# -> (people, setting, arrow, emphasis, consequence).
# Design source: STAGING_files_2_1.md §4 (telicity -> D panel) and the locked
# verb treatment (context C default). The nine 1.5-validated demo verbs keep
# their exact staging. A non-empty consequence == a D-accent card.
# ---------------------------------------------------------------------------
W, P, C = "worker", "professional", "civilian"
VERB_STAGING = {
    363: (W, "a workshop with a workbench", "", "", ""),
    364: (C, "a courtyard with simple play equipment", "", "", ""),
    365: (C, "a small club stage or rehearsal room", "", "", ""),
    366: (W, "a long institutional corridor, the figure walking to the right",
          "one bold arrow pointing to the RIGHT, the exact way the figure faces "
          "and steps (arrow and motion the same direction)", "", ""),
    367: (W, "a plain institutional courtyard or street, the figure running to "
          "the right",
          "one bold arrow pointing to the RIGHT, the exact way the figure faces "
          "and runs (arrow and motion the same direction)", "", ""),
    368: (W, "a road, the truck cab seen from the side",
          "one bold arrow showing the forward direction of travel", "", ""),
    369: (W, "the open sky above fields",
          "one bold arrow showing the forward direction of flight", "", ""),
    370: (C, "a swimming-pool lane",
          "one bold arrow showing the forward direction of swimming", "", ""),
    371: (C, "a home doorway, a packed travel bag in hand, a bus waiting at the "
          "kerb beyond",
          "one bold arrow leading out through the doorway toward the bus",
          "Emphasise LEAVING on a journey: the person steps out of the door with "
          "their bag to set off and depart — clearly going away, not strolling.",
          "the person boarding the waiting bus"),
    372: (W, "a street crossing", "",
          "The figure has STOPPED and stands still, one hand raised palm-out in "
          "the STOP gesture, the other hand holding up a round red stop sign.",
          ""),
    373: (W, "a plain corridor or street, THREE figures walking in single file "
          "one behind another with a clear gap between each, each following the "
          "one ahead",
          "a dashed path line linking the three figures in order", "", ""),
    375: (W, "an office or corridor", "", "", ""),
    376: (W, "a plain workers' canteen with long tables and others eating in "
          "the background", "", "", ""),
    377: (W, "a workers' canteen or rest area with a water station", "", "", ""),
    378: (C, "a kitchen corner", "", "", "the swatted fly lying still"),
    380: (C, "a plain portrait setting", "", "", ""),
    381: (C, "a canteen table", "", "", ""),
    382: (C, "a plain room", "", "", ""),
    383: (C, "a shop counter, the customer handing banknotes to the clerk with "
          "one hand and receiving the wrapped goods with the other, at the same "
          "time",
          "two arrows at once: money going from customer to clerk, wrapped goods "
          "coming back from clerk to customer",
          "Emphasise the EXCHANGE: money out, purchase in — buying.",
          "the customer carrying the wrapped purchase away"),
    384: (C, "a shop counter or cashier's window",
          "one bold arrow on the banknotes passing from customer to clerk",
          "", ""),
    385: (W, "a small shop counter seen from the clerk's side",
          "two small arrows: goods outward to the customer, coins inward to "
          "the clerk", "", "the till drawer with coins"),
    386: (W, "an indoor shooting range", "", "",
          "the paper target with bullet holes"),
    388: (W, "a training yard with a low obstacle",
          "one bold arcing arrow showing the up-and-over jump", "", ""),
    389: (C, "a market flower stall", "", "", ""),
    390: (W, "a workshop with an alarm bell on the far wall", "",
          "Emphasise INVOLUNTARY hearing: the sound arrives and the head "
          "turns toward it.", ""),
    391: (C, "a sitting room with a tabletop radio", "",
          "Emphasise DELIBERATE listening: seated, attentive, ear inclined "
          "to the radio.", ""),
    392: (P, "a canteen kitchen at a soup pot", "", "", ""),
    393: (W, "a plain table", "", "", ""),
    394: (W, "an open field with a distant water tower",
          "a thin dotted sight line from the eye to the distant object", "", ""),
    395: (C, "a sitting room with a television set", "",
          "Emphasise DELIBERATE watching: seated squarely before the screen.",
          ""),
    396: (C, "a doorstep farewell", "", "", ""),
    397: (W, "a fire-safety training yard, at a safe distance", "", "",
          "the plank burnt down to char and embers"),
    398: (W, "a kitchen table", "", "", "the ice reduced to a puddle of water"),
    399: (W, "an open trench line with marker stakes", "", "",
          "the finished straight trench"),
    400: (W, "a demolition training ground with workers behind a barrier",
          "", "", "the cleared rubble after the blast"),
    401: (C, "a plain room with a chair",
          "an arc arrow showing the person lowering down onto the chair",
          "Emphasise SITTING DOWN: an elderly person is in the act of taking a "
          "seat, lowering themselves onto the chair — settling into sitting, "
          "not tying a shoe.", ""),
    402: (W, "a corridor or muster line", "", "", ""),
    404: (C, "a street with a kiosk, the walker shown mid-stride having gone "
          "PAST the kiosk, which is now behind them",
          "a dashed path line running up to the kiosk, alongside it, and "
          "continuing on beyond it, with an arrowhead pointing onward",
          "Emphasise PASSING BY: the person walks past the kiosk and carries on "
          "— the kiosk is a landmark left behind, not a destination.", ""),
    405: (W, "a workshop sawhorse", "", "", "the board cut into two pieces"),
    406: (C, "a boxing ring in a plain gymnasium", "", "", ""),
    407: (W, "a rest room with a cot", "",
          "The figure is AWAKE with open eyes — lying down, not sleeping.", ""),
    408: (C, "a social hall with seated onlookers", "",
          "Emphasise DANCING to music: a couple in dance hold, simple musical "
          "notes in the air — dancing, not jumping.", ""),
    409: (W, "a plain barracks or dormitory bunk room", "", "", ""),
    410: (W, "a dormitory bed at morning with sun through the window", "", "",
          "the worker upright and dressed"),
    411: (C, "a small stage or campfire circle", "", "", ""),
    412: (W, "a stockroom desk with crates", "", "", ""),
    413: (C, "a registry office with an official at a desk", "", "",
          "the couple's joined hands with wedding rings"),
    417: (W, "a construction yard mortar trough",
          "a circular motion arrow over the mixing", "", ""),
    418: (W, "a metal workshop with a vise",
          "a curved arrow following the bend", "",
          "the rod bent to a right angle"),
    419: (W, "a tiled factory or institutional washroom", "", "", ""),
    420: (P, "a canteen kitchen stove", "", "", ""),
    421: (W, "a plain interior door",
          "an arc arrow showing the door swinging open", "",
          "the door standing open"),
    422: (W, "a plain interior door",
          "an arc arrow showing the door swinging shut", "",
          "the door closed"),
    423: (W, "an office desk with paper and pen", "", "", ""),
    424: (W, "an office with a rotary telephone", "", "", ""),
    425: (W, "a boiler room with a large pipe valve",
          "a circular arrow around the turning wheel", "", ""),
    426: (W, "a workshop or construction site with a workbench", "", "",
          "the finished assembled wooden structure or frame"),
    428: (W, "a garden bed",
          "one bold upward arrow beside the growth stages", "",
          "the plant fully grown"),
    429: (C, "a desk with paper", "", "", ""),
    430: (C, "a home interior", "",
          "Emphasise FEEDING A PERSON: a mother spoon-feeding porridge to a baby "
          "in a high chair (maitinti is feeding people, not animals). The baby "
          "opens its mouth for the spoon.", ""),
    431: (W, "a loading yard", "", "",
          "the sack held safely in both arms"),
    432: (W, "a loading yard with a pile of sacks",
          "an arcing arrow tracing the throw", "",
          "the sack landed on the pile"),
    433: (W, "an institutional corridor, one half already clean, the worker "
          "WET-MOPPING the floor with a mop and bucket (not a broom)", "",
          "Emphasise cleaning by wet-mopping and wiping — not sweeping.",
          "the corridor fully clean and gleaming"),
    434: (C, "a garden or yard where children are playing hide-and-seek", "",
          "Emphasise FINDING: a child who was seeking has just discovered "
          "another child hiding behind a tree or fence, pointing at them with a "
          "delighted look — the moment of finding.", ""),
    435: (C, "a kitchen table, a drinking glass caught in mid-air as it falls "
          "off the table edge toward the floor. NO person in the main scene — "
          "the glass falls on its own",
          "one bold downward arrow tracing the glass's fall from table to floor",
          "", "the glass shattered on the floor"),
    436: (W, "a warehouse aisle",
          "one bold arrow showing the forward push", "", ""),
    437: (W, "a yard with a rope-hauled cart",
          "one bold arrow showing the pull toward the worker", "", ""),
    438: (W, "a supply depot or storeroom hall with tall shelves of crates "
          "and a few workers in the background", "",
          "Emphasise horizontal transport: the worker walks and carries the "
          "crate across a distance, holding it steady — this is CARRYING, "
          "not lifting.",
          "a cargo truck being loaded with the carried crates"),
    439: (W, "a firewood yard", "", "", "the stick broken into two pieces"),
    440: (C, "a bedroom by a wardrobe, a person in the act of putting ON and "
          "wearing outdoor clothes — arms going into the sleeves of a buttoned "
          "coat, a scarf already round the neck, a cap on the head",
          "", "Emphasise WEARING clothes: the garments are worn on the body and "
          "the person is dressing in them — this is WEAR, not any workshop task.",
          ""),
    441: (W, "a plain room wall with a hook", "", "",
          "the framed picture hanging level on the wall"),
    442: (W, "an orchard beneath an apple tree", "", "",
          "the fallen apples gathered on the ground"),
    443: (W, "an office desk with a document", "", "",
          "the document bearing a plain scribbled signature mark"),
    444: (C, "a yard with a rug on a beating rack", "", "", ""),
    445: (W, "a supply depot or storeroom with tall shelves of crates",
          "one bold UPWARD arrow showing the crate being raised straight up",
          "Emphasise the vertical upward lift: the worker raises the crate "
          "straight up from the floor — this is LIFTING/RAISING, not walking "
          "with it.",
          "the crate lifted and set up onto the high shelf"),
}

# 1.7.2 (QA round 2) — per-verb custom insets, replacing the default motion
# sequence where card-specific insets read better.
VERB_INSET = {
    369: ("Include 2 to 3 small supporting insets of other things that fly: an "
          "aeroplane in the sky; a kite on a string; a flock of birds in "
          "V-formation."),
    372: ("Include 2 small supporting insets: a red traffic light glowing at "
          "the top (stop); a raised open palm held up in the STOP gesture."),
    373: ("Include 2 small supporting insets: a line of cars driving nose-to-"
          "tail one behind another; a mother goose walking with her goslings "
          "following in a row behind her."),
    433: ("Include 2 small supporting insets: a hand wiping a window pane clean "
          "with a cloth; a mop wet-mopping a floor. (Not sweeping.)"),
}


def slug(lt: str) -> str:
    """ASCII slug of the first Lithuanian form: 'gydytojas/gydytoja' ->
    'gydytojas'; 'žemė (dirvožemis)' -> 'zeme'."""
    first = lt.split("/")[0].split("(")[0].strip().lower()
    ascii_ = unicodedata.normalize("NFD", first)
    ascii_ = "".join(c for c in ascii_ if not unicodedata.combining(c))
    ascii_ = ascii_.replace("š", "s").replace("ž", "z")  # safety, post-NFD
    return "".join(c if c.isalnum() else "_" for c in ascii_).strip("_")


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def eligible(rows, include_pending=False):
    """Yield (key, row, route) for every generable row, in wordlist order."""
    out, skipped = [], []
    for r in rows:
        n = int(r["#"])
        if r["depictable"] not in ("yes", "category-multi"):
            continue
        if not r["subject_phrase_EN"].strip():
            skipped.append((n, "no subject phrase"))
            continue
        if n in PENDING and not include_pending:
            skipped.append((n, "PENDING: " + PENDING[n]))
            continue
        if n in OVERRIDE_CLASS:
            cls = OVERRIDE_CLASS[n]
        elif r["type"] == "V":
            if n not in VERB_STAGING:
                skipped.append((n, "verb missing from VERB_STAGING"))
                continue
            cls = "verb"
        else:
            cls = route(r["category"], r["type"], r["flags"])
        key = f"{n:03d}_{slug(r['lithuanian_TARGET'])}"
        out.append((key, r, cls))
    return out, skipped


def build_call(key, r, cls):
    """Return the kwargs for GOGenerator.generate() for this row."""
    subject = r["subject_phrase_EN"].strip()
    if cls == "verb":
        people, setting, arrow, emphasis, consequence = VERB_STAGING[int(r["#"])]
        # 1.7.2: VERB_INSET lets a verb override the default motion-sequence
        # inset with card-specific insets (as NOUN_STAGING inset_note does).
        vi = VERB_INSET.get(int(r["#"]))
        return dict(subject=subject,
                    scene=scene_for(setting, arrow=arrow, emphasis=emphasis,
                                    people=people),
                    inset_note=(vi if vi else inset_for(consequence)), insets=True,
                    text=False, people=people, glyph=False,
                    filename=f"{key}.png")
    scene, inset_note, _, people, insets = compose_class(cls, r["category"])
    st = NOUN_STAGING.get(int(r["#"]), {})
    if "main" in st:
        scene = st["main"] + SCENE_TAIL
    people = st.get("people", people)
    if "inset_note" in st:
        inset_note = st["inset_note"]
    return dict(subject=subject, scene=scene, inset_note=inset_note,
                insets=insets, text=False, people=people,
                glyph=int(r["#"]) in GLYPH_ROWS,
                filename=f"{key}.png")


def main():
    ap = argparse.ArgumentParser(description="Lietuvių 625 deck builder")
    ap.add_argument("--wordlist", default=WORDLIST)
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--backend", default="openai", choices=["openai", "zimage"])
    ap.add_argument("--ratio", default=RATIO)
    ap.add_argument("--trial", type=int, default=0, help="first N rows only")
    ap.add_argument("--category", default="", help="one category block")
    ap.add_argument("--only", default="", help="comma-separated keys (re-roll)")
    ap.add_argument("--include-pending", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and prompts; no API calls")
    a = ap.parse_args()

    rows = load_rows(a.wordlist)
    work, skipped = eligible(rows, a.include_pending)
    if a.category:
        work = [w for w in work if w[1]["category"] == a.category]
    if a.only:
        want = {k.strip() for k in a.only.split(",")}
        work = [w for w in work if w[0] in want]
        missing = want - {w[0] for w in work}
        if missing:
            print("WARNING: --only keys not found:", ", ".join(sorted(missing)))
    if a.trial:
        work = work[:a.trial]

    keys = [w[0] for w in work]
    assert len(keys) == len(set(keys)), "key collision — should be impossible"
    n_verbs = sum(1 for w in work if w[2] == "verb")
    print(f"plan: {len(work)} cards  ({n_verbs} verbs, "
          f"{len(work)-n_verbs} noun/attribute/chart)  -> {a.out}")
    for n, why in skipped:
        print(f"  skip #{n}: {why}")

    if a.dry_run:
        from go_generator import build_prompt
        for key, r, cls in work:
            kw = build_call(key, r, cls)
            prompt = build_prompt(kw["subject"], scene=kw["scene"],
                                  insets=kw["insets"],
                                  inset_note=kw["inset_note"], text=False,
                                  people=kw["people"], glyph=kw["glyph"],
                                  backend=a.backend)
            print(f"\n--- {key}  [{cls}]  #{r['#']} {r['english']}\n{prompt}")
        return

    gen = GOGenerator(backend=a.backend, ratio=a.ratio)
    lf, lw = GOGenerator.open_ledger(os.path.join(a.out, "ledger.csv"))
    cf, cw = GOGenerator.open_cards(os.path.join(a.out, "cards.csv"))
    done = 0
    try:
        for key, r, cls in work:
            kw = build_call(key, r, cls)
            dest, seed, prompt = gen.generate(out_dir=a.out, **kw)
            lw.writerow([key, kw["subject"], seed, gen.backend, gen.size,
                         os.path.basename(dest), prompt]); lf.flush()
            cw.writerow([key, r["lithuanian_TARGET"], r["english"],
                         r["lt_pron"], r["gender"], r["#"], r["category"],
                         f"{key}.png"]); cf.flush()
            done += 1
            print(f"    {r['#']:>3}  {r['lithuanian_TARGET']} "
                  f"({r['english']})  [{cls}]")
    finally:
        lf.close(); cf.close()
        print(f"done: {done}/{len(work)} -> {a.out} "
              "(images + ledger.csv + cards.csv)")


if __name__ == "__main__":
    main()
