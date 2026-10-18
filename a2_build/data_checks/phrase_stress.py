# -*- coding: utf-8 -*-
"""B3 follow-up (2026-10-18): assemble a stressed pron, word by word from kirtis.info, for the A1-tagged
A2-list rows that have none (mostly PHRASE rows). A word is taken only when every kirtis analysis gives the
same stressed form; monosyllables kirtis leaves unmarked stay plain. A row is proposed only when no word with
two or more syllables is ambiguous or unknown. Writes proposals.json (id -> pron) and ambiguous.json.
    BUDGET=160 python3 a2_build/data_checks/phrase_stress.py"""
import json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import check_A1 as C          # runs the checks (cached) and gives K(), stressed(), results
res = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
A2 = {r["id"]: r for r in C.A2}
VOW = re.compile("[aąeęėiįyouųū]", re.I)
def syl(w):
    return len(re.findall(r"(ie|uo|ai|au|ei|ui|[aąeęėiįyouųū])", w.lower()))
prop, amb = {}, {}
for key, lt, src, _ in res["B3"]:
    if src != "a2_wordlist":
        continue
    toks = re.split(r"(\w+)", A2[key]["lithuanian_TARGET"])
    out, bad = [], []
    for t in toks:
        if not re.fullmatch(r"\w+", t) or t.isdigit():
            out.append(t); continue
        a = C.K(t)
        if a is None:
            bad.append(t + " (not fetched)"); out.append(t); continue
        forms = sorted({x["word"].lower() for x in a}) if isinstance(a, list) else []
        if len(forms) == 1:
            f = forms[0]
            out.append(f[0].upper() + f[1:] if t[0].isupper() else f)
        elif syl(t) <= 1 and (not forms or all(not C.stressed(f) for f in forms)):
            out.append(t)
        else:
            bad.append(f"{t}: {' / '.join(forms) if forms else 'no analysis'}"); out.append(t)
    s = "".join(out)
    if bad or not C.stressed(s):
        amb[key] = {"lt": A2[key]["lithuanian_TARGET"], "partial": s, "why": bad or ["no stressed word"]}
    else:
        prop[key] = s
json.dump(C.kc, open(C.CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(prop, open(os.path.join(HERE, "proposals.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(amb, open(os.path.join(HERE, "ambiguous.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(prop), "proposed,", len(amb), "ambiguous/unknown")
