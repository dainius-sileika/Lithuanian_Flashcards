# -*- coding: utf-8 -*-
"""Apply the clear B1 / B3 fixes (2026-10-18) to a2_build/a2_wordlist.csv; log -> fixes_applied.csv.
B1: gender of the 15 A1-tagged nouns that had none, from kirtis.info's analysis (dktv. + gender + number).
B3: the stressed prons of proposals.json (phrase_stress.py). check column gets a note either way.
B2 needs no data change: every rule-derived form kirtis knows was confirmed; the check note is updated."""
import csv, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, HERE)
import check_A1 as C
res = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
prop = json.load(open(os.path.join(HERE, "proposals.json"), encoding="utf-8"))
P = "a2_build/a2_wordlist.csv"
raw = open(P, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys())
by = {r["id"]: r for r in rows}; log = []
def note(r, s):
    r["check"] = (r["check"] + "; " if r["check"] else "") + s
for key, lt, src, _ in res["B1"]:
    if src != "a2_wordlist":
        continue
    a = C.K(lt) or []
    n = [x for x in a if isinstance(x, dict) and x.get("class") == "dktv."]
    gs = {("M" if "vyr.gim." in x["state"] else "F" if "mot.gim." in x["state"] else "?") +
          (" pl" if "dgsk." in x["state"] and "vnsk." not in x["state"] else "") for x in n}
    if len(gs) == 1 and "?" not in next(iter(gs)):
        g = next(iter(gs)); r = by[key]
        log.append([key, lt, "gender", r["gender"], g, "kirtis.info " + "; ".join(" ".join(x["state"]) for x in n[:2])])
        r["gender"] = g; note(r, "gender: kirtis.info (2026-10-18)")
    else:
        print("B1 unclear", key, lt, gs)
for key, pron in prop.items():
    r = by[key]; log.append([key, r["lithuanian_TARGET"], "lt_pron", r["lt_pron"], pron, "kirtis.info per word"])
    r["lt_pron"] = pron; note(r, "stress: kirtis.info per word (2026-10-18) — verify phrase stress")
ok = {x[0] for x in res["B2_ok"]}
for key in ok:
    r = by[key]
    r["check"] = r["check"].replace("gen_sg: rule-derived", "gen_sg: rule-derived, kirtis.info K. confirmed 2026-10-18").replace(
        "fem: rule", "fem: rule, kirtis.info confirmed 2026-10-18")
out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
open(P, "w", encoding="utf-8", newline="").write(out.getvalue())
with open(os.path.join(HERE, "fixes_applied.csv"), "w", newline="", encoding="utf-8") as f:
    cw = csv.writer(f); cw.writerow(["id", "lithuanian", "field", "old", "new", "source"]); cw.writerows(log)
print(len(log), "fixes;", len(ok), "B2 check notes")
