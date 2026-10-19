# -*- coding: utf-8 -*-
"""Round 6 data change (2026-10-19), idempotent; run after apply_round5.py.
Source: the owner on A2-0359 (Round 5 Fixes): "Final panel should be a man leaving the hospital, not entering it".
The round-5 inset 2 ("walking out through the hospital's front doors onto the steps, seen from behind") was drawn as a
man seen from behind going UP the steps toward the doors, which reads as entering. Round 6 keeps the main scene and
inset 1 word for word and stages inset 2 so that it cannot be read the other way: he comes DOWN the steps toward the
viewer, face and coat front visible, bag in hand, the doors BEHIND him. Whole re-roll (spec 3.1.0 working rule).
Try 1 failed QA GAZE (the inset man looked at the viewer); try 2 lowers his eyes to the steps.
Log: a2_build/round6/data_applied.csv. Then: python3 a2_build/src/build_situations.py"""
import csv, io, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
TODAY = "2026-10-19"; LOG = []
R6 = "a2_build/round6"


def rd(p):
    raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(raw)))
    return rows, list(rows[0].keys()), nl


def wr(p, rows, fields, nl):
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(out.getvalue())


RB = "a2_build/restage_bubbles.csv"; rows, F, nl = rd(RB)
last = {}
for r in rows:
    for i in [x.strip() for x in r["ids"].split(",") if x.strip()]:
        if r["render"].strip().startswith("yes"):
            last[i] = r
MARK = "round 6 (owner review 2026-10-19; whole re-roll)"

OLD_INSET2 = ("the same man in his brown overcoat walking out through the hospital's front doors onto the steps, "
              "seen from behind")
TRY1_INSET2 = ("the same man LEAVING the hospital, with the same greying hair, the same long brown overcoat buttoned "
              "and the checked scarf, a small brown leather bag in his RIGHT hand, coming DOWN the front steps TOWARD "
              "the viewer and away from the building, his face and the front of his coat turned to us with a quiet, "
              "relieved look, the hospital entrance with its glass double doors BEHIND him at the top of the steps and "
              "closing after him, his back to the building (he does not face or approach the doors)")
# try 1 failed QA GAZE (the man in the inset looked out at the viewer): try 2 keeps him facing us but lowers his eyes
NEW_INSET2 = ("the same man LEAVING the hospital, with the same greying hair, the same long brown overcoat buttoned "
              "and the checked scarf, a small brown leather bag in his RIGHT hand, coming DOWN the front steps TOWARD "
              "the viewer and away from the building, the front of his coat turned to us, his eyes lowered to the "
              "steps in front of his feet (he does not look at the viewer), the hospital entrance with its glass double "
              "doors BEHIND him at the top of the steps and closing after him, his back to the building (he does not "
              "face or approach the doors)")

base = last["A2-0359"]
if base["old_format"] == MARK:
    new = base
else:
    new = dict(base); new["old_format"] = MARK; new["render"] = "yes — round 6 (supersedes the earlier rows)"
    rows.append(new); LOG.append([RB, "A2-0359", "row", "", "appended (round 6)"])
st = new["new_staging"]
for prior in (OLD_INSET2, TRY1_INSET2):
    if prior in st:
        st = st.replace(prior, NEW_INSET2); new["new_staging"] = st
        LOG.append([RB, "A2-0359", "new_staging", prior, NEW_INSET2])
if NEW_INSET2 not in st:
    raise SystemExit("A2-0359: round-5 inset text not found; staging changed since round 5")
wr(RB, rows, F, nl)

os.makedirs(R6, exist_ok=True)
logp = f"{R6}/data_applied.csv"
prev = list(csv.reader(open(logp, encoding="utf-8"))) if os.path.exists(logp) else [["date", "file", "key", "field", "old", "new"]]
with open(logp, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerows(prev); w.writerows([[TODAY] + l for l in LOG])
print(len(LOG), "changes")
