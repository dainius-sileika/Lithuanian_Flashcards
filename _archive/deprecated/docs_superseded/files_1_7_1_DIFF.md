# files 1.7.1 — DIFF for sign-off (noun-inset dress + inset-meaning gate)

> Two changes on top of 1.7. Diffs generated from snapshots `*.bak17` (1.7) →
> live (`1.7.1`). No wordlist change (still 2.3). `verb_flashcards.py` untouched.

## Why
1. **Noun insets were populated by coverall workers by default.** Everything
   outside Job/People/Location fell through to `DEFAULT_PEOPLE = "worker"`, and
   the grammar inset prose literally said "worker" (a *worker* wearing a dress, a
   *worker* drinking coffee). Nouns should follow the same principle verbs already
   do: dress the human to the setting — **civilian unless the setting genuinely
   suits a worker.**
2. **The 1.7 guessability gate lived only in human QA**, which is what drove the
   re-roll cost (one card took 66 tries). Encoding the gate in the prompt itself
   should catch confusable insets before a human has to.

## Change A — noun-inset dress follows the setting (go_grammars.py)
- `DEFAULT_PEOPLE`: **worker → civilian** (the baseline human is now an ordinary
  civilian).
- `PEOPLE_CLASS`: **+ `Materials: worker`** (workshop/industrial samples). Job
  stays professional; People/Location stay civilian.
- Inset prose **de-hard-codes "worker"** in creature / food / beverage / vehicle /
  garment / object — now neutral ("a person" / "people"), letting the engine dress
  class decide.
- Net effect by category: **worker** = Materials (+ tool/industry rows, see
  Change C); **professional** = Job; **civilian** = everything else (Animal, Food,
  Beverages, Transportation, Clothing, Body, Home, Electronics, Misc, Math, Art,
  Nature, People, Location). Existing `NOUN_STAGING` per-row `people` overrides
  still win.

```diff
--- go_grammars.py.bak17
+++ go_grammars.py
@@ PEOPLE_CLASS / DEFAULT_PEOPLE @@
 PEOPLE_CLASS = {"Job": "professional", "People": "civilian",
-                "Location": "civilian"}
-DEFAULT_PEOPLE = "worker"
+                "Location": "civilian", "Materials": "worker"}
+DEFAULT_PEOPLE = "civilian"
@@ NOUN_GRAMMARS insets — de-hard-code "worker" @@
-  creature: "a civic scene of an ordinary worker tending or handling it"
+  creature: "a civic scene of a person tending or handling it"
-  food:     "a plain canteen scene of workers with the food"
+  food:     "a plain canteen scene of people with the food"
-  beverage: "a worker drinking it in a canteen or rest area"
+  beverage: "a person drinking it in a canteen or rest area"
-  vehicle:  "the vehicle in use, driven or loaded by workers"
+  vehicle:  "the vehicle in use, driven or loaded by ordinary people"
-  garment:  "a worker wearing it"
+  garment:  "a person wearing it"
-  object:   "a worker using it in a plain civic setting"
+  object:   "a person using it in a plain civic setting"
```

## Change B — inset-meaning gate baked into the prompt (go_generator.py)
New `INSET_MEANING_RULE`, appended on the OpenAI path whenever insets are present
(applies to nouns and verbs alike):

```diff
--- go_generator.py.bak17
+++ go_generator.py
@@ after INSET_RULE @@
+INSET_MEANING_RULE = (
+    "Every inset must serve the meaning of THIS card: at best it should make the "
+    "main subject easier to recognise; at the least it must stay attractive and "
+    "on-theme. An inset must NEVER depict something that could be mistaken for a "
+    "different, neighbouring subject, and must never compete with or pull "
+    "attention away from what the card is teaching."
+)
@@ _prompt_openai(): if insets @@
     segs.append(inset_note if inset_note else INSET_RULE)
+    segs.append(INSET_MEANING_RULE)
     segs.append(NO_CUTAWAY_RULE)
```

## Change C — tool/industry worker rows (deck_builder.py)
With civilian now the noun default, the few rows whose insets genuinely belong to
workers are pinned back via the existing per-row `people` override. **Editable
seed list** — extend as later tool/industrial rows are reviewed. (Materials cards
get worker dress by category, so they need no per-row entry.)

```diff
--- deck_builder.py.bak17
+++ deck_builder.py
@@ NOUN_STAGING @@
-    195: {"inset_note": (... machine oil, mechanic insets ...)}
+    195: {"people": "worker",           # tepalas — carers are mechanics
+          "inset_note": (... machine oil, mechanic insets ...)}
+    21:  {"people": "worker"},   # variklis (engine)
+    245: {"people": "worker"},   # įrankis (tool)
```

## Validation (dry-run, no API)
`python deck_builder.py --dry-run` on representative rows confirms the intended
dress and that `INSET_MEANING_RULE` is present on every insetted card:

| card | category | dress (1.7.1) | was (1.7) |
|------|----------|---------------|-----------|
| 001 suo (dog) | Animal | **civilian** | worker |
| 057 kepurė (hat) | Clothing | **civilian** | worker |
| 172 kava (coffee) | Beverages | **civilian** | worker |
| 019 padanga (tire) | Transportation | **civilian** | worker |
| 323 metalas (metal) | Materials | **worker** | worker |
| 195 tepalas (machine oil) | Food→tool/ind. | **worker** | worker |
| 245 įrankis (tool) | Home→tool/ind. | **worker** | (n/a, ungenerated) |

## Impact on existing cards
1.7.1 changes only affect **future** generations and re-rolls. The 190 images
already on disk were made under the old worker default and are unchanged. Noun
cards whose insets should now be civilian will only update when re-rolled — a
separate, larger pass to schedule (not part of this revision).

## Post-sample QA fixes (wordlist 2.4 + staging)
Found while QA'ing the first live 1.7.1 batches; all per-row, house style untouched.
- **#232 lubos (ceiling)** — wordlist 2.4 phrase rewrite (ceiling plane, not a
  hanging lamp) + `NOUN_STAGING` (ceiling-forward main, cornice/corner insets).
  Blind-read went from "lamp" → "ceiling".
- **#19 padanga (tire)** — `NOUN_STAGING` inset override (tread / tire-stack /
  changing a tire); removes the vehicle-grammar engine-bay inset that voted
  "engine".
- **#235 spyna (padlock)** — OpenAI *output* moderation false-positive ("illicit")
  on a plain padlock; `NOUN_STAGING` steers to a benign hardware depiction
  (closed shackle, no hands forcing/picking). Passes on re-roll.
- **#238 kiemas (yard)** — wordlist 2.4 phrase rewrite + `NOUN_STAGING`: the old
  "yard with a fence" blind-read as "gate" (gate centred, all insets were gate
  latches). Now the enclosed yard SPACE and its use (swept ground, woodpile,
  bench, laundry, chickens; sweeping inset). Blind-read → "yard".

Wordlist is now **2.4** (2.3 preserved as `master_wordlist.csv.bak23`): the two
phrase rewrites above on top of 2.3.
