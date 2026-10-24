#!/usr/bin/env python3
"""Screenshots for the "Backs and Type" review (three owner decisions), all at 390 px.

    python3 build_reports/backs_type_review/make_review.py PACKAGE.apkg

A  backs, current vs proposed (thumbnail), 6 cards ............ A/A_cur_<key>.jpg, A/A_prop_<key>.jpg
B  proposed back, thumbnail vs full picture, 3 cards .......... B/B_thumb_<key>.jpg, B/B_full_<key>.jpg
C  type set: 3 cards (front over proposed back) in each FONT_OPTIONS face, C/C_<font>_<key>.jpg,
   the band captions close up (C/C_bands_<font>.jpg), the stress specimen (C/C_specimen.jpg)
   and the stacked clusters at 52 px (C/C_specimen_clusters.jpg)

Everything goes through frame_preview.py (the package's own templates and CSS, with the
review switches --back / --pic / --font); the package and the default build are untouched.
The package used for the published review: build_apkg.py with
A1_IMAGE_DIRS=_cloud_media/f62,images A2_IMAGE_DIRS=_cloud_media/a2,_cloud_media/phrases.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
import frame_preview  # noqa: E402

A_KEYS = ["183_sriuba", "069_raudonas", "375_sakyti", "110_mokytojas", "A2-0001", "A2-0899"]
B_KEYS = ["183_sriuba", "375_sakyti", "A2-0899"]
C_KEYS = ["243_kortele", "404_praeiti", "A2-0001"]


def run(apkg, keys, out, *extra):
    subprocess.run([sys.executable, os.path.join(ROOT, "frame_preview.py"), apkg, "--keys", ",".join(keys),
                    "--out", out, *extra], check=True, cwd=ROOT)


def collect(src, dst):
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if f.endswith(".jpg"):
            shutil.copy(os.path.join(src, f), os.path.join(dst, f))


def bands(html_dir, keys, out_jpg):
    """The front's top and bottom band of each card, at 3x, stacked."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    parts = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=frame_preview.CHROMIUM, args=["--allow-file-access-from-files"])
        pg = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3).new_page()
        for k in keys:
            pg.goto("file://" + os.path.join(html_dir, f"{k}.html")); pg.wait_for_timeout(500)
            for sel in (".sf-top", ".sf-bot"):
                p = os.path.join(html_dir, f"_band_{k}{sel}.png")
                pg.locator(sel).first.screenshot(path=p)
                im = Image.open(p).convert("RGB")
                # drop the sub-pixel row of picture the element box catches at its picture edge
                im = im.crop((0, 0, im.width, im.height - 5)) if sel == ".sf-top" else im.crop((0, 5, im.width, im.height))
                parts.append(im)
        br.close()
    gap = 12
    w = max(p.width for p in parts)
    im = Image.new("RGB", (w, sum(p.height for p in parts) + (gap + 4) * (len(parts) // 2)), "#ead6b4")
    y = 0
    for i, p in enumerate(parts):
        im.paste(p, (0, y)); y += p.height + (gap if i % 2 else 4)   # 4 px between a card's two bands
    im.save(out_jpg, quality=90)


def main():
    apkg = os.path.abspath(sys.argv[1])
    frame_preview.fetch_review_fonts()
    tmp = tempfile.mkdtemp()
    run(apkg, A_KEYS, f"{tmp}/a_cur", "--sides", "back", "--fold", "--prefix", "A_cur_")
    run(apkg, A_KEYS, f"{tmp}/a_prop", "--back", "proposed", "--pic", "thumb", "--sides", "back", "--fold",
        "--prefix", "A_prop_")
    run(apkg, B_KEYS, f"{tmp}/b_thumb", "--back", "proposed", "--pic", "thumb", "--sides", "back", "--fold",
        "--prefix", "B_thumb_")
    run(apkg, B_KEYS, f"{tmp}/b_full", "--back", "proposed", "--pic", "full", "--sides", "back", "--fold",
        "--prefix", "B_full_")
    for d in ("a_cur", "a_prop"):
        collect(f"{tmp}/{d}", os.path.join(HERE, "A"))
    for d in ("b_thumb", "b_full"):
        collect(f"{tmp}/{d}", os.path.join(HERE, "B"))
    os.makedirs(os.path.join(HERE, "C"), exist_ok=True)
    for f in frame_preview.FONT_OPTIONS:
        extra = ["--specimen", os.path.join(HERE, "C", "C_specimen.jpg")] if f == "current" else []
        run(apkg, C_KEYS, f"{tmp}/c_{f}", "--back", "proposed", "--pic", "thumb", "--font", f,
            "--prefix", f"C_{f}_", *extra)
        collect(f"{tmp}/c_{f}", os.path.join(HERE, "C"))
        bands(f"{tmp}/c_{f}/html", C_KEYS, os.path.join(HERE, "C", f"C_bands_{f}.jpg"))
    print("review screenshots ->", HERE)


if __name__ == "__main__":
    main()
