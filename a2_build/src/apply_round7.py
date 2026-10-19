# -*- coding: utf-8 -*-
"""Round 7 data change (2026-10-20), idempotent; run after apply_round6.py.
Source: the owner on A2-0359 (Round 6 Fixes): "Can't be flowers in the first insert, because the flowers come after his
release; redo". The round-6 render put flowers in inset 1 (the patient in bed). Round 7 keeps the main scene and inset 2
word for word and stages inset 1 with what IS there: plain bedding, the nurse holding the clipboard, a bedside table
with only a glass of water and a folded towel, plain walls; the flowers belong to the main scene only.
Whole re-roll (spec 3.1.0 working rule). Log: a2_build/round7/data_applied.csv.
Then: python3 a2_build/src/build_situations.py"""
import csv, io, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
TODAY = "2026-10-20"; LOG = []
R7 = "a2_build/round7"


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
MARK = "round 7 (owner review 2026-10-20; whole re-roll)"

OLD_INSET1 = ("the same man some days earlier as a patient in striped pyjamas, sitting up in a hospital bed, the same "
              "nurse standing beside the bed")
NEW_INSET1 = ("the same man some days earlier as a patient in striped pyjamas, sitting up in a hospital bed with plain "
              "white sheets, the same nurse in her white coat and cap standing beside the bed with the dark clipboard "
              "in both hands, a small bare bedside table holding only a glass of water and a folded white towel, plain "
              "pale green walls (this moment is before his discharge: the flowers appear only in the main scene)")

base = last["A2-0359"]
if base["old_format"] == MARK:
    new = base
else:
    new = dict(base); new["old_format"] = MARK; new["render"] = "yes — round 7 (supersedes the earlier rows)"
    rows.append(new); LOG.append([RB, "A2-0359", "row", "", "appended (round 7)"])
st = new["new_staging"]
if NEW_INSET1 not in st:
    if OLD_INSET1 not in st:
        raise SystemExit("A2-0359: round-6 inset-1 text not found; staging changed since round 6")
    st = st.replace(OLD_INSET1, NEW_INSET1, 1); new["new_staging"] = st
    LOG.append([RB, "A2-0359", "new_staging", OLD_INSET1, NEW_INSET1])
wr(RB, rows, F, nl)

os.makedirs(R7, exist_ok=True)
logp = f"{R7}/data_applied.csv"
prev = list(csv.reader(open(logp, encoding="utf-8"))) if os.path.exists(logp) else [["date", "file", "key", "field", "old", "new"]]
with open(logp, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerows(prev); w.writerows([[TODAY] + l for l in LOG])
print(len(LOG), "changes")
