#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_keys_v1.py — after the naturalness round: every card keeps its key NUMBER; only the two minted cards are new.

    python3 rounds/2026-10-28_naturalness/check_keys_v1.py <study_order.csv before> [<study_order.csv after>]

Each key of the earlier order is followed through every data/key_maps/key_map_v*.csv (tools/keymap.canonical) to
its current key; its number (the first four digits) must be unchanged and the current key must be in the later
order. The later order may only add keys; those are listed (expected: 2434_ka_daryti, 2435_spustis).
Exit 1 on any difference.
"""
import csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import keymap   # noqa: E402


def keys(p):
    return [r["key"] for r in csv.DictReader(open(p, encoding="utf-8"))]


def main(before, after):
    old, new = keys(before), keys(after)
    newset = set(new)
    bad, renamed = [], []
    for k in old:
        cur = keymap.canonical(k) or k
        if cur not in newset:
            bad.append(f"{k} -> {cur}: not in {after}")
        elif cur[:4] != k[:4]:
            bad.append(f"{k} -> {cur}: number changed")
        elif cur != k:
            renamed.append(f"{k} -> {cur}")
    added = sorted(newset - {keymap.canonical(k) or k for k in old})
    print(f"before: {len(old)} keys; after: {len(new)} keys")
    print(f"numbers unchanged for all {len(old) - len(bad)} earlier keys; re-slugged (same number): {len(renamed)}")
    for r in renamed:
        print("  ", r)
    print(f"new keys: {len(added)} {added}")
    print(f"numbers in use: {len({k[:4] for k in new})} distinct of {len(new)} keys")
    for b in bad:
        print("FAIL", b)
    return 1 if bad or len({k[:4] for k in new}) != len(new) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data/study_order.csv")))
