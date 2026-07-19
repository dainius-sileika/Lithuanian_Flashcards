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
