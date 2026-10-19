# -*- coding: utf-8 -*-
"""Round 6: append the two A2-0359 renders to the out_phrases_v3 ledger. gen_0359.py called GOGenerator.generate()
directly, which writes no ledger row; the prompts are rebuilt here with the same call (try 2 = the current staging,
try 1 = the same prompt with the first round-6 inset text). Rows: try 1 (file now _rerolled/A2-0359.r7.png), then
try 2 (A2-0359.png = current picture, last row per key). Appends to ~/a2_work/v3_ledger.csv and copies it over
out_phrases_v3/ledger.csv, as out_phrases_v3/gen.py does. Run once.
    python3 a2_build/round6/ledger_r6.py"""
import csv, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "a2_build", "src"))
import go_generator as g
from gen_phrases import build_situation_call
K = "A2-0359"
row = next(r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8")) if r["id"] == K)
kw = build_situation_call(row); kw.pop("filename")
p2 = g.build_prompt(backend="openai", **kw)
src = open("a2_build/src/apply_round6.py", encoding="utf-8").read()
ns = {}; exec(src[src.index("TRY1_INSET2 = ("):src.index("\n\nbase =")], ns)
assert ns["NEW_INSET2"] in p2
p1 = p2.replace(ns["NEW_INSET2"], ns["TRY1_INSET2"])
LOCAL = os.path.expanduser("~/a2_work/v3_ledger.csv")
f, w = g.GOGenerator.open_ledger(LOCAL)
for p in (p1, p2):
    w.writerow([K, kw["subject"], "", f"openai/{g.OPENAI_MODEL}", "1536x1024", K + ".png", p])
f.close()
shutil.copyfile(LOCAL, "out_phrases_v3/ledger.csv")
print("2 rows appended")
