# -*- coding: utf-8 -*-
"""gen_phrases.py — generation driver for the phrase / question-word / sentence-pattern cards.

2026-10-17 — BUBBLE-FREE "SITUATION" GRAMMAR (a2_build/RESTAGE_PROPOSAL.md §2(f), PILOT_24.md).
With an English caption on every front, the picture no longer has to make the words guessable:
its job is the situation. Every row is now routed by `situations.py` (generated from
a2_build/restage_bubbles.csv) to one of three layouts:

    situation     one calm scene, no bubble (default)
    situation_2   two panels, ask -> visible answer, same two people, no bubble in either
    sequence      the one three-panel strip (I need water)

Changes against the bubble version (kept in git history; bubbles.py UTTER/EXCH stay for history):
  - no QMARK, no is_question branching: nothing is ever drawn inside a bubble, so no "?";
  - text=False always; exact_text only for a row's declared object lettering (card_text);
  - `exclude` is no longer passed (naming the forbidden word primes it; the no-text rule covers it);
  - generate(..., situation=True) swaps NO_TEXT_RULE for NO_TEXT_RULE_SITUATION + NO_BUBBLE_RULE;
  - question-word rows DO get a picture (owner 2026-10-17, PILOT_24 supersedes §2(c));
  - merged rows (render "no (merged)") are skipped: they share their partner's image.

The two lessons of the bubble version still hold: never put a condition in a prompt (Python
decides; the prompt only states), and a text exception suspends the no-text rule, so only
rows with declared card_text get one.

    python3 gen_phrases.py [count] [budget_seconds]                  # A1 phrase pack (wordlist_a2_pending)
    A2_LIST=a2_build/a2_wordlist.csv python3 gen_phrases.py 8 60      # the A2 list's phrase rows
    PHRASES_OUT=media/images (default since the tidy of 2026-10-24: the one home of the current pictures)

The production driver for the pilot / roll-out is media/generation/out_phrases_v3/gen.py (was
out_phrases_v3/gen.py), which imports build_situation_call() from here so both paths build the same prompt.
"""
import csv, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from go_generator import GOGenerator
from go_grammars import NOUN_GRAMMARS, SCENE_TAIL
import deck_builder as db
from situations import SITUATIONS, BY_ID

OUT = os.environ.get("PHRASES_OUT", "media/images")


def situation_for(row):
    """The SITUATIONS entry for a wordlist row (by id first, then by English gloss)."""
    en = BY_ID.get((row.get("id") or "").strip()) or (row.get("english") or "").strip()
    return en, SITUATIONS.get(en)


def _split_insets(scene):
    """'… ; no bubble. Insets: a; b' -> ('…; no bubble', 'a; b')."""
    m = re.search(r"\s*Insets?:\s*(.*)$", scene)
    if not m:
        return scene, ""
    return scene[:m.start()].rstrip(" .;"), m.group(1).strip().rstrip(".")


def build_situation_call(row):
    """kwargs for GOGenerator.generate() for one restaged row, or None if the row gets
    no picture of its own (merged / no image). `row` needs id, english, and optionally
    type/category/card_text (the A2 list's columns)."""
    en, s = situation_for(row)
    if not s or not s["format"] or not s["render"].startswith("yes"):
        return None
    scene, insets = _split_insets(s["scene"])
    fmt = s["format"]
    is_q = (row.get("category") == "Question words" or (row.get("type") or "").upper() == "Q")
    subject = (f"the everyday moment that calls for the question word '{en}'" if is_q
               else f"the everyday moment when someone says '{en}'")
    if row.get("route") == "IMG":      # the 3 IMG rows (ask, speak, question): their old
        subject = f"the everyday act named by the word '{en}'"   # subject phrase names a bubble
    if fmt == "sequence":
        panels = db.SEQUENCE_BY_GLOSS.get(en) or [p.strip() for p in scene.split(";") if p.strip()]
        # the strip's numbered circles would be lettering; this card is wordless
        main = (NOUN_GRAMMARS["sequence"]["main"].replace(
                    " Number the panels in small plain circles in their upper-left corners.", "")
                + " The panels, in order: "
                + "; ".join(f"({i + 1}) {p}" for i, p in enumerate(panels))
                + ". No speech bubble in any panel." + SCENE_TAIL)
        staging = ""
    else:
        main = NOUN_GRAMMARS[fmt]["main"] + SCENE_TAIL
        staging = f"Staging: {scene}."
    if s["cue"]:
        staging += f" The detail that makes this moment unmistakable, clearly visible at small size: {s['cue']}."
    kw = dict(subject=subject, scene=main, staging=staging.strip(), insets=bool(insets),
              inset_note=(f"Include 2 small supporting insets: {insets}." if insets else ""),
              text=False, people="civilian", glyph=False, composition="vignette",
              setting="", motion_strip=False,
              exact_text=(row.get("card_text") or "").strip(), exclude="",
              flag="lt", situation=True,
              gaze=s.get("gaze", "conversation"),
              panels=(2 if fmt == "situation_2" else 3 if fmt == "sequence" else 1),
              filename=f"{(row.get('id') or en).strip()}.png")
    if any(i in db.DIRECTION_FREE_ROWS for i in s.get("ids", [])):   # spec 3.1.0 DIRECTION_RULE exemption
        kw["direction"] = False
    return kw


def main():
    a2_list = os.environ.get("A2_LIST")
    if a2_list:
        rows = [r for r in csv.DictReader(open(a2_list, encoding="utf-8"))
                if r.get("route") == "PHRASE" or r.get("category") == "Question words"]
    else:
        rows = [r for r in csv.DictReader(open("wordlist_a2_pending.csv", encoding="utf-8"))
                if r["status"] == "pending" and r["level"] == "A1"
                and (r["category"] == "Question words" or r["phase"] == "P-G")]
    os.makedirs(OUT, exist_ok=True)
    gen = GOGenerator(backend="openai", ratio="4:3")
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    BUD = float(sys.argv[2]) if len(sys.argv) > 2 else 38
    t0 = time.time()

    jobs = []
    for r in rows:
        kw = build_situation_call(r)
        if kw is None or os.path.exists(f"{OUT}/{kw['filename']}"):
            continue
        if len(jobs) >= N:
            break
        jobs.append((r["id"], r["english"], kw))

    def run(job):
        key, en, kw = job
        gen.generate(out_dir=OUT, **kw)
        return key

    done = 0
    # Tier 1 allows 5 images/minute; raise GO_WORKERS on a higher tier.
    with ThreadPoolExecutor(max_workers=int(os.environ.get("GO_WORKERS", "4"))) as ex:
        futs = {ex.submit(run, j): j for j in jobs}
        for fut in as_completed(futs):
            key, en = futs[fut][0], futs[fut][1]
            try:
                fut.result()
                done += 1
                print(f"  {key} {en[:40]}")
            except Exception as e:
                print(f"  {key}: FAIL {str(e)[:70]}")
            if time.time() - t0 > BUD:
                print("  budget reached — rerun to continue")
                break
    total = len([f for f in os.listdir(OUT) if f.endswith('.png')])
    print(f"generated {done} | total {total}/{len(rows)}")


if __name__ == "__main__":
    main()
