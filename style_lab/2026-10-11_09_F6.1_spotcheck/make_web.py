"""Blind pairwise review for the F6.1 spot-check (gpt-image-2 vs Sunburst) + strict paper tone."""
import json, os, random, secrets, csv, importlib.util
from PIL import Image
D = "style_lab/2026-10-11_09_F6.1_spotcheck"
spec = importlib.util.spec_from_file_location("pt2", "style_lab/tools/papertone2.py"); pt2 = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(pt2)
except SystemExit: pass
plan = json.load(open(f"{D}/plan.json"))
rows = {f"{int(r['#']):03d}": r for r in csv.DictReader(open("master_wordlist.csv", encoding="utf-8"))}
keys = [k for s in plan["strata"].values() for k in s]
rng = random.Random(19811011); order = keys[:]; rng.shuffle(order)
os.makedirs(f"{D}/web/img", exist_ok=True); pub, key = [], {}
for n, card in enumerate(order, 1):
    r = rows[card[:3]]
    vs = [(j["vid"], f"{D}/img/{j['vid']}.png") for j in plan["images"] if j["card"] == card]; rng.shuffle(vs); cells = []
    for v, p in vs:
        cid = secrets.token_hex(4)
        Image.open(p).convert("RGB").resize((1200, 800), Image.LANCZOS).save(f"{D}/web/img/{cid}.jpg", quality=80)
        cells.append(cid); key[cid] = {"round": n, "card": card, "variant": v}
    pub.append({"round": n, "label": f"{r['lithuanian_TARGET'].split('/')[0]} · {r['english']}", "cells": cells})
json.dump(pub, open(f"{D}/web/rounds.json", "w"), indent=1, ensure_ascii=False); json.dump(key, open(f"{D}/web_key.json", "w"), indent=1)
fn = next((getattr(pt2, n) for n in dir(pt2) if n.startswith("paper") and callable(getattr(pt2, n))), None)
tone = {}
for cid, k in key.items():
    try: tone[k["variant"]] = fn(f"{D}/web/img/{cid}.jpg")
    except Exception as e: tone[k["variant"]] = str(e)
json.dump(tone, open(f"{D}/paper_tone_strict.json", "w"), indent=1, default=str)
t = open("style_lab/2026-10-10_08_F6_roll/web/index.html", encoding="utf-8").read()
import re
t = re.sub(r"const ROUNDS = \[.*?\];", "const ROUNDS = " + json.dumps(pub, ensure_ascii=False, separators=(",", ":")) + ";", t, count=1, flags=re.S)
t = t.replace("<title>F6 Style Check</title>", "<title>F6.1 Spot Check</title>")
t = t.replace("<h1>F6 style check</h1><span class=\"sub\">Blind check of the revised prompt · 14 cards</span>",
              "<h1>F6.1 spot check</h1><span class=\"sub\">Production prompt, two engines · 30 cards</span>")
t = re.sub(r'<p class="how">.*?</p>', '<p class="how">The production prompt on thirty cards it has never drawn: ten scenes, ten single figures, ten objects and animals. Each round shows the same card from two different engines, in random order. Put the better one first, and tick <b>Would ship</b> on every version you\'d put in the deck as it is. Comment on anything that looks wrong: proportions, glitches, gaze, paper, the Lithuanian setting. Click a picture to see it full size. Everything saves as you go.</p>', t, count=1, flags=re.S)
open(f"{D}/web/index.html", "w", encoding="utf-8").write(t)
print(len(key), "cells", len(pub), "rounds")
import statistics as st
for m in "GS":
    L = [v[0] for k, v in tone.items() if k.startswith(m + "_") and isinstance(v, (list, tuple))]
    b = [v[1] for k, v in tone.items() if k.startswith(m + "_") and isinstance(v, (list, tuple))]
    print(m, "L* median", st.median(L), "range", min(L), max(L), "| b* median", st.median(b), "range", min(b), max(b))
