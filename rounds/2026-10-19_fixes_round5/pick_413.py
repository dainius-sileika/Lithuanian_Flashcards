# -*- coding: utf-8 -*-
"""Round 5 pick for 413_tuoktis (three whole re-rolls of the first round-3 staging; try 1 = r6 has the cleanest hands): the picture the owner prefers is copied back
from <dir>/_rerolled/ (the copy there stays), the rejected render moves to <dir>/_rerolled/<key>.r<next>.png.
Nothing is deleted or overwritten. A ledger row 'RESTORED 2026-10-19' makes the restored picture the last row.
    python3 a2_build/round5/pick_413.py          # idempotent: a key already restored is skipped"""
import filecmp, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
import go_generator as g

TODAY = "2026-10-19"
JOBS = [("413_tuoktis", "out_deck_f62", "413_tuoktis.r6.png")]
LEDGER = {"out_deck_f62": os.path.expanduser("~/f62_work/ledger.csv"),
          "out_deck_a2": os.path.expanduser("~/a2_work/ledger.csv")}
LOG = os.path.join(HERE, "pick_log.txt")
done = set(l.split()[0] for l in open(LOG, encoding="utf-8")) if os.path.exists(LOG) else set()
touched = set()
for key, d, src in JOBS:
    if key in done:
        print("skip", key); continue
    cur, keep = f"{d}/{key}.png", f"{d}/_rerolled/{src}"
    assert os.path.exists(keep), keep
    if filecmp.cmp(cur, keep, shallow=False):
        print("already the kept picture:", key); continue
    n = 1
    while os.path.exists(f"{d}/_rerolled/{key}.r{n}.png"):
        n += 1
    os.replace(cur, f"{d}/_rerolled/{key}.r{n}.png")
    shutil.copyfile(keep, cur)
    msg = (f"{key} restored from {keep} | try 3 -> {d}/_rerolled/{key}.r{n}.png")
    lf, lw = g.GOGenerator.open_ledger(LEDGER[d])
    lw.writerow([key, "", "", "restored", "1536x1024", f"{key}.png",
                 f"PICKED {TODAY} (round 5: try 1 of 3, cleanest hands; tries 2-3 kept in _rerolled): {keep} is the current picture again; {msg}"])
    lf.close()
    open(LOG, "a", encoding="utf-8").write(msg + "\n")
    touched.add(d); print(msg)
for d in touched:
    shutil.copyfile(LEDGER[d], f"{d}/ledger.csv")
