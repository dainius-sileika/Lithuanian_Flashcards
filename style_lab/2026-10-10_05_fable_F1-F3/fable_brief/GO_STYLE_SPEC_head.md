# Lietuvių 625 — Art Style Specification (files 1.7.1)

## Direction — GOVERNING PRINCIPLE: deadpan civic procedure

### House style — one publication
Every card should look like a single page torn from the SAME fictional 1981
Lithuanian vocational training manual. Deck-wide coherence is the goal: a
learner flipping 500 cards should believe they are scanned pages of one
publication, one printing process, one house illustrator. Consistency comes
from three fixed things — the frozen style clause, the per-category visual
grammars (go_grammars.py), and a human QA/re-roll pass — NOT from expecting a
probabilistic renderer to obey a template every time. Bias hard, then catch
the misses.


The deck is rendered as pages torn from a Soviet civil-defense
(Grazhdanskaya Oborona, "GO") instructional manual — the wall-mounted
emergency-procedure posters produced by Voenizdat and hung in workplaces,
schools, and training rooms from the mid-1950s through the 1980s.

The governing principle is **deadpan civic procedure**. Every image is staged
as one calm, numbered step in a procedure that every citizen is presumed to
already half-know. Catastrophe is never dramatized; it is *bureaucratized* —
folded into civic routine and taught with the same flat, patient, instructional
temperature as a poster on how to file paperwork. The horror may be fully
present (rubble, gas masks, fire, stretchers) but the emotional volume is turned
all the way down. The message is never "be afraid"; it is "here is what you do,
in order, and you will be alright."

This flatness-over-horror is the entire soul of the style. It is the *sincere
original* of the joke that American duck-and-cover manuals and Fallout's Vault
Boy tell ironically: a friendly diagram teaching you to survive the
unsurvivable, with no wink at all. We want that deadpan calm — not "scary,"
not "cheerful cartoon."

Two structural commitments follow:
- **Figures are types, not individuals.** Anonymous everypersons — clerks,
  housewives, schoolchildren, gas-masked workers. The style is about the
  coordinated *many* performing a procedure, never the exalted one. (This is
  the deepest break from the superseded 0.4 heroic-agitprop direction.)
- **The diagram is the voice.** Because we strip all text, the diagrammatic
  overlays carry the "manual" feeling in its place: directional arrows, dashed
  motion / wind-direction lines, circular zoom-in detail insets, and small
  numbered callout dots. Lean into these.

### Rendering register
Economical **semi-realistic gouache illustration** — opaque, matte, no oil
gloss — with confident black outlines and flat economical shading. Technical-
manual draftsmanship: legible before it is beautiful. Reproduced as if by
four-color offset lithography on cheap absorbent paper: faint halftone dot,
muted saturation, dun paper drinking the color. (Historical note: the
constrained palette is authentic — Soviet lithographers aimed "to make four
colors look like twenty-four.") NOT heroic oil painting, NOT flat cartoon.

### Hard exclusions
No readable text or lettering; no Soviet state symbols (hammer-and-sickle,
red star, portraits, slogans); no glossy oil rendering; no heroic sunrise
lighting; no vibrant/saturated color; no watermark; no border.

## Palette (cooled & greyed institutional set — supersedes 0.4 warm palette)
The 0.4 hues remain the family, desaturated ~15–20% and cooled toward the
overcast-corridor mood. Brick-orange is an *accent used sparingly* as the
alert color, never the field.
- Pale cream / grey   #E4DCC8  (paper / ground)
- Blue-grey teal      #3C5E5A  (cooled from #2F6B5E; fields, coveralls, shadow)
- Dun / tan           #B8A176  (cooled ochre; earth, wood, kraft)
- Brick-orange alert  #B5482F  (sparing accent only: flags, fire, hazard signs)
- Charcoal            #2C2620  (outlines, linework, callouts)

## Master prompt template (owned by the GO Generator; only {SUBJECT}/{SCENE} vary)
"1970s Soviet civil defense (grazhdanskaya oborona) instructional manual
illustration of {SUBJECT}, {SCENE}, {OVERLAYS}, economical semi-realistic
gouache illustration with confident black outlines and flat matte shading,
deadpan instructional calm, anonymous everyperson figures drawn as types,
muted cool institutional palette of desaturated blue-grey teal, tan and dun,
sparing brick-orange alert accent, on pale cream-grey ground, four-color offset
print feel with faint halftone dots and cheap absorbent paper texture, matte
finish, overcast mid-century emergency-procedure mood, no readable text, no
lettering, no watermark, no border, no state symbols, no glossy oil painting,
no heroic sunrise lighting, no vibrant saturated color"

## Generation settings (Z-Image-Turbo via HF Space mcp-tools/Z-Image-Turbo)
- Resolution: 864x1152 (3:4) portrait is the poster-native default;
  1024x1024 (1:1) for square flashcards after style lock
- Steps: 8; random seed during exploration; record seed of every accepted image
- Auth: run authenticated (HF_TOKEN in env) for quota; anonymous throttles fast

## Consistency rules for mass production
- QA gate (1.7, the guessability test): before a card passes QA, ask —
  if you did not already know the target word, could you readily infer it
  from the MAIN image alone? If not, the card fails regardless of style
  compliance. Insets must SUPPORT the target meaning (or at least not
  compete with it); a beautiful inset that votes for a neighbouring word
  (workers in a basement on a "city" card) is a FAIL.
- Population follows the place (1.7): location cards show the people who
  characteristically use them, dressed for that place (children at school,
  white coats at hospital, young civilians at the club); workers appear
  where workers belong (factories, ports, construction). Person cards use
  "typical role", not "working role" — a patient rests, a fan cheers.
- Population follows the setting for ALL nouns (1.7.1): the baseline human in
  any noun inset is a CIVILIAN, not a coverall worker. Coveralls appear only
  where the setting is genuinely a work setting — the Materials class by
  default, plus specific tool/industry rows (engine, machine oil, tool) pinned
  worker in deck_builder. The grammar inset prose no longer hard-codes
  "worker"; it names a neutral person and the engine dress class decides.
- Insets never confuse the meaning (1.7.1): every inset must support the target
  (best), or at least be attractive and on-theme; it must NEVER depict anything
  mistakable for a neighbouring subject. This gate now lives in the prompt
  (go_generator INSET_MEANING_RULE), not only in human QA, to cut re-rolls.
- Style clause is defined ONCE in the GO Generator and never edited per-image;
  only {SUBJECT} and {SCENE}/staging vary
- Record the full prompt of every accepted image in the master CSV ledger. NOTE
  (1.7): on the OpenAI gpt-image-1.5 backend there is NO seed to record (the
  field is blank); the prompt is the reproducibility record. Seeds exist only on
  the Z-Image fallback path.
- Figures always anonymous types; overlays always present (subtle for nouns)
- Disambiguation pairs (girl/daughter etc.) staged per Fluent Forever notes
- Category words: multi-subject compositions (e.g. gyvūnas = dog, cat, fish)
- Occasional Lithuanian staging (Vilnius, rural Lithuania) where apt

## Architecture
- go_generator.py   — reusable "Grazhdanskaya Oborona Generator" engine
                      (style + feeling + palette + overlays + generation).
                      Importable, CLI-runnable, project-agnostic.
- go_grammars.py    — the executable design bible: category -> semantic class
                      (13 classes at 1.6: the 11 validated noun classes plus
                      "attribute" for adjectives/color clusters and "chart" for
                      the category-multi words, both inset-free); route() maps a
                      wordlist row to its class.
- noun_flashcards.py — grammar DEMO app (one noun per class; spot checks).
- verb_flashcards.py — verb DEMO app; context C default / D accent; actor
                      dress class threaded (1.6).
- deck_builder.py   — the PRODUCTION runner (1.6): reads master_wordlist.csv,
                      routes every depictable row, collision-proof keys
                      ({row#}_{slug}), wordlist numbering, per-verb staging
