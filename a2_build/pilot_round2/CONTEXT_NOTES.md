# Back-of-card context notes — where they go (Fable, 2026-10-17)

Data: `context_notes.csv` (32 rows: key, lithuanian, context_line, source_url, confidence, source_note). 28 high, 3 medium (Sveiki, Sudie, Užeikite), 1 unverified (nieko baisaus). The main source is the "Kalbos etiketas" chapter of *Kompiuterinis lietuvių kalbos žinynas* (ed. P. Kniūkšta, Šviesa 2004), read in full as PDF; it is the reference en.wiktionary itself cites for prašom/prašau. **vlkk.lt could not be fetched from this session** (Cloudflare challenge on every URL, direct and via the fetch tool); the two VLKK consultations that bear on these rows (8094 laba diena, 9416 prašom/prašau) are named in `source_note` as unread. The owner may want to open those two himself.

Two notes contradict a deck gloss and are flagged in `source_note`: *dėkui* is not more casual than *ačiū* (the reference calls them absolute synonyms), and *iki pasimatymo* is classed with farewells for people you are close to, not as the neutral "see you".

## Which field carries the note

The picture note type "Lietuvių GO" (`build_apkg.py` `GO_FIELDS`, 13 fields) has no free text field: `english` is on the **front** band (`card_frame._PIC_FRAME`), so a note there would leak the context onto the question side; `fem`/`gen_sg`/`pres3` are grammatical and rendered with separators.

**Recommendation: a 14th field `usage`, appended to `GO_FIELDS`** (order of the existing 13 unchanged), rendered on the back only, under the gloss:

```python
GO_FIELDS = ['key', 'lithuanian', 'english', 'gender', 'gen_sg',
             'pres3', 'past3', 'fem', 'number', 'category', 'image', 'audio', 'pron', 'usage']
```
in both back templates (`build_apkg.BACK` and `card_frame._PIC_FRAME`'s back), after `<div class="gloss">{{english}}</div>`:
```html
{{#usage}}<div class="usage">{{usage}}</div>{{/usage}}
```
CSS (`anki/go_theme.css`): `.usage { font-size: 0.85em; line-height: 1.35; opacity: 0.8; margin: 0.5em 1.2em 0; text-align: left; }` — small, below the answer, never on the front.

Data path: `build_apkg.add_a2_notes()` reads `a2_build/context_notes.csv` by `key` (promoted from `pilot_round2/` once the owner has read the lines) and fills `usage`; every other note gets `""`. The sentence note type (S-0051) has its own fields; the executor adds the same line to its back the same way.

Cost, stated plainly: adding a field is the schema change the 2026-10-17 study-order note declined ("conflicting notes on import unless note types are merged, then a one-way sync"). The same note already tells existing users to delete the deck and import the new package, so a display field rides on the reimport the owner has accepted. If he wants to hold the no-schema-change line instead, the fallback is to pack the line into `fem` (empty on every PHRASE row; already rendered on the back as `.forms`) — it works, and it is a hack the public repo would carry. I recommend the field.

## Phrase pairs covered

labas / sveiki / laba diena / labas rytas / labas vakaras / labanakt; viso gero / sudie / iki / iki pasimatymo / iki rytojaus; ačiū / dėkui / labai ačiū; prašau / prašom; nėra už ką / nieko tokio / nieko baisaus; atsiprašau (both cards) / atleiskite; ar galite / ar galėtumėte; kiek jums / kiek tau metų; kaip sekasi / man gerai; malonu susipažinti; sveiki atvykę / užeikite; alio.
