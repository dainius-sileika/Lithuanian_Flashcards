# -*- coding: utf-8 -*-
"""edit_inset.py — additions round 2 (a2_build/additions_round2/README.md §2): repaint only the
named inset box(es) of an existing A2 picture with the gpt-image edit endpoint, keep the rest.

    python3 a2_build/additions_round2/edit_inset.py --dry A2-1918        # masks + previews only
    timeout 170 python3 a2_build/additions_round2/edit_inset.py A2-1918 A2-1879

Regions: edit_regions.json (inset rects snapped to the drawn frame line, or a polygon). Prompt:
the house lead + an edit instruction + the new inset sentence(s) from a2_staging.json (and, for
A2-1915, the painting clause) + PANEL_CONTINUITY_RULE where the staging says "the same" +
NO_TEXT_RULE + ANATOMY_PROPS_RULE. The model's output is composited back onto the original
through the mask (a 3 px feather), so nothing outside the mask changes; the raw edit's mean
difference outside the mask is logged ("outside_diff", 0-255) for the record. The previous PNG
moves to out_deck_a2/_rerolled/<key>.r<n>.png; the ledger gets a row whose prompt starts "EDIT".
Fallback (README): a full re-roll with the same staging line, out_deck_a2/gen.py REROLL=<key>.
"""
import base64, csv, io, json, os, re, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import go_generator as g
OUT = "out_deck_a2"
MODEL = os.environ.get("GO_EDIT_MODEL", g.OPENAI_MODEL)
REG = json.load(open(os.path.join(HERE, "edit_regions.json"), encoding="utf-8"))
STAGING = json.load(open("a2_build/a2_staging.json", encoding="utf-8"))["notes"]
LOCAL = os.path.expanduser("~/a2_work")
PREVIEW = os.path.join(HERE, "page", "media")


def snap(gray, rect, pad=12):
    """Move each edge of rect to the darkest straight line within +-pad px (the ruled frame)."""
    x0, y0, x1, y1 = rect
    dark = gray < 110
    def best_row(y, xa, xb):
        ys = range(max(0, y - pad), min(gray.shape[0], y + pad + 1))
        return max(ys, key=lambda yy: dark[yy, xa:xb].sum())
    def best_col(x, ya, yb):
        xs = range(max(0, x - pad), min(gray.shape[1], x + pad + 1))
        return max(xs, key=lambda xx: dark[ya:yb, xx].sum())
    mx, my = (x1 - x0) // 6, (y1 - y0) // 6
    return [best_col(x0, y0 + my, y1 - my), best_row(y0, x0 + mx, x1 - mx),
            best_col(x1, y0 + my, y1 - my), best_row(y1, x0 + mx, x1 - mx)]


def make_mask(key, src):
    im = Image.open(src).convert("RGB"); W, H = im.size
    gray = np.asarray(im.convert("L")).astype(int)
    keep = Image.new("L", (W, H), 0)           # 255 = repaint
    d = ImageDraw.Draw(keep); boxes = []
    for r in REG[key]["regions"]:
        if "rect" in r:
            b = snap(gray, r["rect"]); boxes.append(b)
            d.rectangle([b[0] + 6, b[1] + 6, b[2] - 6, b[3] - 6], fill=255)
        else:
            d.polygon([tuple(p) for p in r["poly"]], fill=255); boxes.append(r["poly"])
    return im, keep, boxes


def insets_of(staging):
    m = re.search(r"Insets?:\s*(.*)$", staging)
    items = [s.strip().rstrip(".") for s in m.group(1).split(";")] if m else []
    return [re.sub(r"^\((keep[^)]*)\)\s*", "", s) for s in items]


def prompt_for(key):
    st = STAGING[key]; ins = insets_of(st); spec = REG[key]
    parts = [g.CONCEPT_LEAD,
             "EDIT of an existing card: repaint ONLY the masked area(s) and leave everything outside them "
             "exactly as it is, matching the existing ink outlines, matte gouache fills, halftone, palette and "
             "aged cream paper so the repainted part is indistinguishable in style from the rest of the card."]
    if spec.get("main"):
        parts.append(f"In the main picture, {spec['main']}.")
    picked = [ins[i] for i in spec.get("insets", [])]
    if picked:
        lab = ["upper", "middle", "lower"] if len(ins) == 3 else ["upper", "lower"]
        parts.append("The repainted inset box" + ("es show" if len(picked) > 1 else " shows") + ": "
                     + "; ".join(f"({lab[i] if i < len(lab) else i + 1} inset) {ins[i]}" for i in spec["insets"]) + ".")
    if "the same" in st:
        parts.append(g.PANEL_CONTINUITY_RULE)
    parts += [g.NO_TEXT_RULE, g.ANATOMY_PROPS_RULE]
    return " ".join(parts)


def main():
    dry = "--dry" in sys.argv
    keys = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(PREVIEW, exist_ok=True)
    if not dry:
        from openai import OpenAI
        os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
        client = OpenAI(timeout=170, max_retries=0)
    for key in keys:
        src = f"{OUT}/{key}.png"
        im, mask, boxes = make_mask(key, src)
        prompt = prompt_for(key)
        if dry:
            pv = im.copy(); red = Image.new("RGB", im.size, (255, 0, 0))
            pv = Image.composite(Image.blend(pv, red, 0.35), pv, mask); pv.thumbnail((1024, 1024))
            pv.save(f"{PREVIEW}/mask_{key}.jpg", "JPEG", quality=70)
            print(key, boxes, len(prompt), "chars\n ", prompt[len(g.CONCEPT_LEAD):][:600]); continue
        # the mask's colour is ignored (only alpha counts), so a flat RGBA keeps it tiny; the input
        # image goes up as a q92 JPEG (the VM's upload link is slow; a 3 MB PNG timed out)
        rgba = Image.new("RGBA", im.size, (0, 0, 0, 255)); rgba.putalpha(Image.eval(mask, lambda v: 0 if v else 255))
        mb = io.BytesIO(); rgba.save(mb, "PNG", optimize=True); mb.name = "mask.png"; mb.seek(0)
        ib = io.BytesIO(); im.save(ib, "JPEG", quality=92); ib.name = "image.jpg"; ib.seek(0)
        t = time.time()
        try:
            r = client.images.edit(model=MODEL, image=ib, mask=mb, prompt=prompt, size="1536x1024", quality="medium", n=1)
        except Exception as e:
            print("ERR", key, type(e).__name__, str(e)[:300], flush=True)
            open(f"{LOCAL}/edit_log.jsonl", "a").write(json.dumps({"key": key, "error": str(e)[:300], "model": MODEL, "t": time.strftime("%H:%M:%S")}) + "\n")
            continue
        new = Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json))).convert("RGB")
        if new.size != im.size:
            new = new.resize(im.size, Image.LANCZOS)
        out_mask = np.asarray(mask) == 0
        diff = float(np.abs(np.asarray(new).astype(int) - np.asarray(im).astype(int)).mean(axis=2)[out_mask].mean())
        soft = mask.filter(ImageFilter.GaussianBlur(1.5))
        comp = Image.composite(new, im, soft)
        os.makedirs(f"{OUT}/_rerolled", exist_ok=True)
        n = 1
        while os.path.exists(f"{OUT}/_rerolled/{key}.r{n}.png"):
            n += 1
        os.replace(src, f"{OUT}/_rerolled/{key}.r{n}.png")
        comp.save(f"{OUT}/{key}.tmp.png"); os.replace(f"{OUT}/{key}.tmp.png", src)
        new.save(f"{OUT}/_rerolled/{key}.edit_raw{n}.png")
        u = r.usage.model_dump() if getattr(r, "usage", None) else None
        with open(f"{LOCAL}/ledger.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([key, "", "", f"openai/{MODEL} edit", "1536x1024", f"{key}.png",
                                    f"EDIT mask={json.dumps(boxes)} :: {prompt}"])
        with open(f"{LOCAL}/gen_log.jsonl", "a") as f:
            f.write(json.dumps({"key": key, "model": MODEL, "edit": True, "s": round(time.time() - t), "usage": u,
                                "outside_diff": round(diff, 2), "prev": f"_rerolled/{key}.r{n}.png",
                                "t": time.strftime("%H:%M:%S")}) + "\n")
        print("OK", key, round(time.time() - t), "s outside_diff", round(diff, 2), flush=True)
    if not dry:
        import shutil
        for name in ("ledger.csv", "gen_log.jsonl"):
            shutil.copyfile(f"{LOCAL}/{name}", f"{OUT}/{name}")


if __name__ == "__main__":
    main()
