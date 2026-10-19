# files 1.7 / wordlist 2.3 — DIFF for sign-off (guessability pass)

## go_grammars.py (1.6 -> 1.7)
```diff
--- go_grammars.py.bak161	2026-07-13 18:00:57.098710262 -0400
+++ go_grammars.py	2026-07-13 18:02:02.236509642 -0400
@@ -48,8 +48,12 @@
 # classes whose composition is complete in itself — no supporting insets
 NO_INSET_CLASSES = {"attribute", "chart"}
 
-# category -> dress class for any people on the card
-PEOPLE_CLASS = {"Job": "professional", "People": "civilian"}
+# category -> dress class for any people on the card.
+# 1.7: population follows the place — Location cards default to civilians
+# (schools, banks, clubs are civilian spaces); industrial locations override
+# back to worker per-row via deck_builder.NOUN_STAGING.
+PEOPLE_CLASS = {"Job": "professional", "People": "civilian",
+                "Location": "civilian"}
 DEFAULT_PEOPLE = "worker"
 
 # each class: a main-composition imperative + 2-3 supporting inset ideas.
@@ -69,9 +73,15 @@
         "insets": ["its source container — a jug, bottle, or pot",
                    "a worker drinking it in a canteen or rest area"]},
     "place": {
-        "main": "Draw it from the front as a clear architectural elevation.",
+        # 1.7: occupants ARE the disambiguating signal for places — a school
+        # reads as a school because of children, a hospital because of white
+        # coats. Populate accordingly.
+        "main": ("Draw it from the front as a clear architectural elevation, "
+                 "with the people who characteristically use it visible at or "
+                 "around it, dressed for that place."),
         "insets": ["a detail of the entrance or a characteristic feature",
-                   "a glimpse of the interior, or of people using it"]},
+                   "a glimpse of the people who characteristically use it, "
+                   "inside or at the entrance, doing what one does there"]},
     "vehicle": {
         "main": "Draw it in clear static side profile.",
         "insets": ["a close-up of a key part — a wheel, the engine, or a fitting",
@@ -97,9 +107,11 @@
         "insets": ["a close-up of the texture",
                    "an everyday object made from it"]},
     "person": {
-        "main": "Draw them in their typical working role.",
-        "insets": ["a tool or object of their trade",
-                   "a plain civic scene of them at work"]},
+        # 1.7: "role", not "working role" — a patient, a fan, or a brother has
+        # a typical role that is not a trade. Insets follow the role.
+        "main": "Draw them in their typical role, dress, and setting.",
+        "insets": ["an object characteristic of them in that role",
+                   "a plain civic scene of them in their usual role"]},
     # 1.6 — the phrase IS the composition; no insets for these two.
     "attribute": {
         "main": ("Stage the scene exactly as the subject describes, as ONE "
@@ -116,6 +128,12 @@
 }
 
 
+# the frozen framing clause appended to every main composition (1.7: exposed
+# as a constant so deck_builder per-row main overrides keep the house framing)
+SCENE_TAIL = (" Keep the subject large and dominant in the foreground, "
+              "floating cleanly on the cream paper on a simple background.")
+
+
 def class_for(category: str) -> str:
     return CAT2CLASS.get(category, DEFAULT_CLASS)
 
@@ -136,9 +154,7 @@
     semantic class. The engine supplies the Subject and the frozen
     house-style; this only sets the class-specific composition."""
     g = NOUN_GRAMMARS[cls]
-    scene = (g["main"] + " Keep the subject large and dominant in the "
-             "foreground, floating cleanly on the cream paper on a simple "
-             "background.")
+    scene = g["main"] + SCENE_TAIL
     insets = cls not in NO_INSET_CLASSES
     inset_note = ("Include 2 to 3 small supporting insets: "
                   + "; ".join(g["insets"]) + ".") if insets else ""
```

## deck_builder.py (1.6.1 -> 1.7)
```diff
--- deck_builder.py.bak161	2026-07-13 18:00:57.102526176 -0400
+++ deck_builder.py	2026-07-13 18:03:08.673644890 -0400
@@ -1,7 +1,16 @@
 #!/usr/bin/env python3
 # -*- coding: utf-8 -*-
 """
-Deck builder (files 1.6.1) — the wordlist-driven production runner.
+Deck builder (files 1.7) — the wordlist-driven production runner.
+
+1.7 (the guessability pass, owner QA of cards 1-127): NOUN_STAGING gives
+nouns the same per-row staging verbs already had (main-clause override,
+dress class, card-specific insets); OVERRIDE_CLASS re-routes 51/56/101 to
+attribute, 52 to chart, 53 to nature; population follows the place
+(go_grammars 1.7: Location defaults to civilians, place cards show their
+characteristic occupants, person cards say "role" not "working role").
+QA gate added to the spec: the target word must be inferable from the main
+image alone, and insets must support it — not vote for a neighbouring word.
 
 1.6.1: the 8 open design decisions are IN (see GO_STYLE_SPEC ledger). PENDING
 is now empty; glyph rows 227/350/351 generate via the engine's single-glyph
@@ -37,7 +46,7 @@
 import os, csv, sys, argparse, unicodedata
 
 from go_generator import GOGenerator
-from go_grammars import route, compose_class
+from go_grammars import route, compose_class, SCENE_TAIL
 from verb_flashcards import scene_for, inset_for
 
 WORDLIST = "master_wordlist.csv"
@@ -52,9 +61,98 @@
 PENDING = {}   # all design questions resolved at 1.6.1
 
 # rows whose composition is complete in the phrase itself (no class grammar,
-# no motion insets): wedding scene, gravestone
+# no motion insets): wedding scene, gravestone; 1.7 adds guessability
+# re-routes — 51 šalis (map, phrase-complete), 56 vieta (pointing hand on
+# map), 101 vaikas (age-row + arrow), 52 pastatas (specimen chart of
+# building types), 53 žemė (soil is nature, not architecture).
 OVERRIDE_CLASS = {137: "attribute", 379: "attribute",
-                  227: "attribute", 350: "attribute", 351: "attribute"}
+                  227: "attribute", 350: "attribute", 351: "attribute",
+                  51: "attribute", 56: "attribute", 101: "attribute",
+                  52: "chart", 53: "nature"}
+
+# ---------------------------------------------------------------------------
+# 1.7 — per-row noun staging (the guessability pass, Dainius QA of cards
+# 1-127). Same idea as VERB_STAGING but for nouns: row# -> overrides applied
+# AFTER compose_class. Keys: "main" (replaces the class main clause; the
+# frozen SCENE_TAIL framing is re-appended), "people" (dress class),
+# "inset_note" (replaces the class inset menu with card-specific insets).
+# Insets must SUPPORT the target word or at least not vote for a wrong one.
+# ---------------------------------------------------------------------------
+NOUN_STAGING = {
+    # sparnas: creature grammar forces a full-body bird; the word is WING.
+    9: {"main": ("Draw the single outstretched wing alone, detached and "
+                 "diagram-like, its feather groups clearly drawn."),
+        "inset_note": ("Include 2 small supporting insets: a bird in flight "
+                       "with both wings spread; a close-up of the feather "
+                       "structure.")},
+    # bilietas: a blank slip is unguessable — tell the ticket's story.
+    22: {"people": "civilian",
+         "inset_note": ("Include 3 small supporting insets telling one "
+                        "sequence: a conductor handing the ticket to a "
+                        "passenger; the conductor punching the ticket; the "
+                        "passenger boarding the train, ticket in hand.")},
+    # miestas: no basement workers — city is streets, crowds, traffic.
+    24: {"inset_note": ("Include 2 small supporting insets: a rooftop "
+                        "skyline of the city; a busy pedestrian crossing "
+                        "with civilians and cars.")},
+    32: {"inset_note": ("Include 2 to 3 small supporting insets: a tidy "
+                        "hotel room with two made-up beds ready for guests; "
+                        "the reception desk with a wall rack of room keys; "
+                        "a guest's suitcase.")},
+    # ūkis: the one Location row that genuinely belongs to workers.
+    34: {"people": "worker"},
+    35: {"inset_note": ("Include 2 to 3 small supporting insets: a close-up "
+                        "of the wooden gavel; the courthouse facade; the "
+                        "scales of justice.")},
+    36: {"inset_note": ("Include 2 to 3 small supporting insets: a classroom "
+                        "with a woman teacher at a chalkboard and children "
+                        "at desks; children playing in the schoolyard.")},
+    40: {"inset_note": ("Include 2 small supporting insets: a lecture hall "
+                        "with rows of young adult students; a library "
+                        "reading room.")},
+    41: {"inset_note": ("Include 2 small supporting insets: the club "
+                        "entrance at night with young people arriving; a "
+                        "record player with musical notes in the air.")},
+    43: {"inset_note": ("Include 2 to 3 small supporting insets: a "
+                        "children's playground with a slide and swings; a "
+                        "bench under a tree; a flowerbed.")},
+    48: {"people": "professional",
+         "inset_note": ("Include 2 to 3 small supporting insets: a "
+                        "white-coated doctor and nurse at a patient's "
+                        "bedside; a nurse pushing a wheelchair; a plain red "
+                        "cross on a white circle.")},
+    55: {"inset_note": ("Include 2 to 3 small supporting insets: a teller "
+                        "counting banknotes at a counter window; a neat "
+                        "stack of banknotes and coins; a strongbox safe.")},
+    # vyras/žmona (married): the rings carry the meaning.
+    93: {"inset_note": ("Include 2 small supporting insets: a close-up of "
+                        "the couple's clasped hands with wedding rings; the "
+                        "couple exchanging rings before a registry "
+                        "official.")},
+    94: {"inset_note": ("Include 2 small supporting insets: a close-up of "
+                        "the couple's clasped hands with wedding rings; the "
+                        "couple exchanging rings before a registry "
+                        "official.")},
+    # sirgalius: insets must be SPORT, not markets.
+    107: {"inset_note": ("Include 2 small supporting insets: the football "
+                         "match seen from the stands; a waved knitted scarf "
+                         "and a small plain two-colour pennant.")},
+    # pacientas: the person-grammar "role" clause still needs forcing here —
+    # patients REST and RECEIVE care. Dress professional so carers get
+    # white coats; the main clause dresses the patients themselves.
+    114: {"main": ("Draw them as patients at rest in neighbouring hospital "
+                   "beds, in plain pyjamas or hospital gowns with blankets "
+                   "over them — resting and receiving care, not working."),
+          "people": "professional",
+          "inset_note": ("Include 2 to 3 small supporting insets: a bedside "
+                         "table with medicine bottles and a thermometer; a "
+                         "white-coated doctor checking a patient's pulse; a "
+                         "patient carried on a stretcher toward an "
+                         "ambulance.")},
+    # vestuvės: wedding guests are not coverall workers (moved from
+    # the 1.6.1 special case in build_call).
+    137: {"people": "civilian"},
+}
 
 # rows generated with the engine's single-glyph exception (decision Q2)
 GLYPH_ROWS = {227, 350, 351}
@@ -272,8 +370,12 @@
                     text=False, people=people, glyph=False,
                     filename=f"{key}.png")
     scene, inset_note, _, people, insets = compose_class(cls, r["category"])
-    if int(r["#"]) == 137:
-        people = "civilian"          # wedding guests are not coverall workers
+    st = NOUN_STAGING.get(int(r["#"]), {})
+    if "main" in st:
+        scene = st["main"] + SCENE_TAIL
+    people = st.get("people", people)
+    if "inset_note" in st:
+        inset_note = st["inset_note"]
     return dict(subject=subject, scene=scene, inset_note=inset_note,
                 insets=insets, text=False, people=people,
                 glyph=int(r["#"]) in GLYPH_ROWS,
```

## master_wordlist.csv (2.2 -> 2.3) — subject_phrase_EN changes

**24 miestas** (city)
- OLD: a compact city street panorama of mid-rise buildings
- NEW: a busy city street panorama — crowds of pedestrians and cars among tall mid-rise buildings

**32 viešbutis** (hotel)
- OLD: a hotel building
- NEW: a hotel building with a doorman and an arriving guest carrying a suitcase

**35 teismas** (court)
- OLD: a courthouse building
- NEW: a courtroom with a judge at the raised bench, wooden gavel in hand

**36 mokykla** (school)
- OLD: a schoolhouse building
- NEW: a schoolhouse building with young children with satchels arriving at the door

**37 biuras** (office)
- OLD: an office room with desks
- NEW: an office room with desks, clerks in everyday clothes at typewriters and telephones

**39 miestelis** (town)
- OLD: a small town main street
- NEW: a small town square — a single church spire above low wooden houses, open fields visible beyond the rooftops

**40 universitetas** (university)
- OLD: a university main building
- NEW: a university main building with a columned portico, young adult students with books on the steps

**41 klubas** (club)
- OLD: a social club building with people entering
- NEW: young people dancing in a club hall in the evening

**48 ligoninė** (hospital)
- OLD: a hospital building
- NEW: a hospital building with an ambulance at the entrance

**51 šalis** (country)
- OLD: a rural landscape with a roadside border post flying the Lithuanian tricolor
- NEW: a wall map of one whole country, its national border drawn as a single bold outline, a small Lithuanian tricolor planted at its centre

**52 pastatas** (building)
- OLD: a large multi-storey building
- NEW: three different buildings side by side — a dwelling house, an office block, and a public hall

**53 žemė** (ground)
- OLD: a patch of bare earth ground
- NEW: a mound of dark earth soil with a spade thrust into it, a pair of cupped hands holding a handful of soil beside it

**56 vieta** (location)
- OLD: a wall map with one location marked by a bold pin, small scenes of a house, a school and a park around it
- NEW: a hand with a pointing finger marking one circled spot on a local wall map

**84 tėvai** (parent)
- OLD: two parents standing with a child between them
- NEW: a mother and father standing side by side, arrows indicating both adults, their small child standing apart beside them

**88 brolis** (brother)
- OLD: two brothers — an older and a younger boy — side by side, an arrow indicating one
- NEW: two brothers close in age and alike in features, side by side, an arrow indicating one

**97 prezidentas/prezidentė** (president)
- OLD: a male president and a female president at matching plain podiums, side by side
- NEW: a male president and a female president at matching plain podiums, side by side, the Lithuanian tricolor draped on the wall behind them

**98 kaimynas/kaimynė** (neighbor)
- OLD: two neighbours — a man and a woman — greeting each other over a garden fence
- NEW: two neighbours — a man and a woman — greeting each other from opposite sides of a low garden fence, one on each side

**101 vaikas** (child)
- OLD: a child playing with a ball
- NEW: an age row — a baby, a child, a teenager, and a grown adult — one bold arrow indicating the child

**104 draugas/draugė** (friend)
- OLD: two friends — a man and a woman — shaking hands
- NEW: two friends — two men — with arms around each other's shoulders, laughing together

**106 žaidėjas/žaidėja** (player)
- OLD: two players — a man and a woman — with a ball on a sports field
- NEW: two players — a man and a woman — in plain sports jerseys and shorts with a ball on a sports field

**111 studentas/studentė** (student)
- OLD: two students — a man and a woman — at desks with books
- NEW: two university students — a man and a woman — young adults with books in a lecture hall, a lecturer at the lectern behind them

**124 vadovas/vadovė** (manager)
- OLD: two managers — a man and a woman — at a desk directing workers
- NEW: two managers — a man and a woman — standing before seated staff, one pointing at a wall chart, directing the work

