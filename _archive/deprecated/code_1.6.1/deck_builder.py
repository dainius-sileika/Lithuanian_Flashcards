#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deck builder (files 1.6.1) — the wordlist-driven production runner.

1.6.1: the 8 open design decisions are IN (see GO_STYLE_SPEC ledger). PENDING
is now empty; glyph rows 227/350/351 generate via the engine's single-glyph
exception; rows 137 (wedding) and 379 (die: gravestone) are phrase-complete
and routed "attribute"; superseded color duplicates 518-527 are excluded by
the wordlist itself (depictable=superseded).

This is the file Cowork drives. It reads master_wordlist.csv and generates the
whole picture deck (or any slice of it) through the frozen GO pipeline:

  nouns        -> go_grammars visual grammars (per category)
  adjectives   -> "attribute" class: marked-contrast scene, no insets
  category-C   -> "chart" class: specimen chart, no insets
  verbs        -> context C default / D accent, staged per-verb (VERB_STAGING)

Fixes carried from the 1.5.1 audit:
  - collision-proof keys: {row#}_{ascii-slug} (eiti x2, sokti x2, peda x2,
    vyras x2, zeme x2, senas x2 would otherwise overwrite each other)
  - card numbers come from the wordlist '#' column (no BASE_NUMBER)
  - cards.csv now carries lt_pron + gender for the Anki layer
  - --only for the QA re-roll pass; --category for block-by-block production
  - rows pending a design decision are SKIPPED by default (see PENDING)

Run:
  export OPENAI_API_KEY=sk-...
  python deck_builder.py --dry-run                 # plan + prompts, no API
  python deck_builder.py --trial 6                 # first 6 eligible rows
  python deck_builder.py --category Animal         # one category block
  python deck_builder.py --only 001_suo,113_gydytojas   # re-roll pass
  python deck_builder.py                           # the full deck
"""
from __future__ import annotations
import os, csv, sys, argparse, unicodedata

from go_generator import GOGenerator
from go_grammars import route, compose_class
from verb_flashcards import scene_for, inset_for

WORDLIST = "master_wordlist.csv"
OUT_DIR = "./out_deck"
RATIO = "4:3"

# ---------------------------------------------------------------------------
# Rows awaiting an owner design decision (see STAGING_files_2_1.md §5).
# Generating them would burn credits on cards that may change. Override with
# --include-pending once decided, or delete entries here.
# ---------------------------------------------------------------------------
PENDING = {}   # all design questions resolved at 1.6.1

# rows whose composition is complete in the phrase itself (no class grammar,
# no motion insets): wedding scene, gravestone
OVERRIDE_CLASS = {137: "attribute", 379: "attribute",
                  227: "attribute", 350: "attribute", 351: "attribute"}

# rows generated with the engine's single-glyph exception (decision Q2)
GLYPH_ROWS = {227, 350, 351}

# ---------------------------------------------------------------------------
# Per-verb staging: row# -> (people, setting, arrow, emphasis, consequence).
# Design source: STAGING_files_2_1.md §4 (telicity -> D panel) and the locked
# verb treatment (context C default). The nine 1.5-validated demo verbs keep
# their exact staging. A non-empty consequence == a D-accent card.
# ---------------------------------------------------------------------------
W, P, C = "worker", "professional", "civilian"
VERB_STAGING = {
    363: (W, "a workshop with a workbench", "", "", ""),
    364: (C, "a courtyard with simple play equipment", "", "", ""),
    365: (C, "a small club stage or rehearsal room", "", "", ""),
    366: (W, "a long institutional corridor",
          "one bold arrow showing the forward direction of walking", "", ""),
    367: (W, "a plain institutional courtyard or street",
          "one bold arrow showing the forward direction of running", "", ""),
    368: (W, "a road, the truck cab seen from the side",
          "one bold arrow showing the forward direction of travel", "", ""),
    369: (W, "the open sky above fields",
          "one bold arrow showing the forward direction of flight", "", ""),
    370: (C, "a swimming-pool lane",
          "one bold arrow showing the forward direction of swimming", "", ""),
    371: (W, "a doorway opening onto the street",
          "one bold arrow leading away through the doorway",
          "Emphasise DEPARTURE: the figure is setting off and leaving — "
          "going, not merely strolling.", ""),
    372: (W, "a street crossing with a lowered barrier", "",
          "Emphasise the HALT: the figure has stopped mid-step before the "
          "barrier.", ""),
    373: (W, "a plain corridor or street",
          "a dashed path line showing one figure following the route of the "
          "other", "", ""),
    375: (W, "an office or corridor", "", "", ""),
    376: (W, "a plain workers' canteen with long tables and others eating in "
          "the background", "", "", ""),
    377: (W, "a workers' canteen or rest area with a water station", "", "", ""),
    378: (C, "a kitchen corner", "", "", "the swatted fly lying still"),
    380: (C, "a plain portrait setting", "", "", ""),
    381: (C, "a canteen table", "", "", ""),
    382: (C, "a plain room", "", "", ""),
    383: (C, "a small shop counter",
          "one bold arrow on the wrapped goods passing from clerk to customer",
          "", "the customer carrying the wrapped purchase away"),
    384: (C, "a shop counter or cashier's window",
          "one bold arrow on the banknotes passing from customer to clerk",
          "", ""),
    385: (W, "a small shop counter seen from the clerk's side",
          "two small arrows: goods outward to the customer, coins inward to "
          "the clerk", "", "the till drawer with coins"),
    386: (W, "an indoor shooting range", "", "",
          "the paper target with bullet holes"),
    388: (W, "a training yard with a low obstacle",
          "one bold arcing arrow showing the up-and-over jump", "", ""),
    389: (C, "a market flower stall", "", "", ""),
    390: (W, "a workshop with an alarm bell on the far wall", "",
          "Emphasise INVOLUNTARY hearing: the sound arrives and the head "
          "turns toward it.", ""),
    391: (C, "a sitting room with a tabletop radio", "",
          "Emphasise DELIBERATE listening: seated, attentive, ear inclined "
          "to the radio.", ""),
    392: (P, "a canteen kitchen at a soup pot", "", "", ""),
    393: (W, "a plain table", "", "", ""),
    394: (W, "an open field with a distant water tower",
          "a thin dotted sight line from the eye to the distant object", "", ""),
    395: (C, "a sitting room with a television set", "",
          "Emphasise DELIBERATE watching: seated squarely before the screen.",
          ""),
    396: (C, "a doorstep farewell", "", "", ""),
    397: (W, "a fire-safety training yard, at a safe distance", "", "",
          "the plank burnt down to char and embers"),
    398: (W, "a kitchen table", "", "", "the ice reduced to a puddle of water"),
    399: (W, "an open trench line with marker stakes", "", "",
          "the finished straight trench"),
    400: (W, "a demolition training ground with workers behind a barrier",
          "", "", "the cleared rubble after the blast"),
    401: (W, "a plain office with a chair and desk", "", "", ""),
    402: (W, "a corridor or muster line", "", "", ""),
    404: (W, "a street with a kiosk",
          "a dashed path line passing the kiosk and carrying on beyond it",
          "", "the kiosk left behind as the walker continues on"),
    405: (W, "a workshop sawhorse", "", "", "the board cut into two pieces"),
    406: (C, "a boxing ring in a plain gymnasium", "", "", ""),
    407: (W, "a rest room with a cot", "",
          "The figure is AWAKE with open eyes — lying down, not sleeping.", ""),
    408: (C, "a social hall with seated onlookers", "",
          "Emphasise DANCING to music: a couple in dance hold, simple musical "
          "notes in the air — dancing, not jumping.", ""),
    409: (W, "a plain barracks or dormitory bunk room", "", "", ""),
    410: (W, "a dormitory bed at morning with sun through the window", "", "",
          "the worker upright and dressed"),
    411: (C, "a small stage or campfire circle", "", "", ""),
    412: (W, "a stockroom desk with crates", "", "", ""),
    413: (C, "a registry office with an official at a desk", "", "",
          "the couple's joined hands with wedding rings"),
    417: (W, "a construction yard mortar trough",
          "a circular motion arrow over the mixing", "", ""),
    418: (W, "a metal workshop with a vise",
          "a curved arrow following the bend", "",
          "the rod bent to a right angle"),
    419: (W, "a tiled factory or institutional washroom", "", "", ""),
    420: (P, "a canteen kitchen stove", "", "", ""),
    421: (W, "a plain interior door",
          "an arc arrow showing the door swinging open", "",
          "the door standing open"),
    422: (W, "a plain interior door",
          "an arc arrow showing the door swinging shut", "",
          "the door closed"),
    423: (W, "an office desk with paper and pen", "", "", ""),
    424: (W, "an office with a rotary telephone", "", "", ""),
    425: (W, "a boiler room with a large pipe valve",
          "a circular arrow around the turning wheel", "", ""),
    426: (W, "a workshop or construction site with a workbench", "", "",
          "the finished assembled wooden structure or frame"),
    428: (W, "a garden bed",
          "one bold upward arrow beside the growth stages", "",
          "the plant fully grown"),
    429: (C, "a desk with paper", "", "", ""),
    430: (W, "a farmyard with chickens", "", "", ""),
    431: (W, "a loading yard", "", "",
          "the sack held safely in both arms"),
    432: (W, "a loading yard with a pile of sacks",
          "an arcing arrow tracing the throw", "",
          "the sack landed on the pile"),
    433: (W, "an institutional corridor, one half already clean", "", "",
          "the corridor fully clean"),
    434: (W, "a workshop with a workbench", "", "",
          "the worker holding up the found keys"),
    435: (W, "a warehouse shelf",
          "one bold downward arrow tracing the fall", "",
          "the crate landed on the floor"),
    436: (W, "a warehouse aisle",
          "one bold arrow showing the forward push", "", ""),
    437: (W, "a yard with a rope-hauled cart",
          "one bold arrow showing the pull toward the worker", "", ""),
    438: (W, "a supply depot or storeroom hall with tall shelves of crates "
          "and a few workers in the background", "",
          "Emphasise horizontal transport: the worker walks and carries the "
          "crate across a distance, holding it steady — this is CARRYING, "
          "not lifting.",
          "a cargo truck being loaded with the carried crates"),
    439: (W, "a firewood yard", "", "", "the stick broken into two pieces"),
    440: (W, "an equipment room", "",
          "This is a protective-clothing chart: the garments being WORN are "
          "the subject.", ""),
    441: (W, "a plain room wall with a hook", "", "",
          "the framed picture hanging level on the wall"),
    442: (W, "an orchard beneath an apple tree", "", "",
          "the fallen apples gathered on the ground"),
    443: (W, "an office desk with a document", "", "",
          "the document bearing a plain scribbled signature mark"),
    444: (C, "a yard with a rug on a beating rack", "", "", ""),
    445: (W, "a supply depot or storeroom with tall shelves of crates",
          "one bold UPWARD arrow showing the crate being raised straight up",
          "Emphasise the vertical upward lift: the worker raises the crate "
          "straight up from the floor — this is LIFTING/RAISING, not walking "
          "with it.",
          "the crate lifted and set up onto the high shelf"),
}


def slug(lt: str) -> str:
    """ASCII slug of the first Lithuanian form: 'gydytojas/gydytoja' ->
    'gydytojas'; 'žemė (dirvožemis)' -> 'zeme'."""
    first = lt.split("/")[0].split("(")[0].strip().lower()
    ascii_ = unicodedata.normalize("NFD", first)
    ascii_ = "".join(c for c in ascii_ if not unicodedata.combining(c))
    ascii_ = ascii_.replace("š", "s").replace("ž", "z")  # safety, post-NFD
    return "".join(c if c.isalnum() else "_" for c in ascii_).strip("_")


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def eligible(rows, include_pending=False):
    """Yield (key, row, route) for every generable row, in wordlist order."""
    out, skipped = [], []
    for r in rows:
        n = int(r["#"])
        if r["depictable"] not in ("yes", "category-multi"):
            continue
        if not r["subject_phrase_EN"].strip():
            skipped.append((n, "no subject phrase"))
            continue
        if n in PENDING and not include_pending:
            skipped.append((n, "PENDING: " + PENDING[n]))
            continue
        if n in OVERRIDE_CLASS:
            cls = OVERRIDE_CLASS[n]
        elif r["type"] == "V":
            if n not in VERB_STAGING:
                skipped.append((n, "verb missing from VERB_STAGING"))
                continue
            cls = "verb"
        else:
            cls = route(r["category"], r["type"], r["flags"])
        key = f"{n:03d}_{slug(r['lithuanian_TARGET'])}"
        out.append((key, r, cls))
    return out, skipped


def build_call(key, r, cls):
    """Return the kwargs for GOGenerator.generate() for this row."""
    subject = r["subject_phrase_EN"].strip()
    if cls == "verb":
        people, setting, arrow, emphasis, consequence = VERB_STAGING[int(r["#"])]
        return dict(subject=subject,
                    scene=scene_for(setting, arrow=arrow, emphasis=emphasis,
                                    people=people),
                    inset_note=inset_for(consequence), insets=True,
                    text=False, people=people, glyph=False,
                    filename=f"{key}.png")
    scene, inset_note, _, people, insets = compose_class(cls, r["category"])
    if int(r["#"]) == 137:
        people = "civilian"          # wedding guests are not coverall workers
    return dict(subject=subject, scene=scene, inset_note=inset_note,
                insets=insets, text=False, people=people,
                glyph=int(r["#"]) in GLYPH_ROWS,
                filename=f"{key}.png")


def main():
    ap = argparse.ArgumentParser(description="Lietuvių 625 deck builder")
    ap.add_argument("--wordlist", default=WORDLIST)
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--backend", default="openai", choices=["openai", "zimage"])
    ap.add_argument("--ratio", default=RATIO)
    ap.add_argument("--trial", type=int, default=0, help="first N rows only")
    ap.add_argument("--category", default="", help="one category block")
    ap.add_argument("--only", default="", help="comma-separated keys (re-roll)")
    ap.add_argument("--include-pending", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and prompts; no API calls")
    a = ap.parse_args()

    rows = load_rows(a.wordlist)
    work, skipped = eligible(rows, a.include_pending)
    if a.category:
        work = [w for w in work if w[1]["category"] == a.category]
    if a.only:
        want = {k.strip() for k in a.only.split(",")}
        work = [w for w in work if w[0] in want]
        missing = want - {w[0] for w in work}
        if missing:
            print("WARNING: --only keys not found:", ", ".join(sorted(missing)))
    if a.trial:
        work = work[:a.trial]

    keys = [w[0] for w in work]
    assert len(keys) == len(set(keys)), "key collision — should be impossible"
    n_verbs = sum(1 for w in work if w[2] == "verb")
    print(f"plan: {len(work)} cards  ({n_verbs} verbs, "
          f"{len(work)-n_verbs} noun/attribute/chart)  -> {a.out}")
    for n, why in skipped:
        print(f"  skip #{n}: {why}")

    if a.dry_run:
        from go_generator import build_prompt
        for key, r, cls in work:
            kw = build_call(key, r, cls)
            prompt = build_prompt(kw["subject"], scene=kw["scene"],
                                  insets=kw["insets"],
                                  inset_note=kw["inset_note"], text=False,
                                  people=kw["people"], glyph=kw["glyph"],
                                  backend=a.backend)
            print(f"\n--- {key}  [{cls}]  #{r['#']} {r['english']}\n{prompt}")
        return

    gen = GOGenerator(backend=a.backend, ratio=a.ratio)
    lf, lw = GOGenerator.open_ledger(os.path.join(a.out, "ledger.csv"))
    cf, cw = GOGenerator.open_cards(os.path.join(a.out, "cards.csv"))
    done = 0
    try:
        for key, r, cls in work:
            kw = build_call(key, r, cls)
            dest, seed, prompt = gen.generate(out_dir=a.out, **kw)
            lw.writerow([key, kw["subject"], seed, gen.backend, gen.size,
                         os.path.basename(dest), prompt]); lf.flush()
            cw.writerow([key, r["lithuanian_TARGET"], r["english"],
                         r["lt_pron"], r["gender"], r["#"], r["category"],
                         f"{key}.png"]); cf.flush()
            done += 1
            print(f"    {r['#']:>3}  {r['lithuanian_TARGET']} "
                  f"({r['english']})  [{cls}]")
    finally:
        lf.close(); cf.close()
        print(f"done: {done}/{len(work)} -> {a.out} "
              "(images + ledger.csv + cards.csv)")


if __name__ == "__main__":
    main()
