#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_v2.py — the proofreading export, v2 (2026-10-20): every Lithuanian sentence and phrase of the deck
(A1 + A2) in study order, A1 first, with the current keys (key_map_v1 + v2) and the owner's corrections of
returned_plan_v1 applied. Same format as v1 (whose files stay untouched):

  sentences_for_proofreading_v2.csv  order,key,level,kind,lt_with_blank,lt_plain,target,en,status,lt_corrected,en_corrected,note
                                     (UTF-8 with BOM, CRLF; the blank in braces; empty columns to fill)
  sentences_lt_only_v2.txt           key <TAB> Lithuanian (plain)
  sentences_lt_en_v2.txt             key <TAB> Lithuanian <TAB> English

Rows: A2-list CLOZE/PAIR (kind cloze) and PHRASE (kind phrase) rows with example_lt, and the sentence cards
(kind "sentence card", sentences.csv lt/en). `order` = position in study_order.csv. `status` carries v1's
status (the dep37 rewordings) through the key map, and marks the rows changed by returned_plan_v1.

    python3 a2_build/proofread/export_v2.py [--check]   # --check: compare with v1 through the key map, write nothing
"""
import csv, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import keymap   # noqa: E402

V1 = f"{HERE}/sentences_for_proofreading_v1.csv"
PLAN = f"{HERE}/returned_plan_v1.csv"
COLS = ["order", "key", "level", "kind", "lt_with_blank", "lt_plain", "target", "en", "status",
        "lt_corrected", "en_corrected", "note"]


def rows():
    order = {r["key"]: int(r["order"]) for r in csv.DictReader(open("study_order.csv", encoding="utf-8"))}
    v1 = {keymap.canonical(r["key"]): r for r in csv.DictReader(open(V1, encoding="utf-8-sig"))}
    plan = {keymap.canonical(r["new_key"]): r["action"] for r in csv.DictReader(open(PLAN, encoding="utf-8"))}
    out = []
    for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8")):
        route = r.get("route", "")
        if route not in ("CLOZE", "PAIR", "PHRASE") or not r.get("example_lt", "").strip():
            continue
        out.append((r["id"], r["level"], "phrase" if route == "PHRASE" else "cloze", r["example_lt"], r["example_en"]))
    for r in csv.DictReader(open("a2_build/sentences/sentences.csv", encoding="utf-8")):
        out.append((r["id"], r["level"], "sentence card", r["lt"], r["en"]))
    res = []
    for k, lv, kind, lt, en in out:
        m = re.search(r"\{([^}]*)\}", lt)
        status = (v1.get(k) or {}).get("status", "")
        if k in plan:
            status = "; ".join(x for x in (status, f"corrected 2026-10-20 ({plan[k]}, returned_plan_v1)") if x)
        res.append({"order": order[k], "key": k, "level": lv, "kind": kind, "lt_with_blank": lt,
                    "lt_plain": lt.replace("{", "").replace("}", ""), "target": m.group(1) if m else "", "en": en,
                    "status": status, "lt_corrected": "", "en_corrected": "", "note": ""})
    res.sort(key=lambda d: d["order"])
    return res, v1, plan


def check(res, v1, plan):
    """Every v1 row is in v2 (by current key); rows outside the plan carry v1's text unchanged."""
    cur = {d["key"]: d for d in res}
    missing = [k for k in v1 if k not in cur]
    extra = [k for k in cur if k not in v1]
    diff = [k for k in cur if k in v1 and k not in plan and
            (cur[k]["lt_with_blank"], cur[k]["en"], cur[k]["kind"], cur[k]["level"]) !=
            (v1[k]["lt_with_blank"], v1[k]["en"], v1[k]["kind"], v1[k]["level"])]
    changed = [k for k in cur if k in plan and k in v1 and cur[k]["lt_with_blank"] != v1[k]["lt_with_blank"]]
    print(f"v2 rows {len(res)} | v1 rows {len(v1)} | missing from v2 {len(missing)} {missing[:5]} | new in v2 {len(extra)} "
          f"{extra[:5]} | text differs outside the plan {len(diff)} {diff[:5]} | plan rows whose text changed "
          f"{len(changed)} of {len(plan)}")
    return not (missing or extra or diff)


def main():
    res, v1, plan = rows()
    ok = check(res, v1, plan)
    if "--check" in sys.argv:
        return 0 if ok else 1
    if not ok:
        raise SystemExit("check failed; nothing written")
    for p in (f"{HERE}/sentences_for_proofreading_v2.csv", f"{HERE}/sentences_lt_only_v2.txt", f"{HERE}/sentences_lt_en_v2.txt"):
        if os.path.exists(p):
            raise SystemExit(f"refusing to overwrite {p}")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\r\n"); w.writeheader(); w.writerows(res)
    open(f"{HERE}/sentences_for_proofreading_v2.csv", "w", encoding="utf-8-sig", newline="").write(buf.getvalue())
    open(f"{HERE}/sentences_lt_only_v2.txt", "w", encoding="utf-8", newline="").write(
        "".join(f"{d['key']}\t{d['lt_plain']}\n" for d in res))
    open(f"{HERE}/sentences_lt_en_v2.txt", "w", encoding="utf-8", newline="").write(
        "".join(f"{d['key']}\t{d['lt_plain']}\t{d['en']}\n" for d in res))
    print("written: sentences_for_proofreading_v2.csv, sentences_lt_only_v2.txt, sentences_lt_en_v2.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
