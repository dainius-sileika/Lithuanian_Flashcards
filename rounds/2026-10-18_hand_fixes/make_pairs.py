# -*- coding: utf-8 -*-
"""Before/after media for the Hand Fixes review page: page/media/<key>_before.jpg and _after.jpg
(800 px, q80) and <key>_zoom.jpg (the edited region, before | after). The 'before' is the file named in
before.json (the picture the hand scan judged).
    python3 a2_build/hand_fixes/make_pairs.py KEY ...      (no keys = every key in fix_plan.csv)"""
import csv, json, os, re, sys, glob
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
MEDIA = os.path.join(HERE, "page", "media"); os.makedirs(MEDIA, exist_ok=True)
REG = json.load(open(os.path.join(HERE, "edit_regions.json")))
DIRS = {"A1": ["out_phrases_v3", "out_deck_f62", "images"], "A2": ["out_phrases_v3/round2", "out_phrases_v3", "out_deck_a2"]}


def current(key):
    for d in DIRS["A2" if key.startswith("A2") else "A1"]:
        for e in (".png", ".webp", ".jpg"):
            if os.path.exists(f"{d}/{key}{e}"):
                return d, f"{d}/{key}{e}"


BEFORE = json.load(open(os.path.join(HERE, "before.json")))["before"]


def before(key, d):
    p = BEFORE.get(key)
    return p if p and os.path.exists(p) else None


def bbox(key):
    pts = []
    for r in REG.get(key, {}).get("regions", []):
        pts += [r["rect"][:2], r["rect"][2:]] if "rect" in r else r["poly"]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]; pad = 40
    return max(0, min(xs) - pad), max(0, min(ys) - pad), min(1536, max(xs) + pad), min(1024, max(ys) + pad)


def small(src, dst, w=800):
    im = Image.open(src).convert("RGB"); im.thumbnail((w, w)); im.save(dst, "JPEG", quality=80)


keys = sys.argv[1:] or [r["key"] for r in csv.DictReader(open("build_reports/hand_scan/fix_plan.csv"))]
for k in keys:
    d, cur = current(k); b = before(k, d)
    if not b:
        print("no before", k); continue
    small(b, f"{MEDIA}/{k}_before.jpg"); small(cur, f"{MEDIA}/{k}_after.jpg")
    bb = bbox(k)
    if bb:
        A = Image.open(b).convert("RGB").crop(bb); B = Image.open(cur).convert("RGB").crop(bb)
        s = 450 / max(A.size); A = A.resize((int(A.width * s), int(A.height * s))); B = B.resize(A.size)
        z = Image.new("RGB", (A.width * 2 + 8, A.height), (255, 255, 255)); z.paste(A, (0, 0)); z.paste(B, (A.width + 8, 0))
        z.save(f"{MEDIA}/{k}_zoom.jpg", "JPEG", quality=82)
    print("ok", k, b)
