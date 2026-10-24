# -*- coding: utf-8 -*-
"""build_review_f62.py — owner review page for the F6.2 / Sunburst re-render.

One row per card: the shipped 1.5 master (out_deck/) on the left, the new
F6.2 render (out_deck_f62/) on the right, with the word, gloss, the QA verdict
and the cold read. Media are real files in review/media/ (see build_review.py
for why data URIs are not used). Per-card OK / Redo buttons are kept in the
browser's localStorage; "copy Redo list" puts the rejected keys on the clipboard.

    python out_deck_f62/build_review_f62.py
"""
import csv, html, json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NEW, OLD = "out_deck_f62", "out_deck"
OUT = f"{NEW}/review"; MEDIA = f"{OUT}/media"; W = 480
os.makedirs(MEDIA, exist_ok=True)

cards = list(csv.DictReader(open(f"{NEW}/cards.csv", encoding="utf-8")))
qa = {r["key"]: r for r in csv.DictReader(open(f"{NEW}/qa_f62.csv", encoding="utf-8"))}
plan = {j["key"]: j for j in json.load(open(f"{NEW}/plan.json"))["jobs"]}
rerolled = {}
if os.path.isdir(f"{NEW}/_rerolled"):
    for f in os.listdir(f"{NEW}/_rerolled"):
        k = f.split(".r")[0]; rerolled[k] = rerolled.get(k, 0) + 1
try:
    paper = json.load(open(f"{NEW}/paper_tone_strict.json"))
except Exception:
    paper = {}

def thumb(src, dst):
    if not os.path.exists(src):
        return None
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB")
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=74, optimize=True)
    return "media/" + os.path.basename(dst)

rows, n_old, counts = [], 0, {"PASS": 0, "WARN": 0, "FAIL": 0}
for c in cards:
    k = c["key"]
    new = thumb(f"{NEW}/{k}.png", f"{MEDIA}/{k}_new.jpg")
    old = thumb(f"{OLD}/{k}.png", f"{MEDIA}/{k}_old.jpg")
    n_old += bool(old)
    q = qa.get(k, {}); st = q.get("status", "")
    counts[st] = counts.get(st, 0) + 1
    note = q.get("fails") or q.get("warnings") or ""
    p = plan.get(k, {})
    tags = []
    if rerolled.get(k): tags.append(f"re-rolled ×{rerolled[k]}")
    if p.get("exact_text"): tags.append("lettering declared")
    if p.get("setting"): tags.append("LT setting")
    if p.get("composition") == "scene": tags.append("full scene")
    rows.append(dict(k=k, lt=c["lithuanian"], en=c["english"], cat=c["category"], new=new, old=old,
                     st=st, note=note, guess=q.get("guess", ""), lettering=q.get("lettering", ""),
                     tags=tags, n=int(c["number"])))

def card_html(r):
    badge = f'<span class="qa {r["st"].lower()}">{r["st"]}</span>' if r["st"] else ""
    tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in r["tags"])
    note = f'<p class="note">{html.escape(r["note"])}</p>' if r["note"] else ""
    guess = f'<p class="guess">read cold as: <i>{html.escape(r["guess"])}</i></p>' if r["guess"] else ""
    lett = f'<p class="guess">lettering read: <code>{html.escape(r["lettering"])}</code></p>' if r["lettering"] else ""
    old = f'<figure><img loading="lazy" src="{r["old"]}" alt=""><figcaption>1.5 master (shipped)</figcaption></figure>' if r["old"] else '<figure><div class="none">no 1.5 master (new card)</div></figure>'
    new = f'<figure><img loading="lazy" src="{r["new"]}" alt=""><figcaption>F6.2 · Sunburst</figcaption></figure>' if r["new"] else '<figure><div class="none">missing</div></figure>'
    return f'''<section class="card" data-key="{r["k"]}" data-st="{r["st"]}" data-tags="{html.escape(' '.join(r["tags"]))}" data-cat="{html.escape(r["cat"])}">
<header><span class="num">{r["n"]:03d}</span> <b>{html.escape(r["lt"])}</b> <span class="en">{html.escape(r["en"])}</span> <span class="cat">{html.escape(r["cat"])}</span> {badge} {tags}
<span class="verdict"><button class="ok" onclick="mark('{r["k"]}','ok')">OK</button><button class="redo" onclick="mark('{r["k"]}','redo')">Redo</button></span></header>
<div class="pair">{old}{new}</div>
{guess}{lett}{note}
<textarea placeholder="note for this card (kept in your browser)" oninput="noteFor('{r["k"]}',this.value)"></textarea>
</section>'''

body = "\n".join(card_html(r) for r in rows)
doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>F6.2 re-render — review</title><style>
:root{{--paper:#e7ddc6;--paper2:#efe7d4;--red:#8c2a1b;--ink:#2c2620;--teal:#3c5e5a;--dun:#8a7d61}}
*{{box-sizing:border-box}}body{{font-family:Georgia,"Times New Roman",serif;color:var(--ink);background:var(--paper);margin:0}}
.top{{position:sticky;top:0;z-index:5;background:var(--red);color:var(--paper);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
.top b{{font-variant:small-caps;letter-spacing:.12em;font-size:1.05rem}}
.top button,.top select{{font:inherit;font-size:.85rem;padding:3px 8px;border:1px solid var(--paper);background:transparent;color:var(--paper);cursor:pointer}}
.top button.on{{background:var(--paper);color:var(--red)}}
.lead{{max-width:1100px;margin:14px auto;padding:0 16px;line-height:1.5}}
.card{{max-width:1100px;margin:0 auto 22px;background:var(--paper2);border:2px solid var(--red);padding:10px 12px 12px}}
.card.hide{{display:none}}
header{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}}
header b{{font-size:1.4rem}} .num{{color:var(--dun);font-size:.9rem}} .en{{color:#4a4238}} .cat{{font-size:.7rem;color:var(--dun);font-variant:small-caps;letter-spacing:.08em}}
.qa,.tag{{font-size:.68rem;font-variant:small-caps;letter-spacing:.08em;padding:1px 6px;border-radius:2px}}
.qa{{color:#fff}}.qa.pass{{background:#3f7d4f}}.qa.warn{{background:#b7791f}}.qa.fail{{background:#97301f}}
.tag{{border:1px solid var(--teal);color:var(--teal)}}
.verdict{{margin-left:auto;display:flex;gap:4px}}
.verdict button{{font:inherit;font-size:.8rem;padding:3px 10px;border:1px solid var(--ink);background:transparent;cursor:pointer}}
.card.v-ok .verdict .ok{{background:#3f7d4f;color:#fff;border-color:#3f7d4f}}
.card.v-redo .verdict .redo{{background:#97301f;color:#fff;border-color:#97301f}}
.card.v-redo{{border-color:#97301f;box-shadow:0 0 0 3px #97301f44}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
@media(max-width:700px){{.pair{{grid-template-columns:1fr}}}}
figure{{margin:0}} figure img{{width:100%;display:block;border:1px solid #b9a98a}}
figcaption{{font-size:.72rem;color:var(--dun);font-variant:small-caps;letter-spacing:.08em;margin-top:3px}}
.none{{padding:60px 10px;text-align:center;color:var(--dun);font-style:italic;background:#e2d8bf}}
.note{{font-size:.82rem;color:#7a4a3a;margin:8px 0 0;line-height:1.4}} .guess{{font-size:.82rem;color:var(--dun);margin:6px 0 0}}
code{{font-size:.8rem}} textarea{{width:100%;margin-top:8px;font:inherit;font-size:.85rem;background:#f6f0e0;border:1px solid #c9b995;padding:4px 6px;min-height:28px;resize:vertical}}
</style></head><body>
<div class="top"><b>F6.2 re-render — review</b>
<span>show:</span>
<button class="f on" data-f="all">all {len(rows)}</button>
<button class="f" data-f="FAIL">FAIL {counts.get("FAIL",0)}</button>
<button class="f" data-f="WARN">WARN {counts.get("WARN",0)}</button>
<button class="f" data-f="PASS">PASS {counts.get("PASS",0)}</button>
<button class="f" data-f="re-rolled">re-rolled {len(rerolled)}</button>
<button class="f" data-f="lettering">lettering {sum(1 for r in rows if 'lettering declared' in r['tags'])}</button>
<button class="f" data-f="redo">my Redo <span id="nredo">0</span></button>
<select id="cat"><option value="">all categories</option>{''.join(f'<option>{html.escape(c)}</option>' for c in sorted({r["cat"] for r in rows}))}</select>
<button onclick="copyRedo()">copy Redo list</button>
<button onclick="exportAll()">download verdicts.json</button>
</div>
<div class="lead"><p><b>{len(rows)} cards</b> re-rendered on gpt-image-2.5-sunburst with the F6.2 house style; {n_old} have a shipped 1.5 master
to compare against. Left: the master in the current deck. Right: the new render. QA: {counts.get("PASS",0)} pass ·
{counts.get("WARN",0)} warn (a cold-read synonym or a reviewer note, usually harmless) · {counts.get("FAIL",0)} fail. {len(rerolled)} cards were re-rolled
(up to twice) after QA or my own look. <i>Read cold as</i> is what the vision model guessed without being told the word.</p>
<p>Press <b>OK</b> or <b>Redo</b> on each card (kept in this browser), add a note if you like, then <b>copy Redo list</b> and
paste it back to me. Nothing is pushed until you confirm.</p></div>
{body}
<script>
const KEY='f62_review_v1';let V={{}};try{{V=JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{}}
function save(){{try{{localStorage.setItem(KEY,JSON.stringify(V))}}catch(e){{}}document.getElementById('nredo').textContent=Object.values(V).filter(v=>v.v==='redo').length}}
function mark(k,v){{V[k]=Object.assign(V[k]||{{}},{{v:(V[k]&&V[k].v===v)?'':v}});paint();save()}}
function noteFor(k,t){{V[k]=Object.assign(V[k]||{{}},{{note:t}});save()}}
function paint(){{document.querySelectorAll('.card').forEach(c=>{{const k=c.dataset.key,v=V[k]||{{}};c.classList.toggle('v-ok',v.v==='ok');c.classList.toggle('v-redo',v.v==='redo');const ta=c.querySelector('textarea');if(ta&&v.note&&ta.value!==v.note)ta.value=v.note}})}}
let F='all';function filter(){{const cat=document.getElementById('cat').value;document.querySelectorAll('.card').forEach(c=>{{let ok=true;if(F==='redo')ok=(V[c.dataset.key]||{{}}).v==='redo';else if(F==='re-rolled')ok=c.dataset.tags.includes('re-rolled');else if(F==='lettering')ok=c.dataset.tags.includes('lettering');else if(F!=='all')ok=c.dataset.st===F;if(cat&&c.dataset.cat!==cat)ok=false;c.classList.toggle('hide',!ok)}})}}
document.querySelectorAll('.top .f').forEach(b=>b.onclick=()=>{{F=b.dataset.f;document.querySelectorAll('.top .f').forEach(x=>x.classList.toggle('on',x===b));filter()}});
document.getElementById('cat').onchange=filter;
function copyRedo(){{const t=Object.entries(V).filter(([k,v])=>v.v==='redo').map(([k,v])=>k+(v.note?'  # '+v.note:'')).join('\\n');navigator.clipboard.writeText(t||'(nothing marked Redo)').then(()=>alert((t?t.split('\\n').length:0)+' keys copied'))}}
function exportAll(){{const a=document.createElement('a');a.href='data:application/json,'+encodeURIComponent(JSON.stringify(V,null,1));a.download='f62_verdicts.json';a.click()}}
paint();save();
</script></body></html>'''
open(f"{OUT}/index.html", "w", encoding="utf-8").write(doc)
print(f"{OUT}/index.html  {os.path.getsize(f'{OUT}/index.html')/1024:.0f} KB · {len(rows)} cards · {n_old} with masters · media in {MEDIA}")
