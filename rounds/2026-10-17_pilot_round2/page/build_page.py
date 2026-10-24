# -*- coding: utf-8 -*-
"""Review page "Pilot Round 2" (2026-10-18): the 14 round-2 redraws beside their round-1
pictures and the owner's round-1 notes, with the round-1 controls (Situation yes/nearly/no,
neighbour-fail toggle, stray toggle, note), plus three phone-width backs showing the new
usage notes. Verdicts go to the artifact db: collection "pilot2", general notes
"pilot2_meta/general" (capabilities db + user); localStorage is the offline mirror.

    python3 build_page.py <repo root> <out dir>      # writes <out>/index.html; media/ beside it
media/: <key>_r2.jpg (1024 px), <key>_r1.jpg and <key>_roll<rN>.jpg (640 px), back_<key>.jpg
"""
import csv, json, os, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(ROOT, p)
HERE = os.path.dirname(os.path.abspath(__file__))
red = {r["key"]: r for r in csv.DictReader(open(R("a2_build/pilot_round2/redraw_list.csv"), encoding="utf-8"))}
plan = {j["key"]: j for j in json.load(open(R("out_phrases_v3/round2/plan.json"), encoding="utf-8"))["jobs"]}
qa = {r["key"]: r for r in csv.DictReader(open(R("out_phrases_v3/round2/qa_round2.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open(R("a2_build/a2_wordlist.csv"), encoding="utf-8"))}
led = list(csv.DictReader(open(R("out_phrases_v3/round2/ledger.csv"), encoding="utf-8")))
rolls_n = {k: sum(1 for r in led if r["key"] == k) for k in red}
FIX = {"A2-0360": "Conversation gaze", "A2-0377": "Conversation gaze", "A2-0928": "Conversation gaze",
       "A2-0897": "Panel continuity + conversation gaze", "A2-0898": "Panel continuity; the door named in both panels",
       "A2-0900": "Anatomy/props (no figure in the counter) + conversation gaze",
       "A2-0895": "Anatomy/props; staging assigns each arm",
       "A2-0383": "Anatomy/props; continuity on insets; staging names the insets",
       "A2-0114": "Staging names her right hand; anatomy/props honours it",
       "A2-0882": "New scene: paints and easel", "A2-0881": "New scene: boy, football, broken pane",
       "A2-0362": "New scene: the bump on the trolleybus", "A2-0113": "New scene as you designed it: main panel + two insets",
       "A2-0352": "Extended hand added"}
HIST = {"A2-0113": "roll 1 failed CONTINUITY (the board inset is a different moment, as staged) and read as 'how'; roll 2 current",
        "A2-0114": "all three rolls read as the price phrase in the neighbour test; roll 1 also failed GAZE (seller looks at the scale); roll 3 current",
        "A2-0362": "roll 1 read as 'Excuse me, please…' with a clear margin; roll 2 (current) only slightly",
        "A2-0881": "all three rolls fail GAZE: the staging bows the boy's head, so the two never meet eyes; roll 3 current",
        "A2-0895": "all three rolls read as 'Goodbye' in the neighbour test; roll 3 current"}
SETS = [("Rule-caused in round 1", "Gaze, continuity, limbs and props. Did the new rules fix them?",
         ["A2-0360", "A2-0377", "A2-0928", "A2-0897", "A2-0898", "A2-0900", "A2-0895", "A2-0383"]),
        ("Staging-caused in round 1", "New or amended staging, drawn under the new rules as well.",
         ["A2-0114", "A2-0882", "A2-0881", "A2-0362", "A2-0113", "A2-0352"])]
data = []
for sname, hint, keys in SETS:
    for k in keys:
        j, q, r = plan[k], qa.get(k, {}), red[k]
        st = j["staging"]
        n = rolls_n.get(k, 1)
        data.append({"k": k, "set": sname, "lt": j["lt"], "pron": (a2.get(k) or {}).get("lt_pron", ""), "en": j["en"],
                     "fmt": {"situation": "single scene", "situation_2": "two panels"}.get(j["format"], j["format"]),
                     "staging": st.split(" Insets:")[0], "insets": st.split(" Insets:")[1].strip() if " Insets:" in st else "",
                     "cue": j["cue"], "conf": j["confusables"], "qa": q.get("status", ""), "fails": q.get("fails", ""),
                     "warns": q.get("warnings", ""), "nb": q.get("neighbour", ""), "rr": n - 1,
                     "img": f"{k}_r2.jpg", "r1": f"{k}_r1.jpg", "owner": r["reason_owner"],
                     "rolls": [f"{k}_rollr{i}.jpg" for i in range(1, n)], "hist": HIST.get(k, ""),
                     "cause": "rule" if sname.startswith("Rule") else "staging", "fix": FIX[k]})
sets_meta = [{"name": s, "hint": h, "n": len(ks)} for s, h, ks in SETS]
notes = list(csv.DictReader(open(R("a2_build/context_notes.csv"), encoding="utf-8")))
nv = sum(1 for x in notes if x["confidence"] in ("high", "medium"))
BACKS = [("A2-0348", "Labas", "Hello"), ("A2-0362", "Atleiskite", "Excuse me (formal)"), ("A2-1157", "Kiek jums metų?", "How old are you?")]
extra = {"sets": sets_meta,
         "lead": ["The 14 cards you sent back from round 1, redrawn under the round-2 rules: speakers look at each other and nobody looks at the viewer; "
                  "panels, strips and insets that repeat a scene keep the same people, places and props; every arm on its own body, the named hand does the action, "
                  "carried things are gripped. Your round-1 picture and note sit small under each new one.",
                  "Same rubric as round 1: a card passes with Situation yes or nearly, not mistakable for its neighbour, and no stray act. "
                  "Machine QA (with the new gaze, continuity, limb and prop checks) re-rolled a hard fail at most twice; three cards still fail it and are shown as they are. "
                  "The other ~133 bubble cards are not drawn yet: they wait for your verdict here."],
         "backs_lead": [f"{nv} of the {len(notes)} context notes are on the backs now (verified against a read source, or medium confidence). "
                        f"The {len(notes) - nv} unverified ones wait for you in a2_build/context_notes_unverified.csv. A tu/jūs variant goes on a second line."],
         "backs": [{"k": k, "lt": lt, "en": en, "f": f"back_{k}.jpg"} for k, lt, en in BACKS]}
TPL = open(os.path.join(HERE, "template2.html"), encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Pilot Round 2").replace("/*__MODE__*/", json.dumps("pilot2"))
          .replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
          .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
print("pilot2", len(data), "cards")
