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
# 2026-10-18 roll-out: a region entry may name its own folder ("dir"), free staging text for
# cards outside a2_staging.json ("staging"; situation cards), and "gaze": "conversation" to use
# the conversation lead. Logs per folder: out_deck_a2 -> ~/a2_work/ledger.csv, gen_log.jsonl;
# out_phrases_v3/round2 -> ~/a2_work/v3_round2_ledger.csv, v3_round2_gen_log.jsonl.
# 2026-10-18 hand-scan fixes (build_reports/hand_scan/fix_plan.csv): the A1 folders join the
# map (out_deck_f62 -> f62_ledger.csv, images -> images_ledger.csv); a region file other than
# edit_regions.json can be named with GO_EDIT_REGIONS (a2_build/hand_fixes/edit_regions.json);
# an entry may carry a free "instruction" for the masked area instead of staging insets; and
# the source may be a .webp or .jpg master (images/*.webp): it is read, sent to the endpoint and
# composited as RGB (the PNG round-trip) and written back in its own format, the old file moving
# to <dir>/_rerolled/<key>.r<n>.<ext>. A local ledger missing from ~/a2_work is first seeded from
# <dir>/ledger.csv, so the copy-back at the end never shortens a folder's ledger.
LOGS = {"out_deck_a2": "", "out_phrases_v3/round2": "v3_round2_", "out_phrases_v3": "v3_",
        "out_deck_f62": "f62_", "images": "images_", "out_deck_sent": "sent_"}


def dir_of(key):
    return REG[key].get("dir", OUT)


def src_of(key):
    """(folder, path, extension) of the current picture for key: .png first, then .webp/.jpg."""
    D = dir_of(key)
    for ext in (".png", ".webp", ".jpg"):
        if os.path.exists(f"{D}/{key}{ext}"):
            return D, f"{D}/{key}{ext}", ext
    raise FileNotFoundError(f"{D}/{key}.png|.webp|.jpg")
MODEL = os.environ.get("GO_EDIT_MODEL", g.OPENAI_MODEL)
REG = json.load(open(os.environ.get("GO_EDIT_REGIONS", os.path.join(HERE, "edit_regions.json")), encoding="utf-8"))
STAGING = json.load(open("a2_build/a2_staging.json", encoding="utf-8"))["notes"]
LOCAL = os.path.expanduser("~/a2_work")
PREVIEW = os.environ.get("GO_EDIT_PREVIEW", os.path.join(HERE, "page", "media"))


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
        elif "ring" in r:      # 2026-10-19 round 4: a border band only (seams of a pasted patch)
            x0, y0, x1, y1 = r["ring"]; w = int(r.get("width", 14))
            d.rectangle([x0, y0, x1, y1], fill=255); d.rectangle([x0 + w, y0 + w, x1 - w, y1 - w], fill=0)
            boxes.append({"ring": r["ring"], "width": w})
        else:
            d.polygon([tuple(p) for p in r["poly"]], fill=255); boxes.append(r["poly"])
    return im, keep, boxes


def insets_of(staging):
    m = re.search(r"Insets?:\s*(.*)$", staging)
    items = [s.strip().rstrip(".") for s in m.group(1).split(";")] if m else []
    return [re.sub(r"^\((keep[^)]*)\)\s*", "", s) for s in items]


def prompt_for(key):
    spec = REG[key]; st = STAGING.get(key) or spec.get("staging", ""); ins = insets_of(st)
    lead = g.CONCEPT_LEAD
    if spec.get("gaze") == "conversation":
        lead = g._conversation_lead(g.CONCEPT_LEAD, g.STYLE_SUFFIX)[0]
    parts = [lead,
             "EDIT of an existing card: repaint ONLY the masked area(s) and leave everything outside them "
             "exactly as it is, matching the existing ink outlines, matte gouache fills, halftone, palette and "
             "aged cream paper so the repainted part is indistinguishable in style from the rest of the card."]
    if spec.get("main"):
        parts.append(f"In the main picture, {spec['main']}.")
    if spec.get("instruction"):
        parts.append("Inside the masked area only: " + spec["instruction"].rstrip(".") + ".")
    picked = [ins[i] for i in spec.get("insets", [])]
    if picked:
        lab = ["upper", "middle", "lower"] if len(ins) == 3 else ["upper", "lower"]
        parts.append("The repainted inset box" + ("es show" if len(picked) > 1 else " shows") + ": "
                     + "; ".join(f"({lab[i] if i < len(lab) else i + 1} inset) {ins[i]}" for i in spec["insets"]) + ".")
    if "the same" in st:
        parts.append(g.PANEL_CONTINUITY_RULE)
    # 2026-10-19 round 4: an entry may declare lettering ("exact_text", the card's card_text) for a poster or
    # playbill; the text exception then stands in for the no-text rule, as in a full render
    if spec.get("exact_text"):
        parts += [g._exact_text_rule(spec["exact_text"], spec.get("exclude", "")), g.ANATOMY_PROPS_RULE]
    else:
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
        D, src, ext = src_of(key); T = LOGS.get(D, "")
        im, mask, boxes = make_mask(key, src)
        prompt = prompt_for(key)
        if dry:
            pv = im.copy(); red = Image.new("RGB", im.size, (255, 0, 0))
            pv = Image.composite(Image.blend(pv, red, 0.35), pv, mask); pv.thumbnail((1024, 1024))
            pv.save(f"{PREVIEW}/mask_{key}.jpg", "JPEG", quality=70)
            print(key, boxes, len(prompt), "chars\n ", prompt[len(g.CONCEPT_LEAD):][:600]); continue
        # the mask's colour is ignored (only alpha counts), so a flat RGBA keeps it tiny; the input
        # image goes up as a q92 JPEG (the VM's upload link is slow; a 3 MB PNG timed out)
        # "prefill": "blur" (removals): the masked pixels go up as a heavy blur of the card, so the
        # endpoint no longer sees the shape it is asked to remove (it redraws what it sees otherwise);
        # the composite below still uses the untouched original outside the mask
        send = im
        if REG[key].get("prefill") == "blur":
            send = Image.composite(im.filter(ImageFilter.GaussianBlur(28)), im, mask.filter(ImageFilter.MaxFilter(9)))
        elif str(REG[key].get("prefill", "")).startswith("file:"):   # 2026-10-19 round 4: an earlier version's pixels
            send = Image.composite(Image.open(REG[key]["prefill"][5:]).convert("RGB"), im, mask)
        rgba = Image.new("RGBA", im.size, (0, 0, 0, 255)); rgba.putalpha(Image.eval(mask, lambda v: 0 if v else 255))
        mb = io.BytesIO(); rgba.save(mb, "PNG", optimize=True); mb.name = "mask.png"; mb.seek(0)
        ib = io.BytesIO(); send.save(ib, "JPEG", quality=92); ib.name = "image.jpg"; ib.seek(0)
        t = time.time()
        try:
            r = client.images.edit(model=MODEL, image=ib, mask=mb, prompt=prompt, size="1536x1024", quality="medium",
                                   n=1, background="opaque")
        except Exception as e:
            print("ERR", key, type(e).__name__, str(e)[:300], flush=True)
            open(f"{LOCAL}/edit_log.jsonl", "a").write(json.dumps({"key": key, "error": str(e)[:300], "model": MODEL, "t": time.strftime("%H:%M:%S")}) + "\n")
            continue
        raw = Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json)))
        if raw.size != im.size:
            raw = raw.resize(im.size, Image.LANCZOS)
        # 2026-10-18: on a large mask the endpoint sometimes hands the area back TRANSPARENT (or as a
        # flat empty fill), which convert("RGB") turned into a black or blank box; refuse such a result
        a = np.asarray(raw.convert("RGBA"))[..., 3]; inside = np.asarray(mask) > 0
        rgb = np.asarray(raw.convert("RGB")).astype(int)
        flat = float(rgb[inside].std(axis=0).mean()) if inside.any() else 99
        if (a[inside] < 200).mean() > 0.02 or flat < 6:
            print("ERR", key, f"empty/transparent fill in the mask (alpha<200 {(a[inside] < 200).mean():.2f}, std {flat:.1f})", flush=True)
            open(f"{LOCAL}/edit_log.jsonl", "a").write(json.dumps({"key": key, "error": "empty fill", "model": MODEL, "t": time.strftime("%H:%M:%S")}) + "\n")
            continue
        new = raw.convert("RGB")
        out_mask = np.asarray(mask) == 0
        diff = float(np.abs(np.asarray(new).astype(int) - np.asarray(im).astype(int)).mean(axis=2)[out_mask].mean())
        # 2026-10-18: the endpoint's output drifts a few levels in colour (outside_diff ~5), which shows
        # as a box on flat ground (a shirt, paper); shift the repaint so its mean in a 24 px ring just
        # outside the mask matches the original there, per channel
        ring = np.asarray(mask.filter(ImageFilter.MaxFilter(49))) > 0
        ring &= ~(np.asarray(mask) > 0)
        if ring.sum() > 500:
            o = np.asarray(im).astype(float); nn = np.asarray(new).astype(float)
            shift = o[ring].mean(axis=0) - nn[ring].mean(axis=0)
            new = Image.fromarray(np.clip(nn + shift, 0, 255).astype("uint8"))
        soft = mask.filter(ImageFilter.GaussianBlur(1.5))
        comp = Image.composite(new, im, soft)
        os.makedirs(f"{D}/_rerolled", exist_ok=True)
        n = 1
        while os.path.exists(f"{D}/_rerolled/{key}.r{n}{ext}"):
            n += 1
        os.replace(src, f"{D}/_rerolled/{key}.r{n}{ext}")
        if ext == ".png":
            comp.save(f"{D}/{key}.tmp.png"); os.replace(f"{D}/{key}.tmp.png", src)
        else:   # webp/jpg master: keep the composite as PNG too, write the master back in its format
            comp.save(f"{D}/_rerolled/{key}.edit_comp{n}.png")
            fmt = "WEBP" if ext == ".webp" else "JPEG"
            comp.save(f"{D}/{key}.tmp{ext}", fmt, quality=int(os.environ.get("GO_EDIT_Q", "88")))
            os.replace(f"{D}/{key}.tmp{ext}", src)
        new.save(f"{D}/_rerolled/{key}.edit_raw{n}.png")
        import shutil
        for name in ("ledger.csv", "gen_log.jsonl"):
            if not os.path.exists(f"{LOCAL}/{T}{name}") and os.path.exists(f"{D}/{name}"):
                shutil.copyfile(f"{D}/{name}", f"{LOCAL}/{T}{name}")
        u = r.usage.model_dump() if getattr(r, "usage", None) else None
        with open(f"{LOCAL}/{T}ledger.csv", "a", newline="", encoding="utf-8") as f:
            g._LedgerWriter(csv.writer(f)).writerow([key, "", "", f"openai/{MODEL} edit", "1536x1024", f"{key}{ext}",
                                    f"EDIT mask={json.dumps(boxes)} :: {prompt}"])
        with open(f"{LOCAL}/{T}gen_log.jsonl", "a") as f:
            f.write(json.dumps({"key": key, "model": MODEL, "edit": True, "s": round(time.time() - t), "usage": u,
                                "outside_diff": round(diff, 2), "prev": f"_rerolled/{key}.r{n}{ext}",
                                "t": time.strftime("%H:%M:%S")}) + "\n")
        print("OK", key, round(time.time() - t), "s outside_diff", round(diff, 2), flush=True)
    if not dry:
        import shutil
        for D in sorted({dir_of(k) for k in keys}):
            T = LOGS.get(D, "")
            for name in ("ledger.csv", "gen_log.jsonl"):
                if os.path.exists(f"{LOCAL}/{T}{name}"):
                    shutil.copyfile(f"{LOCAL}/{T}{name}", f"{D}/{name}")


if __name__ == "__main__":
    main()
