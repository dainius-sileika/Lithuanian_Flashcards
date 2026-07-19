# Anki note type — "Lietuvių GO"

Paste these into a new **Note Type** (Tools → Manage Note Types → Add → Clone "Basic",
then Cards…). Fields must match the columns in `out_deck/cards.csv`.

## Fields  (import from `cards_anki.csv` in the repo root)
`key`, `lithuanian`, `english`, `gender`, `gen_sg`, `pres3`, `past3`, `fem`,
`number`, `category`, `image_file`

- **nouns** carry `gen_sg` (genitive singular → shows declension): *namas · namo · m.*
- **verbs** carry `pres3` · `past3` (principal parts): *šokti · šoka · šoko*
- **adjectives** carry `fem` (feminine): *geras · gera*
- Forms are machine-generated and **flagged VERIFY** — accents and irregulars
  (esp. the 88 blank -is/-uo/irregular noun genitives) need a native pass.

> **Image field**: put the media filename, e.g. `001_suo.webp`, and copy the
> `images/` webp files into your Anki `collection.media` folder. In the CSV the
> `image_file` column already holds `NNN_slug.png` — bulk-rename the reference to
> `.webp` (or re-export cards.csv pointing at the webp).
>
> **Gender field** should be `m`, `f`, `n`, or empty — the CSS colour-codes the chip.

## Front template (question = image)
```html
<div class="page">
  <div class="bar"><span class="plate">LIETUVIŲ KALBA</span><span class="plate">{{number}}</span></div>
  <img class="art" src="{{image_file}}">
  <div class="bar bottom"><span>{{category}}</span><span>?</span></div>
</div>
```

## Back template (answer = word + details)
```html
<div class="page">
  <div class="bar"><span class="plate">LIETUVIŲ KALBA</span><span class="plate">{{number}}</span></div>
  <img class="art" src="{{image_file}}">
  <div class="answer">
    <div class="word">{{lithuanian}}</div>
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

## Verb forms (your note)
Add two fields `Form3sg` and `FormPast` and populate the conjugation triple
(infinitive · 3rd-person singular · past), e.g. **šokti · šoka · šoko**. The back
template above shows the line only when `Form3sg` is filled, so nouns are
unaffected. I can auto-populate these for all ~78 verbs (see chat) — they follow
regular patterns but need a native check.
