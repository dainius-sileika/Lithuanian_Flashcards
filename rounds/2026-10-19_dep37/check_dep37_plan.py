#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_dep37_plan.py — dry-run of a2_build/study_order/dep37_plan.csv against the v3 dependency audit.

    python3 a2_build/study_order/check_dep37_plan.py [plan.csv] [study_order.csv]

Applies the plan IN MEMORY (nothing on disk changes): RETIER_WORD rows move the named teaching card(s)
to A1; REWORD / BOTH rows replace the card's example sentence (for an S-#### card also its text and
words_used). Then it re-runs build_study_order_v3's dependency detection — same tokeniser, same
simplemma lemma logic, same ne- rule — against the positions of the given study_order.csv and prints:

  * every word of every new sentence with the A1 card that teaches it and that card's v3 position
    (target = the cloze word itself; A1-LATER = taught in A1 but after this card: the rebuild pulls it
    forward; A2-ONLY / OUTSIDE would be defects of the plan);
  * the audit's own count of "A1 cards needing a word taught only in A2" before and after the plan
    (the number that must read 0), and the residual list if any;
  * sanity checks: key exists, exactly one {…} cloze, the cloze word unchanged (lemma) for list cards
    and literally unchanged for sentence cards, new rows differ from the current text.

Exit status 1 when the residual count is not 0 or a sanity check fails.
"""
import csv, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
import build_study_order_v3 as B   # noqa: E402

PLAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "dep37_plan.csv")
ORDER = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "study_order.csv")


def cross_list(cards, pos):
    """(card, word, teaching keys) for A1 reading cards whose word is taught only by A2 cards."""
    bylvl = {c["key"]: c["level"] for c in cards}
    out = []
    for c in cards:
        if c["route"] not in B.READING or c["level"] != "A1" or c["key"] not in pos:
            continue
        for t, ks in c["deps"]:
            ks = [k for k in ks if k in pos]
            if ks and min(pos[k] for k in ks) > pos[c["key"]] and all(bylvl[k] == "A2" for k in ks):
                out.append((c, t, ks))
    return out


def main():
    sub, press, vu = B.load_sources()
    cards = B.load_cards({}, {})            # the data files' levels (retier_v3 already applied on disk)
    B.score_cards(cards, sub, press, vu)
    B.build_dependencies(cards)
    pos = {r["key"]: int(r["order"]) for r in csv.DictReader(open(ORDER, encoding="utf-8"))}
    bykey = {c["key"]: c for c in cards}
    before = cross_list(cards, pos)
    print(f"before the plan: {len(before)} A1 word uses depend on an A2-only card "
          f"({len({c['key'] for c, _, _ in before})} cards)")

    plan = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    ok = True
    moved = {}
    for r in plan:
        k = r["key"]
        if k not in bykey:
            print(f"!! {k}: unknown key"); ok = False; continue
        c = bykey[k]
        if r["action"] in ("RETIER_WORD", "BOTH"):
            for tk in r["retier_key"].split():
                if tk not in bykey:
                    print(f"!! {k}: retier key {tk} unknown"); ok = False; continue
                moved[tk] = bykey[tk]["lt"]
                bykey[tk]["level"] = "A1"
        if r["action"] in ("REWORD", "BOTH"):
            new = r["new_example_lt"].strip()
            if not new or new == r["current_example_lt"].strip():
                print(f"!! {k}: REWORD without a new sentence"); ok = False; continue
            targets = re.findall(r"\{([^{}]+)\}", new)
            if len(targets) != 1:
                print(f"!! {k}: expected exactly one {{…}} in '{new}'"); ok = False; continue
            old_t = re.findall(r"\{([^{}]+)\}", c["ex"])
            if c["route"] == "SENT":
                if old_t and B.base(old_t[0]) != B.base(targets[0]):
                    print(f"!! {k}: sentence card's cloze word changed {old_t[0]} -> {targets[0]}"); ok = False
                c["lt"] = new
                if r.get("new_words_used", "").strip():
                    c["words"] = r["new_words_used"].strip()
            else:
                t = B.base(targets[0])
                if t not in c["intro"] and B.lemma(t) not in c["intro"] and not (
                        old_t and B.base(old_t[0]) == t):
                    print(f"!! {k}: cloze word '{targets[0]}' is not a form of the headword {c['lt']}"); ok = False
            c["ex"] = new
    if moved:
        print("moved to A1:", ", ".join(f"{k} {w}" for k, w in sorted(moved.items())))

    B.build_dependencies(cards)             # fresh intro table: the moved cards now count as A1
    intro = defaultdict(set)
    for c in cards:
        for f in c["intro"]:
            intro[f].add(c["key"])

    def introducers(t):
        t = B.FORM_ALIAS.get(t, t)
        ks = set(intro.get(t, ())) | set(intro.get(B.lemma(t), ()))
        if not ks and t.startswith("ne") and len(t) > 4:
            ks = set(intro.get(t[2:], ())) | set(intro.get(B.lemma(t[2:]), ()))
        return ks

    print("\n== words of the new sentences ==")
    for r in plan:
        c = bykey.get(r["key"])
        if not c or r["action"] not in ("REWORD", "BOTH"):
            continue
        p = pos[c["key"]]
        print(f"{c['key']:8} @{p:4} {c['ex']}")
        seen = set()
        for t, is_name in B.sentence_tokens(c["ex"]):
            if is_name or len(t) == 1 or t in seen:
                continue
            seen.add(t)
            if c["route"] != "SENT" and (t in c["intro"] or B.lemma(t) in c["intro"]):
                print(f"    {t:16} target"); continue
            if c["route"] == "SENT" and re.search(r"\{[^{}]*\b" + re.escape(t) + r"\b[^{}]*\}", B.base(c["ex"])):
                print(f"    {t:16} target (sentence card: the audit still counts it as a dependency)")
            ks = sorted(((pos.get(k, 10 ** 6), k) for k in introducers(t) - {c["key"]}))
            a1 = [(pp, k) for pp, k in ks if bykey[k]["level"] == "A1"]
            if not ks:
                tag = "OUTSIDE"; ok = False
            elif not a1:
                tag = "A2-ONLY"; ok = False
            elif a1[0][0] < p:
                tag = "ok"
            elif a1[0][1] in moved:
                tag = "moved (rebuild places it before this card)"
            else:
                tag = "A1-LATER (rebuild pulls it forward)"
            show = ", ".join(f"{k}@{pp} {bykey[k]['lt']}" for pp, k in (a1 or ks)[:3])
            print(f"    {t:16} {tag:44} {show}")

    after = cross_list(cards, pos)
    print(f"\nafter the plan: {len(after)} A1 word uses depend on an A2-only card "
          f"({len({c['key'] for c, _, _ in after})} cards)")
    for c, t, ks in after:
        print(f"    {c['key']:8} @{pos[c['key']]:5} {c['ex'][:40]:40} {t:16} <- {ks[0]} {bykey[ks[0]]['lt']} @{pos[ks[0]]}")
        ok = False
    # the plan must cover every current cross dependency
    uncovered = [(c["key"], t) for c, t, _ in before if c["key"] not in {r["key"] for r in plan}]
    if uncovered:
        print("!! current cross dependencies not covered by the plan:", uncovered); ok = False
    print("\nRESULT:", "OK — residual A1→A2 dependencies 0" if ok else "FAIL (see !! lines / residual list)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
