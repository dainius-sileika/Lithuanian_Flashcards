# Lietuvių 625 — Art Style Specification (files 1.6.1)

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
- Style clause is defined ONCE in the GO Generator and never edited per-image;
  only {SUBJECT} and {SCENE}/staging vary
- Record seed + full prompt of every accepted image in the master CSV ledger
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
                      table, --only re-roll flag, --dry-run, pending-decision
                      guard. This is the Cowork hand-off entry point.

## File batches ledger
- files 0.1 — prototype: 6 notes, espeak audio, flat SVG art
- files 0.2 — v2 neural audio, poster palette CSS, restyled cards
- files 0.3 — detailed flat-style dog proofs; style superseded
- files 0.4 — heroic Govorkov agitprop spec; approved dog proof (seed 811725);
              direction later superseded
- files 0.5 — THIS spec: pivot to Grazhdanskaya Oborona civil-defense
              instructional style; governing principle "deadpan civic
              procedure"; cooled palette; GO Generator engine + noun/verb apps
              (Z-Image-Turbo backend)
- files 0.6 — backend swap to OpenAI gpt-image-1.5 (quality medium); prompt
              strategy inverted to CONCEPT-FORWARD (name the style, let the
              competent model carry palette/texture) with the decomposed
              Z-Image clause retained as a selectable fallback; Lithuanian
              symbol substitution (tricolor / Vytis / Columns of Gediminas)
              baked into the fixed clause; small Lithuanian detail-labels baked
              into art, headword/gloss left to Anki fields
- files 0.6b — refined register to "late Soviet instructional wall chart /
              civil-defense training poster (1975-1985), technical textbook
              illustration, NOT propaganda"; ANNOTATION RULE: label only curated
              SUPPORTING Lithuanian words, target word never shown; multiple
              supporting inset panels; header/gloss remain Anki chrome
              (image leaves a clean top band); landscape default, portrait a
              one-word toggle
- files 0.6c — baked-in printed-card chrome restored (red header band
              "LIETUVIŲ KALBA • NNN", thin red border, red footer band with
              category + number) since review randomizes card order; symbol
              options expanded to include the Vytis Cross (double-barred cross,
              Lithuanian Special Operations Forces) and the Lithuanian Riflemen's
              Union (Šauliai); chrome supplied by the app layer so the engine
              stays project-agnostic
- files 0.6d — removed the legacy "faint civic procedure behind the subject"
              backdrops (CIVIC_BACKDROPS / pick_backdrop). The GO feeling is
              carried by the rendering register, insets, palette, and chrome,
              not a literal background scene; a clean subject reads better as a
              flashcard. Engine is now free of app-level staging. Verb settings
              (real action contexts like a washbasin) are unaffected.
- files 0.7 — TEXT REMOVED from the image (gpt-image can't reliably spell
              diacritic-heavy Lithuanian; the original cards only looked correct
              because they were less busy, used simpler words, and ran at higher
              quality). Front is now clean art: dominant subject/action, 2-3
              visual insets, symbol box, and EMPTY red header/footer bars for the
              card feel. Correct vocabulary moves to a companion cards.csv as the
              single source of truth for the Anki layer (rendered as normal
              fields, no fragile overlay positioning). Figures are ordinary
              Soviet-era Lithuanian workers in plain muted blue-grey civil-defense
              coveralls (not military olive). Landscape default; portrait a
              one-word toggle for phone-first review.
- files 0.8 — after the first full text-free batch: period-correct headwear
              (soft flat cloth workers' cap, never a baseball cap) fixing the
              anachronism and the "looks American" drift; anatomical cutaways
              BANNED everywhere (they failed as body-horror; external close-ups
              only, simple fruit/object slices still fine); verbs hard-capped at
              EXACTLY 2 insets (a civic procedural sequence — the strongest GO
              element, kept by choice — plus a Lithuanian symbol box) to stop the
              stray-hand / nonsense-panel pileup. Nouns' 2-3 inset balance kept.
- files 0.9 — SYMBOLS reduced to flag-only and OCCASIONAL: intricate heraldry
              (Vytis, Columns of Gediminas, Vytis Cross, Šauliai) garbled like
              text did, so only a small Lithuanian tricolor where it fits, not on
              every card, no coats of arms. Light anatomy steer (five-finger
              hands, clean paws/feet) to cut the extra-finger/distorted-paw rate
              (can't eliminate; re-roll the rest). Black kirza-style work boots
              (black was standard issue; brown was the officer/long-service
              exception). Considered the styling essentially locked after this.
- files 0.6e — (mislabelled 0.6b until 1.6) surgical revision after reviewing ChatGPT's self-authored
              meta-prompt. Adopted two structural ideas: (1) diagrammatic
              DECOMPOSITION — 2-4 inset panels showing how the subject/action
              works (parts, sequence, cross-section, silhouette), the authentic
              GO "how it works" convention; (2) sharpened ANNOTATION rule —
              labels are SUPPORTING vocabulary with leader lines, never the
              target word. Deliberately REJECTED: baked-in header band (kept as
              editable Anki chrome), verbose two-color/palette re-specification
              (regression toward the over-specification concept-forward
              replaced). Rationale: the loved reference cards came from a
              one-sentence prompt, validating concept-forward.
- files 1.0 — styling LOCKED. Verb treatment finalised: context C default
              (floating institutional scene) + context D accent (consequence
              panel) for telic verbs; kelti/nešti split onto vertical vs
              horizontal axes.
- files 1.1 — legacy supporting-label machinery stripped from the app layer
              and cards.csv (baked text was dropped at 0.7); engine keeps its
              optional text=True path for other projects.
- files 1.2 — per-category VISUAL GRAMMARS made executable (go_grammars.py);
              the noun app composes per category.
- files 1.3 — three dress classes (worker / professional / civilian) threaded
              as an engine `people` param; conditional phrasing + no-stray-
              figure guard.
- files 1.5 — consolidation batch: this spec becomes the single canonical
              document (GO Design Bible + Manual of Editorial Illustration
              folded in and deprecated); all 11 noun grammars validated on
              real output.
- files 1.5.1 — frame-containment clause (nothing crosses the red bars).
- files 1.6 — production hardening after the full-code audit, prompts for the
              locked classes UNCHANGED. Engine: transient-error retry with
              backoff on the OpenAI path; cards.csv carries lt_pron + gender.
              Grammars: two new classes — "attribute" (adjective marked-
              contrast / color clusters, inset-free) and "chart" (category-
              multi specimen charts, inset-free) — plus route(). Verb app:
              actor dress class parametrised (dance/kiss/marry no longer
              render as coverall workers). NEW deck_builder.py production
              runner (collision-proof keys, wordlist numbering, per-verb
              staging, --only re-roll, --dry-run, pending-decision guard).
              Companion data batch 2.1: corrected stress marks (209 fixes),
              all 437 subject phrases drafted, STAGING doc (category-multi +
              disambiguation designs, verb telicity table, 8 open questions).
- files 1.6.1 — the 8 open design questions DECIDED by the owner and
              implemented (companion wordlist 2.2, 429 generable rows):
              Q1 Color rows 69-78 carry the m/f pairs; 518-527 superseded.
              Q2 letter/consonant/vowel generate via a new engine single-glyph
                 exception (glyph=True: only the subject letterform permitted;
                 red bars and all other text prohibitions kept).
              Q3 phone/laptop = deadpan CHUNKY anachronism (period-plausible
                 casing, thick antenna / heavy keyboard).
              Q4 heart = hand-on-chest + schematic symbol; brain = standalone
                 textbook-plate schematic (approved as drafted).
              Q5 die = plain uninscribed gravestone with wilting flowers,
                 phrase-complete, no motion insets; kill = fly swat.
              Q6 wedding (vestúvės) and sign (ženklas) promoted to the deck.
              Q7 dual m/f person rows (19 rows) = ONE card with TWO figures,
                 one masculine one feminine.
              Q8 eiti stays twice (walk / go, staged distinctly).
              Glyph, wedding and gravestone rows routed "attribute"
              (phrase-complete, inset-free) via deck_builder.OVERRIDE_CLASS.
- files 1.7 — the GUESSABILITY pass, from the owner's QA of cards 1-127.
              New QA gate: target word must be inferable from the main image;
              insets must support it. go_grammars: Location people default
              CIVILIAN; place cards populated by characteristic occupants;
              person grammar "role" not "working role"; SCENE_TAIL exposed.
              deck_builder: NOUN_STAGING (per-row main/people/inset overrides
              for rows 9, 22, 24, 32, 34, 35, 36, 40, 41, 43, 48, 55, 93, 94,
              107, 114, 137); OVERRIDE_CLASS adds 51/56/101 attribute,
              52 chart, 53 nature. Wordlist 2.3: 22 subject phrases sharpened
              (24, 32, 35, 36, 37, 39, 40, 41, 48, 51, 52, 53, 56, 84, 88, 97,
              98, 101, 104, 106, 111, 124). Prompt boilerplate otherwise
              UNCHANGED; house style untouched.
