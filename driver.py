#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cowork production driver. Wraps deck_builder.py WITHOUT touching prompts
or grammars: runs N cards in parallel (each via `deck_builder.py --only KEY
--out out_par/KEY`), then merges PNG + ledger/cards rows into ./out_deck.
Resumable: skips keys whose PNG already exists in out_deck (unless --reroll).

Usage:
  python3 driver.py <Category> [N] [BUDGET_s]          # next N missing cards
  python3 driver.py --reroll key1,key2 [N] [BUDGET_s]  # forced re-rolls
"""
import csv, os, sys, time, shutil, subprocess

args = sys.argv[1:]
reroll = args and args[0] == "--reroll"
if reroll:
    only_keys = args[1].split(",")
    rest = args[2:]
else:
    cat = args[0]
    rest = args[1:]
N = int(rest[0]) if len(rest) > 0 else 3
BUDGET = float(rest[1]) if len(rest) > 1 else 37.0

import deck_builder as db
rows = db.load_rows("master_wordlist.csv")
work, _ = db.eligible(rows)

if reroll:
    want = set(only_keys)
    keys = [k for k, r, c in work if k in want]
    missing = keys  # force regeneration
else:
    keys = [k for k, r, c in work if r["category"] == cat]
    missing = [k for k in keys if not os.path.exists(f"out_deck/{k}.png")]

batch = missing[:N]
print(f"scope={len(keys)} remaining={len(missing)} batch={batch}")
if not batch:
    print("BLOCK_COMPLETE")
    sys.exit(0)

procs = []
for k in batch:
    od = f"out_par/{k}"
    shutil.rmtree(od, ignore_errors=True)
    os.makedirs(od, exist_ok=True)
    p = subprocess.Popen(
        [sys.executable, "deck_builder.py", "--only", k, "--out", od],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    procs.append((k, od, p))

t0 = time.time()
os.makedirs("out_deck", exist_ok=True)
for k, od, p in procs:
    remain = BUDGET - (time.time() - t0)
    try:
        out, _ = p.communicate(timeout=max(1.0, remain))
    except subprocess.TimeoutExpired:
        p.kill()
        print(f"{k}: TIMEOUT (will retry next call)")
        continue
    png = os.path.join(od, f"{k}.png")
    if os.path.exists(png):
        shutil.move(png, f"out_deck/{k}.png")
        for name in ("ledger.csv", "cards.csv"):
            src, dst = os.path.join(od, name), f"out_deck/{name}"
            if not os.path.exists(src):
                continue
            with open(src, newline="", encoding="utf-8") as f:
                lines = f.readlines()
            new = not os.path.exists(dst)
            with open(dst, "a", newline="", encoding="utf-8") as f:
                if new:
                    f.write(lines[0])
                f.writelines(lines[1:])
        print(f"{k}: OK")
    else:
        print(f"{k}: FAIL")
        print((out or "")[-400:])
    shutil.rmtree(od, ignore_errors=True)
