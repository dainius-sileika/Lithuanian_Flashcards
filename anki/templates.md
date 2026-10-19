> **SUPERSEDED by docs/DESIGN_SPEC_CURRENT.md on 2026-10-19** — kept as history; where this file and the code disagree, the code and the spec are right.

# Anki note type — "Lietuvių GO"

**You normally don't need this.** `build_apkg.py` creates this note type
automatically and bundles it into `Lietuviu_Flashcards.apkg`. This file documents
the layout for anyone who wants to rebuild it by hand or tweak the design.

## Fields

Imported from `cards_anki.csv` (repo root). The note type has these fields, in
order:

`key`, `lithuanian`, `english`, `gender`, `gen_sg`, `pres3`, `past3`, `fem`,
`number`, `category`, `image`, `audio`, `pron`

- **nouns** carry `gen_sg` (genitive singular → shows declension): *namas · namo*
- **verbs** carry `pres3` · `past3` (principal parts): *šokti · šoka · šoko*
- **adjectives** carry `fem` (feminine): *geras · gera*
- `pron` is the stress-accented headword (e.g. *šuõ*), shown as a pronunciation line
- `image` holds a full media tag, e.g. `<img class="art" src="001_suo.jpg">`, and
  `audio` holds `[sound:001_suo.mp3]`. Embedding the tags in the field (rather than
  building them from the filename in the template) lets Anki's *Check Media* see the
  files as used, so they render everywhere and aren't flagged as unused.

> The build transcodes the repo's WebP images to **JPEG** for the `.apkg`, because
> some Anki clients don't render WebP inside cards. Set `IMG_FMT=webp` to override.

## Front template (question = image)
```html
<div class="page">
  <div class="bar"><span class="plate">LIETUVIŲ KALBA</span><span class="plate">{{number}}</span></div>
  {{image}}
  <div class="bar bottom"><span>{{category}}</span><span>?</span></div>
</div>
```

## Back template (answer = word + audio + forms + gloss)
```html
<div class="page">
  <div class="bar"><span class="plate">LIETUVIŲ KALBA</span><span class="plate">{{number}}</span></div>
  {{image}}
  <div class="answer">
    <div class="word">{{lithuanian}}</div>
    {{#pron}}<div class="pron">{{pron}}</div>{{/pron}}
    {{audio}}
    {{#gender}}<div class="gender {{gender}}">{{gender}}</div>{{/gender}}
    {{#gen_sg}}<div class="forms">{{lithuanian}} · {{gen_sg}}</div>{{/gen_sg}}
    {{#pres3}}<div class="forms">{{lithuanian}} · {{pres3}} · {{past3}}</div>{{/pres3}}
    {{#fem}}<div class="forms">{{lithuanian}} · {{fem}}</div>{{/fem}}
    <hr id="answer">
    <div class="gloss">{{english}}</div>
  </div>
  <div class="bar bottom"><span>{{category}}</span><span>{{number}}</span></div>
</div>
```

## Styling
Paste the contents of `go_theme.css` into the **Styling** box (shared by front & back).

## Note on data quality
Grammar forms (genitive, principal parts, feminine) and stress accents are
sourced/machine-assembled and are being verified by a native speaker — treat them
as provisional in this beta.

## Note type 2 — "Lietuvių GO Cloze" (A2, 2026-10-11)

Native Anki cloze model (`model_type = CLOZE`), built by `build_apkg.py` from the A2 list
(`a2_build/a2_wordlist.csv`, rows with `route` CLOZE or PAIR). Fields, in order:

`Text`, `SentenceEN`, `Word`, `Pron`, `Gender`, `Forms`, `Gloss`, `Number`, `Category`, `Audio`, `Key`

- `Text` is `example_lt` with the {braces} turned into `{{c1::…}}` — Anki blanks the form itself.
- Front: the sentence with the blank and the English sentence as a hint. Back: the sentence
  revealed, the headword, its stress-marked form, gender symbol, forms line (genitive /
  principal parts / feminine), gloss, audio.
- Styling: `go_theme.css` plus a small `.cloze-text / .hint` block defined in `build_apkg.py`.
- Picture rows of the A2 list (IMG, PHRASE) use note type 1 above; their key is the list id
  (`A2-0108`) and their image is looked up by that id in `images_a2/`, `out_phrases/`, `out_deck_a2/`.

## Identity and study order (2026-10-11)
- Note GUID = `genanki.guid_for(key)` — the permanent card key (`001_suo`, `A2-0108`, `S-0001`). Model and deck ids are constants. A re-import therefore updates fields in place and keeps review history. Keys are never renamed or reused.
- New-card position comes from `study_order.csv` (made by `build_study_order_v3.py`; usefulness-first order adopted 2026-10-17, v3 with dependency ordering 2026-10-19). Anki applies it to cards it imports for the first time only. Owner's line for existing collections: deck coherence over old study history — delete the deck and import the new package (sorting by Key and repositioning only reproduces the wordlist order).
- The cloze note type has `SentenceAudio` (owner's recording of the example sentence, `audio_a2/<id>_s.mp3`) and `Image` (filled for the sentence cards `S-####`; when present the English hint is hidden on the front).
