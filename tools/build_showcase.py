"""Showcase PDF: a selection of cards, front and back, rendered from a released package exactly as Anki shows them.

Usage (needs `pip install anki playwright pillow numpy`; Chromium at /opt/pw-browsers/chromium, else Playwright's own):
    python3 tools/build_showcase.py Lietuviu_Flashcards_v3.0_A1.apkg docs/showcase/Lietuviu_Flashcards_showcase_A1.pdf

Steps: import the package into a scratch Anki collection; render each selected card's question and answer with
the note type's CSS (sound tags stripped); screenshot at 430 px phone width (3x); crop to the card; JPEG; lay out
A4 landscape pages (cover, contents grid, one page per section, one page per card); print to PDF with Chromium.
The selection and captions are the `sections` table below (2026-10-24: 24 A1 cards, from the golden set plus one
card of each kind and the history cards). Cover counts are written in the cover text: update them per release.
"""
import os, re, sys, glob, html, asyncio, tempfile, shutil
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest

CHROMIUM = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None

sections=[
 ("Words","Every word card is a plate from the manual: one subject drawn large, with small insets that show it in use.",[
  ("0027_suo","Picture card · noun","Animal vignette on bare paper. The insets show the head, the paw, and the dog at work. The back gives stress, gender and the genitive."),
  ("0452_kiausinis","Picture card · noun","Food: whole, cracked, cooked, eaten."),
  ("0556_kepure","Picture card · noun","Clothing, shown worn and close up."),
  ("1096_variklis","Picture card · noun","A machine drawn whole; the insets put it to work."),
  ("0400_motina","Picture card · people","A mother and child, with scenes of everyday care."),
  ("0523_senele","Picture card · people","Grandmother under a cotton headscarf."),
  ("0045_mokytojas","Picture card · professions","The teacher at the blackboard."),
  ("0407_policininkas","Picture card · professions","A traffic officer at a crossing, with the tools of the job."),
  ("0850_vestuves","Picture card · society","A wedding, in Sunday best."),
 ]),
 ("Places","Places are full scenes, filled edge to edge, with insets below.",[
  ("0022_miestas","Picture card · places","A city: trolleybus, crowd, tiled roofs."),
  ("0175_gatve","Picture card · places","A street with a zebra crossing and period cars."),
  ("1074_ukis","Picture card · places","A farm at work."),
 ]),
 ("Actions and qualities","Verbs move left to right; qualities are drawn by contrast. The backs give the forms a learner needs.",[
  ("0011_eiti","Picture card · verb","Motion in three phases with a single arrow. The back gives the infinitive, present and past."),
  ("0178_aukstas","Picture card · adjective","Tall, by contrast with short. The back gives the masculine and the feminine."),
  ("0617_raudonas","Picture card · colour","The colour carried by plain objects."),
  ("0079_trys","Picture card · number","The numeral in period print, and three of everything."),
 ]),
 ("Phrases and situations","Phrases are taught as situations, without speech bubbles: the people look at each other, and the panels tell a small story.",[
  ("0223_galvoti","Situation card","Thinking, drawn without symbols."),
  ("0247_man_reikia_pagalbos","Phrase card · two panels","Asking for help, and getting it."),
  ("0092_labai_aciu","Phrase card","A patient, his thanks, his discharge. The back carries a note on when to use the phrase."),
 ]),
 ("Sentences","Sentence cards and cloze cards put the words to work in short, natural sentences.",[
  ("0747_mama_gamina_vakariene","Sentence card","The picture carries the sentence; the learner supplies the missing verb. The back gives the whole sentence and its grammar point."),
  ("0128_tureti","Cloze card","Function words and verb forms, practised in a sentence, with the English as a hint."),
 ]),
 ("History","A few cards show real people and places from interwar Lithuania.",[
  ("0335_lektuvas","Picture card · history","The Lituanica, 1933, with Darius and Girėnas."),
  ("0245_gydytojas","Picture card · history","Jonas Basanavičius as the doctor."),
  ("1044_menininkas","Picture card · history","M. K. Čiurlionis as the artist, painting after his own <i>Fairy Tale of the Kings</i>."),
 ]),
]


def render_cards(col, keys, outdir):
    idx = {}
    for nid in col.find_notes(""):
        n = col.get_note(nid)
        idx[n["key"] if "key" in n else n["Key"]] = nid
    media = col.media.dir()
    files = []
    for k in keys:
        c = col.get_note(idx[k]).cards()[0]
        css = c.note_type()["css"]
        for side, body in (("front", c.question()), ("back", c.answer())):
            body = re.sub(r"\[(sound|anki:play):[^\]]+\]", "", body)
            doc = (f'<!doctype html><html><head><meta charset="utf-8"><base href="file://{media}/">'
                   f'<meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style></head>'
                   f'<body class="card"><div class="card">{body}</div></body></html>')
            p = os.path.join(outdir, f"{k}_{side}.html"); open(p, "w").write(doc); files.append(p)
    return files

async def shoot(files, outdir):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROMIUM)
        pg = await b.new_page(viewport={"width": 430, "height": 900}, device_scale_factor=3)
        for f in files:
            await pg.goto("file://" + f); await pg.wait_for_timeout(400)
            png = f[:-5] + ".png"; await pg.screenshot(path=png, full_page=True)
            im = Image.open(png).convert("RGB"); a = np.asarray(im).astype(int)
            bg = a[-5, 5]; rows = (np.abs(a - bg).sum(axis=2) > 30).any(axis=1)
            im = im.crop((0, 0, im.width, min(im.height, np.where(rows)[0].max() + 7)))
            im.thumbnail((1200, 4000)); im.save(os.path.join(outdir, os.path.basename(f)[:-5] + ".jpg"), quality=85, optimize=True)
        await b.close()

def layout(M, C):
    fonts=f"""@font-face{{font-family:B;src:url(file://{M}/_Brygada1918-Regular.ttf)}}
    @font-face{{font-family:B;font-weight:700;src:url(file://{M}/_Brygada1918-Bold.ttf)}}
    @font-face{{font-family:B;font-style:italic;src:url(file://{M}/_Brygada1918-Italic.ttf)}}"""
    css=fonts+"""
    @page{size:A4 landscape;margin:0}
    *{box-sizing:border-box} body{margin:0;font-family:B,serif;color:#2b2420;background:#ead6b4}
    .page{width:297mm;height:210mm;page-break-after:always;position:relative;overflow:hidden;background:#ead6b4}
    .band{background:#8f2f25;color:#f3ead6;letter-spacing:.18em;text-transform:uppercase;font-size:9pt;padding:4mm 14mm;display:flex;justify-content:space-between}
    .inner{padding:7mm 14mm 0}
    h2{font-size:15pt;margin:0 0 1mm;color:#8f2f25} .kind{font-size:9pt;letter-spacing:.14em;text-transform:uppercase;color:#6b5a4a}
    .cap{font-size:11pt;margin:1.5mm 0 5mm;max-width:250mm}
    .pair{display:flex;gap:9mm;align-items:flex-start;justify-content:center;margin-top:6mm}
    .pair figure{margin:0;width:131mm} .pair img{width:100%;display:block;box-shadow:0 1.2mm 3mm rgba(60,40,20,.25)}
    figcaption{font-size:8pt;letter-spacing:.16em;text-transform:uppercase;color:#6b5a4a;margin-bottom:1.5mm}
    .foot{position:absolute;bottom:5mm;left:14mm;right:14mm;font-size:8pt;color:#6b5a4a;display:flex;justify-content:space-between}
    .cover{display:grid;grid-template-columns:1.05fr 1fr;gap:12mm;padding:16mm 16mm 0;align-items:center;height:186mm}
    .cover h1{font-size:40pt;line-height:1;margin:0 0 3mm;color:#8f2f25}
    .cover .sub{font-size:14pt;font-style:italic;margin:0 0 8mm}
    .cover p{font-size:11pt;line-height:1.5;margin:0 0 3mm}
    .cover img{width:100%;box-shadow:0 1.5mm 4mm rgba(60,40,20,.3)}
    .sec{display:flex;flex-direction:column;justify-content:center;height:186mm;padding:0 30mm}
    .sec .num{font-size:11pt;letter-spacing:.2em;text-transform:uppercase;color:#6b5a4a}
    .sec h1{font-size:34pt;color:#8f2f25;margin:2mm 0 4mm} .sec p{font-size:13pt;max-width:180mm;line-height:1.5}
    .grid{display:grid;grid-template-columns:repeat(6,1fr);gap:3mm;padding:6mm 14mm} .grid img{width:100%;display:block}
    """
    roman=['I','II','III','IV','V','VI']
    P=[]
    P.append(f"""<div class="page"><div class="band"><span>Lietuvių Flashcards</span><span>A1 · v3.0</span></div><div class="cover">
    <div><h1>Lietuvių<br>Flashcards</h1><p class="sub">Lithuanian from zero, drawn as a civil-defence manual of a free Lithuania, 1981</p>
    <p>An Anki deck for learners of Lithuanian, from the first word to A2. Every card is a plate in a training manual that never existed: brush-ink outlines, matte gouache, cream paper, a red band with the chapter in Lithuanian and the plate number.</p>
    <p>The A1 subdeck has 1,191 cards: 687 pictures, 135 phrases, 334 cloze sentences and 35 sentence cards, in the order of usefulness. Stress marks are sourced, never guessed. 547 cards already carry recordings by a native speaker.</p>
    <p>The following pages show a selection, front and back.</p></div>
    <div><img src="file://{C}/0022_miestas_front.jpg"></div></div>
    <div class="foot"><span>CC BY-NC 4.0</span><span>github.com/dainius-sileika/Lithuanian_Flashcards</span></div></div>""")
    allk=[k for _,_,cs in sections for k,_,_ in cs]
    P.append('<div class="page"><div class="band"><span>Turinys · contents</span><span>'+str(len(allk))+' cards</span></div><div class="grid">'+''.join(f'<img src="file://{C}/{k}_front.jpg">' for k in allk)+'</div></div>')
    n=0
    for si,(title,intro,cards) in enumerate(sections):
      P.append(f'<div class="page"><div class="band"><span>{roman[si]} skyrius</span><span>{html.escape(title)}</span></div><div class="sec"><div class="num">{roman[si]} · {len(cards)} cards</div><h1>{html.escape(title)}</h1><p>{intro}</p></div></div>')
      for k,kind,cap in cards:
        n+=1
        P.append(f"""<div class="page"><div class="band"><span>{roman[si]} · {html.escape(title)}</span><span>{n} / {len(allk)}</span></div><div class="inner">
    <div class="kind">{kind}</div><div class="cap">{cap}</div>
    <div class="pair"><figure><figcaption>Front</figcaption><img src="file://{C}/{k}_front.jpg"></figure><figure><figcaption>Back</figcaption><img src="file://{C}/{k}_back.jpg"></figure></div></div></div>""")
    return '<!doctype html><html><head><meta charset="utf-8"><style>' + css + '</style></head><body>' + ''.join(P) + '</body></html>'

async def to_pdf(html_path, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROMIUM)
        pg = await b.new_page(); await pg.goto("file://" + html_path); await pg.wait_for_timeout(1500)
        await pg.pdf(path=out, width="297mm", height="210mm", print_background=True, prefer_css_page_size=True)
        await b.close()

def main():
    apkg, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    work = tempfile.mkdtemp(prefix="showcase_")
    col = Collection(os.path.join(work, "col.anki2"))
    col.import_anki_package(ImportAnkiPackageRequest(package_path=apkg))
    keys = [k for _, _, cs in sections for k, _, _ in cs]
    cards = os.path.join(work, "cards"); os.makedirs(cards)
    files = render_cards(col, keys, cards)
    media = col.media.dir(); col.close()
    asyncio.run(shoot(files, cards))
    page = os.path.join(work, "showcase.html")
    open(page, "w").write(layout(media, cards))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    asyncio.run(to_pdf(page, out))
    print("wrote", out, "(work folder", work + ")")

if __name__ == "__main__":
    main()
