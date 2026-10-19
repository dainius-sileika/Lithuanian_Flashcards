# AnkiWeb description — Lietuvių Flashcards, A1 subdeck, release v3.0

Drafted 2026-10-19 (A1_WRAPUP item F1; planner drafts, **owner approves the text**). The counts are
placeholders in braces: the final study order v3 may move a few cards between A1 and A2, so they are
filled in from the build manifest (`build_reports/builds/Lietuviu_Flashcards_v3.0_A1.apkg.json`) after
the build. The values the data gave on 2026-10-19 are listed at the end for reference.
The paste-ready HTML is `docs/ANKIWEB_DESCRIPTION_A1_v3.0.html`. The owner's decisions follow the text.

---

**Lietuvių Flashcards — A1 (v3.0)**

Lithuanian from zero to A1 through pictures, phrases and sentences. The first of two subdecks; A2 follows as a separate package.

**What is in the deck**

{A1_CARD_COUNT} cards, ordered by usefulness: survival words and everyday phrases come first.

- {A1_PICTURE_COUNT} picture cards for words
- {A1_PHRASE_COUNT} phrase cards (greetings, thanks, asking for things)
- {A1_CLOZE_COUNT} cloze cards for function words and forms
- {A1_SENTENCE_COUNT} sentence cards with a picture

**How a card works**

The front shows a picture with an English caption in the band below it. The back gives the Lithuanian word with its stress mark, gender and forms (genitive, present and past, or the feminine), and the English gloss. Phrase cards add a note on when to use the phrase. Cloze cards show a Lithuanian sentence with a blank and the English as a hint; sentence cards pair the blank with a picture.

Stress marks are taken from Wiktionary, kirtis.info and the LKŽ, never guessed.

**The pictures**

The art is an original house style: a civil-defence training manual from a free Lithuania of 1981. The pictures are AI-generated in that style and reviewed by hand. A few cards show real interwar places and people: the Lituanica with Darius and Girėnas, Basanavičius as the doctor, Čiurlionis as the artist, with a painting after one of his public-domain works on the easel.

**Audio**

{A1_HUMAN_AUDIO_COUNT} cards carry recordings by the author, a native speaker, reading the word and its forms. {A1_SYNTH_AUDIO_COUNT} older cards still use a synthetic voice, and the newer A1 cards are silent until the next update.

Fonts: Brygada 1918 (SIL Open Font Licence), embedded. In night mode, leave image inversion off.

**Upgrading from an earlier version**

The note types changed in v3.0. Delete the old deck before importing this one; study history from older versions does not carry over. From v3.0 onward the card IDs are stable, so future updates import in place and keep your progress.

**Licence and credits**

CC BY-NC 4.0: share and adapt for non-commercial use, with credit and a link to the source. Word list from the Fluent Forever 625, extended from A1 English word lists. Pictures, data and recordings by the author.

Source and issues: https://github.com/dainius-sileika/Lithuanian_Flashcards

---

## Owner decisions before upload

1. **Licence wording.** The repo `LICENSE` is CC BY-NC 4.0 (not BY-NC-SA) and names the owner in the required attribution string. The text follows it. If a different licence is wanted for the published deck, change `LICENSE` first, then this line.
2. **Signing the description.** The rule "name no living person" was applied to the owner too: the text says "the author" and leaves the credit to the GitHub link and `LICENSE`. Decide whether to sign it with a name.
3. **Audio sentence.** The brief said "the 520 core cards have native-speaker recordings"; the data says otherwise. `audio_source.tsv` marks 427 recordings as human and 93 as `azure-neural` (the files differ: 48 kbps, no ID3 tag). On 2026-10-19, of the 446 base cards in the A1 block, 427 were human, 18 synthetic, 1 without audio (`531_batonas`); the 75 base rows with `level = A2` are exactly the 75 remaining synthetic ones. If the 18 were re-recorded without updating the ledger, correct the ledger first. The retag for order v3 may move some of these between subdecks; recount from the manifest.
4. **Historical cards left out on purpose.** Gustaitis (A2-0782), the 1939 basketball team (138 komanda, `level = A2`; A2-1297) and the two posters (*Velnio nuotaka* on A2-1191, *Milžino paunksmė* on A2-1360) are A2-level rows and not in this package. They belong in the A2 description. 097 prezidentas and 123 autorius ship without likenesses. If order v3 retags any of them A1, add them to "The pictures".
5. **Title** for the AnkiWeb share, e.g. "Lietuvių Flashcards — Lithuanian A1 (pictures, audio, stress marks)". Decide also whether the v2.0 share is replaced or kept (F3).
6. **Tags** on AnkiWeb, e.g. `lithuanian lietuvių a1 vocabulary pictures audio`.

## Placeholder values from the data on 2026-10-19 (order v2, for reference only)

| placeholder | value | source |
|---|---|---|
| `{A1_CARD_COUNT}` | 1,198 | 1,163 A1 rows in `study_order.csv` + 35 A1 sentences |
| `{A1_PICTURE_COUNT}` | 708 | 446 base rows `level = A1` + 262 A2-list `IMG` rows `level = A1` |
| `{A1_PHRASE_COUNT}` | 134 | A2-list `PHRASE` rows `level = A1` |
| `{A1_CLOZE_COUNT}` | 321 | A2-list `CLOZE` 315 + `PAIR` 6, `level = A1`, all with `example_lt` |
| `{A1_SENTENCE_COUNT}` | 35 | `sentences.csv` rows `level = A1` |
| `{A1_HUMAN_AUDIO_COUNT}` | 427 | `audio_source.tsv` = human, base rows `level = A1` |
| `{A1_SYNTH_AUDIO_COUNT}` | 18 | `audio_source.tsv` = azure-neural, base rows `level = A1` |

These assume every picture row resolves an image at build time; the manifest's A1 note count is the number to publish.
