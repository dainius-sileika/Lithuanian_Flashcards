# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

> ## Standing rule: review before push
>
> **A review HTML is built and confirmed by the owner *before* anything is pushed
> to GitHub — never after.** Automated QA (`qa_images.py`) is a gate, not a
> substitute for the owner's eye: it can prove a card carries no stray text, but
> not that the picture teaches the right word. The order is always:
>
> ```
> generate → qa_images.py → build_review.py → owner confirms → push
> ```

**Last updated: 2026-10-10 · audit fixes pushed; gpt-image-2 probed; A2 re-base sheets built**

The clock: `gpt-image-1.5` is switched off on **1 Dec 2026**, `gpt-5-mini` (QA)
on **11 Dec 2026**. Both are now overridable per run (`GO_IMAGE_MODEL`,
`GO_QA_MODEL`), so the switch is one environment variable once you decide.

---

## 1 → Decide the image model: `_proto/gpt-image-2/compare_sheet.jpg`

10 shipped cards (left, gpt-image-1.5) re-run on the same prompts through
gpt-image-2 (right), ~$0.04 each. House language carries over (paper, red bars,
flag, workwear, insets, staging). Drift: softer, more naturalistic rendering;
arrows turned **red** on 3 of 10; inner ruled frame often missing; *karas* lost its
arrow. Likely fixable in the prompt. **The one-publication test is your eye.**
Everything after this depends on the answer.

## 2 → Sign off genders: `review_genders_2026-10-10.csv` (63 rows, ~5 min)

60 nouns that shipped with no ♂/♀ plus 3 adjectives, already filled into
`cards_anki.csv` (uncommitted). Blank `owner_ok` = yes. Once you're done they get
committed and the `.apkg` rebuilt.

## 3 → Re-base the A2 queue: `a2_rebase/` (start with its README)

- `official_missing_triage.csv`: 910 official-list words the deck lacks, each
  glossed and routed (329 picture, 303 cloze, 41 phrase, 14 aspect pair, 8 swap…).
  Second-reviewed blind; 15 corrections applied.
- `queue_offlist.csv`: 478 queue rows not on the list → 315 keep, 139 defer,
  8 swap, 16 drop.
- **Caveat:** the official list omits much of the frequent core (*laikas, prašau,
  vėl*), so "off-list" alone is not a reason to cut. The audit overstated this.

## 4 → Decide where the repo lives

On 10 Oct, Proton Drive rolled a file back ten minutes, spawned eight
"edit conflict" copies and locked freshly written files until `git add` crashed.
No data lost; everything here is pushed. Either pause Proton sync during working
sessions, or keep the git working copy outside Proton and let Proton hold only
the heavy artwork (`out_deck/`, `out_phrases/`, `_qa/`).

---

## Older backlog (untouched since July)

- **16 amber WARN phrase cards** in `review/new_cards_review.html` (e.g. A2-0913
  *I am twenty years old* read cold as "birthday cake"). Most of these phrases are
  KEEP in the re-base, so they still matter.
- **`review_A1.csv`**: 312 rows · **`review_A1_duplicates.csv`**: 101 rows.
- **`accents_todo_kirtis.csv`**: 185 manual lookups. Skim first: monosyllabic
  function words (*į, su, ten*) don't need one.

## Running QA yourself

```bash
python3 qa_images.py out_phrases --csv _qa/qa_phrases.csv
python3 qa_images.py images --budget 300      # the full 520-card deck, in chunks
```

It caches by file hash, and exits non-zero if anything fails, so it can gate a run.
