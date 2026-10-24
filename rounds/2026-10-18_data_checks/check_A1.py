# -*- coding: utf-8 -*-
"""A1 data checks B1-B3 (a2_build/A1_WRAPUP.md, 2026-10-18).
B1  no noun has an empty gender (cards_anki.csv + the A1-tagged rows of a2_wordlist.csv)
B2  rule-derived gen_sg / fem of the A1-tagged A2-list rows checked against kirtis.info's analyser
    (https://kirtis.info/api/krc/<form>); cache in kirtis_cache.json beside this file
B3  every A1 row has a pron with a stress mark
    python3 a2_build/data_checks/check_A1.py            # report -> results.json (no data changed)"""
import csv, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
CACHE = os.path.join(HERE, "kirtis_cache.json")
kc = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
BUDGET = float(os.environ.get("BUDGET", "150")); t0 = time.time()


def K(w):
    w = w.lower().strip(" ,.;")
    if w in kc:
        return kc[w]
    if time.time() - t0 > BUDGET:
        return None
    try:
        r = urllib.request.urlopen("https://kirtis.info/api/krc/" + urllib.parse.quote(w), timeout=20)
        kc[w] = json.loads(r.read().decode("utf-8") or "[]")
    except Exception as e:
        kc[w] = {"error": str(e)[:100]}
    time.sleep(0.15)
    return kc[w]


STRESS = re.compile("[̀́̃]")
def stressed(s):
    return bool(STRESS.search(unicodedata.normalize("NFD", s or "")))


A1 = list(csv.DictReader(open("cards_anki.csv", encoding="utf-8")))
M = {r["#"]: r for r in csv.DictReader(open("master_wordlist.csv", encoding="utf-8"))}
A2 = [r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8")) if r["level"] == "A1"]
res = {"B1": [], "B2_ok": [], "B2_bad": [], "B2_unknown": [], "B3": []}
# B1
for r in A1:
    if not r["gender"].strip() and M[r["number"]]["type"] == "N":
        res["B1"].append([r["key"], r["lithuanian"], "cards_anki", "typed N in master but a particle (yes/no)"])
for r in A2:
    if r["type"] == "N" and not r["gender"].strip():
        res["B1"].append([r["id"], r["lithuanian_TARGET"], "a2_wordlist", r["english"]])
# B2
GEN = {"M": "vyr.gim.", "F": "mot.gim."}
for r in A2:
    chk = r.get("check", "")
    jobs = []
    if "gen_sg: rule-derived" in chk and r["gen_sg"].strip():
        jobs.append(("gen_sg", r["gen_sg"].split()[-1], "K."))
    if "fem: rule" in chk and r["fem"].strip():
        jobs.append(("fem", r["fem"].split()[-1], "V."))
    for field, form, case in jobs:
        a = K(form)
        if a is None:
            res["B2_unknown"].append([r["id"], r["lithuanian_TARGET"], field, form, "not fetched (budget)"]); continue
        if isinstance(a, dict) or not a:
            res["B2_unknown"].append([r["id"], r["lithuanian_TARGET"], field, form, "kirtis: no analysis"]); continue
        g = (r["gender"] or "").strip().upper()[:1]
        pl = "pl" in (r["gender"] or "").lower()
        def fits(x):
            st = x.get("state", [])
            if case not in st:
                return False
            if field == "gen_sg":
                if x.get("class") != "dktv.":
                    return False
                if ("dgsk." if pl else "vnsk.") not in st:
                    return False
                return g not in GEN or GEN[g] in st or "bendr.gim." in st
            return "mot.gim." in st and "vnsk." in st
        hit = [x for x in a if fits(x)]
        (res["B2_ok"] if hit else res["B2_bad"]).append(
            [r["id"], r["lithuanian_TARGET"], field, form, hit[0]["word"] if hit else "; ".join(f'{x.get("class")} {" ".join(x.get("state", []))}' for x in a[:4])])
# B3
for r in A1:
    if not stressed(r.get("pron", "")):
        res["B3"].append([r["key"], r["lithuanian"], "cards_anki", r.get("pron", "")])
for r in A2:
    if not stressed(r.get("lt_pron", "")):
        res["B3"].append([r["id"], r["lithuanian_TARGET"], "a2_wordlist", r.get("lt_pron", "")])
json.dump(kc, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(res, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in res.items()}, "cache", len(kc))
