# files 1.7 / wordlist 2.3 — DIFF for sign-off (guessability pass) — AS SHIPPED

> **Corrected record (2026-07-13).** The earlier draft of this file under-reported
> `NOUN_STAGING` by five rows (#39, #97, #179, #195, #208), which were added while
> re-rolling cards past the original 1–127 review. This version matches the code
> that actually shipped. The stale original is preserved as
> `files_1_7_DIFF.md.bak_stale`. Diffs below are generated from the archived
> snapshots `*.bak161` (1.6.1) → `*.bak17` (1.7).

## Summary of 1.7
The **guessability pass**. New QA gate: the target word must be inferable from the
main image alone, and insets must support it — never vote for a neighbouring word.
Implemented as (a) `go_grammars` population-follows-the-place changes, (b) a
per-row `NOUN_STAGING` table in `deck_builder`, (c) `OVERRIDE_CLASS` re-routes, and
(d) 22 sharpened wordlist subject phrases. `go_generator.py` is **unchanged** at
1.7 (still 1.6.1). House style, palette, red bars, no-text rules: untouched.

**Shipped scope:** staging edits reach **#208** (maistas). Plain generation then
continued through the Home block to **#231** (grindys). Frontier at interruption:
**cards #1–231 complete, except #227** (raidė — deliberately skipped; glyph cards
are excluded because diacritic-heavy letterforms corrupt).

---

## go_grammars.py (1.6.1 → 1.7)
```diff
--- go_grammars.py.bak161
+++ go_grammars.py.bak17
@@ NO_INSET_CLASSES / PEOPLE_CLASS @@
-# category -> dress class for any people on the card
-PEOPLE_CLASS = {"Job": "professional", "People": "civilian"}
+# category -> dress class for any people on the card.
+# 1.7: population follows the place — Location cards default to civilians
+# (schools, banks, clubs are civilian spaces); industrial locations override
+# back to worker per-row via deck_builder.NOUN_STAGING.
+PEOPLE_CLASS = {"Job": "professional", "People": "civilian",
+                "Location": "civilian"}
 DEFAULT_PEOPLE = "worker"
@@ NOUN_GRAMMARS["place"] @@
-        "main": "Draw it from the front as a clear architectural elevation.",
+        "main": ("Draw it from the front as a clear architectural elevation, "
+                 "with the people who characteristically use it visible at or "
+                 "around it, dressed for that place."),
         "insets": ["a detail of the entrance or a characteristic feature",
-                   "a glimpse of the interior, or of people using it"]},
+                   "a glimpse of the people who characteristically use it, "
+                   "inside or at the entrance, doing what one does there"]},
@@ NOUN_GRAMMARS["person"] @@
-        "main": "Draw them in their typical working role.",
-        "insets": ["a tool or object of their trade",
-                   "a plain civic scene of them at work"]},
+        "main": "Draw them in their typical role, dress, and setting.",
+        "insets": ["an object characteristic of them in that role",
+                   "a plain civic scene of them in their usual role"]},
@@ new module constant @@
+# the frozen framing clause appended to every main composition (1.7: exposed
+# as a constant so deck_builder per-row main overrides keep the house framing)
+SCENE_TAIL = (" Keep the subject large and dominant in the foreground, "
+              "floating cleanly on the cream paper on a simple background.")
@@ compose_class() @@
-    scene = (g["main"] + " Keep the subject large and dominant in the "
-             "foreground, floating cleanly on the cream paper on a simple "
-             "background.")
+    scene = g["main"] + SCENE_TAIL
```

## deck_builder.py (1.6.1 → 1.7)
Header bumped to 1.7. `OVERRIDE_CLASS` gains **51, 56, 101 → attribute; 52 →
chart; 53 → nature**. New `NOUN_STAGING` table with **22 rows** (the full shipped
set), and `build_call` applies it after `compose_class`.

**`NOUN_STAGING` rows as shipped (22):**
`9, 22, 24, 32, 34, 35, 36, 39, 40, 41, 43, 48, 55, 93, 94, 97, 107, 114, 137, 179, 195, 208`

```diff
--- deck_builder.py.bak161
+++ deck_builder.py.bak17
@@ OVERRIDE_CLASS @@
 OVERRIDE_CLASS = {137: "attribute", 379: "attribute",
-                  227: "attribute", 350: "attribute", 351: "attribute"}
+                  227: "attribute", 350: "attribute", 351: "attribute",
+                  51: "attribute", 56: "attribute", 101: "attribute",
+                  52: "chart", 53: "nature"}
@@ new NOUN_STAGING table (row -> {main?, people?, inset_note?}) @@
+NOUN_STAGING = {
+    9:   {main, inset_note}   # sparnas: wing alone, not a whole bird
+    22:  {people=civilian, inset_note}   # bilietas: ticket's story
+    24:  {inset_note}         # miestas: skyline + crossing, no basement workers
+    32:  {inset_note}         # viešbutis: hotel room / reception / suitcase
+    34:  {people=worker}      # ūkis: the one Location that belongs to workers
+    35:  {inset_note}         # teismas: gavel / facade / scales
+    36:  {inset_note}         # mokykla: classroom / schoolyard
+    39:  {inset_note}         # miestelis: town houses + kiosk, not the church  [ADDED post-draft]
+    40:  {inset_note}         # universitetas: lecture hall / library
+    41:  {inset_note}         # klubas: club entrance / record player
+    43:  {inset_note}         # parkas: playground / bench / flowerbed
+    48:  {people=professional, inset_note}   # ligoninė: white coats
+    55:  {inset_note}         # bankas: teller / banknotes / safe
+    93:  {inset_note}         # vyras (married): wedding rings
+    94:  {inset_note}         # žmona (married): wedding rings
+    97:  {inset_note}         # prezidentas: state-leader insets, not a gavel  [ADDED post-draft]
+    107: {inset_note}         # sirgalius: sport, not markets
+    114: {main, people=professional, inset_note}   # pacientas: patients rest
+    137: {people=civilian}    # vestuvės: guests, not coverall workers
+    179: {main}               # gėrimas: drinks-only chart, no people          [ADDED post-draft]
+    195: {inset_note}         # tepalas: machine oil, mechanic insets          [ADDED post-draft]
+    208: {main}               # maistas: foods-only chart, no people           [ADDED post-draft]
+}
@@ build_call() @@
-    if int(r["#"]) == 137:
-        people = "civilian"          # wedding guests are not coverall workers
+    st = NOUN_STAGING.get(int(r["#"]), {})
+    if "main" in st:
+        scene = st["main"] + SCENE_TAIL
+    people = st.get("people", people)
+    if "inset_note" in st:
+        inset_note = st["inset_note"]
```
(The five rows marked `[ADDED post-draft]` are the ones missing from the earlier
draft of this document.)

## go_generator.py
**Unchanged at 1.7** — still the 1.6.1 engine. The 1.7 work is entirely in the
grammars, the staging table, and the wordlist.

## master_wordlist.csv (2.2 → 2.3) — subject_phrase_EN changes
Verified against `master_wordlist.csv.bak22`: exactly these **22** rows changed,
nothing else.

| # | word (EN) | old → new (abridged) |
|---|-----------|----------------------|
| 24 | miestas (city) | compact street → busy panorama, crowds + cars among mid-rises |
| 32 | viešbutis (hotel) | a hotel building → …with a doorman and an arriving guest with a suitcase |
| 35 | teismas (court) | a courthouse building → a courtroom, judge at the bench, gavel in hand |
| 36 | mokykla (school) | a schoolhouse → …with young children with satchels arriving |
| 37 | biuras (office) | desks → desks, clerks in everyday clothes at typewriters/telephones |
| 39 | miestelis (town) | small-town main street → town square, single church spire, open fields beyond |
| 40 | universitetas | main building → …columned portico, students with books on the steps |
| 41 | klubas (club) | club building with people entering → young people dancing in a hall at evening |
| 48 | ligoninė (hospital) | a hospital building → …with an ambulance at the entrance |
| 51 | šalis (country) | roadside border post → wall map of a whole country, bold border, small tricolor at centre |
| 52 | pastatas (building) | a large multi-storey building → three buildings side by side (house, office, hall) |
| 53 | žemė (ground) | bare earth → mound of dark soil, spade thrust in, cupped hands of soil |
| 56 | vieta (location) | wall map with pin + scenes → a pointing finger on one circled spot of a local map |
| 84 | tėvai (parent) | two parents with a child → mother + father, arrows on both adults, child apart |
| 88 | brolis (brother) | older + younger boy, arrow → two brothers close in age & alike, arrow on one |
| 97 | prezidentas | two podiums → …with the tricolor draped on the wall behind |
| 98 | kaimynas (neighbor) | greeting over a fence → …from opposite sides of a low fence, one each side |
| 101 | vaikas (child) | child with a ball → age row (baby/child/teen/adult), one bold arrow on the child |
| 104 | draugas (friend) | man + woman shaking hands → two men, arms around shoulders, laughing |
| 106 | žaidėjas (player) | man + woman with ball → …in plain sports jerseys and shorts |
| 111 | studentas | at desks → two university students, young adults, lecture hall, lecturer behind |
| 124 | vadovas (manager) | at a desk directing → standing before seated staff, one pointing at a wall chart |

## Data / ledger state at 1.7 (post-run)
- **190 images** in `out_deck/`; every one now has a `ledger.csv` + `cards.csv`
  row (rows `172_kava` and `178_pienas` were backfilled — see 1.7.1 notes).
- **Seeds are blank on the OpenAI path** — `gpt-image-1.5` returns no seed; only
  the Z-Image fallback records one. Reproducibility rests on the recorded prompt.
  (The spec's "record seed + full prompt" rule is corrected to reflect this.)
- Re-roll evidence lives in the ledger, not `reroll_log.txt` (which contains only
  `003,004 rerolled`): **47 cards were re-generated**, the worst being
  **#114 pacientas ×66**, #39 ×15, #32/#36/#43/#97 ≈×10.
