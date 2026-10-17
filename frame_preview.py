#!/usr/bin/env python3
"""Preview cards of a built .apkg as HTML and Playwright screenshots (standard-bands check).

Renders the package's own note types (templates + CSS) and media with a small Mustache
subset ({{F}}, {{text:F}}, {{#F}}/{{^F}}, {{cloze:Text}}, {{Tags}}), so what is shown is
what Anki gets, minus Anki's own chrome. Front and back of every chosen note.

    python3 frame_preview.py PACKAGE.apkg [--keys 005_karve,A2-0001,...] [--out build_reports/frame_preview]

Writes <out>/html/ (pages + copies of the media they use; git-ignored) and
<out>/phone_<key>.jpg (390 px wide, front over back) and <out>/desktop_all.jpg (1280 px,
front | back per row). Chromium comes from /opt/pw-browsers (PW_CHROMIUM overrides).
"""
import argparse, html, json, os, re, shutil, sqlite3, tempfile, zipfile

DEFAULT_KEYS = ["A2-0654", "A2-0035", "183_sriuba", "375_sakyti", "005_karve", "002_kate",
                "531_batonas", "A2-1772", "A2-0270", "A2-0928", "A2-0888", "A2-0907", "A2-0001", "A2-1486", "A2-1741", "S-0001"]
CHROMIUM = os.environ.get("PW_CHROMIUM",
                          "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell")


def strip_html(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def render(tpl, f, tags, answer):
    def cloze(_m):
        t = f.get("Text", "")
        if answer:
            return re.sub(r"\{\{c\d+::(.*?)(::.*?)?\}\}", r'<span class="cloze">\1</span>', t)
        return re.sub(r"\{\{c\d+::(.*?)(::.*?)?\}\}", '<span class="cloze">[...]</span>', t)
    out = re.sub(r"\{\{cloze:Text\}\}", cloze, tpl)
    for _ in range(3):
        out = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}",
                     lambda m: m.group(2) if f.get(m.group(1), "").strip() else "", out, flags=re.S)
        out = re.sub(r"\{\{\^(\w+)\}\}(.*?)\{\{/\1\}\}",
                     lambda m: "" if f.get(m.group(1), "").strip() else m.group(2), out, flags=re.S)
    out = out.replace("{{Tags}}", " ".join(tags))
    out = re.sub(r"\{\{text:(\w+)\}\}", lambda m: html.escape(strip_html(f.get(m.group(1), ""))), out)
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: f.get(m.group(1), ""), out)
    # Anki turns [sound:x] into a play button
    return re.sub(r"\[sound:[^\]]+\]", '<span class="pv-play">&#9654;</span>', out)


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>{css}
html, body {{ margin: 0; }}
body.pv {{ padding: 8px 0; }}
.pv-side {{ padding: 6px 8px 14px; }}
.pv-label {{ font: 11px/1.2 monospace; color: #6b5a4a; padding: 0 8px; }}
.pv-play {{ display: inline-block; width: 24px; height: 24px; border-radius: 50%; border: 1px solid #8a7d61;
           font-size: 11px; line-height: 24px; text-align: center; vertical-align: middle; margin: 0 .3em; }}
.pv-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 18px; padding: 0 12px; }}
</style></head><body class="card pv">{body}</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apkg")
    ap.add_argument("--keys", default=",".join(DEFAULT_KEYS))
    ap.add_argument("--out", default="build_reports/frame_preview")
    ap.add_argument("--no-shots", action="store_true")
    a = ap.parse_args()
    keys = [k for k in a.keys.split(",") if k]
    hdir = os.path.join(a.out, "html"); os.makedirs(hdir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(a.apkg) as z:
        z.extractall(tmp)
    media = json.load(open(os.path.join(tmp, "media")))           # "0" -> "name.jpg"
    for num, name in media.items():
        if name.startswith("_") or any(name.startswith(k + "_sf") or name.startswith(k + ".") for k in keys):
            shutil.copy(os.path.join(tmp, num), os.path.join(hdir, name))
    con = sqlite3.connect(os.path.join(tmp, "collection.anki2"))
    models = json.loads(con.execute("select models from col").fetchone()[0])
    notes = {}
    for mid, flds, tags in con.execute("select mid, flds, tags from notes"):
        m = models[str(mid)]
        f = dict(zip([x["name"] for x in m["flds"]], flds.split("\x1f")))
        k = f.get("key") or f.get("Key")
        notes[k] = (m, f, tags.split())
    css = None; rows = []; pages = []
    for k in keys:
        if k not in notes:
            print("not in package:", k); continue
        m, f, tags = notes[k]
        css = css or m["css"]
        t = m["tmpls"][0]
        q = render(t["qfmt"], f, tags, False)
        b = render(t["afmt"], f, tags, True)
        lab = f'<div class="pv-label">{k} · {m["name"]} · {" ".join(tags)}</div>'
        rows.append((lab, q, b, m["css"]))
        body = f'{lab}<div class="pv-side">{q}</div><div class="pv-label">back</div><div class="pv-side">{b}</div>'
        p = os.path.join(hdir, f"{k}.html")
        # the scripts in a template run once per side in Anki; here both sides share a page
        open(p, "w", encoding="utf-8").write(PAGE.format(title=k, css=m["css"], body=body))
        pages.append((k, p))
    grid = "".join(f'{lab}<div class="pv-grid"><div class="pv-side">{q}</div><div class="pv-side">{b}</div></div>'
                   for lab, q, b, _ in rows)
    allp = os.path.join(hdir, "all.html")
    # both note types' CSS: the cloze CSS is the picture CSS plus cloze rules
    css_all = max((r[3] for r in rows), key=len)
    open(allp, "w", encoding="utf-8").write(PAGE.format(title="frame preview", css=css_all, body=grid))
    print(f"{len(pages)} cards -> {hdir}")
    if a.no_shots:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--allow-file-access-from-files"])
        ph = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2).new_page()
        for k, p in pages:
            ph.goto("file://" + os.path.abspath(p)); ph.wait_for_timeout(400)
            ph.screenshot(path=os.path.join(a.out, f"phone_{k}.jpg"), full_page=True, type="jpeg", quality=82)
        dk = br.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1).new_page()
        dk.goto("file://" + os.path.abspath(allp)); dk.wait_for_timeout(600)
        dk.screenshot(path=os.path.join(a.out, "desktop_all.jpg"), full_page=True, type="jpeg", quality=82)
        br.close()
    print("screenshots ->", a.out)


if __name__ == "__main__":
    main()
