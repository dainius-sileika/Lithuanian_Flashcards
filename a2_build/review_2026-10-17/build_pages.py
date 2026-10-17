# -*- coding: utf-8 -*-
"""Review pages for 2026-10-17: (1) the bubble-free pilot (34 cards, PILOT_24 rubric),
(2) the 43 IMG benchmark additions + the 5 picture-fix re-rolls. Reads the repo at ROOT,
writes <OUT>/pilot/index.html and <OUT>/adds/index.html (media/ beside each holds the
1024 px JPEG copies). Same pattern as out_deck_a2/build_review_a2.py: verdicts go to the
artifact db (window.claude.use('db')), localStorage is the offline mirror.

    python3 build_pages.py <repo root> <out dir>
"""
import csv, html, json, os, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(ROOT, p)
esc = html.escape

a2 = {r["id"]: r for r in csv.DictReader(open(R("a2_build/a2_wordlist.csv"), encoding="utf-8"))}
master = {r["#"]: r for r in csv.DictReader(open(R("master_wordlist.csv"), encoding="utf-8"))}
anki = {r["key"]: r for r in csv.DictReader(open(R("cards_anki.csv"), encoding="utf-8"))}

# ---------------------------------------------------------------- pilot
plan = {j["key"]: j for j in json.load(open(R("out_phrases_v3/plan.json"), encoding="utf-8"))["jobs"]}
qa = {r["key"]: r for r in csv.DictReader(open(R("out_phrases_v3/qa_v3.csv"), encoding="utf-8"))}
SETS = [
    ("Greetings", "Time of day and register must carry them.", ["A2-0348", "A2-0349", "A2-0350", "A2-0351", "A2-0352"]),
    ("Thanks, apology, politeness", "The gesture must not cross over.", ["A2-0358", "A2-0881", "A2-0362", "A2-0383"]),
    ("Good luck", "Exam folder against train and suitcase.", ["A2-0887", "A2-0895"]),
    ("Price", "Loaf lifted, purse ready.", ["A2-0377"]),
    ("Two panels", "Same two people, same scale; the right panel answers the left.",
     ["A2-0882", "A2-0360", "A2-0896", "A2-0897", "A2-0898", "A2-0900", "A2-0903", "A2-0905", "A2-0906", "A2-0907", "A2-0909", "A2-0928"]),
    ("Question words", "A situation, not an object: is this the scene in which the word is used?",
     ["A2-0108", "A2-0110", "A2-0111", "A2-0112", "A2-0113", "A2-0114", "A2-0115", "A2-0116", "A2-0117"]),
    ("Galvoti", "Does chin-in-hand survive without the bubble, distinct from to remember / to read?", ["374_galvoti"]),
]
rerolls_v3 = {"A2-0114": 1, "A2-0115": 2}
pilot = []
for sname, shint, keys in SETS:
    for k in keys:
        j = plan[k]; q = qa.get(k, {})
        row = a2.get(k) or {}
        if k == "374_galvoti":
            row = {"lithuanian_TARGET": "galvoti", "lt_pron": anki.get("374_galvoti", {}).get("pron", "")}
        pilot.append({"k": k, "set": sname, "lt": j["lt"] or row.get("lithuanian_TARGET", ""),
                      "pron": row.get("lt_pron", ""), "en": j["en"],
                      "fmt": {"situation": "single scene", "situation_2": "two panels"}.get(j["format"], j["format"]),
                      "staging": j["staging"].split(" Insets:")[0], "insets": (j["staging"].split(" Insets:")[1].strip() if " Insets:" in j["staging"] else ""),
                      "cue": j["cue"], "conf": j["confusables"], "qa": q.get("status", ""),
                      "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "nb": q.get("neighbour", ""),
                      "rr": rerolls_v3.get(k, 0)})
sets_meta = [{"name": s, "hint": h, "n": len(ks)} for s, h, ks in SETS]

# ---------------------------------------------------------------- additions + re-rolls
aplan = {j["key"]: j for j in json.load(open(R("out_deck_a2/plan.json"), encoding="utf-8"))["jobs"]}
aqa = {r["key"]: r for r in csv.DictReader(open(R("out_deck_a2/qa_a2_additions_2026-10-17.csv"), encoding="utf-8"))}
fplan = {j["key"]: j for j in json.load(open(R("out_deck_f62/plan.json"), encoding="utf-8"))["jobs"]}
fqa = {r["key"]: r for r in csv.DictReader(open(R("out_deck_f62/qa_f62_fixes_2026-10-17.csv"), encoding="utf-8"))}
notes = json.load(open(R("card_notes.json"), encoding="utf-8"))["notes"]
FIX = {"290_vandenynas": "Subject phrase no longer asks for a steamship.",
       "318_sala": "Trakai castle setting line removed; plain lake island.",
       "336_kilogramas": "EU/LT flag clause removed from the subject phrase.",
       "338_peda": "US/UK flag clause removed from the subject phrase.",
       "339_svaras": "US/UK flag clause removed from the subject phrase and the card-note inset; rolled twice (the first still drew flags)."}
adds = []
for k in sorted(aplan):
    if k < "A2-1863":
        continue
    r = a2[k]; q = aqa.get(k, {})
    forms = (f"{r['lithuanian_TARGET']} ♂ · {r['fem']} ♀" if r["fem"] else
             (r["gen_sg"] and f"gen. {r['gen_sg']}") or (r["pres3"] and f"{r['pres3']} · {r['past3']}") or "")
    adds.append({"k": k, "group": "New A2 pictures", "lt": r["lithuanian_TARGET"], "pron": r["lt_pron"],
                 "en": r["english"], "forms": forms, "gender": r["gender"], "staging": r["subject_phrase_EN"],
                 "note": "", "ct": r["card_text"], "qa": q.get("status", ""), "fails": q.get("fails", ""),
                 "warns": q.get("warnings", ""), "guess": q.get("guess", ""), "before": "",
                 "rr": 2 if k == "A2-1939" else 0})
for k in FIX:
    n = k.split("_")[0].lstrip("0"); m = master[n]; q = fqa.get(k, {})
    adds.append({"k": k, "group": "Picture fixes (A1, re-rolled)", "lt": m["lithuanian_TARGET"], "pron": m["lt_pron"],
                 "en": m["english"], "forms": "", "gender": m["gender"], "staging": fplan[k]["subject"],
                 "note": FIX[k] + (" Card note: " + notes[k] if k in notes else ""), "ct": m["card_text"],
                 "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""),
                 "guess": q.get("guess", ""), "before": f"{k}_before.jpg", "rr": 2 if k == "339_svaras" else 1})

TPL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), encoding="utf-8").read()
for name, data, extra in [("pilot", pilot, {"sets": sets_meta}), ("adds", adds, {})]:
    doc = (TPL.replace("__TITLE__", {"pilot": "Bubble-free Pilot", "adds": "A2 Additions and Fixes"}[name])
              .replace("/*__MODE__*/", json.dumps(name))
              .replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
              .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
    os.makedirs(os.path.join(OUT, name), exist_ok=True)
    open(os.path.join(OUT, name, "index.html"), "w", encoding="utf-8").write(doc)
    print(name, len(data))
