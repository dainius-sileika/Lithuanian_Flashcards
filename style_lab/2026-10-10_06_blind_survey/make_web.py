"""Images + round data for the web survey. Every cell gets an opaque random id (the repeat
round gets fresh ids), every image the same 1200x800 JPEG re-encode. Writes web/img/<id>.jpg,
web/rounds.json (public: ids only) and web_key.json (unblinding key: stays local)."""
import json, os, random, secrets, sys
from PIL import Image
sys.path.insert(0, "style_lab/2026-10-10_06_blind_survey")
D = "style_lab/2026-10-10_06_blind_survey"
exec(open(f"{D}/make_rounds.py").read().split("W, H, G, LB")[0])   # reuse SRC, d, path()
CARD_LABEL = {"024_miestas": "miestas · city", "113_gydytojas": "gydytojas · doctor", "366_eiti": "eiti · to walk",
  "001_suo": "šuo · dog", "041_klubas": "klubas · club", "090_seima": "šeima · family", "066_paltas": "paltas · coat",
  "405_pjauti": "pjauti · to saw", "108_minia": "minia · crowd", "036_mokykla": "mokykla · school",
  "211_lova": "lova · bed", "137_vestuves": "vestuvės · wedding"}
os.makedirs(f"{D}/web/img", exist_ok=True)
rng = random.Random(5081981); pub, key = [], {}
for r in d["rounds"]:
    vs = list(r["variants"]); rng.shuffle(vs); cells = []
    for v in vs:
        cid = secrets.token_hex(4)
        Image.open(path(v, r["card"])).convert("RGB").resize((1200, 800), Image.LANCZOS).save(f"{D}/web/img/{cid}.jpg", quality=80)
        cells.append(cid); key[cid] = {"round": r["round"], "variant": v, "card": r["card"]}
    pub.append({"round": r["round"], "label": CARD_LABEL[r["card"]], "cells": cells})
json.dump(pub, open(f"{D}/web/rounds.json", "w"), indent=1)
json.dump(key, open(f"{D}/web_key.json", "w"), indent=1)
print(len(key), "cells"); os.system(f"du -sh {D}/web/img")
