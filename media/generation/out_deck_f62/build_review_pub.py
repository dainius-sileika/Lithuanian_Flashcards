# -*- coding: utf-8 -*-
"""build_review_pub.py — the publishable (claude.ai artifact) version of the F6.2
review page. Artifact limits: <=500 supporting files, <=60 MB per publish, so the
deck is split in two parts (001-260 / 261-531), each with ONE composite JPEG per
card (1.5 master left | F6.2 right, 1200 px wide, q72) in its own media/ folder.

Verdicts go to the artifact database (collection "review", one doc per card:
{key, word, verdict: "ok"|"redo"|"", note, updatedAt}) when the page runs inside
claude.ai (window.claude.use("db")); localStorage is the off-line fallback and
mirror. Publish each part with capabilities {db: {}}.

    python out_deck_f62/build_review_pub.py
    python out_deck_f62/build_review_pub.py --rerolls [--since 2026-10-12]

--rerolls (2026-10-12): one page for the A1 Redo round -> review_pub/rerolls_<since>/.
Cards = the owner's Redo verdicts in review_pub/owner_review_2026-10-11.json plus the
Fable fixes (FABLE_FIXES). Each plate: left the render the owner reviewed (the newest
_rerolled/<key>.r*.png older than --since), right the current render; the owner's note
is shown beside each card; QA from qa_f62_rerolls.csv.
"""
import csv, html, json, os, sys, time
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NEW, OLD = "out_deck_f62", "out_deck"
PUB = f"{NEW}/review_pub"
HALF = 600; Q = 72
PARTS = [("part1", 1, 260), ("part2", 261, 9999)]

cards = list(csv.DictReader(open(f"{NEW}/cards.csv", encoding="utf-8")))
qa = {r["key"]: r for r in csv.DictReader(open(f"{NEW}/qa_f62.csv", encoding="utf-8"))}
plan = {j["key"]: j for j in json.load(open(f"{NEW}/plan.json"))["jobs"]}
rerolled = {}
if os.path.isdir(f"{NEW}/_rerolled"):
    for f in os.listdir(f"{NEW}/_rerolled"):
        k = f.split(".r")[0]; rerolled[k] = rerolled.get(k, 0) + 1

def composite(k, dst):
    new = f"{NEW}/{k}.png"; old = f"{OLD}/{k}.png"
    srcs = [p for p in (old, new) if os.path.exists(p)]
    if not srcs:
        return None
    if os.path.exists(dst) and os.path.getmtime(dst) > max(os.path.getmtime(p) for p in srcs):
        return os.path.basename(dst)
    h = round(HALF * 2 / 3)
    sheet = Image.new("RGB", (HALF * 2 + 6, h), (231, 221, 198))
    for i, p in enumerate((old, new)):
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((HALF, h), Image.LANCZOS)
            sheet.paste(im, (i * (HALF + 6), 0))
    sheet.save(dst, "JPEG", quality=Q, optimize=True, progressive=True)
    return os.path.basename(dst)

def card_html(r):
    badge = f'<span class="qa {r["st"].lower()}">{r["st"]}</span>' if r["st"] else ""
    tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in r["tags"])
    note = f'<p class="note">{html.escape(r["note"])}</p>' if r["note"] else ""
    if r.get("owner"):
        note = f'<p class="owner"><b>Owner\'s note (2026-10-11):</b> {html.escape(r["owner"])}</p>' + note
    cap_l, cap_r = r.get("caps", ("1.5 master (shipped)", "F6.2 · Sunburst"))
    guess = f'<p class="guess">read cold as: <i>{html.escape(r["guess"])}</i></p>' if r["guess"] else ""
    lett = f'<p class="guess">lettering read: <code>{html.escape(r["lettering"])}</code></p>' if r["lettering"] else ""
    img = (f'<a class="plate" href="media/{r["img"]}" onclick="return lb(this)"><img loading="lazy" src="media/{r["img"]}" alt=""></a>'
           if r["img"] else '<div class="none">missing</div>')
    return f'''<section class="card" data-key="{r["k"]}" data-st="{r["st"]}" data-tags="{html.escape(' '.join(r["tags"]))}" data-cat="{html.escape(r["cat"])}">
<header><span class="num">{r["n"]:03d}</span> <b>{html.escape(r["lt"])}</b> <span class="en">{html.escape(r["en"])}</span> <span class="cat">{html.escape(r["cat"])}</span> {badge} {tags}
<span class="verdict"><button class="ok" onclick="mark('{r["k"]}','ok')">OK</button><button class="redo" onclick="mark('{r["k"]}','redo')">Redo</button></span></header>
{img}<div class="caps"><span>{html.escape(cap_l)}</span><span>{html.escape(cap_r)}</span></div>
{guess}{lett}{note}
<textarea placeholder="note for this card" oninput="noteFor('{r["k"]}',this.value)"></textarea>
</section>'''

CSS = '''
:root{--paper:#e7ddc6;--paper2:#efe7d4;--red:#8c2a1b;--ink:#2c2620;--teal:#3c5e5a;--dun:#8a7d61}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#2a2420;--paper2:#352d27;--ink:#e8dfcc;--dun:#b2a58a;--teal:#8fb5b0}}
:root[data-theme="dark"]{--paper:#2a2420;--paper2:#352d27;--ink:#e8dfcc;--dun:#b2a58a;--teal:#8fb5b0}
*{box-sizing:border-box}body{font-family:Georgia,"Times New Roman",serif;color:var(--ink);background:var(--paper);margin:0}
.top{position:sticky;top:0;z-index:5;background:var(--red);color:#efe7d4;padding:8px 16px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.top b{font-variant:small-caps;letter-spacing:.12em;font-size:1.05rem}
.top button,.top select{font:inherit;font-size:.82rem;padding:3px 8px;border:1px solid #efe7d4;background:transparent;color:#efe7d4;cursor:pointer;border-radius:2px}
.top button.on{background:#efe7d4;color:var(--red)}
.counter{margin-left:auto;font-size:.95rem;display:flex;gap:10px;align-items:baseline}
.counter b{font-size:1.5rem;letter-spacing:0}
#status{font-size:.75rem;opacity:.85;width:100%}
.lead{max-width:1240px;margin:14px auto;padding:0 16px;line-height:1.5}
.card{max-width:1240px;margin:0 auto 20px;background:var(--paper2);border:2px solid var(--red);padding:10px 12px 12px}
.card.hide{display:none}
header{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
header b{font-size:1.4rem} .num{color:var(--dun);font-size:.9rem} .en{opacity:.8} .cat{font-size:.7rem;color:var(--dun);font-variant:small-caps;letter-spacing:.08em}
.qa,.tag{font-size:.68rem;font-variant:small-caps;letter-spacing:.08em;padding:1px 6px;border-radius:2px}
.qa{color:#fff}.qa.pass{background:#3f7d4f}.qa.warn{background:#b7791f}.qa.fail{background:#97301f}
.tag{border:1px solid var(--teal);color:var(--teal)}
.verdict{margin-left:auto;display:flex;gap:4px}
.verdict button{font:inherit;font-size:.85rem;padding:4px 12px;border:1px solid var(--ink);background:transparent;color:var(--ink);cursor:pointer;border-radius:2px}
.card.v-ok .verdict .ok{background:#3f7d4f;color:#fff;border-color:#3f7d4f}
.card.v-redo .verdict .redo{background:#97301f;color:#fff;border-color:#97301f}
.card.v-redo{box-shadow:0 0 0 3px #97301f66}
.card.v-ok{border-color:#3f7d4f}
.plate img{width:100%;display:block;border:1px solid #b9a98a}
.caps{display:flex;justify-content:space-between;font-size:.72rem;color:var(--dun);font-variant:small-caps;letter-spacing:.08em;margin-top:3px}
.none{padding:60px 10px;text-align:center;color:var(--dun);font-style:italic}
.owner{font-size:.9rem;margin:8px 0 0;line-height:1.4;border-left:3px solid var(--red);padding-left:8px}
.note{font-size:.82rem;color:#a0604c;margin:8px 0 0;line-height:1.4} .guess{font-size:.82rem;color:var(--dun);margin:6px 0 0}
code{font-size:.8rem} textarea{width:100%;margin-top:8px;font:inherit;font-size:.85rem;background:transparent;color:var(--ink);border:1px solid #c9b995;padding:4px 6px;min-height:28px;resize:vertical}
#lbx{position:fixed;inset:0;background:#000d;display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}
#lbx img{max-width:98vw;max-height:96vh}
@media(max-width:600px){header b{font-size:1.15rem}.counter{margin-left:0}}
'''

JS = r'''
const PART=%(part)r, KEY='f62_review_'+PART; let V={}, db=null, timers={};
try{V=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const $=id=>document.getElementById(id);
function status(t,warn){const s=$('status');s.textContent=t;s.style.color=warn?'#ffd9a0':''}
function local(){try{localStorage.setItem(KEY,JSON.stringify(V))}catch(e){}}
function counts(){let ok=0,redo=0;for(const k in V){if(V[k].verdict==='ok')ok++;else if(V[k].verdict==='redo')redo++}
  $('nok').textContent=ok;$('nredo').textContent=redo;$('nleft').textContent=TOTAL-ok-redo;$('nredo2').textContent=redo}
function paint(){document.querySelectorAll('.card').forEach(c=>{const v=V[c.dataset.key]||{};c.classList.toggle('v-ok',v.verdict==='ok');c.classList.toggle('v-redo',v.verdict==='redo');
  const ta=c.querySelector('textarea');if(ta&&(v.note||'')!==ta.value&&document.activeElement!==ta)ta.value=v.note||''});counts()}
async function push(k){const v=V[k];local();if(!db){status('Saved in this browser only (not connected to the artifact store)',true);return}
  try{await db.doc('review/'+k).set({key:k,word:WORDS[k]||'',verdict:v.verdict||'',note:v.note||'',updatedAt:new Date().toISOString()});status('Saved · '+new Date().toLocaleTimeString())}
  catch(e){status('Could not save to the artifact store ('+(e.code||'error')+'); kept in this browser',true)}}
function mark(k,verdict){V[k]=Object.assign({},V[k]||{},{verdict:(V[k]&&V[k].verdict===verdict)?'':verdict});paint();push(k)}
function noteFor(k,t){V[k]=Object.assign({},V[k]||{},{note:t});local();clearTimeout(timers[k]);timers[k]=setTimeout(()=>push(k),800)}
let F='all';function filter(){const cat=$('cat').value;document.querySelectorAll('.card').forEach(c=>{const v=V[c.dataset.key]||{};let ok=true;
  if(F==='redo')ok=v.verdict==='redo';else if(F==='unmarked')ok=!v.verdict;else if(F==='re-rolled')ok=c.dataset.tags.includes('re-rolled');
  else if(F==='lettering')ok=c.dataset.tags.includes('lettering');else if(F!=='all')ok=c.dataset.st===F;if(cat&&c.dataset.cat!==cat)ok=false;c.classList.toggle('hide',!ok)})}
document.querySelectorAll('.top .f').forEach(b=>b.onclick=()=>{F=b.dataset.f;document.querySelectorAll('.top .f').forEach(x=>x.classList.toggle('on',x===b));filter()});
$('cat').onchange=filter;
function copyRedo(){const t=Object.entries(V).filter(([k,v])=>v.verdict==='redo').map(([k,v])=>k+(v.note?'  # '+v.note:'')).join('\n');
  navigator.clipboard.writeText(t||'(nothing marked Redo)').then(()=>status((t?t.split('\n').length:0)+' Redo keys copied to the clipboard'))}
function lb(a){$('lbimg').src=a.href;$('lbx').style.display='flex';return false}
$('lbx').onclick=()=>{$('lbx').style.display='none'};document.addEventListener('keydown',e=>{if(e.key==='Escape')$('lbx').style.display='none'});
paint();
(async()=>{db=window.claude?.use?await window.claude.use('db'):null;
  if(!db){status('Not connected: verdicts stay in this browser (use "copy Redo list")',true);return}
  try{const snap=await db.collection('review').limit(1000).get();let n=0;
    snap.docs.forEach(d=>{const x=d.data();if(!x||!x.key)return;const mine=V[x.key];
      if(!mine||!mine.updatedAt||(x.updatedAt||'')>=mine.updatedAt){V[x.key]={verdict:x.verdict||'',note:x.note||'',updatedAt:x.updatedAt||''};n++}});
    local();paint();status('Connected · '+n+' saved verdicts loaded · saves automatically')}
  catch(e){status('Could not read the artifact store ('+(e.code||'error')+'); working from this browser',true)}})();
'''

FABLE_FIXES = ["084_tevai", "088_brolis", "097_prezidentas", "387_mokytis", "378_zudyti"]
RENDER_KEY = {"265_lupa": "265_lupos"}   # deck_builder renders 265 under its retargeted headword


def composite2(old, new, dst):
    h = round(HALF * 2 / 3)
    sheet = Image.new("RGB", (HALF * 2 + 6, h), (231, 221, 198))
    for i, p in enumerate((old, new)):
        if p and os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((HALF, h), Image.LANCZOS)
            sheet.paste(im, (i * (HALF + 6), 0))
    sheet.save(dst, "JPEG", quality=Q, optimize=True, progressive=True)
    return os.path.basename(dst)


def build_rerolls(since):
    cutoff = time.mktime(time.strptime(since, "%Y-%m-%d"))
    review = json.load(open(f"{PUB}/owner_review_2026-10-11.json", encoding="utf-8"))
    owner = {v["key"]: v.get("note", "") for v in review if v["verdict"] == "redo"}
    keys = list(owner) + [k for k in FABLE_FIXES if k not in owner]
    qa2 = {r["key"]: r for r in csv.DictReader(open(f"{NEW}/qa_f62_rerolls.csv", encoding="utf-8"))}
    byk = {c["key"]: c for c in cards}
    pdir = f"{PUB}/rerolls_{since}"; media = f"{pdir}/media"; os.makedirs(media, exist_ok=True)
    rows, counts, nobefore = [], {"PASS": 0, "WARN": 0, "FAIL": 0}, []
    for k in sorted(keys):
        rk = RENDER_KEY.get(k, k); c = byk.get(rk, {})
        olds = sorted((os.path.getmtime(f"{NEW}/_rerolled/{f}"), f) for f in os.listdir(f"{NEW}/_rerolled")
                      if f.split(".r")[0] == k)
        before = [f for t, f in olds if t < cutoff]
        today = [f for t, f in olds if t >= cutoff]
        old = f"{NEW}/_rerolled/{before[-1]}" if before else None
        if not old: nobefore.append(k)
        q = qa2.get(rk, {}); st = q.get("status", ""); counts[st] = counts.get(st, 0) + 1
        p = plan.get(rk, {}); tags = [f"re-rolled {since} ×{len(today) + 1}"]
        if p.get("exact_text"): tags.append("lettering declared")
        if p.get("setting"): tags.append("LT setting")
        if k in FABLE_FIXES: tags.append("Fable fix")
        rows.append(dict(k=k, n=int(k.split("_")[0]), lt=c.get("lithuanian", ""), en=c.get("english", ""),
                         cat=c.get("category", ""), st=st, note=q.get("fails") or q.get("warnings") or "",
                         guess=q.get("guess", ""), lettering=q.get("lettering", ""), tags=tags,
                         owner=owner.get(k) or ("Fable fix: staging line changed 2026-10-11 (no owner note)" if k in FABLE_FIXES else ""),
                         caps=("reviewed 2026-10-11 (before)", f"re-roll {since} (now)"),
                         img=composite2(old, f"{NEW}/{rk}.png", f"{media}/{k}.jpg")))
    words = {r["k"]: r["lt"] for r in rows}
    title = f"A1 re-rolls {since}"
    body = "\n".join(card_html(r) for r in rows)
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="Owner review of the {len(rows)} A1 cards re-rolled on {since}: the render reviewed on 2026-10-11 beside the new one, with the owner's note and QA verdict.">
<style>{CSS}</style></head><body>
<div class="top"><b>{html.escape(title)}</b>
<button class="f on" data-f="all">all {len(rows)}</button>
<button class="f" data-f="unmarked">unmarked</button>
<button class="f" data-f="redo">Redo <span id="nredo2">0</span></button>
<button class="f" data-f="FAIL">FAIL {counts.get("FAIL",0)}</button>
<button class="f" data-f="WARN">WARN {counts.get("WARN",0)}</button>
<button class="f" data-f="PASS">PASS {counts.get("PASS",0)}</button>
<button class="f" data-f="lettering">lettering {sum(1 for r in rows if 'lettering declared' in r['tags'])}</button>
<select id="cat"><option value="">all categories</option>{''.join(f'<option>{html.escape(c)}</option>' for c in sorted({r["cat"] for r in rows}))}</select>
<button onclick="copyRedo()">copy Redo list</button>
<span class="counter"><span><b id="nok">0</b> OK</span><span><b id="nredo">0</b> Redo</span><span><b id="nleft">{len(rows)}</b> left</span></span>
<span id="status"></span></div>
<div class="lead"><p>The {len(rows)} A1 cards you marked Redo on 2026-10-11 (plus Fable's five staging fixes), drawn again on {since}.
Each plate: <b>left</b> the render you reviewed, <b>right</b> the new one; your note sits under the title. Click a plate to enlarge.
QA badges are from <code>qa_images.py</code>; <i>read cold as</i> is what the vision model guessed without being told the word.
Press <b>OK</b> or <b>Redo</b> on every card; verdicts save to this page's store as you go.</p></div>
{body}
<div id="lbx"><img id="lbimg" alt=""></div>
<script>const TOTAL={len(rows)};const WORDS={json.dumps(words, ensure_ascii=False)};{JS % {"part": "rerolls_" + since}}</script>
</body></html>'''
    open(f"{pdir}/index.html", "w", encoding="utf-8").write(doc)
    mb = sum(os.path.getsize(f"{media}/{f}") for f in os.listdir(media)) / 1e6
    print(f"{pdir}/index.html  {os.path.getsize(f'{pdir}/index.html')/1024:.0f} KB · {len(rows)} cards · "
          f"media {len(os.listdir(media))} files {mb:.1f} MB · without a 'before' render: "
          f"{nobefore or 'none'}")


if "--rerolls" in sys.argv:
    build_rerolls(sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else "2026-10-12")
    sys.exit()

for part, lo, hi in PARTS:
    pdir = f"{PUB}/{part}"; media = f"{pdir}/media"; os.makedirs(media, exist_ok=True)
    rows, counts = [], {"PASS": 0, "WARN": 0, "FAIL": 0}
    for c in cards:
        n = int(c["number"])
        if not (lo <= n <= hi):
            continue
        k = c["key"]; q = qa.get(k, {}); st = q.get("status", ""); counts[st] = counts.get(st, 0) + 1
        p = plan.get(k, {}); tags = []
        if rerolled.get(k): tags.append(f"re-rolled ×{rerolled[k]}")
        if p.get("exact_text"): tags.append("lettering declared")
        if p.get("setting"): tags.append("LT setting")
        if p.get("composition") == "scene": tags.append("full scene")
        if not os.path.exists(f"{OLD}/{k}.png"): tags.append("new card, no 1.5 master")
        rows.append(dict(k=k, n=n, lt=c["lithuanian"], en=c["english"], cat=c["category"], st=st,
                         note=q.get("fails") or q.get("warnings") or "", guess=q.get("guess", ""),
                         lettering=q.get("lettering", ""), tags=tags, img=composite(k, f"{media}/{k}.jpg")))
    words = {r["k"]: r["lt"] for r in rows}
    first, last = rows[0]["n"], rows[-1]["n"]
    title = f"F6.2 review {first:03d}–{last:03d}"
    other = "part2" if part == "part1" else "part1"
    body = "\n".join(card_html(r) for r in rows)
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="Owner review of the F6.2 Sunburst re-render, cards {first:03d}–{last:03d}: shipped 1.5 master beside the new render, with QA verdicts.">
<style>{CSS}</style></head><body>
<div class="top"><b>{html.escape(title)}</b>
<button class="f on" data-f="all">all {len(rows)}</button>
<button class="f" data-f="unmarked">unmarked</button>
<button class="f" data-f="redo">Redo <span id="nredo2">0</span></button>
<button class="f" data-f="FAIL">FAIL {counts.get("FAIL",0)}</button>
<button class="f" data-f="WARN">WARN {counts.get("WARN",0)}</button>
<button class="f" data-f="PASS">PASS {counts.get("PASS",0)}</button>
<button class="f" data-f="re-rolled">re-rolled {sum(1 for r in rows if rerolled.get(r["k"]))}</button>
<button class="f" data-f="lettering">lettering {sum(1 for r in rows if 'lettering declared' in r['tags'])}</button>
<select id="cat"><option value="">all categories</option>{''.join(f'<option>{html.escape(c)}</option>' for c in sorted({r["cat"] for r in rows}))}</select>
<button onclick="copyRedo()">copy Redo list</button>
<span class="counter"><span><b id="nok">0</b> OK</span><span><b id="nredo">0</b> Redo</span><span><b id="nleft">{len(rows)}</b> left</span></span>
<span id="status"></span></div>
<div class="lead"><p>Cards {first:03d}–{last:03d} of the F6.2 re-render on gpt-image-2.5-sunburst ({other} holds the rest).
Each plate: <b>left</b> the 1.5 master now in the deck, <b>right</b> the new render; click to enlarge.
QA badges are from <code>qa_images.py</code>; <i>read cold as</i> is what the vision model guessed without being told the word; a WARN is usually a synonym.
Press <b>OK</b> or <b>Redo</b> on every card and add a note where it helps. Verdicts save to this page's store as you go; nothing is pushed to the deck until you confirm.</p></div>
{body}
<div id="lbx"><img id="lbimg" alt=""></div>
<script>const TOTAL={len(rows)};const WORDS={json.dumps(words, ensure_ascii=False)};{JS % {"part": part}}</script>
</body></html>'''
    open(f"{pdir}/index.html", "w", encoding="utf-8").write(doc)
    mb = sum(os.path.getsize(f"{media}/{f}") for f in os.listdir(media)) / 1e6
    print(f"{pdir}/index.html  {os.path.getsize(f'{pdir}/index.html')/1024:.0f} KB · {len(rows)} cards · media {len(os.listdir(media))} files {mb:.1f} MB")
