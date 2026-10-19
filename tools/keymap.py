#!/usr/bin/env python3
"""keymap.py — every name a card has ever had, and the one it has now.

The rename of 2026-10 (a2_build/rename/PLAN_rename_v1.md) gave every card one key of the form
NNNN_slug. The maps written by tools/rename_keys.py (a2_build/rename/key_map_v<N>.csv) are the
only record linking the older names (001_suo, A2-0348, S-0001, and media-only aliases such as
265_lupos) to the current key. They are never deleted or edited; a later rename appends a new
map, and this module follows the chain.

    import keymap
    keymap.canonical("A2-0348")     -> "0021_labas"   (or the input itself when it is not an alias)
    keymap.aliases("0021_labas")    -> ["A2-0348"]    (every older name, oldest first)
    keymap.lookup(d, "0021_labas")  -> d[key] by the current key, else by any alias (for ledgers
                                       and other append-only records that keep the old names)

Readers of append-only records (ledgers, gen logs, QA sheets, build manifests) use lookup();
live data files carry the current key only.
"""
import csv
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_GLOB = os.path.join(ROOT, "a2_build", "rename", "key_map_v*.csv")

_FORWARD = None     # old -> new, over every map in version order
_BACK = None        # new -> [old, ...]


def _load():
    global _FORWARD, _BACK
    if _FORWARD is not None:
        return
    fwd = {}
    paths = sorted(glob.glob(MAP_GLOB), key=lambda p: int(p.rsplit("_v", 1)[1].split(".")[0]))
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            old, new = r["old_key"].strip(), (r.get("new_key") or "").strip()
            if old and new and old != new:
                fwd[old] = new
    back = {}
    for old, new in fwd.items():
        back.setdefault(canonical(new, fwd), []).append(old)
    _FORWARD, _BACK = fwd, back


def canonical(key, fwd=None):
    """Follow old -> new until the current key (cycle-safe)."""
    if fwd is None:
        _load(); fwd = _FORWARD
    seen = set()
    while key in fwd and key not in seen:
        seen.add(key); key = fwd[key]
    return key


def canonical_take(take):
    """A recorder take key or media stem: '<key>' or '<key>_s' (example sentence) -> the same with the
    current key ('A2-0002_s' -> '0261_valanda_s'). Unknown names come back unchanged."""
    _load()
    if take in _FORWARD:
        return canonical(take)
    if take.endswith("_s") and take[:-2] in _FORWARD:
        return canonical(take[:-2]) + "_s"
    return take


def aliases(key):
    _load()
    return list(_BACK.get(canonical(key), []))


def lookup(mapping, key, default=None):
    """mapping[key] by the current key, else by any older name of the same card."""
    k = canonical(key)
    if k in mapping:
        return mapping[k]
    for a in aliases(k):
        if a in mapping:
            return mapping[a]
    if key in mapping:
        return mapping[key]
    return default


def maps():
    """The map files found, in version order."""
    return sorted(glob.glob(MAP_GLOB), key=lambda p: int(p.rsplit("_v", 1)[1].split(".")[0]))
