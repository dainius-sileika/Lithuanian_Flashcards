# -*- coding: utf-8 -*-
"""Round 7: append the A2-0359 render to the out_phrases_v3 ledger. gen_0359.py calls GOGenerator.generate()
directly, which writes no ledger row; the prompt is rebuilt here with the same call (try 1 = the card,
out_phrases_v3/A2-0359.png, last row per key). Appends to ~/a2_work/v3_ledger.csv and copies it over
out_phrases_v3/ledger.csv, as out_phrases_v3/gen.py does. Run once.
    python3 a2_build/round7/ledger_r7.py"""
import csv, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
import go_generator as g
from gen_phrases import build_situation_call
K = "A2-0359"
row = next(r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8")) if r["id"] == K)
kw = build_situation_call(row); kw.pop("filename")
p = g.build_prompt(backend="openai", **kw)
assert "a glass of water and a folded white towel" in p
LOCAL = os.path.expanduser("~/a2_work/v3_ledger.csv")
if not os.path.exists(LOCAL):
    shutil.copyfile("out_phrases_v3/ledger.csv", LOCAL)
f, w = g.GOGenerator.open_ledger(LOCAL)
w.writerow([K, kw["subject"], "", f"openai/{g.OPENAI_MODEL}", "1536x1024", K + ".png", p])
f.close()
shutil.copyfile(LOCAL, "out_phrases_v3/ledger.csv")
print("1 row appended")
