# Playbook: an evidence-based, flashcard-based language-learning system

Written 2026-10-17 from the Lithuanian GO deck (A0→A2). Meant to be reused for future language decks. Sources are listed at the end, each marked by how it was read. Confidence labels:
- **[PR]** peer-reviewed, read
- **[PR-2nd]** peer-reviewed, read through a summary
- **[V]** vendor or advocate material
- **[FP]** first-principles reasoning
- **[U]** unverified

## 1. What the evidence says (and doesn't)

**Retrieval and spacing are the main levers (high confidence).**
- Keep every item in the test loop. In Karpicke & Roediger 2008, items dropped after one correct recall fell from about 80% to about 35% a week later, and re-study added nothing [PR].
- Spacing replicates [PR].
- FSRS gives the same retention with fewer reviews; it does not make learning better. Its benchmark is run by its own authors [2nd]. Anki defaults: desired retention 0.90, re-optimise monthly [read].

**The cue on the front: pictures are not better than English (high confidence).**
- Lotto & de Groot 1998: translation pairs 81.9% vs. picture pairs 76.6% [PR].
- Carpenter & Olson 2012: no difference, and picture learners were overconfident [PR-2nd].
- Aleman 2022 (inside an adaptive spaced-retrieval system): no advantage for pictures [thesis, read].
- Yanagisawa, Webb & Uchihara 2020 (meta-regression): picture vs. text glosses made no difference, and L1 glosses beat L2 glosses [PR, abstract].
- Mahdi et al. 2024: single-mode glosses beat multi-mode [PR, abstract].
- Caution: the "picture + text beats text, g = 0.46" figure (Yun 2011) comes from glosses during reading, not flashcards. The same caveat applies to Yanagisawa and Mahdi. Direct flashcard evidence is thin; the firm finding is negative (pictures alone are not better).

**Cue congruency and transfer (moderate confidence).**
- Recall is best when the practice cue resembles the real-life cue (Lotto & de Groot congruency; Nakata 2016 on recall formats).
- In real life you start from an intention, which an English prompt approximates better than a drawing.

**Pictures can hurt recall of exact wording (moderate–high confidence).**
- Boers et al. 2017 [PR, abstract]; Boers' idiom work [PR-2nd].
- Phrase wording must come from text or audio, not the picture.

**Imagery helps abstract words most (moderate confidence).**
- Shen 2010 [PR, abstract]; Farley, Ramonda & Liu 2012 [PR-2nd].
- This is where symbolic insets earn their place.

**Concreteness (moderate confidence).**
- Concrete, imageable words are learned faster (de Groot & Keijzer 2000; Kole et al. 2020) [PR].

**Interference (small but real).**
- Semantically clustered sets raise wrong-word errors; spacing reduces them (Nakata & Suzuki 2019) [PR].
- Space confusable words apart. A uniform art style adds visual similarity.

**Direction (moderate confidence).**
- "Production beats recognition" did not replicate cleanly (Healy et al. 2025) [PR].
- Test the direction you need to perform. Recognition first, then production, is a safe order, not a proven one.

**Context (moderate confidence).**
- One sentence of context doesn't improve word retention (Webb 2007), but it teaches use.
- Word cards learn many words fast; they don't teach use (Nation). Sentence and cloze cards are for grammar and use.

**Size and time.**
- A2 vocabulary is roughly 1,500–2,500 words (Milton & Alexiou) [PR].
- Guided hours to A2 are about 180–200 for English learners [V]; more for harder languages [FP].
- A deck is one of Nation's four strands. Input, output and fluency must come from elsewhere: graded listening, a textbook, speaking.

**Rosetta Stone.**
- Method: hear, read, match a picture, no L1 [V].
- The favourable study (Vesselinov 2009) was vendor-commissioned [V].
- An independent government trial (Nielson 2011) saw 99.4% attrition [PR-2nd].
- Picture-matching is a pleasant recognition exercise, not evidence that pictures teach production.

**Fluent Forever, sorted.**
- **Supported:** Anki, retrieval, frequency-first words, early pronunciation, target-language answers.
- **Dogma:** "no translations", "pictures are more memorable", "make your own cards". The generation effect from self-made cards is lost in a premade deck.
- **What pictures genuinely buy:** a non-L1 cue, disambiguation (cup vs. mug), mood, branding, and motivation to open the deck.

## 2. Card architecture (as decided for the Lithuanian deck)

**Images are text-free.** All lettering lives in the card template, so one image serves every card type, nothing is misspelled by the image model, and it is sharp on a phone. Exception: lettering that is part of the object itself (a price tag, a calendar, "ONE DOLLAR") is declared per card and read back by QA.

**English caption on every front** (owner decision 2026-10-17), styled to the deck's aesthetic. The target language is always the answer.

**Backs:**
- Target word with stress or accent marks, gender and principal forms.
- Native-speaker audio (the owner records).
- A small English gloss.
- A thumbnail of the image.

**Card types:**

| Type | Front | Answer |
|---|---|---|
| Concrete nouns, verbs, adjectives, abstract nouns | Picture + English caption | Target word |
| Function words | Cloze in a target-language sentence; English hint on tap | The blanked word |
| Inflection | Cloze on the ending inside a short pattern sentence with a picture cue (e.g. *į parduotuvę* vs. *parduotuvėje*); contrast cards for case and stress pairs | The form |
| Phrases (proposal, paused) | 3-panel strip (situation → utterance → consequence) + a situation line; first-letter skeleton only as a hint | The phrase |

- Phrases also get an audio "Hear" card that shows them for the first time.
- Paradigm tables are reference material, not cards.

**Listening:** audio → meaning cards are worth adding (independent reviewer).

**Study order:** words → set phrases → sentences. Confusable words are spaced apart. Each card has a fixed ID, so updates change existing cards instead of adding duplicates (`guid_for(key)`).

**Load:** about 3,600 cards to A2 for an inflected language. At 15 new a day that's about 8 months and 25–40 minutes a day [FP; measure it in a pilot].

## 3. How to test a design question properly (independent reviewer)

- Don't judge your own deck if you know the language: native or heritage speakers judge clarity only.
- Use 6–8 real learners, a 30-word mini-deck, and conditions rotated by Latin square, so every word appears in every condition across learners.
- Run 10 days of normal Anki use, then a final test with a neutral cue (spoken L1 prompt → target; audio → meaning). Read the Anki review logs (lapses, time, retention) per condition.
- Fix the decision rule in advance: a non-default design must win by ≥10 points; otherwise keep the cheaper one.
- A single 10-minute exposure with day-2 recall gives floor scores and can't separate conditions.

## 4. Production lessons (image pipeline)

**Settle the aesthetic with blind, ranked owner surveys:**
- shuffled variants, drag-to-rank, ship ticks and per-image comments, read back from a database;
- measured paper tone (CIE L\*/b\*) to calibrate words like "aged cream";
- a separate strong model (Fable) to analyse results and write candidate prompts.

**Prompt rules that held:**
- Positive phrasing; naming a forbidden thing primes it.
- The main picture alone must carry the word; insets broaden it with variety, not repeats.
- Dead-matte finish (models add highlights otherwise).
- Distinct faces in groups; of two main figures, only one faces the viewer.
- Props named in global rules prime onto every card. A "well-sweep" example put wells everywhere.
- Per-card staging lines for hard cards; class grammars for easy ones.
- Real places on most scene cards, hand-assigned. Keyword auto-matching produced absurd pairings.

**Engine choice by blind dual-render on a stratified 30-card sample** (scenes, figures, objects), with the decision rule fixed in advance. Sunburst won 19/30 at a third of the cost.

**QA:**
- A vision model reads every image: undeclared text, target word in the art, declared strings read back exactly, a cold-read guessability check.
- Plus the owner's review pages (OK/Redo + note per card, stored in a database), with the owner's notes turned into staging fixes.

**Versioning:**
- Never overwrite images, audio or packages until a deliberate clean-up; superseded files go to `_rerolled/` or `_superseded/`.
- Text lives in git; heavy media stays out of git.
- Keep append-only logs out of cloud-synced folders. Proton Drive produced edit-conflict copies and file locks.

**Division of labour that worked:** a strong model plans and judges (aesthetics, research, staging); a cheaper model executes the plan; an independent "blind" reviewer evaluates major plans.

## 5. Sources

Read:
- Karpicke & Roediger 2008: https://www.brucehayes.org/Teaching/papers/2008_Roediger_Karpicke_Science.pdf
- Lotto & de Groot 1998: https://research.unipd.it/retrieve/e14fb267-6261-3de1-e053-1705fe0ac030/Learning%20Method.pdf
- Aleman 2022 (thesis; summarises Carpenter & Olson 2012, Chen 1990, Plass et al. 1998): https://gmwpublic.studenttheses.ub.rug.nl/445/1/Thesis_AF_Aleman.pdf
- Healy, Schneider & Kole 2025: https://www.mdpi.com/2076-328X/15/5/692
- Yun 2011 (dissertation): https://kuscholarworks.ku.edu/bitstream/1808/6459/1/Yun_ku_0099D_10940_DATA_1.pdf
- Vasiljevic 2015: https://e-flt.nus.edu.sg/wp-content/uploads/2020/09/v12n12015/vasiljevic.pdf
- Kole et al. 2020: https://bilingualism.northwestern.edu/wp-content/uploads/2020/01/languages-05-00002.pdf
- Nakata & Suzuki 2019: https://www.cambridge.org/core/journals/studies-in-second-language-acquisition/article/effects-of-massing-and-spacing-on-the-learning-of-semantically-related-and-unrelated-words/F58BA8D70385603B9C42E408BFCB8A10
- Nation, "My ideal vocabulary teaching course": https://vuw-web.matrix.squiz.cloud/lals/resources/paul-nations-resources/paul-nations-publications/publications/documents/my-ideal-vocabulary-teaching-course.pdf
- Milton & Alexiou: https://www.enl.auth.gr/gala/14th/Papers/English%20papers/Milton&Alexiou.pdf
- Cambridge guided learning hours: https://support.cambridgeenglish.org/hc/en-gb/articles/202838506-Guided-learning-hours
- Anki manual (FSRS): https://docs.ankiweb.net/deck-options.html
- CEFR global scale: https://www.coe.int/en/web/common-european-framework-reference-languages/table-1-cefr-3.3-common-reference-levels-global-scale
- Lithuanian accentuation: https://en.wikipedia.org/wiki/Lithuanian_accentuation
- CASALC review (Webb 2007, Laufer & Shmueli 1997, Prince 1996): https://journals.muni.cz/casalc-review/article/download/14192/11864
- McQuillan 2019 (advocate; summarises Nielson 2011): https://mail.sdkrashen.com/content/articles/and_then_there_were_none_mcquillan_2019.pdf
- Rosetta Stone "How it works" (vendor): https://www.rosettastone.com/how-it-works/

Abstract only:
- Yanagisawa, Webb & Uchihara 2020: https://cambridge.org/core/journals/studies-in-second-language-acquisition/article/how-do-different-forms-of-glossing-contribute-to-l2-vocabulary-learning-from-reading/38124150D59DF3039EE1FF5AE88FE922
- Mahdi et al. 2024: https://doaj.org/article/d4e748b431a644d080453ea22b22db8e
- Boers et al. 2017: https://ir.lib.uwo.ca/edupub/99
- Shen 2010: https://iro.uiowa.edu/esploro/outputs/journalArticle/Imagery-and-verbal-coding-approaches-in/9984397917102771
- Farley, Ramonda & Liu 2012: https://journals.sagepub.com/doi/10.1177/1362168812436910
- Nakata 2016: https://www.degruyterbrill.com/document/doi/10.1515/iral-2015-0022/html
- Zheng et al. 2026: https://pressto.amu.edu.pl/index.php/ssllt/article/view/49487
- Webb 2005: https://cambridge.org/core/journals/studies-in-second-language-acquisition/article/receptive-and-productive-vocabulary-learning-the-effects-of-reading-and-writing-on-word-knowledge/DDF362AE7B13D1949B1CD591DA2F3414

Second-hand or unverified:
- Carpenter & Olson 2012 original: https://doi.org/10.1037/a0024828
- Nielson 2011: https://www.lltjournal.org/item/593/
- Vesselinov 2009 (via Krashen)
- FSRS benchmark: https://github.com/open-spaced-repetition/srs-benchmark
