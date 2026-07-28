# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

**Last updated: 2026-07-28 · all 57 new cards generated and QA'd; audio fixed**

---

## → Review now: `review/new_cards_review.html`

Open in a browser. **All 57 new cards now have both image and audio**, and the
audio actually plays this time — every clip is a real file in `review/media/`
rather than an inlined data URI, which is why nothing played before.

Each card shows its format — **question** (enquiry scene + bubble), **utterance**
(one pane + bubble), **exchange** (two panels, ask then answer) — and its
automated QA verdict.

**The 16 amber WARN cards are the ones worth your time.** Each carries a line
reading *"read cold as: …"* — what a vision model guessed the picture meant
without being told the answer. Where that guess misses the gloss, the picture may
not be carrying its own weight:

| Card | Teaches | Read cold as |
|---|---|---|
| A2-0882 | No problem | hello |
| A2-0883 | Of course | yes |
| A2-0885 | Here you are | give |
| A2-0902 | Please repeat | listen |
| A2-0913 | I am twenty years old | birthday cake |
| A2-0914 | I have a brother | My name is |

Some of these are fine — *Of course* read as *yes* is close enough that the card
still works. Others may need a re-roll. **That call is yours**; the machine can
tell you the picture is ambiguous but not whether the ambiguity matters.

Nothing is failing QA: 0 FAIL, 16 WARN, 41 PASS.

## → Then, whenever convenient

**`review_A1.csv` — 312 rows** · **`review_A1_duplicates.csv` — 101 rows** ·
**185 accents** in `accents_todo_kirtis.csv` for manual kirtis.info lookup.

---

## Running QA yourself

```bash
python3 qa_images.py out_phrases --csv _qa/qa_phrases.csv
python3 qa_images.py images --budget 300      # the full 520-card deck, in chunks
```

It caches by file hash, so re-running only costs for images that changed, and it
exits non-zero if anything fails — it can gate a generation run.

## Done this round

- **Automated image QA** (`qa_images.py`), replacing per-card eyeballing. It found
  both defects you spotted plus one you hadn't, and cleared the re-rolls.
- **The question-mark bug fixed at the root**: no prompt in the engine now
  contains a condition, because the model ignores them.
- **Target-word leakage fixed**: a text exception no longer silently disables the
  no-text rule, and the target is now named as forbidden on every card.
- **All 57 new images generated**, 11 re-rolled to clean.

## Still to do (not blocked on you)

- P-A's 97 images · cloze on sentence-card backs · fold the 57 into the `.apkg`.
