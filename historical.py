# -*- coding: utf-8 -*-
"""historical.py (2026-10-18): per-card precedent / likeness arguments for the historical places
and figures plan (a2_build/historical/implementation/). hist_args(key) returns the keyword
arguments deck_builder.build_call and a2_adapter.build_call_a2 add for that card:
{"precedent": <description>, "likeness": <formatted LIKENESS_RULE text, one per figure>},
or {} for every card not listed as active in likeness_args.json (they render as before)."""
import json, os
import go_generator as g
_P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "a2_build", "historical", "implementation", "likeness_args.json")
_D = json.load(open(_P, encoding="utf-8")) if os.path.exists(_P) else {"active": [], "cards": {}}
ACTIVE = set(_D.get("active", []))


def hist_args(key):
    c = _D["cards"].get(key)
    if key not in ACTIVE or not c:
        return {}
    out = {}
    if c.get("precedent"):
        out["precedent"] = c["precedent"]
    figs = [g.LIKENESS_RULE.format(**f) for f in c.get("likeness", [])]
    if figs:
        out["likeness"] = " ".join(figs)
    return out
