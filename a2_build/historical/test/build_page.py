# -*- coding: utf-8 -*-
"""Review page "Historical Test" (2026-10-18): the six renders of
a2_build/historical/implementation/test_plan.csv beside the card as it ships now, the plan's
judging questions per render (yes / partly / no), QA, and OK / Redo + note.
db (capabilities db + user): collection "histtest", general notes "histtest_meta/general".
    python3 a2_build/historical/test/build_page.py <repo root> <out dir>   # media/<key>.jpg, <key>_now.jpg"""
import csv, json, os, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(ROOT, p)
HERE = os.path.dirname(os.path.abspath(__file__))
plan = list(csv.DictReader(open(R("a2_build/historical/implementation/test_plan.csv"), encoding="utf-8")))
qa = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "qa_histtest.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open(R("a2_build/a2_wordlist.csv"), encoding="utf-8"))}
master = {r["#"].zfill(3): r for r in csv.DictReader(open(R("master_wordlist.csv"), encoding="utf-8"))}
LA = json.load(open(R("a2_build/historical/implementation/likeness_args.json"), encoding="utf-8"))["cards"]
O = [["yes", "Yes"], ["nearly", "Partly"], ["no", "No"]]
Q = {
 "T1": [("word", "Reads as “plane” at a glance, the aircraft the largest thing?"),
        ("plane", "An orange strutted high-wing monoplane with a ring cowl and spoked wheels?"),
        ("faces", "The two men differ, and does either look like Darius or Girėnas?"),
        ("text", "No lettering on the fuselage?")],
 "T2": [("word", "Reads as “author / writer”, not “grandmother”?"),
        ("zemaite", "Do you see Žemaitė without being told?"),
        ("binkis", "Does the man pass for Binkis, or at least a 1930s writer?")],
 "T3": [("hall", "Steel arches and skylights clean, without garble?"),
        ("kit", "White kit with one clean diagonal tricolour band (not a flag on a shirt)?"),
        ("word", "The shot at the hoop is still the subject?")],
 "T4": [("place", "Behind the judge: a skylit hall, marble columns with carved capitals?"),
        ("cross", "The double-barred cross drawn once, clean, no extra bars?"),
        ("word", "Still “court” at a glance?")],
 "T5": [("face", "Do you recognise Valdas Adamkus?"),
        ("vytis", "The Vytis whole and clean: knight, rearing horse, sword up, shield?"),
        ("word", "Still “president” at a glance? (QA's cold read said “Lithuania”.)"),
        ("woman", "The woman president stays anonymous?")],
 "T6": [("statue", "Winged striding figure with broken chains and a banner, on a plinth, bell tower behind?"),
        ("word", "Reads as “monument”, not angel and not Statue of Liberty?")],
}
NOTE = {
 "T5": "The API accepted the named likeness (no refusal). Face words corrected before the render: the planner's draft had spectacles and a long face; his official portrait shows neither.",
 "T1": "Face words corrected to the portraits before the render: Darius has the broad square face, Girėnas the narrower oval one (the draft had them the other way round).",
 "T2": "Binkis wears a tie in his portrait; the draft said no tie.",
 "T4": "The re-roll also carries the hand-scan fix for 035 (the gavel held in his right fist).",
}
data = []
for t in plan:
    k = t["key"]
    if k.startswith("A2"):
        w = a2[k]; lt, pron, en = w["lithuanian_TARGET"], w["lt_pron"], w["english"]
    else:
        m = master[k[:3]]; lt, pron, en = m["lithuanian_TARGET"], m["lt_pron"], m["english"]
    q = qa.get(k, {})
    lk = "; ".join(f"{x['name']} ({x['period']}): {x['features']}" for x in LA.get(k, {}).get("likeness", []))
    data.append({"k": k, "group": "Six-render test", "lt": lt, "pron": pron, "en": en,
                 "imgs": [{"src": f"{k}.jpg", "label": f"{t['test']} test render", "cls": "after"},
                          {"src": f"{k}_now.jpg", "label": "The card as it ships now", "w": 480, "h": 320}],
                 "chips": [t["test"]], "questions": [{"id": i, "text": s, "opts": O} for i, s in Q[t["test"]]],
                 "facts": [["Tests", t["what_is_tested"]], ["Precedent", LA.get(k, {}).get("precedent", "")],
                           ["Likeness", lk], ["Expected", t["expected_outcome"]], ["Executor", NOTE.get(t["test"], "")]],
                 "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", "")})
extra = {"col": "histtest", "title": "Historical test", "hints": {"Six-render test": "judge the word first, the style second, the reference third"},
 "lead": ["The six approved test renders for the historical places and figures plan, drawn with the new precedent, likeness and emblem rules. "
          "They are rendered into a2_build/historical/test/ and do not replace any shipped picture; the roll-out to the other cards (A5) waits for your verdict here.",
          "Answer the questions under each render, then OK or Redo. A render passes only if the word is still guessable. "
          "Your answers on T4 (Cross of Vytis) and T5 (Vytis) decide whether the emblem text becomes the default flag rule."]}
TPL = open(R("a2_build/review_template/template_review.html"), encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Historical Test").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
          .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
print("histtest", len(data))
