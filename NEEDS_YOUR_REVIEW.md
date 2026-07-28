# What needs *your* eyes right now

This file is the single answer to "where's the bottleneck?". It is rewritten
every time a batch moves, so whatever is at the top is what unblocks the project.

**Last updated: 2026-07-28 · click removed from all audio; 18/57 new images; folder tidied**

---

## → Review now: `review/new_cards_review.html`

Open in a browser. **18 of 57 new cards have images**; **all 57 have your audio**,
playable inline, with the click removed. Cards below the fold are listed by word
with images still pending.

Each card is tagged with its format — **question** (enquiry scene + bubble),
**utterance** (one pane + bubble), **exchange** (two-panel ask/answer). Worth a
look now: if a format assignment is wrong, saying so costs nothing today and a
re-roll tomorrow.

## → Then, whenever convenient

**`review_A1.csv` — 312 rows** · **`review_A1_duplicates.csv` — 101 rows**.

---

## Where the work folder stands

The root now holds **only live files**: the six docs, the six engine scripts,
four data files, two open review packs, and the built deck. Everything else is
under `deprecated/` (frozen versions, superseded docs, completed review packs,
raw recording sessions) or is a build artifact.

**Recorder sheets are no longer kept as files** — five stale copies had piled up,
two of them empty, which is why the count looked wrong. Generate one on demand:

```bash
python3 build_recorder.py A1 new    # only words with no human recording yet
```

---

## Done this round

- **Click removed from all 581 clips.** Every take opened with a 10–150 ms
  keypress transient; a fixed 0.25 s cut clears it with margin, verified against
  the earliest speech onset anywhere (0.385 s).
- **18 phrase/question images** generated; 39 to go.
- **Folder tidied properly** — the previous attempt was undone by a `git reset`
  because the moves were only staged, not committed.

## Still to do (not blocked on you)

- 39 remaining phrase images · P-A's 97 images · cloze on sentence backs.
