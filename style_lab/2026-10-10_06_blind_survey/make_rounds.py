"""Build blind survey sheets from survey_design.json. Every image (orig included) goes through the
same resize + JPEG round-trip; grid positions and letters are shuffled per round. Writes
rounds/round_NN.jpg and survey_key.json (the unblinding key: do not open before ranking)."""
import json, os, random, io
from PIL import Image, ImageDraw, ImageFont
D = "style_lab/2026-10-10_06_blind_survey"; L = "style_lab"
SRC = {"orig": "out_deck", "g2_old": f"{L}/2026-10-10_01_gpt-image-2_probe",
       "flare_old": f"{L}/2026-10-10_03_model_comparison/gpt-image-2.5-flare",
       "sun_old": f"{L}/2026-10-10_03_model_comparison/gpt-image-2.5-sunburst",
       "g2_A": f"{L}/2026-10-10_04_levers_A_B/gpt-image-2_A", "g2_B": f"{L}/2026-10-10_04_levers_A_B/gpt-image-2_B",
       "sun_A": f"{L}/2026-10-10_04_levers_A_B/gpt-image-2.5-sunburst_A", "sun_B": f"{L}/2026-10-10_04_levers_A_B/gpt-image-2.5-sunburst_B"}
for cid in ("F1", "F2", "F3"):
    SRC[f"{cid}_g2"] = f"{L}/2026-10-10_05_fable_F1-F3/{cid}_gpt-image-2_medium"
    SRC[f"{cid}_sun"] = f"{L}/2026-10-10_05_fable_F1-F3/{cid}_gpt-image-2.5-sunburst_medium"
SRC["F1_sunlow"] = f"{L}/2026-10-10_05_fable_F1-F3/F1_gpt-image-2.5-sunburst_low"
d = json.load(open(f"{D}/survey_design.json")); newv = {i["vid"] for i in d["new_images"]}
def path(v, card): return f"{D}/new/{v}.png" if v in newv else f"{SRC[v]}/{card}.png"
W, H, G, LB = 720, 480, 14, 54
try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 44); small = ImageFont.truetype("DejaVuSans.ttf", 26)
except OSError: font = small = ImageFont.load_default()
def norm(p):
    im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=82); b.seek(0); return Image.open(b).convert("RGB")
rng = random.Random(19810101); key = {}; os.makedirs(f"{D}/rounds", exist_ok=True)
for r in d["rounds"]:
    vs = list(r["variants"]); rng.shuffle(vs)
    letters = list("ABCDEFGH"[:len(vs)]); rng.shuffle(letters)
    cols = 4; rows = (len(vs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + G) + G, 60 + rows * (H + LB + G) + G), (245, 245, 245))
    dr = ImageDraw.Draw(sheet); dr.text((G, 12), f"Round {r['round']}", fill="black", font=small)
    cells = []
    for i, (v, let) in enumerate(zip(vs, letters)):
        x = G + (i % cols) * (W + G); y = 60 + (i // cols) * (H + LB + G)
        dr.text((x + W // 2 - 14, y), let, fill="black", font=font)
        sheet.paste(norm(path(v, r["card"])), (x, y + LB)); cells.append({"letter": let, "variant": v, "cell": i + 1})
    sheet.save(f"{D}/rounds/round_{r['round']:02d}.jpg", quality=88)
    key[r["round"]] = {"card": r["card"], "repeat_of": r.get("repeat_of"), "cells": cells}
json.dump(key, open(f"{D}/survey_key.json", "w"), indent=1)
print("built", len(key), "rounds")
