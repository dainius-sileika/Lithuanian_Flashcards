# -*- coding: utf-8 -*-
"""Round 7: whole re-roll of A2-0359 (staging from a2_build/src/apply_round7.py via situations.py).
The picture in $PHRASES_OUT/A2-0359.png (default out_phrases_v3) moves to $PHRASES_OUT/_rerolled/A2-0359.r<n>.png (next
free n) first; nothing is overwritten. One render per run.
    PHRASES_OUT=<project>/out_phrases_v3 python3 a2_build/round7/gen_0359.py"""
import csv, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
from gen_phrases import build_situation_call, OUT
from go_generator import GOGenerator
K = "A2-0359"
row = next(r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8")) if r["id"] == K)
kw = build_situation_call(row)
assert kw and "a glass of water and a folded white towel" in kw["inset_note"], "situations.py does not carry the round-7 staging"
assert "LEAVING the hospital" in kw["inset_note"], "round-6 inset 2 missing"
cur = f"{OUT}/{K}.png"
if os.path.exists(cur):
    os.makedirs(f"{OUT}/_rerolled", exist_ok=True)
    n = 1
    while os.path.exists(f"{OUT}/_rerolled/{K}.r{n}.png"):
        n += 1
    shutil.move(cur, f"{OUT}/_rerolled/{K}.r{n}.png")
    print(f"moved {K}.png -> _rerolled/{K}.r{n}.png")
GOGenerator(backend="openai", ratio="4:3").generate(out_dir=OUT, **kw)
print("rendered", K, os.path.exists(cur))
