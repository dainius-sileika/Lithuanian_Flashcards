# Audit of the card BACKS (Fable, 2026-10-17)

Scope: every note type `build_apkg.py` builds — A1/A2 picture notes ("Lietuvių GO"), A2 phrase notes (same model), A2 cloze ("Lietuvių GO Cloze"), sentence cards (cloze model with Image). Read: `build_apkg.py` templates, `anki/go_theme.css`, `anki/templates.md`, `cards_anki.csv` (521), `a2_build/a2_wordlist.csv` (1,709), `a2_build/sentences/sentences.csv` (55). Rendered real backs with the live templates (`backs_audit/render_backs.py`, phone viewport 390×844 @2x, light and night mode); screenshots in `backs_audit/png/` (`_strip1..4.png` are side-by-side comparisons). Accuracy sample: 60 random notes (30 A1, 30 A2) checked against kirtis.info (Wiktionary rate-limits the cloud IP: 429 on every call) → `backs_audit/accuracy_sample_kirtis.csv`. Data errors → `backs_audit/data_errors.csv` (182 rows). Nothing fixed.

## 1. Findings, ranked

### Severity 1 — wrong information shown to the learner
1. **118 A2 feminine *-a* nouns carry the accusative plural as "genitive singular"**: *viza · vizas, sveikata · sveikatas, pamoka · pamokas, problema · problemas, klaida · klaidas, tiesa · tiesas, pagalba · pagalbas, informacija · informacijas…* (should be *-os*). Source: the rule-derived gen_sg in `build_a2.py` (the `check` column says "gen_sg: rule-derived"). Every one of these backs teaches a wrong form. Fix is mechanical (−as → −os for F nouns in −a), then re-verify the other rule-derived endings (−is masculine vs feminine: *kulkšnis* is F, *-ies*, we have M, *kulkšnio*). A1 has no such error (1 heuristic hit, *moteris · moters*, is correct).
2. **Sentence-card backs show a grammar tag where the meaning should be**: the `Gloss` field is filled with `grammar_point` ("present 3sg; accusative object") and rendered in the gloss style ("— present 3sg; accusative object"), while the English sentence sits as an italic hint under the Lithuanian. The learner's eye lands on the tag. (`add_sentence_notes`, field order.)
3. **9 A1 prons have no stress mark at all** (*ji, jūs, jie, minia, taika, kortelė, data, lėtas, seklus*): the back shows the plain word twice and the learner never hears where the stress falls. 5 more A1 prons and 1 A2 pron use Wiktionary's *i + U+0307 + accent* sequence (*i̇̀lgas, karei̇̃vis, tėvai̇̃, praei̇̃ti, gami̇̀nti*), which renders as a dotted i with a stacked mark in Georgia/Noto (visible on `A1-picture_446_ilgas.png`).

### Severity 2 — the back works against production or against itself
4. **Anki scrolls to `<hr id="answer">`, which sits *below* the word and forms, just above the English gloss.** On any phone where the back is taller than the screen, revealing the answer scrolls the Lithuanian off the top and lands the eye on the English. The anchor must sit above the word. (Both models.)
5. **A1 verbs (86) store the accented form in `lithuanian`** (*sprógti*), nouns do not (*šuo* + pron *šuõ*). Result: verbs show the accented word, then the identical accented pron line, then a forms line in accented small caps; nouns show plain + accented. Inconsistent, and the accented headword breaks Anki's "type the answer" and search. One convention: plain headword in `lithuanian`, accents only in `pron`.
6. **Adjectives are given a gender symbol pair ♂♀ (A1 "M/F", 93 rows)**; A2 adjectives get none. 29 of those 93 have no feminine form at all — the 10 colours carry a *noun* genitive instead (*raudonas · raudono*), so a colour adjective is displayed as a noun paradigm. (People/job nouns *mokytojas, prezidentas* with M/F are a different, legitimate case.)
7. **The English gloss field holds editorial notes** in 355 A2 rows ("small square; car park, playground (head word)", "small, fine (smulkūs pinigai = small change)", "to whom; what for (dat. of kas)"). On the back this reads as the meaning. Needs a short display gloss and a separate note column.
8. **The cloze FRONT shows the English sentence by default** (hint under the blank) — contrary to the owner's decision (English hint on tap). The back then shows the English sentence *and* the gloss, so English appears twice above the fold while the headword is the third element.
9. **Phrase backs are bare**: no pron (141 of 154 blank), no audio yet, no forms; just the phrase, a rule and the gloss. Acceptable as a minimum, but nothing tells the learner the register (tu/jūs) or the stress of the phrase, and there is no space for the variant forms the benchmark asked for (*Ar galite / Ar galėtumėte*).
10. **Plate numbering and section names are three systems**: A1 "1", A2 "0001" (collides visually with A1 numbering), sentences "S 0001"; bottom-band labels are "Animal", "Verbs", "Work & culture", "Misc", "Math", and the Lithuanian "Sakiniai". The top band is the constant "LIETUVIŲ KALBA" on every card. The owner's new decision (English section name in the top band, plate number + English in the bottom band) supersedes all of this.

### Severity 3 — polish
11. **Double frame**: the image already carries drawn red bands, and the template draws red bars above and below it, so every card has two frames (owner has decided: builder trims the drawn bands). Visible on every screenshot.
12. **Fonts**: Georgia / Times — Georgia is absent on Android, so AnkiDroid falls back to Noto Serif; the look differs by platform and neither is the PT Serif / Old Standard TT the design calls for. No `@font-face`.
13. **Night mode**: `.card` has an explicit cream background, so the page stays cream (good: `A1-picture_001_suo_night.png`); only the area outside `.page` goes dark. Fine. AnkiDroid's optional image inversion would wreck the plates — document "do not invert images".
14. **Forms line in small caps** (`font-variant: small-caps`, teal, 1rem): the feminine *ilga* and the genitive are the smallest text on the card, and accented small caps (*SPRÓGSTA*) look wrong; these are the forms we want produced.
15. **Empty fields**: conditionals are correct; no stray labels appear. The sentence back renders an empty `.word` block (blank line) because `Word` is empty; the gloss em-dash prefix is unconditional (gloss is never blank, so harmless).
16. **Mobile fold**: at 390×844 the whole back of a picture note just fits; with Anki's bars the gloss is clipped but the word is visible. Keep the back within one screen: image at most ~45% of viewport height on the back (CSS `max-height: 42vh` on `.art` when inside the answer), or move the thumbnail below the forms.
17. **Polysemy pairs** (*086_vyras* man / *093_vyras* husband) show identical backs; acceptable, but a one-word disambiguator in the gloss ("husband (vyras)") would help.

### Accuracy sample (60 notes vs kirtis.info)
Stress: 46 match, 5 differ, 9 not resolvable (multi-stress or my query lost a diacritic). The 5 differences: *taika* (we have no mark; kirtis *taikà*), *ilgas* and *kareivis* (encoding, see 3), two artefacts of my query. Gender: 38 match, 0 differ. Verb principal parts: all 14 verbs in the sample are valid 3rd-person present/past forms per kirtis. Genitives: all A1 genitives in the sample valid; the three A2 feminine *-a* nouns in the sample (*šaka, dešra, slyva*) all show the *-as* error above. So: A1 forms are sound; A2 rule-derived forms are not, and the error is systematic rather than random.

## 2. Proposed back design (house style, production first)

Common rules (both models): the answer word first and largest; stress and audio immediately under it; then the forms the learner must produce; then the English, smaller; the picture last, as a plate thumbnail. `<hr id="answer">` directly after the top band so the reveal never scrolls past the word. English section name in the top band; plate number + English in the bottom band. Fonts embedded (`_PTSerif-Regular.ttf`, `_PTSerif-Italic.ttf`, `_PTSerif-Bold.ttf`, `_OldStandardTT-Regular.ttf`; OFL; verify ąčęėįšųūž and the stress diacritics render before adoption). The image is trimmed of its drawn bands by the builder, so the template's bars are the only frame.

### CSS additions (sketch, extends go_theme.css)
```css
@font-face{font-family:"PT Serif";src:url("_PTSerif-Regular.ttf")}
@font-face{font-family:"PT Serif";font-style:italic;src:url("_PTSerif-Italic.ttf")}
@font-face{font-family:"PT Serif";font-weight:700;src:url("_PTSerif-Bold.ttf")}
@font-face{font-family:"Old Standard TT";src:url("_OldStandardTT-Regular.ttf")}
.card{font-family:"PT Serif",Georgia,serif}
.bar,.plate{font-family:"Old Standard TT","PT Serif",serif}
.answer .word{font-size:2.6rem;line-height:1.05;margin-top:.35em}
.answer .pron{font-size:1.25rem;font-style:italic;color:var(--teal)}
.forms{font-variant:normal;font-size:1.15rem;color:var(--ink)}   /* produced forms: full size, not small caps */
.forms b{font-weight:700}                                        /* the form being taught in bold */
.reg{font-size:.85rem;color:var(--dun);font-variant:small-caps;letter-spacing:.08em}
.gloss{font-size:1.05rem;color:#5a5047;margin-top:.6em}
.thumb{display:block;width:62%;margin:.9em auto 0;border:1px solid rgba(151,48,31,.35)}
.caption{font-family:"Old Standard TT",serif;font-size:.8rem;letter-spacing:.06em}
hr#answer{border:0;height:0;margin:0}                            /* anchor only, invisible */
```

### A1/A2 picture note — back
```html
<div class="page">
  <div class="bar"><span class="plate">{{section}}</span><span class="plate">{{number}}</span></div>
  <hr id="answer">
  <div class="answer">
    <div class="word">{{lithuanian}}</div>
    {{#pron}}<div class="pron">{{pron}}</div>{{/pron}}
    {{audio}}
    {{#gender}}<div class="gender">{{gender}}</div>{{/gender}}
    {{#gen_sg}}<div class="forms">{{lithuanian}} · <b>{{gen_sg}}</b></div>{{/gen_sg}}
    {{#pres3}}<div class="forms">{{lithuanian}} · <b>{{pres3}}</b> · <b>{{past3}}</b></div>{{/pres3}}
    {{#fem}}<div class="forms">{{lithuanian}} · <b>{{fem}}</b></div>{{/fem}}
    <div class="gloss">{{english}}</div>
    <img class="art thumb" src="{{image_file}}">
  </div>
  <div class="bar bottom"><span class="caption">{{number}}</span><span class="caption">{{english}}</span></div>
</div>
```
Fields to add: `section` (English, from the study-order unit), `image_file` (bare filename; the `image` field with the full tag stays for Check Media). Adjectives: no gender symbol; the feminine on the forms line. Nouns: symbol + genitive. Verbs: principal parts. Plural-only: the `pl.` tag already exists.

### Phrase note — back
Same template plus two lines under the word: `{{#variant}}<div class="forms">{{variant}}</div>{{/variant}}` for the other register (*Ar gali… / Ar galite…*) and `{{#reg}}<div class="reg">{{reg}}</div>{{/reg}}` (informal · formal · neutral). Pron line = phrase stress assembled per word (102 rows already have it), audio = owner's recording. Thumbnail = the situation picture. New fields: `variant`, `reg`.

### Cloze note (A2 word in sentence) — back
```html
<div class="page">
  <div class="bar"><span class="plate">{{Section}}</span><span class="plate">{{Number}}</span></div>
  <hr id="answer">
  <div class="cloze-text">{{cloze:Text}}</div>
  <div class="answer">
    <div class="word">{{Word}}</div>
    {{#Pron}}<div class="pron">{{Pron}}</div>{{/Pron}}{{Audio}}{{SentenceAudio}}
    {{#Gender}}<div class="gender">{{Gender}}</div>{{/Gender}}
    {{#Forms}}<div class="forms">{{Forms}}</div>{{/Forms}}
    <div class="gloss">{{Gloss}}</div>
    <div class="hint">{{SentenceEN}}</div>
  </div>
  <div class="bar bottom"><span class="caption">{{Number}}</span><span class="caption">{{Gloss}}</span></div>
</div>
```
Front: `{{cloze:Text}}` + `{{hint:SentenceEN}}` (tap to reveal) + the English gloss of the *target* in the bottom band (owner's caption decision). English sentence moves to the back, under the word, not above it.

### Sentence card — back
Same cloze model; fields filled differently: `Word` = the full Lithuanian sentence (large), `Gloss` = the English sentence, a new small `.note` line for the grammar point, `Image` on the front (full) and as a thumbnail on the back. `Section` = the unit the sentence belongs to, not "Sakiniai".

### Field-level cleanups the templates assume
- Plain headword in `lithuanian`; stress only in `pron` (A1 verbs).
- `pron` normalised to precomposed ì/ĩ (replace *i + U+0307 + mark* with the precomposed form, as `norm_accent` already does for A2).
- Display gloss ≤ 4 words; notes to a `notes` field that the back may show in small type or not at all.
- One plate numbering: A1 1–531, A2 continues from 1001 (or keep 0001 with an "A2 ·" prefix), sentences "S 1…".
- Section names in English from one list (the study-order units).

## 3. Data errors
`backs_audit/data_errors.csv` — 182 rows: 118 A2 genitive *-as* errors (high), 29 A1 M/F rows without feminine (10 colours high, 19 job nouns low), 9 prons without stress (medium), 6 U+0307 encodings (low), 86 accented A1 verb headwords (medium, 3 listed as examples), *kulkšnis* gender (medium), *metai* without pl/gender (low), plus the structural items (sentence Gloss field, A2 glosses with notes, plate numbers, section names, vyras duplicate).

## 4. Order of work (proposal)
1. Data: −as → −os on the 118; re-run the rule engine's output against kirtis.info for every rule-derived form (the API answers "K." for a genitive, "esam.l. IIIasm." for pres3); fix the 9 prons and 6 encodings; move A1 verb accents into `pron`; feminine forms for the colours; display glosses.
2. Templates: anchor, order, fonts, bands per the owner's decisions; cloze hint on tap; sentence fields.
3. Rebuild and re-screenshot with `render_backs.py` (extend the sample list), light and night, phone width, before packaging.
