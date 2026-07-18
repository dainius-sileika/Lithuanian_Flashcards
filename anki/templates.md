# Anki note type — "Lietuvių GO"

Paste these into a new **Note Type** (Tools → Manage Note Types → Add → Clone "Basic",
then Cards…). Fields must match the columns in `out_deck/cards.csv`.

## Fields
`Lithuanian`, `English`, `Pronunciation`, `Gender`, `Number`, `Category`, `Image`
— optional verb fields: `Form3sg`, `FormPast` (see below).

> **Image field**: put the media filename, e.g. `001_suo.webp`, and copy the
> `images/` webp files into your Anki `collection.media` folder. In the CSV the
> `image_file` column already holds `NNN_slug.png` — bulk-rename the reference to
> `.webp` (or re-export cards.csv pointing at the webp).
>
> **Gender field** should be `m`, `f`, `n`, or empty — the CSS colour-codes the chip.

## Front template (question = image)
```html
<div class="page">
  <div class="bar"><span class="plate">LIETUVIŲ KALBA</span><span class="plate">{{Number}}</span></div>
  <img class="art" src="{{Image}}">
  <div class="bar bottom"><span>{{Category}}</span><span>?</span></div>
</div>
```

## Back template (answer = word + details)
```html
<div class="page">
  <div class="bar"><span class="plate">LIETUVIŲ KALBA</span><span class="plate">{{Number}}</span></div>
  <img class="art" src="{{Image}}">
  <div class="answer">
    <div class="word">{{Lithuanian}}</div>
    <div class="pron">{{Pronunciation}}</div>
    {{#Gender}}<div class="gender {{Gender}}">{{Gender}}</div>{{/Gender}}
    {{#Form3sg}}<div class="forms">{{Lithuanian}} · {{Form3sg}} · {{FormPast}}</div>{{/Form3sg}}
    <hr id="answer">
    <div class="gloss">{{English}}</div>
  </div>
  <div class="bar bottom"><span>{{Category}}</span><span>{{Number}}</span></div>
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
