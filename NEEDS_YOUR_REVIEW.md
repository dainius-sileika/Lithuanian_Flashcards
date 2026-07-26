# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

**Last updated: 2026-07-25 · after the accent pass**

---

## → Do this now: `review_P-A.csv`

**97 rows. One pass, correcting rather than authoring.** This is Phase A —
time, calendar, numbers and the everyday nouns the deck is missing. Nothing
else can be generated until it's checked, because the whole pipeline
(images → audio → forms) is built on the word being right.

How to work it — only three columns need you:

| column | what to do |
|--------|-----------|
| `LT_ok_or_fix` | Leave **blank if my proposed Lithuanian is right**. Type a correction if not. That's the important one. |
| `accent_FILL` | **12 rows** say `<-- from kirtis.info`. Everything else already has a sourced accent in `accent`. |
| `form_ok_or_fix` | **18 rows** are flagged in `form_confidence` (i-stem `-is`, plural-only nouns, irregulars). The other 58 are rule-derived and usually fine — a skim is enough. |

`comment` is free text for anything that smells wrong (a gloss pointing at the
wrong sense, a word that's technically right but nobody says, etc.).

**Ignore** `card_text_plan` — that's my column; it records what lettering the
card is allowed to show (a numeral, a day name on a calendar).

---

## Then: duplicate decisions

**139 rows** in `wordlist_a2_pending.csv` have `status = review-duplicate` —
they collide with something already in the 520-card deck. Most should be
dropped, but some are arguably distinct senses (*sąskaita* = restaurant bill vs
bank account; *kaina* = price vs cost). Filter that column and mark keep/drop.
Quick job, and it shrinks everything downstream.

---

## Background, whenever you have a spare hour

**`accents_todo_kirtis.csv` — 195 words**, sorted by level and category, with an
empty `accented_form_FILL_ME` column. **53 are A1** and worth doing first; the
12 in the P-A pack above are drawn from this list, so doing P-A's first is the
efficient order. No automated source carries these (see the accent-source
evaluation in `ROADMAP.md` — Wiktionary simply lacks the data).

---

## Not blocked on you

I'm handling these in parallel; listed so you know they're not forgotten:

- Rule-deriving the remaining grammar forms across all phases (359 genitives,
  148 verb pairs, 65 feminines) — I flag irregulars rather than guessing them.
- Authoring the ~592 subject phrases for image rows, per phase, after its words
  are confirmed.
- Building the sentence/phrase note type, which unblocks phases B, D, E and G.
- Finishing the `card_text` plans for numerals and calendar cards.

---

## The loop, for reference

For each phase: **I produce a review pack → you correct it → I author the scene
phrases, generate, QA, and merge** (with audio, level tags and a rebuilt
recorder). Then the next phase. Order: **P-A → P-C → P-F** (in three chunks),
with **P-B / P-D / P-E / P-G** following once the sentence note type exists.
