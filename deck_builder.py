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

# 1.7.4 — the abstract/unfinished set. Each has a self-contained scene in its
# subject phrase, so route to "attribute" (render the described scene as one
# composition, no forced generic insets). Per-card insets are turned back on
# via NOUN_STAGING {"insets": True, "inset_note": ...}. Includes the abstract
# "verbs" (think/learn/love/pray/win/lose/teach) and the two new feed verbs,
# routed attribute so they don't need VERB_STAGING.
ABSTRACT_ATTR = {
    133,134,135,151,152,154,158,153,162,131,132,143,144,147,148,149,150,160,161,
    136,128,129,130,165,164,145,146,508,212,284,286,298,312,320,352,353,357,140,
    142,141,479,354,355,464,465,509,138,155,156,157,159,139,250,252,167,169,171,
    334,335,337,336,339,338,345,340,341,342,343,344,346,347,356,362,
    510,511,512,513,514,515,516,517,
    374,387,403,414,415,416,427,528,529,
}

# measurement cards: metric -> EU flag, imperial -> US+UK flags.
FLAG_OVERRIDE = {334: "eu", 335: "eu", 336: "eu",
                 337: "imperial", 338: "imperial", 339: "imperial"}

# ---------------------------------------------------------------------------
# 1.7 — per-row noun staging (the guessability pass, Dainius QA of cards
# 1-127). Same idea as VERB_STAGING but for nouns: row# -> overrides applied
# AFTER compose_class. Keys: "main" (replaces the class main clause; the
# frozen SCENE_TAIL framing is re-appended), "people" (dress class),
# "inset_note" (replaces the class inset menu with card-specific insets).
# Insets must SUPPORT the target word or at least not vote for a wrong one.
# ---------------------------------------------------------------------------
NOUN_STAGING = {
    350: {"subject": "the consonants of the alphabet",
          "main": ("the five consonant letters B C D F G standing in one neat "
          "evenly-spaced row across the middle of the card, drawn as bold clean "
          "display letterforms on plain paper, all five the same size, with "
          "nothing else in the scene and NO single letter singled out, enlarged, "
          "sculpted, mounted on a stand or marked with an arrow")},
    # -- attribute-routed verbs and the vowel card (1.7.7 owner QA) --
    403: {"subject": "to love", "main": ("two people embracing each other warmly "
          "and closely, face to face, with one single clean red heart symbol "
          "floating clearly above and between them against open paper. Draw NO "
          "arrow anywhere; nothing may overlap or cross the heart, which must be "
          "drawn whole, unbroken and complete")},
    374: {"subject": "to think", "insets": True,
          "main": ("a person seated with one hand to their chin in thought, a "
          "clean empty thought-bubble rising above their head"),
          "inset_note": ("Include 2 small supporting insets: Rodin's statue "
          "'The Thinker' seated on its plinth, chin on hand; a person at a desk "
          "frowning in concentration over a problem.")},
    351: {"subject": "the vowels of the alphabet",
          "main": ("the five vowel letters A E I O U standing in one neat "
          "evenly-spaced row across the middle of the card, drawn as bold clean "
          "display letterforms on plain paper, with nothing else in the scene")},
    # ===== 1.7.7 owner QA round 4 =====
    # -- pronouns: the arrow marks the referent, never the speaker --
    516: {"subject": "a speaker addressing a group of several people (the pronoun 'you', plural)", "main": ("a speaker standing to one side with open arms, addressing a "
          "facing GROUP of several people; exactly one bold arrow runs from the "
          "speaker to the GROUP, marking the group as the ones addressed")},
    514: {"subject": "a person indicating one inanimate object (the pronoun 'it')", "main": ("a person pointing down at one plain inanimate object — a ball "
          "on the ground — exactly one bold arrow from the pointing hand to the "
          "BALL; the person looks at the ball, not out of the card")},
    512: {"subject": "a speaker indicating one other man (the pronoun 'he')", "main": ("a speaker on one side turned toward a single man standing "
          "apart from them; exactly one bold arrow runs from the speaker across "
          "to THAT MAN. No arrow touches or overlays the man's body")},
    511: {"subject": "one person addressing one other person face to face (the pronoun 'you', singular)", "main": ("one person facing and pointing a finger directly at one other "
          "person who stands opposite them, close and face to face. Draw NO arrow "
          "anywhere; the pointing finger alone carries the meaning")},
    510: {"subject": "a person indicating their own self (the pronoun 'I')", "main": ("a person pointing their THUMB back at their own chest, the "
          "thumb clearly touching their own breastbone, head slightly inclined "
          "toward themselves; exactly one bold short arrow curves from the thumb "
          "to that same person's chest")},
    # -- adjectives with owner-specified staging (override the pair base) --
    477: {"main": ("a blind person with dark glasses sweeping a white cane at a "
          "street crossing; exactly one bold arrow points at THE PERSON, and a "
          "second short arrow points at their unseeing eyes behind the dark "
          "glasses"), "insets": True},
    466: {"main": ("two shirts hanging side by side on the same washing line, one "
          "soaking WET and dripping, one bone DRY; exactly one bold arrow points "
          "directly AT THE WET SHIRT itself"), "insets": True},
    # -- nouns --
    362: {"subject": "handwriting, written script",
          "main": ("a sheet of writing paper on a plain desk, a hand holding a "
          "fountain pen part-way down the page, the upper half already covered "
          "in even lines of flowing running handwriting and the lower half still "
          "blank, the pen nib touching the paper mid-word"),
          "insets": True,
          "inset_note": ("Include 2 small supporting insets: an old handwritten "
          "manuscript page with a wax seal; a sheet fed into a typewriter with "
          "typed lines on it.")},
    361: {"subject": 'a picture, a depicted image', "main": ("a framed painted picture standing upright on an easel in the "
          "middle of a plain room, the painted image inside the frame clearly "
          "visible as a depicted landscape scene, the frame resting on the easel "
          "and NOT hanging on any wall"),
          "inset_note": ("Include 2 small supporting insets: a photograph lying "
          "on a table; a portrait picture propped on a shelf.")},
    356: {"main": ("a bar of chocolate with one single square clearly broken off "
          "and set apart on the table beside the rest of the bar; exactly one "
          "bold arrow points directly at THAT ONE BROKEN-OFF SQUARE")},
    354: {"main": ("a man smiling and giving a clear thumbs-up with one hand, and "
          "beside him a single large bold green tick check-mark")},
    352: {"main": ("a flashlight lying on its side casting one bright widening "
          "beam across a dark room, the beam clearly the brightest thing on the "
          "card. Draw NO arrow anywhere")},
    346: {"insets": True, "subject": 'the edge of a cliff, where solid ground ends', "main": ("a person standing well back from the EDGE of a high cliff, "
          "the cliff edge running across the card where solid ground stops and "
          "empty air and sea begin far below; exactly one bold arrow points at "
          "the cliff EDGE itself"),
          "inset_note": ("Include 2 small supporting insets: the overhanging "
          "edge of a table seen from the side; the rim edge of a flat roof with "
          "a low parapet.")},
    345: {"insets": True, "subject": 'a heavy iron weight', "main": ("a single heavy cast-iron weight sitting solidly on a plain "
          "table, its compact mass and carrying ring clearly drawn. Draw NO "
          "arrow anywhere"),
          "inset_note": ("Include 2 small supporting insets: a stack of similar "
          "iron weights; a balance scale pan sitting low under a heavy load.")},
    344: {"insets": True, "subject": 'a calendar grid of days', "main": ("a wall calendar page filling the card, drawn as a clean "
          "empty grid of seven columns and five rows of day squares, with one "
          "single square boldly ringed in red. Leave every square blank"),
          "inset_note": ("Include 2 small supporting insets: a desk day-block "
          "calendar with one leaf being torn off; a pocket diary lying open at "
          "a ruled empty page.")},
    343: {"insets": True, "subject": 'a thermometer measuring temperature', "main": ("a large upright thermometer with a clearly marked mercury "
          "column standing at mid height, drawn plainly against a neutral "
          "background. Draw NO sun, NO fire and NO arrow anywhere"),
          "inset_note": ("Include 2 small supporting insets: a frozen winter "
          "scene with icicles and a thermometer reading very low; a blazing "
          "summer scene with a thermometer reading very high.")},
    340: {"insets": True, "main": ("a round loaf of bread cut cleanly through the middle into "
          "two equal halves lying side by side, the flat cut faces turned to the "
          "viewer; exactly one bold arrow points at ONE of the two halves"),
          "inset_note": ("Include 2 small supporting insets: an apple cut into "
          "two equal halves; a piece of meat cut into two equal halves.")},
    333: {"insets": True, "subject": 'raw building materials', "main": ("a builder's yard laid out as a materials store: a stack of "
          "sawn timber planks, a heap of rough stones, a pile of stacked bricks, "
          "and rolled bolts of cloth standing together in one plain scene, each "
          "kind clearly distinct as raw stuff waiting to be made into something"),
          "inset_note": ("Include 2 small supporting insets: a roll of sheet "
          "metal; a sack of cement standing open.")},
    301: {"inset_note": ("Include 2 small supporting insets: a NIGHT sky, dark "
          "with a moon and scattered stars; a stormy overcast sky with heavy "
          "grey cloud.")},
    298: {"main": ("a globe of the Earth on a small stand, the continents and "
          "oceans clearly drawn across its face. Draw NO arrow anywhere")},
    285: {"inset_note": ("Include 2 small supporting insets: a whole human "
          "skeleton standing complete; a dog gnawing a bone.")},
    265: {"inset_note": ("Include 2 small supporting insets: two people kissing, "
          "lips meeting; a woman applying lipstick to her lips before a mirror.")},
    252: {"insets": True, "subject": 'a computer program', "main": ("a desktop computer of the period standing on a desk, its "
          "screen filled with a neat grid of small application icons, the "
          "machine drawn plainly and squarely facing the viewer"),
          "inset_note": ("Include 2 small supporting insets: a printed program "
          "flowchart diagram with boxes and arrows beside a punched card; a "
          "computer screen filled with columns of falling code characters.")},
    224: {"main": ("one single door key lying flat and alone on a plain table, "
          "its bit and bow clearly shaped, drawn cleanly with nothing else on "
          "the table"),
          "inset_note": ("Include 2 small supporting insets: a hand turning a "
          "key in a door lock; a key hanging alone on a hook.")},
    199: {"main": ("one single table fork lying flat and alone on a plain "
          "surface, its four tines clearly separated and evenly drawn, nothing "
          "else anywhere in the frame"),
          "inset_note": ("Include 2 small supporting insets: a hand holding a "
          "fork over a plate; a fork resting beside a plate at a place setting.")},
    198: {"main": ("one single soup spoon lying flat and alone on a plain "
          "surface, its bowl and handle clearly drawn, and NO other spoon "
          "anywhere in the frame"),
          "inset_note": ("Include 2 small supporting insets: a hand lifting a "
          "spoonful of soup from a bowl; a spoon resting in a cup.")},
    189: {"main": ("two bananas on a plain surface: one whole unpeeled banana "
          "and beside it one banana half peeled with the skin folded down, both "
          "drawn cleanly and anatomically correctly"),
          "inset_note": ("Include 2 small supporting insets: a bunch of bananas "
          "still joined at the stem; a banana sliced into round coins on a "
          "plate.")},
    188: {"main": ("one whole red apple with a short stem and one leaf, and "
          "beside it the same apple cut in half showing the core and pips, both "
          "drawn cleanly and correctly"),
          "inset_note": ("Include 2 small supporting insets: apples growing on "
          "a laden branch; a basket of picked apples.")},
    157: {"subject": 'physical exercise in a gym', "main": ("a plain gym hall where one man does star-jump jumping jacks "
          "mid-motion and another man does press-ups on the floor, while a coach "
          "with a whistle at his lips stands beside them directing the exercise")},
    156: {"main": ("three runners sprinting hard down a running track, the "
          "leading runner breasting the finishing tape; exactly one bold arrow "
          "runs forward along the track in the direction of the race, marking "
          "the contest itself")},
    154: {"insets": True, "subject": 'an assortment of weapons', "main": ("a plain wall rack in a hunting lodge displaying an assortment "
          "of weapons together: a wooden-stocked hunting rifle, a sheathed sword, "
          "a spear and a bow with arrows, arranged as an orderly museum display"),
          "inset_note": ("Include 2 small supporting insets: a medieval axe and "
          "shield mounted on a wall; an archer's quiver of arrows standing "
          "upright.")},
    149: {"main": ("a sergeant in military uniform standing and gesturing his "
          "squad forward; the advancing figures storming the bunker are all "
          "helmeted SOLDIERS in uniform carrying packs — no civilians anywhere "
          "in the scene"), "people": "worker"},
    138: {"main": ("a sports team of players in matching kit lined up together "
          "in a row on the pitch, with a coach in a tracksuit standing at each "
          "end of the line; every figure is either a kitted player or a coach — "
          "no ordinary civilians anywhere")},
    109: {"insets": True, "subject": 'one individual person singled out from others', "main": ("a row of plain dark faceless silhouette figures standing "
          "shoulder to shoulder across the card, and in the middle of the row "
          "ONE fully drawn real individual person with face, clothes and detail, "
          "standing out clearly from the silhouettes on either side"),
          "inset_note": ("Include 2 small supporting insets: a dense crowd of "
          "silhouetted people with exactly one bold arrow singling out one "
          "individual within it; a single identity card portrait photograph.")},
    103: {"main": ("one ordinary person standing upright and facing the "
          "viewer, FULLY CLOTHED in plain modest everyday clothes — shirt, "
          "trousers and shoes — drawn simply and completely from head to foot "
          "as the plain example of a human being, in the calm manner of a "
          "civic handbook figure"),
          "inset_note": ("Include 2 small supporting insets: a human figure "
          "beside a horse and a dog, the human clearly distinct from the "
          "animals; the outline of a human body drawn as a simple diagram.")},
    102: {"main": ("a man and a woman standing side by side with a small child "
          "beside them, all three on the same ground; exactly one bold arrow "
          "points at the two GROWN-UP adults, and no arrow touches the child")},
    51: {"subject": 'one country among its neighbours', "main": ("a wall map showing one whole country with its national border "
          "drawn as a bold continuous line and its territory shaded, SURROUNDED "
          "on every side by the outlines of the neighbouring countries drawn in "
          "plain unshaded outline so the one country stands out among them")},
    46: {"subject": 'a theatre stage with a performance in progress', "main": ("the inside of a theatre seen from the audience: a lit "
          "proscenium STAGE with open curtains drawn back and actors performing "
          "upon it, the dark rows of seated audience heads in the foreground")},
    # ===== 1.7.4 abstract/unfinished cards needing insets (attribute class is
    # inset-free by default, so turn insets back on here) =====
    162: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "dishevelled man sleeping on a park bench; police arresting that man "
          "and putting him into a police car.")},
    143: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "chalk body outline with bloodstains on the ground; plain-clothes "
          "police detectives investigating the scene.")},
    131: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "cardiogram trace showing a beating heart rhythm; the same trace then "
          "going FLAT into a single straight line.")},
    148: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "round peace symbol (CND) drawn in the muted GO style; a white dove "
          "carrying an olive branch.")},
    129: {"insets": True, "inset_note": ("Include 2 small supporting insets: "
          "GO-style winged angels with haloes; a golden harp.")},
    130: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "cluster of devils' pitchforks; wailing tormented faces amid the "
          "flames.")},
    414: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "Catholic kneeling in prayer with a rosary before a crucifix; an "
          "Orthodox believer crossing themselves before gilded icons.")},
    284: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "black-and-yellow biohazard symbol; germs and bacteria magnified under "
          "a lens.")},
    312: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "green oxygen (O2) gas cylinder; a pair of lungs drawing breath.")},
    140: {"insets": True, "inset_note": ("Include 2 small supporting insets: "
          "interlocking hands of many different skin tones; a row of diverse "
          "human faces in profile.")},
    141: {"insets": True, "inset_note": ("Include 2 small supporting insets: a "
          "man and woman sitting very close and intimate together at a dim bar; "
          "an old-fashioned key sliding into a keyhole lock.")},
    528: {"people": "worker"},   # šerti: feeding livestock is farm work
    # ginklas (gun): a bare rifle tripped output moderation; frame it as a calm
    # hunting-lodge display to keep the sense without the flag.
    # ===== 1.7.3 QA round 3 (owner full-deck review) =====
    187: {"inset_note": ("Include 2 to 3 small supporting insets: a slice of raw "
                         "red beef; a cooked beef dish; a live COW in a field to "
                         "show the source animal.")},
    186: {"inset_note": ("Include 2 to 3 small supporting insets: a cut of raw "
                         "pork; a cooked pork dish; a live PIG in a pen to show "
                         "the source animal.")},
    194: {"main": ("Draw a clear glass bottle and cruet of golden cooking oil, a "
                   "little oil poured into a shallow dish beside it. Do NOT show "
                   "any national flag anywhere on this card."),
          "inset_note": ("Include 2 small supporting insets: a sunflower and its "
                         "seeds (the source); oil being poured into a frying pan.")},
    204: {"people": "civilian",
          "main": ("Draw a FAMILY — parents and their children — sitting together "
                   "around a home dining table sharing an evening meal, a served "
                   "dish and plates on the table, a warm domestic evening.")},
    215: {"people": "civilian",
          "main": ("Draw a tidy home BEDROOM with a bed, wardrobe and window; a "
                   "woman in ordinary clothes is making up the bed, smoothing the "
                   "blanket and plumping a pillow.")},
    216: {"people": "civilian",
          "main": ("Draw a home KITCHEN with a stove, cupboards and a table; a "
                   "woman in an apron and ordinary clothes cooks and manages it, "
                   "stirring a pot on the stove.")},
    246: {"inset_note": ("Include 3 small supporting insets of clock faces each "
                         "showing a DIFFERENT time — one near three o'clock, one "
                         "near six o'clock, one near nine o'clock.")},
    258: {"inset_note": ("Include 2 to 3 small supporting insets, all about the "
                         "head itself: a head in profile silhouette; a close-up "
                         "of a face; a head wearing a cap. No unrelated scenes.")},
    259: {"main": ("Draw a clear study of the human NECK on a clothed figure from "
                   "the front-side, one bold arrow pointing at the neck, in the "
                   "same restrained semi-realistic instructional style as the "
                   "rest of the deck — NOT cartoonish."),
          "inset_note": ("Include 2 small supporting insets: a hand at the side "
                         "of the neck; a scarf worn around the neck.")},
    279: {"main": ("Draw a hand placed flat on a person's chest over the heart, "
                   "with a schematic red heart symbol and a heartbeat line beside "
                   "it, in the restrained semi-realistic instructional style of "
                   "the deck — NOT a cute cartoon heart."),
          "inset_note": ("Include 2 small supporting insets: a doctor listening "
                         "to a chest with a stethoscope; a simple textbook heart "
                         "diagram.")},
    283: {"main": ("Draw a man mopping heavy SWEAT from his brow with a cloth, "
                   "beads of sweat on his face and damp patches on his shirt, "
                   "under a blazing hot SUN glaring in the background sky.")},
    # ===== (earlier rounds below) =====
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
# 1.7.7: 351 balsis moves OFF the single-glyph exception — its lone "A"
# collided with 227 raidė. It now renders the vowel set via TEXT_EXCEPTION.
GLYPH_ROWS = {227}

# ---------------------------------------------------------------------------
# Per-verb staging: row# -> (people, setting, arrow, emphasis, consequence).
# Design source: STAGING_files_2_1.md §4 (telicity -> D panel) and the locked
# verb treatment (context C default). The nine 1.5-validated demo verbs keep
# their exact staging. A non-empty consequence == a D-accent card.
# ---------------------------------------------------------------------------
W, P, C = "worker", "professional", "civilian"
VERB_STAGING = {
    # 1.7.7: transitive "melt" — a foundry, so it reads as melting SOMETHING
    # (contrast 398 tirpti, ice melting by itself).
    530: (W, "a foundry floor with a furnace",
          "", "A foundry worker in heavy apron, gloves and face shield tips a "
          "crucible of glowing white-hot molten metal, which pours as a bright "
          "liquid stream into a mould; solid metal ingots wait in a stack "
          "beside the furnace.", "the finished cast metal ingot cooling in its mould"),
    363: (W, "a stretch of public road under repair, with striped barriers, "
          "a warning sign on a tripod and a heap of gravel",
          "", "Several workmen in overalls and caps are at work together on the "
          "road surface — one swinging a pick, one shovelling, one tamping — "
          "plainly labouring rather than mending one single broken object.", ""),
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
    371: (C, "a home doorway in a SOLID OPAQUE wall (not see-through), a packed "
          "travel bag in hand, a bus waiting at the kerb beyond",
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
    410: (C, "a home bedroom in the morning, sun through the window", "",
          "Emphasise WAKING UP: a civilian in PYJAMAS is sitting up in bed and "
          "getting up, rubbing their eyes, having just woken — not a worker.",
          "the person standing up out of bed in pyjamas"),
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
          "an arc arrow that curves from the door back TOWARD the person, showing "
          "the door being pulled OPEN toward them, the door already standing ajar", "",
          "the door standing open"),
    422: (W, "a plain interior door",
          "an arc arrow showing the door swinging shut", "",
          "the door closed"),
    423: (W, "an office desk with paper and pen", "", "", ""),
    424: (W, "an office with a rotary telephone", "", "", ""),
    425: (W, "a boiler room with a large pipe valve",
          "a circular arrow around the turning wheel", "", ""),
    426: (W, "a construction site where workers are raising the TIMBER FRAME of "
          "a house — upright wooden posts and cross-beams going up", "",
          "Emphasise BUILDING: workers timber-framing, fitting and hammering the "
          "wooden frame of the building together.",
          "the finished timber frame standing"),
    428: (W, "a garden bed",
          "one bold upward arrow beside the growth stages", "",
          "the plant fully grown"),
    429: (C, "a desk with paper", "", "", ""),
    430: (C, "a home interior", "",
          "Emphasise FEEDING A CHILD: ONLY a mother spoon-feeding porridge to a "
          "baby in a high chair, the baby opening its mouth for the spoon. "
          "maitinti is feeding PEOPLE — absolutely no animals, birds or livestock "
          "anywhere on the card.", ""),
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
          "with a cloth; someone on their knees scrubbing a floor with a stiff "
          "hand BRUSH. (Not sweeping, not another mop.)"),
    386: ("Include 2 to 3 small supporting insets: a paper bullseye target with "
          "bullet holes in it; a close-up of a steady hand on the rifle trigger; "
          "spent brass cartridge cases on the ground."),
}


def slug(lt: str) -> str:
    """ASCII slug of the first Lithuanian form: 'gydytojas/gydytoja' ->
    'gydytojas'; 'žemė (dirvožemis)' -> 'zeme'."""
    first = lt.split("/")[0].split("(")[0].strip().lower()
    ascii_ = unicodedata.normalize("NFD", first)
    ascii_ = "".join(c for c in ascii_ if not unicodedata.combining(c))
    ascii_ = ascii_.replace("š", "s").replace("ž", "z")  # safety, post-NFD
    return "".join(c if c.isalnum() else "_" for c in ascii_).strip("_")


# ===========================================================================
# 1.7.7 — ADJECTIVE RULESET (owner QA: "adjectives don't have a ruleset")
#
# Two rules, both applied automatically to every Adjectives row:
#
#  (1) PAIRED OPPOSITES SHARE ONE BASE SCENE. An adjective is only legible
#      against its opposite, so each pair is staged as ONE composition drawn
#      identically for both cards; only the marking arrow moves to the other
#      pole. ADJ_PAIR_BASE holds the shared scene, ADJ_PAIR says which pole
#      this row marks.
#  (2) ADJECTIVES GET INSETS. The attribute class is inset-free by default;
#      adjectives now carry 2 insets showing the SAME quality in other
#      everyday objects, which is what makes the quality (not the object)
#      read as the target. Per-card NOUN_STAGING inset_note still wins.
# ===========================================================================
ADJ_PAIR_BASE = {
    "length":   ("One single scene: two otherwise identical ropes lying side by "
                 "side on the same plain ground, one clearly LONG and one clearly "
                 "SHORT, drawn to the same scale."),
    "height":   ("One single scene: two people of the same build standing side by "
                 "side on the same floor, one clearly TALL and one clearly SHORT."),
    "width":    ("One single scene: two doorways in the same wall, one clearly WIDE "
                 "and one clearly NARROW, drawn to the same scale."),
    "size":     ("One single scene: two otherwise identical suitcases side by side "
                 "on the same floor, one clearly BIG and one clearly SMALL."),
    "speed":    ("One single scene: on one side a tortoise plodding slowly, on the "
                 "other a hare bounding fast, both on the same stretch of road, "
                 "speed-lines only behind the fast one."),
    "temp_hi":  ("One single scene: two identical mugs side by side on the same "
                 "table, one steaming HOT with rising steam, one frosted COLD with "
                 "ice, drawn to the same scale."),
    "temp_mid": ("One single scene: two identical rooms side by side, one WARM with "
                 "a lit stove and a person in shirtsleeves, one COOL with an open "
                 "window and a person in a light jacket."),
    "age_obj":  ("One single scene: two of the same object side by side, one BRAND "
                 "NEW and clean, one OLD, worn and battered, drawn to the same scale."),
    "age_人":   ("One single scene: a YOUNG person and an OLD person of the same "
                 "family standing side by side in the same plain room."),
    "quality":  ("One single scene: two identical baskets of apples side by side, one "
                 "full of GOOD sound fruit, one full of BAD rotten spotted fruit."),
    "wet":      ("One single scene: two identical shirts hanging side by side on the "
                 "same washing line, one soaking WET and dripping, one bone DRY."),
    "health":   ("One single scene: two people side by side in the same plain room, "
                 "one SICK in bed with a thermometer and a flushed face, one HEALTHY "
                 "standing upright and well."),
    "volume":   ("One single scene: on one side a loud clanging alarm bell with bold "
                 "radiating sound-lines, on the other the same room hushed and still "
                 "with a person holding one finger to their lips."),
    "mood":     ("One single scene: two people of the same build side by side in the "
                 "same plain room, one plainly HAPPY and smiling, one plainly SAD "
                 "with downturned mouth and slumped shoulders."),
    "beauty":   ("One single scene: two flower arrangements side by side in identical "
                 "vases, one BEAUTIFUL and fresh in full bloom, one UGLY, wilted, "
                 "brown and drooping."),
    "kindness": ("One single scene: on one side a KIND person gently helping a frail "
                 "old lady across the street; on the other a MEAN scowling man "
                 "sneering and roughly shoving a smaller person aside."),
    "wealth":   ("One single scene: two houses side by side on the same street, one "
                 "RICH and grand with a fine motor car, one POOR and shabby with a "
                 "patched roof."),
    "thick":    ("One single scene: two books side by side on the same table, one "
                 "very THICK and one very THIN, drawn to the same scale."),
    "price":    ("One single scene: a shop counter with two identical-looking goods "
                 "side by side, one marked with a very high price and one marked with "
                 "a very low price, a fat wad of banknotes beside the dear one and a "
                 "single small coin beside the cheap one."),
    "curve":    ("One single scene: two metal bars side by side against the same "
                 "plain wall, one perfectly FLAT and straight, one strongly CURVED "
                 "into an arc."),
    "sex":      ("One single scene: a woman teacher standing before a class, pointing "
                 "her long pointer stick at a blackboard. The blackboard carries ONE "
                 "single large plain lavatory-door pictogram silhouette and nothing "
                 "else."),
    "fit":      ("One single scene: the same man twice side by side, wearing the same "
                 "suit — on one side the suit is far too TIGHT and straining at the "
                 "buttons, on the other it is far too LOOSE and baggy."),
    "level":    ("One single scene: two shelves on the same wall, one mounted very "
                 "HIGH near the ceiling and one mounted very LOW near the floor, a "
                 "person standing beside them for scale."),
    "hardness": ("One single scene: two identical cubes side by side on the same "
                 "table, one SOFT (a squashed pillow-like cube denting under a "
                 "pressing finger) and one HARD (a solid stone cube unmoved by the "
                 "same finger)."),
    "depth":    ("One single scene: a cross-section of one swimming pool, the SHALLOW "
                 "end on one side where the water reaches a standing child's knees, "
                 "the DEEP end on the other where the water is far over an adult's "
                 "head, the sloping floor joining them."),
    "clean":    ("One single scene: two boys of the same age standing side by side in "
                 "the same plain room, one perfectly CLEAN and neat, one thoroughly "
                 "DIRTY with mud on his face, hands and clothes."),
    "strength": ("One single scene: two men side by side lifting the same heavy "
                 "barbell, one STRONG and raising it easily overhead, one WEAK and "
                 "straining, unable to lift it off the ground."),
    "life":     ("One single scene: two potted plants side by side on the same sill, "
                 "one ALIVE, green and upright, one DEAD, brown, shrivelled and bare."),
    "weight":   ("One single scene: a balance scale on a table with an anvil on one "
                 "pan sinking heavily down and a single feather on the other pan "
                 "riding high."),
    "light":    ("One single scene: the SAME room drawn twice side by side — on one "
                 "side brightly lit by a lamp with clear light falling across the "
                 "floor, on the other the identical room dark and unlit in deep "
                 "shadow. Both halves must show the same furniture in the same "
                 "positions."),
}

# row -> (base key, the pole this card marks)
ADJ_PAIR = {
    446: ("length", "the LONG rope"),        447: ("length", "the SHORT rope"),
    448: ("height", "the TALL person"),      449: ("height", "the SHORT person"),
    450: ("width", "the WIDE doorway"),      451: ("width", "the NARROW doorway"),
    452: ("size", "the BIG suitcase"),       453: ("size", "the SMALL suitcase"),
    454: ("speed", "the SLOW tortoise"),     455: ("speed", "the FAST hare"),
    456: ("temp_hi", "the HOT steaming mug"), 457: ("temp_hi", "the COLD iced mug"),
    458: ("temp_mid", "the WARM room"),      459: ("temp_mid", "the COOL room"),
    460: ("age_obj", "the NEW object"),      461: ("age_obj", "the OLD worn object"),
    462: ("age_人", "the YOUNG person"),     463: ("age_人", "the OLD person"),
    464: ("quality", "the GOOD sound fruit"), 465: ("quality", "the BAD rotten fruit"),
    466: ("wet", "the WET dripping shirt"),  467: ("wet", "the DRY shirt"),
    468: ("health", "the SICK person in bed"), 469: ("health", "the HEALTHY person"),
    470: ("volume", "the LOUD clanging bell"), 471: ("volume", "the QUIET hushed side"),
    472: ("mood", "the HAPPY smiling person"), 473: ("mood", "the SAD person"),
    474: ("beauty", "the BEAUTIFUL fresh arrangement"),
    475: ("beauty", "the UGLY wilted arrangement"),
    478: ("kindness", "the KIND person helping the old lady"),
    479: ("kindness", "the MEAN man shoving the smaller person"),
    480: ("wealth", "the RICH grand house"), 481: ("wealth", "the POOR shabby house"),
    482: ("thick", "the THICK book"),        483: ("thick", "the THIN book"),
    484: ("price", "the EXPENSIVE item with the high price"),
    485: ("price", "the CHEAP item with the low price"),
    486: ("curve", "the FLAT straight bar"), 487: ("curve", "the CURVED bar"),
    490: ("fit", "the TIGHT straining suit"), 491: ("fit", "the LOOSE baggy suit"),
    492: ("level", "the HIGH shelf"),        493: ("level", "the LOW shelf"),
    494: ("hardness", "the SOFT denting cube"), 495: ("hardness", "the HARD stone cube"),
    496: ("depth", "the DEEP end"),          497: ("depth", "the SHALLOW end"),
    498: ("clean", "the CLEAN boy"),         499: ("clean", "the DIRTY boy"),
    500: ("strength", "the STRONG man lifting easily"),
    501: ("strength", "the WEAK straining man"),
    502: ("life", "the DEAD shrivelled plant"), 503: ("life", "the ALIVE green plant"),
    504: ("weight", "the HEAVY anvil"),      505: ("weight", "the LIGHT feather"),
    506: ("light", "the DARK unlit half"),   507: ("light", "the BRIGHTLY LIT half"),
}

# 488/489 differ by what is ON the blackboard, not by an arrow, so they carry
# their own tail rather than the generic "mark this pole" clause.
ADJ_PAIR_TAIL = {
    507: (" Mark the BRIGHTLY LIT half with exactly one bold arrow placed "
          "INSIDE that lit half, above the lit room and pointing straight DOWN "
          "into it. The arrow must sit wholly within the picture and must never "
          "point outward off the edge of the card or toward the dark half. Draw "
          "no other arrow anywhere."),
    506: (" Mark the DARK unlit half with exactly one bold arrow placed INSIDE "
          "that dark half, above the dark room and pointing straight DOWN into "
          "it. The arrow must sit wholly within the picture and must never point "
          "outward off the edge of the card or toward the lit half. Draw no "
          "other arrow anywhere."),
    479: (" Mark the scowling MEAN man who is doing the shoving with exactly one "
          "bold arrow placed directly ABOVE HIS HEAD and pointing straight DOWN "
          "onto him. The arrowhead must touch that man and no one else — it must "
          "not point at the person being shoved, and no other arrow appears."),
    478: (" Mark the KIND person who is helping the old lady with exactly one "
          "bold arrow placed directly ABOVE THAT HELPER and pointing straight "
          "DOWN onto them. The arrowhead must touch the helper and no one else, "
          "and no other arrow appears."),
    488: (" The pictogram on the blackboard is the plain MALE lavatory-door "
          "figure (straight-sided body, trousers). The teacher's pointer touches it."),
    489: (" The pictogram on the blackboard is the plain FEMALE lavatory-door "
          "figure (triangular skirted body). The teacher's pointer touches it."),
}
ADJ_PAIR[488] = ("sex", "")
ADJ_PAIR[489] = ("sex", "")

ADJ_MARK = (" Mark {target} with exactly one bold clear arrow whose HEAD lands "
            "directly on {target} and nothing else. The arrow must point INTO "
            "the marked side and must never point away from it toward the "
            "opposite side — if the marked side is on the left the arrow points "
            "leftward, if it is on the right the arrow points rightward. Place "
            "the arrow beside the marked side, not in the gap between the two "
            "sides. Every arrow must lie wholly inside the picture and must "
            "never point outward off the edge of the card. Draw no other "
            "arrow anywhere.")


def adj_inset_note(english):
    """1.7.7 default adjective insets: the same quality, other objects."""
    q = (english or "").split("-")[0].strip()
    return ("Include 2 small supporting insets, each showing the SAME quality "
            f"— {q} — in a different everyday object or situation, so that the "
            "insets reinforce this one quality and never suggest a neighbouring "
            "word. Do not repeat the main scene's objects in the insets.")


# ===========================================================================
# 1.7.9 — TEXT EXCEPTIONS ARE NOW DATA. Any wordlist row may carry a `card_text`
# column naming exactly what lettering that card may show; it overrides the
# table below. This is what makes undepictable-but-teachable cards possible
# (days of the week on a calendar, numerals, unit marks) without hardcoding
# each one. Everything without card_text stays wordless under NO_TEXT_RULE.
# ===========================================================================
# legacy in-code exceptions (kept working; new rows should use the column)
# 1.7.7 — TEXT EXCEPTION rows (owner QA). A handful of cards cannot teach
# their word without a little lettering. Each value names EXACTLY what may be
# written; everything else on the card stays wordless.
# ===========================================================================
TEXT_EXCEPTION = {
    362: ('the flowing handwritten script on the page itself, drawn as ordinary '
          'running handwriting in even lines; the individual words need not be '
          'legible. No other lettering, label or caption anywhere.'),
    350: ('the five consonant letters "B C D F G" written once in a single '
          'neat row as the subject of the card.'),
    334: ('the unit mark "m" written once beside the metre-stick, and the '
          'number "100" with "cm" written once beneath it to show that one '
          'metre is a hundred centimetres.'),
    335: ('the unit mark "cm" written once beside the marked centimetre '
          'division on the ruler.'),
    337: ('the unit mark "in" written once beside the marked inch division on '
          'the ruler.'),
    110: ('the letters "ABC" written once on the blackboard with the numbers '
          '"123" written once beneath them.'),
    160: ('the price "5 Lt." written once on the large hand-written price tag.'),
    151: ('the magazine masthead "NAUJOJI ROMUVA" written once across the top '
          'of the magazine cover.'),
    351: ('the five vowel letters "A E I O U" written once in a single neat '
          'row as the subject of the card.'),
}


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
        if n in ABSTRACT_ATTR:
            cls = "attribute"
        elif n in OVERRIDE_CLASS:
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
    n = int(r["#"])

    # --- 1.7.7 adjective ruleset: shared base scene per opposite-pair, and
    # insets on (both are overridable per row by NOUN_STAGING below).
    if n in ADJ_PAIR:
        base_key, target = ADJ_PAIR[n]
        scene = ADJ_PAIR_BASE[base_key]
        scene += ADJ_PAIR_TAIL.get(n, ADJ_MARK.format(target=target) if target else "")
        scene += SCENE_TAIL
        insets = True
        inset_note = adj_inset_note(r["english"])
        # the pair base IS the composition, so the subject must be the quality
        # itself — the row's old scene-phrase would contradict the new staging.
        subject = "the quality " + r["english"].split("-")[0].strip().upper()
    elif r["category"] == "Adjectives" and r["type"] == "A":
        insets = True                       # unpaired adjectives still get insets
        inset_note = adj_inset_note(r["english"])

    st = NOUN_STAGING.get(n, {})
    if "subject" in st:          # 1.7.7: keep phrase and re-staged scene in step
        subject = st["subject"]
    if "main" in st:
        scene = st["main"] + SCENE_TAIL
    people = st.get("people", people)
    if "inset_note" in st:
        inset_note = st["inset_note"]
    insets = st.get("insets", insets)   # 1.7.4: per-card inset toggle
    return dict(subject=subject, scene=scene, inset_note=inset_note,
                insets=insets, text=False, people=people,
                glyph=n in GLYPH_ROWS,
                exact_text=(r.get("card_text", "").strip()
                            or TEXT_EXCEPTION.get(n, "")),
                flag=FLAG_OVERRIDE.get(n, "lt"),
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
                                  backend=a.backend, flag=kw.get("flag", "lt"))
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
