#!/usr/bin/env python3
"""Preview cards of a built .apkg as HTML and Playwright screenshots (standard-bands check).

Renders the package's own note types (templates + CSS) and media with a small Mustache
subset ({{F}}, {{text:F}}, {{#F}}/{{^F}}, {{cloze:Text}}, {{Tags}}), so what is shown is
what Anki gets, minus Anki's own chrome. Front and back of every chosen note.

    python3 frame_preview.py PACKAGE.apkg [--keys 1035_karve,0318_laikas,...] [--out build_reports/frame_preview]

Writes <out>/html/ (pages + copies of the media they use; git-ignored) and
<out>/phone_<key>.jpg (390 px wide, front over back) and <out>/desktop_all.jpg (1280 px,
front | back per row). Chromium comes from /opt/pw-browsers (PW_CHROMIUM overrides).

Review switches (preview only; the package and the default build are untouched):

    --back proposed      swap in the proposed back (card_frame.proposed_backs, BACKS_AUDIT.md §2)
    --pic thumb|full     picture on the proposed back: thumbnail (default) or full plate width
    --font KEY           re-set the type in one of FONT_OPTIONS (current, oldstandard, literata,
                         notoserif, brygada); review faces come from fonts/review/ (git-ignored),
                         fetched from github.com/google/fonts at REVIEW_FONT_REV by --fetch-fonts
    --sides front|back   shoot only one side (default both); --fold marks the 844 px screen edge
    --prefix NAME_       prefix for the screenshot files (default "phone_")
    --specimen FILE      also render the Lithuanian stress specimen in every FONT_OPTIONS face
"""
import argparse, html, json, os, re, shutil, sqlite3, tempfile, urllib.request, zipfile
import card_frame

DEFAULT_KEYS = ["A2-0654", "0861_lapkritis", "0033_sriuba", "0094_sakyti", "1035_karve", "0030_kate",
                "0007_batonas", "0609_litas", "0155_saskaita", "0855_kiek_kainuoja_bilietas", "0187_i_sveikata", "0647_iskvieskite_gydytoja", "0318_laikas", "1500_aikstele", "1909_smulkus", "0102_vyras_geria_kava"]
CHROMIUM = os.environ.get("PW_CHROMIUM",
                          "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell")


HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW_FONT_DIR = os.path.join(HERE, "fonts", "review")
REVIEW_FONT_REV = "47d54ca1ebb14fd864695f1d39dc734f39017c33"     # google/fonts main, 2026-10-17
REVIEW_FONT_SRC = {                                                 # local file -> path in google/fonts
    "OldStandard-Italic.ttf": "ofl/oldstandardtt/OldStandard-Italic.ttf",
    "OldStandard-Bold.ttf": "ofl/oldstandardtt/OldStandard-Bold.ttf",
    "Literata[opsz,wght].ttf": "ofl/literata/Literata[opsz,wght].ttf",
    "Literata-Italic[opsz,wght].ttf": "ofl/literata/Literata-Italic[opsz,wght].ttf",
    "NotoSerif[wdth,wght].ttf": "ofl/notoserif/NotoSerif[wdth,wght].ttf",
    "NotoSerif-Italic[wdth,wght].ttf": "ofl/notoserif/NotoSerif-Italic[wdth,wght].ttf",
    "Brygada1918[wght].ttf": "ofl/brygada1918/Brygada1918[wght].ttf",
    "Brygada1918-Italic[wght].ttf": "ofl/brygada1918/Brygada1918-Italic[wght].ttf",
}
# key -> (label, [(file, weight, style)]); "current" = the package's own CSS (PT Serif with
# Old Standard TT as the fallback for the clusters PT Serif lacks). Files starting with "_"
# are the deck's shipped fonts in fonts/, the rest are review faces in fonts/review/.
FONT_OPTIONS = {
    "current": ("Brygada 1918 (the package's own faces since 2026-10-18)", []),
    "oldstandard": ("Old Standard TT only", [("_OldStandardTT-Regular.ttf", "400", "normal"),
                                             ("OldStandard-Italic.ttf", "400", "italic"),
                                             ("OldStandard-Bold.ttf", "700", "normal")]),
    "literata": ("Literata", [("Literata[opsz,wght].ttf", "200 900", "normal"),
                              ("Literata-Italic[opsz,wght].ttf", "200 900", "italic")]),
    "notoserif": ("Noto Serif", [("NotoSerif[wdth,wght].ttf", "100 900", "normal"),
                                 ("NotoSerif-Italic[wdth,wght].ttf", "100 900", "italic")]),
    "brygada": ("Brygada 1918", [("Brygada1918[wght].ttf", "400 700", "normal"),
                                 ("Brygada1918-Italic[wght].ttf", "400 700", "italic")]),
}


def fetch_review_fonts():
    os.makedirs(REVIEW_FONT_DIR, exist_ok=True)
    for name, path in REVIEW_FONT_SRC.items():
        dst = os.path.join(REVIEW_FONT_DIR, name)
        if not os.path.exists(dst):
            url = f"https://raw.githubusercontent.com/google/fonts/{REVIEW_FONT_REV}/{path}"
            print("fetch", url)
            urllib.request.urlretrieve(url.replace("[", "%5B").replace("]", "%5D"), dst)


def font_path(name):
    if not name.startswith("_"):
        return os.path.join(REVIEW_FONT_DIR, name)
    p = os.path.join(HERE, "fonts", name)                       # shipped faces; the old pair moved
    return p if os.path.exists(p) else os.path.join(HERE, "fonts", "_superseded", name)


def font_css(key, hdir):
    """CSS that re-sets every text on the card in one face; copies the font files to hdir."""
    faces = FONT_OPTIONS[key][1]
    if not faces:
        return ""
    fam = f"RF-{key}"
    out = []
    for name, weight, style in faces:
        src = font_path(name)
        if not os.path.exists(src):
            raise SystemExit(f"missing {src}: run with --fetch-fonts")
        shutil.copy(src, os.path.join(hdir, name))
        url = name.replace("[", "%5B").replace("]", "%5D")
        out.append(f'@font-face{{font-family:"{fam}";font-weight:{weight};font-style:{style};src:url("{url}")}}')
    out.append(f':root{{--sf-body:"{fam}",serif;--sf-display:"{fam}",serif}}')
    out.append(f'.card,.word,.pron,.forms,.gloss,.hint,.cloze-text,.plate,.bar{{font-family:"{fam}",serif}}')
    return "\n".join(out) + "\n"


FOLD = ('<div style="position:absolute;left:0;right:0;top:844px;border-top:2px dashed #1d6fb8;z-index:9">'
        '<span style="position:absolute;right:4px;top:2px;font:11px/1.2 monospace;color:#1d6fb8;'
        'background:#fff8;padding:0 3px">844 px · one phone screen</span></div>')

# every stressed form a Lithuanian dictionary prints: grave on short vowels, acute and tilde
# on long ones and on the second element of a diphthong (l m n r), plus the ogonek/dot/macron
# letters carrying a mark (combining sequences: no precomposed form exists)
SPECIMEN = [
    ("letters", "ą č ę ė į š ų ū ž  Ą Č Ę Ė Į Š Ų Ū Ž", 30),
    ("precomposed", "à á ã è é ẽ ì í ĩ ò ó õ ù ú ũ ý ỹ", 34),
    ("combining", " ".join(["\u0117\u0303", "\u0117\u0301", "\u016b\u0303", "\u016b\u0301",
                            "\u0105\u0301", "\u0105\u0303", "\u0119\u0301", "\u0119\u0303",
                            "\u012f\u0301", "\u012f\u0303", "\u0173\u0301", "\u0173\u0303",
                            "l\u0303", "m\u0303", "n\u0303", "r\u0303", "i\u0307\u0300"]), 40),
    ("words", "kortẽlė · praeĩti · praė\u0303jo · jū\u0303s · vil\u0303kas · sriubà · raudónas", 26),
    ("italic", "kortẽlė · praeĩti · praė\u0303jo · jū\u0303s · vil\u0303kas", 26),
    ("bold", "kortẽlė · praeĩti · praė\u0303jo · jū\u0303s", 26),
]


def specimen_html(hdir, css_current):
    blocks = []
    font_rules = [css_current]
    for key, (label, faces) in FONT_OPTIONS.items():
        fam = f"'RF-{key}', serif" if faces else 'var(--sf-body)'
        if faces:
            font_rules.append(font_css(key, hdir).split(":root")[0])
        lines = "".join(
            f'<div class="sp-l" style="font-size:{px}px;font-family:{fam};'
            f'{"font-style:italic;" if lab == "italic" else ""}{"font-weight:700;" if lab == "bold" else ""}">'
            f'<span class="sp-k">{lab}</span>{html.escape(txt)}</div>'
            for lab, txt, px in SPECIMEN)
        blocks.append(f'<div class="sp-b"><div class="sp-h">{html.escape(label)}</div>{lines}</div>')
    css = "\n".join(font_rules) + """
body{background:#ead6b4;color:#2c2620;margin:0;padding:10px 12px}
.sp-b{border-top:3px solid #952f25;padding:6px 0 10px}
.sp-h{font:600 13px/1.3 monospace;color:#952f25;letter-spacing:.04em;text-transform:uppercase}
.sp-l{line-height:1.35;margin:4px 0 2px;word-spacing:.05em}
.sp-k{display:block;font:10px/1.2 monospace;color:#6b5a4a;font-style:normal;font-weight:400}
"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(blocks)}</body></html>'


CLUSTERS = ["\u0117\u0303", "\u016b\u0303", "\u0117\u0301", "\u016b\u0301", "\u0105\u0301",
            "i\u0307\u0300", "\u00ec", "l\u0303"]


def clusters_html(hdir, css_current):
    """The stacked clusters at 64 px, one row per FONT_OPTIONS face: ė̃ must show the dot
    under the tilde, ū̃ the macron under the tilde (needs mark-to-mark positioning)."""
    rules, rows = [css_current], []
    for key, (label, faces) in FONT_OPTIONS.items():
        fam = f"'RF-{key}', serif" if faces else "var(--sf-body)"
        if faces:
            rules.append(font_css(key, hdir).split(":root")[0])
        rows.append(f'<div class="cl-r"><span class="cl-k">{html.escape(label)}</span>'
                    f'<span style="font-family:{fam}">{" ".join(CLUSTERS)}</span></div>')
    css = "\n".join(rules) + """
body{background:#ead6b4;color:#2c2620;margin:0;padding:6px 12px}
.cl-r{font-size:52px;line-height:1.25;border-top:1px solid #952f2555;padding:2px 0 4px;white-space:nowrap}
.cl-k{display:block;font:11px/1.4 monospace;color:#952f25;letter-spacing:.03em}
"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(rows)}</body></html>'


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
    ap.add_argument("--back", choices=["current", "proposed"], default="current")
    ap.add_argument("--pic", choices=["thumb", "full"], default="thumb")
    ap.add_argument("--font", choices=["pkg"] + list(FONT_OPTIONS), default="pkg")
    ap.add_argument("--sides", choices=["both", "front", "back"], default="both")
    ap.add_argument("--fold", action="store_true")
    ap.add_argument("--prefix", default="phone_")
    ap.add_argument("--specimen")
    ap.add_argument("--fetch-fonts", action="store_true")
    a = ap.parse_args()
    if a.fetch_fonts:
        fetch_review_fonts()
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
    if a.back == "proposed":
        pb_back, pb_cloze = card_frame.proposed_backs(a.pic)
        pcss = card_frame.proposed_css()
        for m in models.values():
            m["tmpls"][0]["afmt"] = pb_cloze if m.get("type") == 1 else pb_back
            m["css"] = m["css"] + "\n" + pcss
    extra = font_css(a.font, hdir) if a.font != "pkg" else ""
    if extra:
        for m in models.values():
            m["css"] = m["css"] + "\n" + extra
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
        if a.sides == "front":
            body = f'{lab}<div class="pv-side">{q}</div>'
        elif a.sides == "back":
            body = f'{lab}<div class="pv-side">{b}</div>'
        else:
            body = f'{lab}<div class="pv-side">{q}</div><div class="pv-label">back</div><div class="pv-side">{b}</div>'
        if a.fold:
            body = FOLD + body
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
    if a.specimen:
        sp = os.path.join(hdir, "specimen.html")
        open(sp, "w", encoding="utf-8").write(specimen_html(hdir, css_all))
        cl = os.path.join(hdir, "clusters.html")
        open(cl, "w", encoding="utf-8").write(clusters_html(hdir, css_all))
    if a.no_shots:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--allow-file-access-from-files"])
        ph = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2).new_page()
        for k, p in pages:
            ph.goto("file://" + os.path.abspath(p)); ph.wait_for_timeout(400)
            ph.screenshot(path=os.path.join(a.out, f"{a.prefix}{k}.jpg"), full_page=True, type="jpeg", quality=82)
        if a.specimen:
            ph.set_viewport_size({"width": 390, "height": 200})       # no padding to a full screen
            ph.goto("file://" + os.path.abspath(sp)); ph.wait_for_timeout(600)
            ph.screenshot(path=a.specimen, full_page=True, type="jpeg", quality=85)
            ph.goto("file://" + os.path.abspath(cl)); ph.wait_for_timeout(600)
            ph.screenshot(path=re.sub(r"(\.\w+)$", r"_clusters\1", a.specimen), full_page=True, type="jpeg", quality=88)
        if a.prefix != "phone_" or a.back != "current" or a.font != "pkg":
            br.close(); print("screenshots ->", a.out); return     # review runs: phone shots only
        dk = br.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1).new_page()
        dk.goto("file://" + os.path.abspath(allp)); dk.wait_for_timeout(600)
        dk.screenshot(path=os.path.join(a.out, "desktop_all.jpg"), full_page=True, type="jpeg", quality=82)
        br.close()
    print("screenshots ->", a.out)


if __name__ == "__main__":
    main()
