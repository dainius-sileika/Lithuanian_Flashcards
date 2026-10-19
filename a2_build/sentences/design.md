> **SUPERSEDED by docs/DESIGN_SPEC_CURRENT.md on 2026-10-19** — kept as history; where this file and the code disagree, the code and the spec are right.

# Sentence cards — design (Fable, cloud round 2026-10-11)

## The question
Do we break the Fluent Forever rule (no English on the front) to teach simple sentences, or is there another way — e.g. the owner's proposal: picture of a man at a counter with his hand out toward the server with coffee; on the answer side the Lithuanian sentence *and* English, so the picture starts to carry meaning?

## Decision: picture + Lithuanian cloze on the front; Lithuanian sentence + English on the back
The rule holds where it matters — nothing English on the front — and the owner's proposal is kept where it helps: the English appears on the **answer** side, next to the full Lithuanian sentence, so the picture, the sentence and the meaning fuse at the moment of checking.

Why not picture-only front → whole sentence back (the literal proposal)? A picture admits many true sentences (*Vyras geria kavą / Jis perka kavą / Kava karšta*); the learner cannot know which one is "right", so nothing is gradable and Anki's again/good becomes a coin toss. Fluent Forever's own sentence cards are clozes for this reason: the picture gives the meaning, the sentence gives the context, the blank gives one gradable answer.

Why not cloze alone (no picture)? Without a picture the front needs an English hint to fix the meaning, i.e. English on the front — the rule broken, and the sentence memorised as translation. With a picture the hint is unnecessary: `Vyras ____ kavą.` + a man drinking coffee → *geria*.

So the card:
- **Front:** picture (GO house style, the main picture carries the whole sentence's meaning) + the Lithuanian sentence with the target form blanked (`Vyras {{c1::geria}} kavą.`). Nothing English.
- **Back:** picture, the full sentence with the form revealed, the English translation of the sentence (owner's point: meaning association), the headword line of the blanked word (*gerti · geria · gėrė*), audio of the whole sentence (owner's recording, `audio_a2/S-0001.mp3`).
- The blank is the **grammar point** (the inflected verb, the case ending), never a content noun the picture would simply name — otherwise the card collapses into a picture-word card.

## Note type
`Lietuvių GO Cloze` gets an `Image` field (empty for the plain cloze rows of the A2 list, filled for sentence rows). One model serves both: `build_apkg.py` reads `a2_build/sentences/sentences.csv`, key = `S-####`, GUID = `guid_for(key)`, image `<dir>/S-####.webp|jpg`, audio `audio_a2/S-####.mp3`. Deck: by `level`. Tag `SENT`.

## When English appears
Only on the back, as the translation of the whole sentence (not of the blanked word alone). The A2 list's plain cloze rows (no picture) keep their English hint on the front — there the hint is the only way to fix the meaning; those are grammar/vocabulary drills, not picture cards.

## How many for A2
Fluent Forever suggests the first ~100 picture words, then sentences continuously. For this deck: **~150 sentence cards** across A1→A2 — roughly one for every 12 vocabulary cards — concentrated on the grammar A2 needs: present/past/future endings, the seven cases in their commonest uses (į + acc., locative, genitive of negation, dative experiencer *man reikia/patinka/skauda*, instrumental of means), reflexive verbs, modal + infinitive, comparatives. First batch here: 55 (`sentences.csv`), 35 built on A1 deck words, 20 reaching into P-A/P-B (*turėti, norėti, reikėti, važiuoti*). Grammar verified sentence by sentence (notes column); every word is a deck key or an A2 list id in `words_used`.

## Staging (staging.json)
One line per sentence, house rules: the main picture shows the whole proposition (the actor doing the action to the object), positive phrasing, 1981 free Lithuania, declared lettering only where the sentence needs it (prices, the age numeral, a temperature). Speech-act sentences (*Kiek kainuoja?*) use the question-mark bubble grammar from the phrase cards.

## Study order
Sentence cards are placed in `study_order.csv` after the unit that completes their words (next step: `build_study_order.py` reads `words_used` and inserts each sentence right after its last word; not yet implemented — they currently follow the A1 block).
