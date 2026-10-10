"""Blind review data for the F5 confirmation run + paper-tone measurement (Fable's paper_tone method)."""
import json, os, random, secrets
import numpy as np
from PIL import Image
D = "style_lab/2026-10-10_07_confirmation"
plan = json.load(open(f"{D}/plan.json"))
LABEL = {"024_miestas":"miestas · city","036_mokykla":"mokykla · school","050_turgus":"turgus · market","405_pjauti":"pjauti · to saw",
 "366_eiti":"eiti · to walk","376_valgyti":"valgyti · to eat","113_gydytojas":"gydytojas · doctor","090_seima":"šeima · family",
 "108_minia":"minia · crowd","137_vestuves":"vestuvės · wedding","066_paltas":"paltas · coat","211_lova":"lova · bed",
 "001_suo":"šuo · dog","147_karas":"karas · war","454_letas":"lėtas · slow"}
ORDER = ["024_miestas","366_eiti","113_gydytojas","001_suo","137_vestuves","405_pjauti","066_paltas","108_minia",
         "036_mokykla","211_lova","090_seima","147_karas","376_valgyti","050_turgus","454_letas"]
def paper_tone(im):
    w,h=im.size; px=np.asarray(im.crop((int(w*.04),int(h*.12),int(w*.96),int(h*.88)))).reshape(-1,3).astype(float)
    mx=px.max(1); mn=px.min(1); sat=(mx-mn)/np.maximum(mx,1); paper=px[(mx>150)&(sat<0.35)]
    if len(paper)<100: paper=px
    c=paper/255.0; c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    M=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
    xyz=c@M.T; xyz/=np.array([0.95047,1.0,1.08883]); f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
    lab=np.stack([116*f[:,1]-16,500*(f[:,0]-f[:,1]),200*(f[:,1]-f[:,2])],1)
    return round(float(np.median(lab[:,0])),1), round(float(np.median(lab[:,2])),1)
os.makedirs(f"{D}/web/img", exist_ok=True); rng = random.Random(1981); pub, key, tone = [], {}, {}
for n, card in enumerate(ORDER, 1):
    vs = [("orig", f"out_deck/{card}.png")] + [(i["vid"], f"{D}/img/{i['vid']}.png") for i in plan["images"] if i["card"] == card]
    rng.shuffle(vs); cells = []
    for v, p in vs:
        im = Image.open(p).convert("RGB").resize((1200, 800), Image.LANCZOS); cid = secrets.token_hex(4)
        im.save(f"{D}/web/img/{cid}.jpg", quality=80); cells.append(cid)
        key[cid] = {"round": n, "card": card, "variant": v}; tone[v if v != "orig" else f"orig_{card}"] = paper_tone(im)
    pub.append({"round": n, "label": LABEL[card], "cells": cells})
json.dump(pub, open(f"{D}/web/rounds.json","w"), indent=1, ensure_ascii=False); json.dump(key, open(f"{D}/web_key.json","w"), indent=1)
json.dump(tone, open(f"{D}/paper_tone.json","w"), indent=1)
inband = {k:v for k,v in tone.items() if k.startswith("A_")}
ok = [k for k,(L,b) in inband.items() if 80<=L<=87 and 20<=b<=28]
print(len(key),"cells in",len(pub),"rounds; arm A paper in band (L 80-87, b* 20-28):",len(ok),"/",len(inband))
for k,(L,b) in sorted(tone.items()): print(f"  {k:<22} L*={L:5.1f} b*={b:5.1f}")
