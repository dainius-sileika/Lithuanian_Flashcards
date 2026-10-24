# Back-of-card context notes — where they go (Fable, 2026-10-17; extended per owner's review notes)

Owner's decision: the phrase variant/register lines go on the backs **now**, not after the audio. `context_notes.csv` is the first batch.

Data: `context_notes.csv`, **80 rows** (key, lithuanian, context_line, variant_tu_jus, source_url, confidence, source_note). 54 high, 16 medium, 10 unverified. Coverage: every phrase card whose meaning hinges on register or a near-synonym — the greeting / farewell / thanks / please / apology sets, the jūs-form questions and imperatives (each with its tu or jūs variant in `variant_tu_jus`, 28 rows), noriu vs norėčiau, the wish formulas (genitive wishes vs the su-pattern), the "of course" / "just a moment" / "great" clusters and the two time questions.

Sources actually read: the "Kalbos etiketas" chapter of *Kompiuterinis lietuvių kalbos žinynas* (ed. P. Kniūkšta, Šviesa 2004; the reference en.wiktionary itself cites for prašom/prašau), Ivanauskaitė & Hilbig 2023 (*Taikomoji kalbotyra* 19) for the tu/jūs principle, en/lt.wiktionary entries, Jasiūnaitė 1997 (*Kalbotyra* 46) for sudie, the Wikivoyage phrasebook, and en.wiktionary conjugation tables for kalbėti, galėti, gyventi, dirbti, turėti, veikti, eiti, atleisti, norėti, užrašyti. Variant forms of pakartoti, sėstis, iškviesti, pasveikti, gelbėti could not be fetched (rate limit) and are marked as unverified forms inside otherwise-sourced rows. **vlkk.lt could not be fetched from this session** (Cloudflare challenge, direct and via the fetch tool); the VLKK consultations named in `source_note` (8094 laba diena, 9416 prašom/prašau) are unread.

The 10 unverified rows are the "of course" cluster (žinoma / aišku / be abejo), "just a moment" (akimirką / minutėlę), the "great" cluster (puiku / šaunu / nuostabus) and Kiek tai kainuoja?; their lines are my own shading and are flagged for the owner to confirm or cut before they reach a back.

Findings that touch the deck itself, all flagged in `source_note`:
- **Postposed prašau.** The reference marks *Pakartokite, prašau / Užrašykite, prašau / Kalbėkite lėčiau, prašau / Sėskitės, prašau* (imperative + prašau) as an "atbulinis prašau", a Russian-pattern calque, and recommends *Prašom pakartoti* etc. (§7.2–7.3). Modern speech uses the postposed form constantly and VLKK's current line could not be checked. Owner's call whether the four cards' Lithuanian stays; the back note carries the recommended form either way.
- *dėkui* is not more casual than *ačiū* (absolute synonyms per the reference); the gloss "thanks" implies otherwise.
- *Į sveikatą!* to a sneezer is marked improper outside family joking; the deck's confusable "Bless you (same words)" should be reconsidered.
- *Iki pasimatymo* is classed with farewells for people you are close to, not as a neutral "see you".
- *Skanaus* is recorded as common but the reference prefers *Gero apetito! / Skanių pietų!*.
- One tangent, not pursued: A2-0954 *Ar galiu mokėti kortele?* (pay by card) sits oddly in a 1981 setting.

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
The `variant_tu_jus` column is appended to the same field at build time as a second short line (e.g. "tu: Kalbėk lėčiau"), so one field carries both; no second field.
CSS (`anki/go_theme.css`): `.usage { font-size: 0.85em; line-height: 1.35; opacity: 0.8; margin: 0.5em 1.2em 0; text-align: left; }` — small, below the answer, never on the front.

Data path: `build_apkg.add_a2_notes()` reads `a2_build/context_notes.csv` by `key` (promoted from `pilot_round2/` once the owner has read the lines) and fills `usage`; every other note gets `""`. The sentence note type (S-0051) has its own fields; the executor adds the same line to its back the same way.

Cost, stated plainly: adding a field is the schema change the 2026-10-17 study-order note declined ("conflicting notes on import unless note types are merged, then a one-way sync"). The same note already tells existing users to delete the deck and import the new package, so a display field rides on the reimport the owner has accepted. If he wants to hold the no-schema-change line instead, the fallback is to pack the line into `fem` (empty on every PHRASE row; already rendered on the back as `.forms`) — it works, and it is a hack the public repo would carry. I recommend the field.

## Sets covered (80 rows)

Greetings: labas / sveiki / laba diena / labas rytas / labas vakaras / labanakt / sveiki atvykę / užeikite / alio. Farewells: viso gero / sudie / iki / iki pasimatymo / iki rytojaus / geros dienos. Thanks and replies: ačiū / dėkui / labai ačiū / prašau / prašom / nėra už ką / nieko tokio / nieko baisaus / į sveikatą. Apology: atsiprašau (×2) / atleiskite / gaila. Requests: ar galite / ar galėtumėte / ar galite pakartoti / pakartokite / užrašykite / kalbėkite lėčiau / sėskitės / sąskaitą prašau / ar galite rekomenduoti / ar turite / noriu / norėčiau (×3). jūs-questions with tu variants: ar kalbate, koks jūsų vardas, iš kur jūs, kur gyvenate, kuo dirbate, kiek jums metų (+ S-0051), kaip sekasi / man gerai / viskas gerai / šiaip sau; tu-phrases with jūs variants: kur tu eini, ką veiki, greitai pasveik. Imperatives: eikite tiesiai, iškvieskite gydytoją, gelbėkit. Wishes and occasions: sėkmės, geros kelionės, gero savaitgalio, skanaus, su gimtadieniu, sveikinu, laimingų Naujųjų metų, linksmų Kalėdų, su šventėmis. Introductions: malonu susipažinti. Clusters: žinoma / aišku / be abejo; akimirką / minutėlė; puiku / šaunu / nuostabus; kiek valandų / kuri valanda; kiek (tai) kainuoja.
