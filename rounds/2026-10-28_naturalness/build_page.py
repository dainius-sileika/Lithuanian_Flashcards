"""Owner's review page for the naturalness + politeness rounds (2026-10-28).
python3 rounds/2026-10-28_naturalness/build_page.py OUT.html   (reads merged_v1.json beside this file)"""
import json, html, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(HERE, "merged_v1.json"), encoding="utf-8"))
NOTES = {
 "2175_rezervuoti": "Packet C: the politeness change makes this word-for-word the phrase card 2194 (Norėčiau rezervuoti kambarį). Right register, but one of the two needs another sentence.",
 "2234_pasimatuoti": "Packet C disagrees: Ar galiu pasimatuoti? duplicates phrase card 2290; the spoken Galiu pasimatuoti? is natural on its own.",
 "1514_eismas": "Your own correction from the proofreading pass (intensyvus). The reviewer thinks didelis is the everyday word and intensyvus is not taught by any card.",
 "1968_vieta_prie_tako": "You corrected the case (Vietą prie tako). The reviewer says takas is a footpath and airlines say vieta prie praėjimo (airBaltic LT).",
 "2200_plansete": "Your correction (žaidžia žaidimus planšetėje). The reviewer says parents say žaidžia planšete (instrumental).",
}
for i in items:
    if i["key"] in ("2175_rezervuoti", "2234_pasimatuoti"):
        i["group"] = "call"
ORDER = [("own", "Your own corrections, challenged",
          "These sentences carry corrections you made in the proofreading pass. A reviewer proposes something else. Unanswered = your correction stays."),
         ("call", "Your call",
          "Where reviewers disagree, or the choice is a matter of register or policy. Unanswered = the current sentence stays."),
         ("change", "Proposed changes",
          "Reviewers judged these unnatural, with the reason and evidence. Unanswered = the change is applied. Choose 'Keep current' to refuse one.")]
esc = lambda s: html.escape(s or "")
def fmt(s):
    return esc(s).replace("{", "<u>").replace("}", "</u>")
def links(ev):
    out = []
    for part in (ev or "").replace(" ; ", ";").split(";"):
        part = part.strip()
        if not part: continue
        words = part.split()
        url = next((w for w in words if w.startswith("http")), None)
        out.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(part.replace(url, "").strip(" :–-") or url)}</a>' if url else esc(part))
    return "<br>".join(out)
rows_html = []
counts = {}
for g, title, intro in ORDER:
    grp = [i for i in items if i["group"] == g]
    counts[g] = len(grp)
    rows_html.append(f'<section><h2>{esc(title)} <span class="n">{len(grp)}</span></h2><p class="intro">{esc(intro)}</p>')
    for i in grp:
        opts = "".join(
            f'<button type="button" data-k="{esc(i["key"])}" data-c="{esc(o["id"])}">Use: {fmt(o["text"])}</button>'
            for o in i["opts"])
        detail = "".join(
            f'<div class="opt"><div class="who">{esc(o["who"])}{(" · " + esc(o.get("conf",""))) if o.get("conf") else ""}</div>'
            f'<div class="prop">{fmt(o["text"])}</div><div class="en">{esc(o["en"])}</div>'
            f'<div class="why">{esc(o["reason"])}</div><div class="ev">{links(o["evidence"])}</div></div>'
            for o in i["opts"])
        note = NOTES.get(i["key"]) or i.get("note_owner") or ""
        rec = '<span class="rec">recorded: a change means a re-take</span>' if i["recorded"] else ""
        rows_html.append(
            f'<article class="item" id="{esc(i["key"])}"><div class="head"><span class="key">{esc(i["key"])}</span>'
            f'<span class="lv">{esc(i["level"])} · #{i["pos"]}</span>{rec}</div>'
            f'<div class="cur"><span class="lab">now</span>{fmt(i["current"])}</div>'
            + (f'<p class="note">{esc(note)}</p>' if note else "") + detail +
            f'<div class="choice">{opts}<button type="button" data-k="{esc(i["key"])}" data-c="keep">Keep current</button></div>'
            f'<textarea data-k="{esc(i["key"])}" placeholder="Your version or a note (optional)" aria-label="Note for {esc(i["key"])}"></textarea>'
            f'<div class="saved" data-k="{esc(i["key"])}"></div></article>')
    rows_html.append("</section>")
page = f'''<title>Naturalness Review</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Brygada+1918:ital,wght@0,400;0,700;1,400&display=swap">
<style>
:root{{--page:#ead6b4;--paper:#f3e6cc;--ink:#2b2420;--soft:#6b5a4a;--rule:#c9b48f;--red:#8f2f25;--red-ink:#f3ead6;--ok:#3d6b4a;
  --f:"Brygada 1918",Georgia,serif;color-scheme:light}}
body{{background:var(--page);color:var(--ink);font:16px/1.5 var(--f);margin:0}}
.band{{background:var(--red);color:var(--red-ink)}}
.wrap{{max-width:860px;margin:0 auto;padding-block:0 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.band .wrap{{padding-block:14px 12px}}
h1{{font-size:clamp(22px,4vw,30px);margin:0;text-wrap:balance}}
.band p{{margin:4px 0 0;font-size:14px;opacity:.92;max-width:70ch}}
h2{{color:var(--red);font-size:20px;margin:30px 0 4px}} .n{{font-size:14px;color:var(--soft);font-weight:400}}
.intro{{color:var(--soft);font-size:14px;margin:0 0 10px;max-width:70ch}}
.item{{background:var(--paper);border-left:4px solid var(--rule);padding:12px 14px;margin:12px 0}}
.item.answered{{border-left-color:var(--ok)}}
.head{{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;font-size:13px;color:var(--soft)}}
.key{{font-weight:700;color:var(--ink)}} .rec{{color:var(--red)}}
.cur{{font-size:19px;margin:6px 0}} .lab{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--soft);margin-right:8px}}
u{{text-decoration-color:var(--red);text-decoration-thickness:2px;text-underline-offset:3px}}
.note{{font-size:14px;background:#efe0c2;padding:6px 8px;margin:6px 0}}
.opt{{border-top:1px dotted var(--rule);padding-top:6px;margin-top:6px}}
.who{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--soft)}}
.prop{{font-size:18px;font-weight:700}} .en{{font-style:italic;color:var(--soft)}}
.why{{font-size:14px;margin-top:3px}} .ev{{font-size:12px;color:var(--soft);margin-top:3px;overflow-wrap:anywhere}} .ev a{{color:var(--red)}}
.choice{{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}}
button{{font:600 14px var(--f);padding:6px 10px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:3px;cursor:pointer;text-align:left}}
button[aria-pressed="true"]{{background:var(--red);color:var(--red-ink);border-color:var(--red)}}
button:focus-visible,textarea:focus-visible{{outline:2px solid var(--red);outline-offset:2px}}
textarea{{width:100%;box-sizing:border-box;margin-top:8px;min-height:38px;font:15px/1.4 var(--f);background:#fbf4e4;color:var(--ink);border:1px solid var(--rule);border-radius:3px;padding:6px 8px}}
.saved{{font-size:12px;color:var(--ok);min-height:1em}} .status{{font-size:13px;color:var(--soft);margin-top:20px}}
.sum{{display:flex;flex-wrap:wrap;gap:14px;font-size:14px;margin-top:8px}}
</style>
<header class="band"><div class="wrap"><h1>Naturalness review: what changes</h1>
<p>Three reviewers read all 1,255 sentences and phrases for what a native speaker would naturally say; a fourth reviewed requests for politeness. 1,183 stay as they are. These {len(items)} need a decision or are proposed for change. The taught word is underlined.</p>
<div class="sum"><span>Your corrections challenged: {counts["own"]}</span><span>Your call: {counts["call"]}</span><span>Proposed changes: {counts["change"]}</span><span id="done"></span></div></div></header>
<main class="wrap">{"".join(rows_html)}
<div class="status" id="status">Connecting…</div></main>
<script>
const state={{}}; let db=null; const timers={{}};
try{{Object.assign(state,JSON.parse(localStorage.getItem("nat_review_v1")||"{{}}"))}}catch(e){{}}
function paint(k){{const s=state[k]||{{}};
  document.querySelectorAll('button[data-k="'+CSS.escape(k)+'"]').forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.c===s.choice)));
  const t=document.querySelector('textarea[data-k="'+CSS.escape(k)+'"]'); if(t&&document.activeElement!==t) t.value=s.note||"";
  const a=document.getElementById(k); if(a) a.classList.toggle("answered",!!(s.choice||s.note));}}
function paintAll(){{document.querySelectorAll("article.item").forEach(a=>paint(a.id));
  const n=Object.values(state).filter(s=>s&&(s.choice||s.note)).length; document.getElementById("done").textContent="Answered: "+n;}}
function save(k){{try{{localStorage.setItem("nat_review_v1",JSON.stringify(state))}}catch(e){{}}
  const el=document.querySelector('.saved[data-k="'+CSS.escape(k)+'"]');
  if(!db){{if(el)el.textContent="Saved on this device only";return;}}
  clearTimeout(timers[k]); timers[k]=setTimeout(async()=>{{
    try{{await db.collection("naturalness").doc(k).set({{...state[k],updatedAt:new Date().toISOString()}}); if(el)el.textContent="Saved";}}
    catch(e){{if(el)el.textContent="Couldn't save just now; kept on this device";}}}},500);}}
document.querySelectorAll("button[data-k]").forEach(b=>b.addEventListener("click",()=>{{const k=b.dataset.k;
  state[k]=state[k]||{{}}; state[k].choice=state[k].choice===b.dataset.c?null:b.dataset.c; paint(k); paintAll(); save(k);}}));
document.querySelectorAll("textarea[data-k]").forEach(t=>t.addEventListener("input",()=>{{const k=t.dataset.k;
  state[k]=state[k]||{{}}; state[k].note=t.value; paintAll(); save(k);}}));
paintAll();
(async()=>{{const st=document.getElementById("status");
  try{{db=window.claude?.use?await window.claude.use("db"):null;
    if(!db){{st.textContent="Offline: your answers stay on this device.";return;}}
    const snap=await db.collection("naturalness").get();
    snap.docs.forEach(d=>{{state[d.id]=d.data();}}); paintAll();
    st.textContent="Connected: your answers save automatically.";}}
  catch(e){{st.textContent="Offline: your answers stay on this device.";}}}})();
</script>'''
open(sys.argv[1], "w", encoding="utf-8").write(page)
print(len(items), counts)
