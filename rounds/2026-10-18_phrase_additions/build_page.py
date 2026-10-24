# -*- coding: utf-8 -*-
"""Review page "Phrase Additions" (2026-10-18): the 64 PHRASE-route benchmark additions rendered from
a2_build/phrase_additions/staging.csv (A2-1944 / A2-1958 merged into A2-1995 / A2-1991 by the plan;
A2-2007, A2-2012, A2-2020 held for the owner's merge decision), each with its staging, cue, confusables,
the round-2 QA and OK / Redo + note. db (db + user): collection "phraseadd", notes "phraseadd_meta/general".
    python3 a2_build/phrase_additions/build_page.py <repo root> <out dir>   # media/<key>.jpg, rerolls.json"""
import csv, json, os, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(ROOT, p)
HERE = os.path.dirname(os.path.abspath(__file__))
st = {r["ids"]: r for r in csv.DictReader(open(R("a2_build/phrase_additions/staging.csv"), encoding="utf-8"))}
qa = {r["key"]: r for r in csv.DictReader(open(os.path.join(OUT, "qa_phraseadd.csv") if os.path.exists(os.path.join(OUT, "qa_phraseadd.csv")) else os.path.join(HERE, "qa_phraseadd.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open(R("a2_build/a2_wordlist.csv"), encoding="utf-8"))}
rr = json.load(open(os.path.join(OUT, "rerolls.json")))
G = {"FAIL": "Still failing a hard QA check after two re-rolls", "WARN": "QA notes to check", "PASS": "Passed QA"}
data = []
for k in sorted(rr):
    s = st[k]; w = a2[k]; q = qa.get(k, {})
    stg = s["new_staging"]
    chips = [s["new_format"], "gaze: " + (s["gaze"] or "conversation")]
    if rr[k]:
        chips.append(f"re-rolled ×{rr[k]}")
    if w.get("card_text"):
        chips.append("lettering declared")
    data.append({"k": k, "group": G[q.get("status", "PASS")], "lt": w["lithuanian_TARGET"], "pron": w.get("lt_pron", ""),
                 "en": w["english"], "imgs": [{"src": f"{k}.jpg", "label": "Render", "cls": "after", "w": 760, "h": 507}],
                 "chips": chips, "facts": [["Staging", stg.split(" Insets:")[0]], ["Insets", stg.split(" Insets:")[1].strip() if " Insets:" in stg else ""],
                                           ["Must see", s["distinguishing_cue"]], ["Must not read as", s["confusables"]],
                                           ["Lettering", w.get("card_text", "")]],
                 "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", "")})
order = [G["FAIL"], G["WARN"], G["PASS"]]
data.sort(key=lambda c: (order.index(c["group"]), c["k"]))
n = {g: sum(c["group"] == g for c in data) for g in order}
extra = {"col": "phraseadd", "title": "Phrase additions", "hints": {G["FAIL"]: "mostly staging-level: the same read on all three rolls"},
 "lead": [f"The {len(data)} new phrase pictures (the PHRASE-route benchmark additions, A2-1897 to A2-2045), drawn bubble-free from the planner's staging "
          "with the round-2 situation rules. A2-1944 and A2-1958 are merged into A2-1995 and A2-1991 as planned. "
          "A2-2007 (one coffee), A2-2012 (recommend) and A2-2020 (pardon?) are held until you decide whether they merge with A2-0917, A2-0964 and A2-0374. "
          "A2-2002 shows the house number 7, declared as its only lettering (the plan's example; change it if you want another).",
          f"Every hard QA fail was re-rolled up to twice and the best roll kept: {n[G['PASS']]} pass, {n[G['WARN']]} carry notes, {n[G['FAIL']]} still fail. "
          "Mark OK or Redo; a note on a Redo says what to change in the staging."]}
TPL = open(R("a2_build/review_template/template_review.html"), encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Phrase Additions").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
          .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
print("phraseadd", len(data), n)
