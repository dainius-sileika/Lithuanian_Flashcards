"""Blind review data for the F6 roll + strict paper tone (Fable's papertone2)."""
import json, os, random, secrets, sys, importlib.util
from PIL import Image
D = "style_lab/2026-10-10_08_F6_roll"
spec = importlib.util.spec_from_file_location("pt2", "style_lab/tools/papertone2.py"); pt2 = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(pt2)
except SystemExit: pass
plan = json.load(open(f"{D}/plan.json"))
LABEL = {"108_minia":"minia · crowd","366_eiti":"eiti · to walk","090_seima":"šeima · family","137_vestuves":"vestuvės · wedding",
 "147_karas":"karas · war","454_letas":"lėtas · slow","049_baznycia":"bažnyčia · church","025_namas":"namas · house",
 "092_senele":"senelė · grandmother","110_mokytojas":"mokytojas · teacher","383_pirkti":"pirkti · to buy","182_duona":"duona · bread",
 "066_paltas":"paltas · coat","113_gydytojas":"gydytojas · doctor"}
ORDER = ["108_minia","025_namas","366_eiti","092_senele","090_seima","182_duona","137_vestuves","110_mokytojas",
         "147_karas","049_baznycia","454_letas","383_pirkti","066_paltas","113_gydytojas"]
os.makedirs(f"{D}/web/img", exist_ok=True); rng = random.Random(19811010); pub, key = [], {}
for n, card in enumerate(ORDER, 1):
    vs = [("orig", f"out_deck/{card}.png")] + [(i["vid"], f"{D}/img/{i['vid']}.png") for i in plan["images"] if i["card"] == card]
    rng.shuffle(vs); cells = []
    for v, p in vs:
        cid = secrets.token_hex(4)
        Image.open(p).convert("RGB").resize((1200, 800), Image.LANCZOS).save(f"{D}/web/img/{cid}.jpg", quality=80)
        cells.append(cid); key[cid] = {"round": n, "card": card, "variant": v}
    pub.append({"round": n, "label": LABEL[card], "cells": cells})
json.dump(pub, open(f"{D}/web/rounds.json","w"), indent=1, ensure_ascii=False); json.dump(key, open(f"{D}/web_key.json","w"), indent=1)
fn = next((getattr(pt2, n) for n in dir(pt2) if n.startswith("paper") and callable(getattr(pt2, n))), None)
tone = {}
if fn:
    for cid, k in key.items():
        try: tone[f"{k['variant']}|{k['card']}"] = fn(f"{D}/web/img/{cid}.jpg")
        except Exception as e: tone[f"{k['variant']}|{k['card']}"] = str(e)
json.dump(tone, open(f"{D}/paper_tone_strict.json","w"), indent=1, default=str)
print(len(key), "cells,", len(pub), "rounds; tone fn:", fn.__name__ if fn else None)
for k in sorted(tone): print(" ", k, tone[k])
