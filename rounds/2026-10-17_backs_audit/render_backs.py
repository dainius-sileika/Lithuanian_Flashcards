#!/usr/bin/env python3
"""Render real card BACKS (and a few fronts) with the live templates from build_apkg.py to HTML
and phone-sized screenshots, for the backs audit (Fable, 2026-10-17). Read-only on data.

    python3 a2_build/backs_audit/render_backs.py          # writes html/ and png/ beside this file

Mustache subset implemented: {{f}}, {{#f}}…{{/f}}, {{^f}}…{{/f}}, {{cloze:Text}} (answer side:
the c1 span revealed and marked .cloze; question side: [...]). Night mode = Anki's
`.night_mode` class on <body> and `.card.night_mode`.
"""
import csv, os, re, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import build_apkg as B
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "html"); PNG = os.path.join(HERE, "png")
os.makedirs(HTML, exist_ok=True); os.makedirs(PNG, exist_ok=True)
MEDIA = {"A1": "_cloud_media/f62", "A2": "_cloud_media/a2", "PH": "_cloud_media/phrases"}

def render(tpl, fields, answer=True):
    def cloze(m):
        txt = fields.get("Text", "")
        if answer:
            return re.sub(r"\{\{c\d+::(.*?)\}\}", r'<span class="cloze">\1</span>', txt)
        return re.sub(r"\{\{c\d+::(.*?)\}\}", '<span class="cloze">[...]</span>', txt)
    out = re.sub(r"\{\{cloze:Text\}\}", cloze, tpl)
    for _ in range(3):
        out = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", lambda m: m.group(2) if fields.get(m.group(1), "").strip() else "", out, flags=re.S)
        out = re.sub(r"\{\{\^(\w+)\}\}(.*?)\{\{/\1\}\}", lambda m: "" if fields.get(m.group(1), "").strip() else m.group(2), out, flags=re.S)
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: fields.get(m.group(1), ""), out)
    return out

def page(body, css, night=False, title=""):
    cls = "card night_mode" if night else "card"
    bcls = "night_mode" if night else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><style>{css}
body{{margin:0}} .night_mode body, body.night_mode{{background:#2f2f31}}
audio-placeholder{{display:inline-block}}</style></head><body class="{bcls}"><div class="{cls}">{body}</div></body></html>"""

def img_tag(path):
    if path and os.path.exists(path):
        return f'<img class="art" src="file://{os.path.abspath(path)}">'
    return ""

def sound_badge(f):
    # Anki shows a small play button for [sound:]; we show a placeholder of similar size
    return '<span style="display:inline-block;width:22px;height:22px;border:1px solid #999;border-radius:50%;vertical-align:middle;margin:0 .3em;font-size:11px;line-height:22px;text-align:center">&#9654;</span>' if f else ""

samples = []
a1 = {r["key"]: r for r in csv.DictReader(open("cards_anki.csv", encoding="utf-8"))}
for k in ["001_suo", "202_pusryciai", "400_sprogti", "401_sedeti", "069_raudonas", "446_ilgas", "086_vyras", "510_as", "354_taip", "265_lupa"]:
    r = a1.get(k)
    if not r: continue
    f = dict(key=k, lithuanian=r["lithuanian"], english=r["english"], gender=B.gender_mark(r["gender"]), gen_sg=r["gen_sg"],
             pres3=r["pres3"], past3=r["past3"], fem=r["fem"], number=r["number"], category=r["category"],
             image=img_tag(f"{MEDIA['A1']}/{B.IMAGE_ALIAS.get(k, k)}.jpg"), audio=sound_badge(os.path.exists(f"audio/{k}.mp3")), pron=r.get("pron", ""))
    samples.append(("A1-picture", k, B.BACK, B.CSS, f, True))
a2 = {r["id"]: r for r in csv.DictReader(open(B.A2_LIST, encoding="utf-8"))}
for k in ["A2-0377", "A2-0358", "A2-1445", "A2-0010", "A2-0262", "A2-1200"]:
    r = a2.get(k)
    if not r: continue
    img = B.find_image(k, [MEDIA["A2"], MEDIA["PH"]])
    f = dict(key=k, lithuanian=r["lithuanian_TARGET"], english=r["english"], gender=B.gender_mark(r.get("gender", "")), gen_sg=r.get("gen_sg", ""),
             pres3=r.get("pres3", ""), past3=r.get("past3", ""), fem=r.get("fem", ""), number=k.replace("A2-", ""), category=r.get("category", ""),
             image=img_tag(img), audio="", pron=r.get("lt_pron", ""))
    samples.append(("A2-picture" if r["route"] == "IMG" else "A2-phrase", k, B.BACK, B.CSS, f, True))
for k in ["A2-0001", "A2-0003", "A2-1137", "A2-0006", "A2-0008", "A2-1300"]:
    r = a2.get(k)
    if not r or r["route"] not in ("CLOZE", "PAIR"): continue
    text, n = B.cloze_text(r.get("example_lt", ""))
    f = dict(Text=text, SentenceEN=r.get("example_en", ""), Word=r["lithuanian_TARGET"], Pron=r.get("lt_pron", ""),
             Gender=B.gender_mark(r.get("gender", "")), Forms=B.a2_forms(r), Gloss=r["english"], Number=k.replace("A2-", ""),
             Category=r.get("category", ""), Audio="", Key=k, SentenceAudio="", Image="")
    samples.append(("A2-cloze", k, B.CLOZE_BACK, B.CLOZE_CSS, f, True))
    samples.append(("A2-cloze-FRONT", k, B.CLOZE_FRONT, B.CLOZE_CSS, f, False))
sent = {r["id"]: r for r in csv.DictReader(open(B.SENTENCES, encoding="utf-8"))}
for k in ["S-0001", "S-0014"]:
    r = sent.get(k)
    if not r: continue
    text, n = B.cloze_text(r["lt"])
    f = dict(Text=text, SentenceEN=r["en"], Word="", Pron="", Gender="", Forms="", Gloss=r.get("grammar_point", ""),
             Number=k.replace("S-", "S "), Category="Sakiniai", Audio="", Key=k, SentenceAudio="", Image=img_tag(None))
    samples.append(("sentence", k, B.CLOZE_BACK, B.CLOZE_CSS, f, True))
    samples.append(("sentence-FRONT", k, B.CLOZE_FRONT, B.CLOZE_CSS, f, False))

files = []
for typ, k, tpl, css, f, ans in samples:
    for night in (False, True):
        body = render(tpl, f, answer=ans)
        name = f"{typ}_{k}{'_night' if night else ''}"
        p = os.path.join(HTML, name + ".html")
        open(p, "w", encoding="utf-8").write(page(body, css, night, name))
        files.append((name, p))

from playwright.sync_api import sync_playwright
EXE = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=EXE, args=["--allow-file-access-from-files"])
    ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    pg = ctx.new_page()
    for name, p in files:
        pg.goto("file://" + os.path.abspath(p))
        pg.wait_for_timeout(150)
        pg.screenshot(path=os.path.join(PNG, name + ".png"), full_page=True)
        # viewport-only shot: what the phone shows before scrolling
        pg.screenshot(path=os.path.join(PNG, name + "_fold.png"), full_page=False)
    br.close()
print(len(files), "pages rendered to", HTML, PNG)
