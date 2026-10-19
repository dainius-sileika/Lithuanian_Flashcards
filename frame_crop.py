#!/usr/bin/env python3
"""Find the drawn dark-red frame in a GO picture and crop it off (on a copy).

The pictures carry a drawn frame: a red band at the top, a red band at the bottom
and thin red side borders. Their thickness varies a lot between pictures (bottom
band 4-10 % of the height, top band 3-7 %), so the "standard" card frame trims the
drawn frame off and redraws it in CSS at one fixed width for every card
(build_apkg.py --frame standard; the look is anki/frame_standard.css).

Some pictures (the phrase cards) draw a double frame: a thin outer red line, a
cream gap, then the bands with black ink rules. The detector takes the INNERMOST
red band and any ink rule hugging it, so both kinds crop to the picture itself.

Everything is measured in fractions of the image size, so the same code works on
the 1024 px working copies and on the full-resolution originals.

    from frame_crop import detect_frame, crop_framed
    det = detect_frame(Image.open(src))
    im = crop_framed(Image.open(src), det)        # the source is never written

CLI (report only, writes nothing next to the pictures):
    python3 frame_crop.py _cloud_media/f62 _cloud_media/a2 _cloud_media/phrases
      -> build_reports/frame_bands.csv (every picture) and frame_flags.csv (flagged)
"""
from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass, field, asdict

import numpy as np

# Bump when the detection or the crop rule changes: build_apkg keys its transcode
# cache on it, so every picture is re-cropped after a change here.
FRAME_CROP_VERSION = "2"

PAD_PX = 2                 # safety pad, in source pixels, taken inside the inner edges
BAND_MIN = 0.020           # a top/bottom band thinner than this (fraction of height) is suspect
BAND_MAX = 0.110           # ... thicker than this too
SIDE_MAX = 0.040           # a side border (incl. a phrase card's cream gap + ink rule)
SIDE_RUN_MAX = 0.018       # a row whose red run from the edge is longer is picture, not border
# Fixed-percentage fallback, per edge, used where detection fails or is out of range.
# Set to the thickest drawn bands measured (top 7.6 %, bottom 10.8 %, sides 1.4 %) so a
# fallback never leaves a red sliver; it costs a little picture instead.
FALLBACK = {"top": 0.078, "bottom": 0.110, "left": 0.015, "right": 0.015}
# 2026-10-18 (A1_WRAPUP C3): the ten pictures of build_reports/frame_flags.csv whose side border
# the detector cannot find. Measured on the current files: the picture starts this many source
# pixels (of 1536) in from the edge, after a plain paper margin (or at the edge itself); the
# fixed 1.5 % fallback either left a cream sliver or cut a little picture. Applied by key
# (detect_frame(im, key)); both sides where a paper margin was measured, so the crop is even.
SIDE_OVERRIDES = {
    "1947_bendrabutis": {"left": 10, "right": 15}, "0985_kavine": {"left": 12, "right": 12},
    "2203_vasarnamis": {"left": 15, "right": 15}, "1794_fotografuoti": {"left": 21, "right": 21},
    "0130_mokykla": {"left": 15, "right": 15}, "0265_rasyti": {"left": 21, "right": 27},
    "0500_nesti": {"left": 33, "right": 33}, "2426_lydyti": {"left": 27, "right": 27},
    "0690_vyras_vairuoja_automobili": {"left": 33, "right": 27}, "1579_jie_perka_bilietus": {"left": 45, "right": 42},
}


def override_tag(key):
    """Short marker for build_apkg's transcode stamp, so an override re-crops only its own card."""
    o = SIDE_OVERRIDES.get(key)
    return "" if not o else " ov" + ",".join(f"{k[0]}{v}" for k, v in sorted(o.items()))


@dataclass
class Detection:
    width: int
    height: int
    # inner edges in source pixels: rows [top, bottom) and cols [left, right) are picture
    top: int = 0
    bottom: int = 0
    left: int = 0
    right: int = 0
    fallback: list = field(default_factory=list)   # edges that fell back to FALLBACK
    reasons: list = field(default_factory=list)

    @property
    def flagged(self) -> bool:
        return bool(self.fallback)

    def fractions(self) -> dict:
        return {"top": self.top / self.height, "bottom": (self.height - self.bottom) / self.height,
                "left": self.left / self.width, "right": (self.width - self.right) / self.width}

    def to_json(self) -> dict:
        d = asdict(self)
        for k in ("width", "height", "top", "bottom", "left", "right"):
            d[k] = int(d[k])                       # numpy ints are not JSON-serialisable
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Detection":
        return cls(**d)


def _masks(a):
    """Boolean masks used by the detector, on an int16 RGB array."""
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    # band red: saturated red, any shade from the printed #8f2e24 (median) to the
    # brighter #c4403a of the phrase cards. Wood, skin, brick-brown and fire are mostly
    # rejected by the G < 130 / R-G > 55 pair; a band is also a near-full row of it.
    red = (R > 100) & (R - G > 55) & (R - B > 45) & (G < 130)
    # anti-aliased / JPEG fringe of the red against cream: weaker but clearly reddish;
    # tan picture paper (R-G ~ 35, G ~ 190) must stay out or every edge creeps inward
    fringe = (R - G > 45) & (R - B > 40) & (R > 90) & (G < 170)
    # side border incl. its JPEG fringe; tan/beige picture paper (R-G ~ 30) stays out
    side = (R - G > 45) & (R - B > 45) & (R > 90) & (G < 175)
    dark = np.maximum(np.maximum(R, G), B) < 100      # black / near-black ink
    return red, fringe, side, dark


def _runs(mask1d):
    """[(start, end_exclusive)] of True runs."""
    m = np.concatenate([[False], mask1d, [False]]).astype(np.int8)
    d = np.diff(m)
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def _lead(blk):
    """Per column of a 2-D bool block: length of the leading True run."""
    return np.argmin(np.vstack([blk, np.zeros((1, blk.shape[1]), bool)]), axis=0)


def _follow(red, fringe, e, n, frac_lim):
    """Follow a wavy / anti-aliased inner edge from line e: per across-position the
    leading run of red|fringe, 97th percentile (so no sliver survives in 97 % of the
    positions; the last 3 % are JPEG noise). Positions where the red runs through the
    whole window are picture red touching the band and are left out."""
    lim = max(2, int(round(n * frac_lim)))
    blk = (red | fringe)[e:e + lim]
    if blk.shape[0] == 0:
        return e
    L = _lead(blk)
    ok = L < blk.shape[0]           # positions where red runs the whole window are picture
    if ok.mean() > 0.3:             # red (a sleeve, a flag) touching the band, not band
        L = L[ok]
    return e + int(np.percentile(L, 97))


def _band_from_edge(red, fringe, dark, n, min_thick, ink_rules=False):
    """Inner edge (lines from the image edge) of a top/bottom band. The arrays are 2-D
    [line, across] views oriented so line 0 is the outer edge. Returns None if no band.

    1. the OUTERMOST run of near-full red lines (>= min_thick, starting in the outer
       6 %) is the band -- not the innermost: a red carpet or a brick wall further in
       must not win (2105_seksas);
    2. its inner edge is followed per column (wavy, anti-aliased edges);
    3. a thin second red rule after a small cream gap is part of the frame (double
       rule, 0704_miegamasis), and so is a thin black ink rule after a gap when the
       picture has the phrase-card frame (ink_rules)."""
    zone = int(n * 0.16)
    frac = red[:zone].mean(1)
    gap_lim = max(3, int(round(n * 0.016)))
    # rules separated by a hairline of cream belong together (an outer thin rule, a
    # cream hairline, then the band: 0186_simtas, 0323_begti and most phrase cards)
    merged = []
    for s, e in _runs(frac > 0.6):
        if merged and s - merged[-1][1] <= gap_lim:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    runs = [(s, e) for s, e in merged if e - s >= min_thick and s <= n * 0.06]
    if not runs:
        return None
    s, e = runs[0]
    e = _follow(red, fringe, e, n, 0.008)
    thin = max(2, int(round(n * 0.010)))
    for _ in range(3):                                  # at most a few extra rules
        look = slice(e, min(e + gap_lim, n))
        rf = red[look].mean(1)
        df = dark[look].mean(1) if ink_rules else np.zeros_like(rf)
        hit = np.flatnonzero((rf > 0.6) | (df > 0.6))
        if not len(hit):
            break
        j = e + int(hit[0])
        k = j
        while k < n and k - j <= thin and ((red[k].mean() > 0.4) or (ink_rules and dark[k].mean() > 0.4)):
            k += 1
        if k - j > thin:                                # not a rule: picture starts here
            break
        e = _follow(red, fringe | (dark if ink_rules else False), k, n, 0.004)
    return e


def _side_from_edge(side, fringe, dark, n, ink_rules=False):
    """Inner edge of a side border, lines (columns) oriented from the outer edge.
    Per row: the leading run of side-border pixels (1-px gaps bridged); the border is
    'found' when at least half the rows start with one, and its inner edge is the 97th
    percentile of the run lengths over the rows that look like border (runs longer
    than SIDE_RUN_MAX are picture red touching the border and are ignored).
    Returns (edge, found, share_of_rows_too_long)."""
    zone = int(n * SIDE_RUN_MAX) + 2
    m = side[:zone] | (dark[:zone] if ink_rules else False)    # phrase cards: brown outer rule
    m = m.copy()
    m[1:-1] |= m[:-2] & m[2:]                                   # bridge 1-px gaps
    # the border may start a few px in (a cream hairline at the very edge)
    k0 = max(2, int(round(n * 0.005)))
    first = np.argmax(m[:k0 + 1], axis=0); has = m[:k0 + 1].any(0)
    for i in range(k0 + 1):
        m[i] |= (i < first) & has
    L = _lead(m)                                                # per row (across)
    found = np.median(L) >= 1
    if not found:
        return 0, False, 0.0
    ok = L < zone
    edge = int(np.percentile(L[ok], 97)) if ok.any() else zone
    too_long = float((~ok).mean())
    if ink_rules:
        # phrase cards: outer brown rule, cream gap, then a thin black rule boxing the
        # picture; take it with the frame
        gap_lim = max(3, int(round(n * 0.022)))
        thin = max(2, int(round(n * 0.006)))
        df = dark[edge:edge + gap_lim + thin + 2].mean(1)
        hit = np.flatnonzero(df > 0.85)
        if len(hit) and hit[0] <= gap_lim:
            j = edge + int(hit[0]); k = j
            while k - edge < len(df) and df[k - edge] > 0.5:
                k += 1
            if k - j <= thin:
                edge = k + int(np.percentile(_lead((dark | fringe)[k:k + 2]), 97))
    return edge, True, too_long


def detect_frame(im, key=None) -> Detection:
    """Detect the drawn frame of a PIL image. Never raises on odd pictures: what it
    cannot find falls back to FALLBACK and is listed in .fallback/.reasons."""
    a = np.asarray(im.convert("RGB"), dtype=np.int16)
    H, W = a.shape[:2]
    red, fringe, side, dark = _masks(a)
    det = Detection(width=W, height=H)
    c0, c1 = int(W * 0.08), int(W * 0.92)
    # phrase-card frame: a dark outer rule all round, the bands inside it, a black
    # ink rule boxing the picture. GO pictures have no dark outer rule.
    ink = bool(dark[0:2, c0:c1].mean() > 0.8 and dark[int(H * .2):int(H * .8), 0:2].mean() > 0.8)

    # --- top / bottom bands: lines are rows, measured across the middle 84 % ---
    min_thick = max(3, int(H * 0.010))
    t = _band_from_edge(red[:, c0:c1], fringe[:, c0:c1], dark[:, c0:c1], H, min_thick, ink)
    b = _band_from_edge(red[::-1, c0:c1], fringe[::-1, c0:c1], dark[::-1, c0:c1], H, min_thick, ink)
    for name, v in (("top", t), ("bottom", b)):
        fb = None
        if v is None:
            fb = f"{name}: no band found"
        elif v / H < BAND_MIN:
            fb = f"{name}: band {v / H:.1%} < {BAND_MIN:.0%}"
        elif v / H > BAND_MAX:
            fb = f"{name}: band {v / H:.1%} > {BAND_MAX:.0%}"
        if fb:
            det.fallback.append(name); det.reasons.append(fb)
            v = int(round(H * FALLBACK[name]))
        if name == "top":
            det.top = v
        else:
            det.bottom = H - v

    # --- side borders: lines are columns, measured between the bands ---
    r0 = det.top + int(H * 0.03); r1 = det.bottom - int(H * 0.03)
    if r1 - r0 < H * 0.3:
        r0, r1 = int(H * 0.15), int(H * 0.85)
    for name, sl in (("left", slice(None)), ("right", slice(None, None, -1))):
        v, found, too_long = _side_from_edge(side[r0:r1, sl].T, fringe[r0:r1, sl].T,
                                             dark[r0:r1, sl].T, W, ink)
        fb = None
        if not found:
            fb = f"{name}: no side border found"
        elif too_long > 0.75:
            fb = f"{name}: picture red runs into the border on {too_long:.0%} of rows"
        elif v / W > SIDE_MAX:
            fb = f"{name}: side {v / W:.1%} > {SIDE_MAX:.0%}"
        if fb:
            det.fallback.append(name); det.reasons.append(fb)
            v = int(round(W * FALLBACK[name]))
        if name == "left":
            det.left = v
        else:
            det.right = W - v
    for name, px in SIDE_OVERRIDES.get(key, {}).items():
        v = int(round(px * W / 1536))
        if name == "left":
            det.left = v
        else:
            det.right = W - v
        if name in det.fallback:
            det.fallback.remove(name)
        det.reasons.append(f"{name}: override {px}px (SIDE_OVERRIDES)")
    return det


def crop_box(det: Detection, pad: int = PAD_PX):
    """PIL box (left, upper, right, lower) inside the frame, with the safety pad."""
    return (det.left + pad, det.top + pad, det.right - pad, det.bottom - pad)


def crop_framed(im, det: Detection | None = None, pad: int = PAD_PX):
    """Return a cropped COPY of a PIL image (the input image object is not modified)."""
    det = det or detect_frame(im)
    return im.crop(crop_box(det, pad))


# ---------------------------------------------------------------------------
FLAG_FIELDS = ["image", "width", "height", "fallback_edges", "reasons",
               "top_pct", "bottom_pct", "left_pct", "right_pct"]


def detection_row(name, det: Detection) -> dict:
    f = det.fractions()
    return {"image": name, "width": det.width, "height": det.height,
            "fallback_edges": " ".join(det.fallback), "reasons": "; ".join(det.reasons),
            "top_pct": f"{f['top'] * 100:.2f}", "bottom_pct": f"{f['bottom'] * 100:.2f}",
            "left_pct": f"{f['left'] * 100:.2f}", "right_pct": f"{f['right'] * 100:.2f}"}


def write_reports(rows, report_dir="build_reports"):
    """rows: [(name, Detection)]. Writes frame_flags.csv (flagged only) and
    frame_bands.csv (all). Returns the number flagged."""
    os.makedirs(report_dir, exist_ok=True)
    rows = sorted(rows, key=lambda t: t[0])
    with open(os.path.join(report_dir, "frame_bands.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, FLAG_FIELDS); w.writeheader()
        for n, d in rows:
            w.writerow(detection_row(n, d))
    flagged = [(n, d) for n, d in rows if d.flagged]
    with open(os.path.join(report_dir, "frame_flags.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, FLAG_FIELDS); w.writeheader()
        for n, d in flagged:
            w.writerow(detection_row(n, d))
    return len(flagged)


def main(argv):
    import argparse
    from PIL import Image
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--report", default="build_reports")
    ap.add_argument("--crops", default="", help="also write cropped copies to this folder")
    a = ap.parse_args(argv)
    rows = []
    for d in a.dirs:
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            p = os.path.join(d, fn)
            with Image.open(p) as im:
                det = detect_frame(im)
                if a.crops:
                    os.makedirs(os.path.join(a.crops, os.path.basename(d)), exist_ok=True)
                    crop_framed(im, det).convert("RGB").save(
                        os.path.join(a.crops, os.path.basename(d), os.path.splitext(fn)[0] + ".jpg"), quality=90)
            rows.append((f"{os.path.basename(os.path.normpath(d))}/{os.path.splitext(fn)[0]}", det))
    n = write_reports(rows, a.report)
    print(f"{len(rows)} pictures, {n} flagged -> {a.report}/frame_flags.csv")


if __name__ == "__main__":
    main(sys.argv[1:])
