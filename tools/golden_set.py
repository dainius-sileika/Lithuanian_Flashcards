#!/usr/bin/env python3
"""Build / refresh the golden reference set (style/golden/) from style/golden/manifest.csv.

For every row of the manifest: find the current render of the key (the build's own resolution
order, then the 1024 px cloud copies), write an ~800 px q85 JPEG to style/golden/<key>.jpg, and
write style/golden/<key>.prompt.txt with the exact prompt of that render from its ledger (the
last row for the key), plus model, size and the spec/style stamp the ledger carries, if any.

  python3 tools/golden_set.py            # fill what is missing, report what cannot be found
  python3 tools/golden_set.py --refresh  # rewrite every JPEG and prompt file
  python3 tools/golden_set.py --status   # list present / missing without writing

Existing files are not overwritten without --refresh. The manifest is the list of record; the
pictures are small copies for comparison, never the masters (docs/DESIGN_SPEC_CURRENT.md §9).
"""
from __future__ import annotations
import argparse, csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD = os.path.join(ROOT, "style", "golden")
MANIFEST = os.path.join(GOLD, "manifest.csv")
WIDTH, QUALITY = 800, 85

# image dirs, first hit wins: the build's order (build_apkg.A1/A2/SENT_IMAGE_DIRS), then the cloud copies
# Ledgers in the build's resolution order (build_apkg.*_IMAGE_DIRS); the picture is taken ONLY from
# the folder of the ledger that holds the key's current row, or from that folder's 1024 px cloud
# mirror (_cloud_media) when the key was never re-rolled after the mirror was made (one ledger row).
# Never images/ (the 1.x masters) nor the bubble-era out_phrases_a2 / _cloud_media/phrases.
LEDGERS = ["out_phrases_v3/round2", "out_phrases_v3", "out_deck_f62", "out_deck_a2", "out_deck_sent"]
MIRROR = {"out_deck_f62": "_cloud_media/f62", "out_deck_a2": "_cloud_media/a2"}


def ledger_row(key):
    """(last ledger row for key, number of rows) from the first ledger, in build order, that has it.
    Ledgers are append-only history and keep the names a card had when it was rendered (spec §12):
    the row matches the current key or any older name of it (tools/keymap.py)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import keymap
    names = {keymap.canonical(key)} | set(keymap.aliases(key)) | {key}
    for d in LEDGERS:
        p = os.path.join(ROOT, d, "ledger.csv")
        if not os.path.exists(p):
            continue
        hit, n = None, 0
        with open(p, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("key") in names:
                    hit, n = dict(r, _ledger=p[len(ROOT) + 1:], _dir=d), n + 1
        if hit:
            return hit, n
    return None, 0


def find_image(key, led, nrows):
    """The render in the ledger's own folder, else its cloud mirror if the key has one ledger row."""
    if not led:
        return None, ""
    dirs = [led["_dir"]]
    if led["_dir"] in MIRROR:
        if nrows == 1:
            dirs.append(MIRROR[led["_dir"]])
        else:
            return _first(key, dirs) or (None, f"{key} was re-rolled ({nrows} ledger rows); the cloud mirror may be "
                                                "stale, so only the local render is accepted")
    return _first(key, dirs) or (None, "")


def _first(key, dirs):
    for d in dirs:
        for ext in ("png", "webp", "jpg"):
            p = os.path.join(ROOT, d, f"{key}.{ext}")
            if os.path.exists(p):
                return p, ""
    return None


def write_prompt(key, row, out):
    lines = [f"key: {key}", f"ledger: {row['_ledger']}", f"backend: {row.get('backend', '')}",
             f"size: {row.get('size', '')}", f"file: {row.get('file', '')}",
             f"spec_version: {row.get('spec_version') or '(pre-3.0.0 render; spec 3.0.0 describes it)'}",
             f"style_hash: {row.get('style_hash') or '(pre-lock render)'}", "", "subject: " + row.get("subject", ""),
             "", "prompt:", row.get("prompt", "")]
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    present = missing = 0
    for r in rows:
        key = r["key"]
        jpg = os.path.join(GOLD, f"{key}.jpg")
        txt = os.path.join(GOLD, f"{key}.prompt.txt")
        led, nrows = ledger_row(key)
        src, why = find_image(key, led, nrows)
        if a.status:
            print(f"{key:14} {'jpg' if os.path.exists(jpg) else '---'} {'prompt' if os.path.exists(txt) else '------'}"
                  f"  src={os.path.relpath(src, ROOT) if src else 'NOT FOUND'}  ledger={led['_ledger'] if led else 'none'}"
                  f" rows={nrows}" + (f"  ({why})" if why else ""))
            continue
        if led and (a.refresh or not os.path.exists(txt)):
            write_prompt(key, led, txt)
        if src and (a.refresh or not os.path.exists(jpg)):
            from PIL import Image
            with Image.open(src) as im0:
                im = im0.convert("RGB")
                if im.width > WIDTH:
                    im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
                im.save(jpg, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            print(f"wrote {os.path.relpath(jpg, ROOT)} from {os.path.relpath(src, ROOT)}")
        if os.path.exists(jpg):
            present += 1
        else:
            missing += 1
            print(f"MISSING picture for {key} ({r['group']}): "
                  + (why or f"no render beside {led['_ledger'] if led else 'any ledger'}")
                  + "; run this script where the renders are")
        if not led:
            print(f"  no ledger row for {key}: prompt to be filled by the executor")
    if not a.status:
        print(f"golden set: {present} pictures present, {missing} missing, {len(rows)} in the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
