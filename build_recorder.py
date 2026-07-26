#!/usr/bin/env python3
"""Build recorder.html — a self-contained, offline browser recorder for the
deck's wordlist. Shows one word at a time, records one clip per card key via the
mic, persists to IndexedDB (resume across sessions), and exports a zip of clips
named by card key (ready to drop into audio/ and rebuild the deck).

Reads cards_anki.csv directly, so the recorder can never drift out of step with
the deck: re-run it after any wordlist change.

    python3 build_recorder.py     ->  recorder.html
"""
import csv
import json
import os
import sys

SRC = "cards_anki.csv"
QUEUE = "wordlist_a2_pending.csv"

# Which level(s) to record. `python3 build_recorder.py A1` builds an A1-only
# sheet; no argument builds everything.
LEVEL = sys.argv[1] if len(sys.argv) > 1 else ""

WORDS = [
    {"key": r["key"], "number": r["number"], "lt": r["lithuanian"],
     "en": r["english"], "pron": r.get("pron", ""), "cat": r["category"]}
    for r in csv.DictReader(open(SRC, encoding="utf-8"))
    if r["lithuanian"].strip() and (not LEVEL or r.get("level", "A1") == LEVEL)
]

# Recording is gated on the WORD being final, not on the image existing — so
# confirmed queue rows are included even before their images are generated.
if os.path.exists(QUEUE):
    for r in csv.DictReader(open(QUEUE, encoding="utf-8")):
        if r.get("status") != "pending":
            continue
        if LEVEL and r.get("level") != LEVEL:
            continue
        if "verify" in (r.get("notes", "") or "").lower():
            continue                      # not owner-confirmed yet
        if not r["lithuanian_TARGET"].strip():
            continue
        WORDS.append({"key": r["id"], "number": r["id"], "lt": r["lithuanian_TARGET"],
                      "en": r["english"], "pron": r.get("lt_pron", ""),
                      "cat": r["category"] + " (new)"})

TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lietuvių Flashcards — voice recorder</title>
<style>
  :root{--paper:#e7ddc6;--paper2:#efe7d4;--red:#97301f;--ink:#2c2620;--teal:#3c5e5a;--dun:#8a7d61;--green:#3f7d4f}
  *{box-sizing:border-box}
  body{font-family:Georgia,"Times New Roman",serif;color:var(--ink);background:var(--paper);margin:0;
       background-image:radial-gradient(rgba(44,38,32,.05) 1px,transparent 1.2px),radial-gradient(rgba(151,48,31,.04) 1px,transparent 1.2px);
       background-size:6px 6px,9px 9px}
  header{background:var(--red);color:var(--paper);padding:10px 16px;display:flex;justify-content:space-between;align-items:center;
         font-variant:small-caps;letter-spacing:.12em;font-weight:700}
  .wrap{max-width:760px;margin:0 auto;padding:16px}
  .card{background:var(--paper2);border:2px solid var(--red);box-shadow:0 1px 0 rgba(0,0,0,.15);padding:26px 22px;text-align:center;margin-top:14px}
  .meta{color:var(--dun);font-variant:small-caps;letter-spacing:.1em;font-size:.8rem}
  .word{font-size:3.4rem;font-weight:700;line-height:1.05;margin:6px 0 2px}
  .pron{font-style:italic;color:var(--teal);font-size:1.5rem;margin-bottom:6px}
  .en{color:#4a4238;font-size:1.15rem}.en:before{content:"— ";color:var(--red)}
  .controls{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:20px}
  button{font-family:inherit;font-size:1rem;padding:11px 18px;border:2px solid var(--red);background:var(--paper);color:var(--red);
         border-radius:3px;cursor:pointer;font-variant:small-caps;letter-spacing:.06em;font-weight:700}
  button:hover{background:var(--red);color:var(--paper)}
  button:disabled{opacity:.4;cursor:not-allowed}
  button.rec{background:var(--red);color:var(--paper)}
  button.recording{background:#c0392b;color:#fff;border-color:#c0392b;animation:pulse 1s infinite}
  @keyframes pulse{50%{opacity:.55}}
  .nav{display:flex;gap:10px;justify-content:space-between;align-items:center;margin-top:14px}
  .bar{height:12px;background:#d8ccae;border:1px solid var(--dun);border-radius:6px;overflow:hidden;margin-top:12px}
  .bar>div{height:100%;background:var(--green);width:0%}
  .status{margin-top:8px;font-size:.9rem;color:var(--teal);min-height:1.2em}
  .row{display:flex;align-items:center;gap:10px;justify-content:center;flex-wrap:wrap}
  label.chk{font-size:.9rem;color:var(--ink)}
  .grid{display:flex;flex-wrap:wrap;gap:4px;margin-top:16px}
  .cell{width:26px;height:22px;font-size:.62rem;display:flex;align-items:center;justify-content:center;border:1px solid var(--dun);
        background:var(--paper2);cursor:pointer;color:var(--dun)}
  .cell.done{background:var(--green);color:#fff;border-color:var(--green)}
  .cell.cur{outline:2px solid var(--red);outline-offset:1px;font-weight:700}
  audio{width:100%;margin-top:12px}
  .hint{font-size:.85rem;color:var(--dun);margin-top:10px;line-height:1.5}
  kbd{background:#d8ccae;border:1px solid var(--dun);border-radius:3px;padding:0 5px;font-family:monospace;font-size:.8rem}
  .big{font-size:1.05rem;padding:13px 22px}
</style></head>
<body>
<header><span>Lietuvių — voice recorder</span><span id="count">0 / 0</span></header>
<div class="wrap">

  <div id="setup" class="card">
    <p style="font-size:1.1rem">Read each Lithuanian word once, clearly and naturally.<br>One clip is saved per word — no editing needed.</p>
    <p class="hint">Your recordings are saved in this browser as you go, so you can close the tab and resume later on the same computer. When finished (or partway), click <b>Export ZIP</b> and send it back.</p>
    <div class="controls"><button class="rec big" id="start">Enable microphone &amp; start</button></div>
    <p class="status" id="setupStatus"></p>
  </div>

  <div id="app" style="display:none">
    <div class="card">
      <div class="meta"><span id="numcat"></span></div>
      <div class="word" id="lt"></div>
      <div class="pron" id="pron"></div>
      <div class="en" id="en"></div>
      <div class="bar"><div id="progress"></div></div>
      <div class="status" id="status">Not recorded yet</div>
      <div class="controls">
        <button class="rec" id="recBtn">● Record</button>
        <button id="playBtn" disabled>▶ Play</button>
      </div>
      <audio id="player" controls style="display:none"></audio>
      <div class="nav">
        <button id="prev">← Prev</button>
        <label class="chk"><input type="checkbox" id="auto" checked> auto-advance after recording</label>
        <button id="next">Next →</button>
      </div>
      <div class="hint">
        Shortcuts: <kbd>Space</kbd> record / stop · <kbd>P</kbd> play · <kbd>→</kbd> next · <kbd>←</kbd> prev
      </div>
    </div>

    <div class="card">
      <div class="row">
        <button id="export" class="big">⬇ Export ZIP</button>
        <span class="hint" id="exportInfo"></span>
      </div>
      <div class="grid" id="grid"></div>
    </div>
  </div>

</div>
<script>
const WORDS = __WORDS__;
document.getElementById('count').textContent = "0 / " + WORDS.length;

/* ---------- IndexedDB (persist clips so a long session can resume) ---------- */
let db;
function openDB(){return new Promise((res,rej)=>{const r=indexedDB.open('lt_recorder',1);
  r.onupgradeneeded=e=>e.target.result.createObjectStore('clips');
  r.onsuccess=e=>{db=e.target.result;res()};r.onerror=()=>rej(r.error);});}
function putClip(k,b){return new Promise((res,rej)=>{const t=db.transaction('clips','readwrite');
  t.objectStore('clips').put(b,k);t.oncomplete=res;t.onerror=()=>rej(t.error);});}
function getClip(k){return new Promise(res=>{const t=db.transaction('clips','readonly');
  const q=t.objectStore('clips').get(k);q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null);});}
function doneKeys(){return new Promise(res=>{const t=db.transaction('clips','readonly');
  const q=t.objectStore('clips').getAllKeys();q.onsuccess=()=>res(new Set(q.result));q.onerror=()=>res(new Set());});}

/* ---------- recording ---------- */
let stream,rec,chunks=[],MIME='',idx=0,done=new Set();
function pickMime(){for(const m of ['audio/webm;codecs=opus','audio/webm','audio/mp4','audio/ogg']){
  if(window.MediaRecorder&&MediaRecorder.isTypeSupported(m))return m;}return '';}
function extFor(type){if(!type)return 'webm';if(type.includes('mp4')||type.includes('m4a')||type.includes('aac'))return 'm4a';
  if(type.includes('ogg'))return 'ogg';return 'webm';}

async function start(){
  const s=document.getElementById('setupStatus');
  try{stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:false}});}
  catch(e){s.textContent="Could not access the microphone: "+e.message;return;}
  MIME=pickMime();
  await openDB(); done=await doneKeys();
  document.getElementById('setup').style.display='none';
  document.getElementById('app').style.display='block';
  buildGrid();
  // jump to first not-yet-recorded word
  let f=WORDS.findIndex(w=>!done.has(w.key)); idx=f<0?0:f;
  render();
}

function startRec(){
  chunks=[]; rec=new MediaRecorder(stream, MIME?{mimeType:MIME}:undefined);
  rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
  rec.onstop=async()=>{
    const blob=new Blob(chunks,{type:MIME||'audio/webm'});
    await putClip(WORDS[idx].key, blob); done.add(WORDS[idx].key);
    updateCell(idx); setPlayer(blob); setCount();
    document.getElementById('status').textContent="Recorded ✓ ("+Math.round(blob.size/1024)+" KB)";
    recBtn.classList.remove('recording'); recBtn.textContent='● Re-record';
    if(document.getElementById('auto').checked) setTimeout(()=>go(1),350);
  };
  rec.start(); recBtn.classList.add('recording'); recBtn.textContent='■ Stop';
  document.getElementById('status').textContent="Recording…";
}
function toggleRec(){ if(rec&&rec.state==='recording'){rec.stop();} else {startRec();} }

/* ---------- UI ---------- */
const recBtn=document.getElementById('recBtn'), playBtn=document.getElementById('playBtn'), player=document.getElementById('player');
function setPlayer(blob){ player.src=URL.createObjectURL(blob); player.style.display='block'; playBtn.disabled=false; }
async function render(){
  const w=WORDS[idx];
  document.getElementById('numcat').textContent = "#"+w.number+"  ·  "+w.cat+"   ("+(idx+1)+" of "+WORDS.length+")";
  document.getElementById('lt').textContent=w.lt;
  document.getElementById('pron').textContent=w.pron||'';
  document.getElementById('en').textContent=w.en;
  recBtn.classList.remove('recording');
  const clip=await getClip(w.key);
  if(clip){ recBtn.textContent='● Re-record'; setPlayer(clip); document.getElementById('status').textContent="Recorded ✓"; }
  else { recBtn.textContent='● Record'; player.style.display='none'; playBtn.disabled=true; document.getElementById('status').textContent="Not recorded yet"; }
  document.querySelectorAll('.cell').forEach((c,i)=>c.classList.toggle('cur',i===idx));
  const curCell=document.querySelectorAll('.cell')[idx]; if(curCell) curCell.scrollIntoView({block:'nearest'});
}
function go(d){ idx=Math.min(WORDS.length-1,Math.max(0,idx+d)); render(); }
function setCount(){ document.getElementById('count').textContent=done.size+" / "+WORDS.length;
  document.getElementById('progress').style.width=(100*done.size/WORDS.length)+"%";
  document.getElementById('exportInfo').textContent=done.size+" recorded, "+(WORDS.length-done.size)+" remaining"; }
function buildGrid(){ const g=document.getElementById('grid'); g.innerHTML='';
  WORDS.forEach((w,i)=>{ const c=document.createElement('div'); c.className='cell'+(done.has(w.key)?' done':'');
    c.textContent=w.number; c.title=w.lt; c.onclick=()=>{idx=i;render();}; g.appendChild(c); });
  setCount(); }
function updateCell(i){ const c=document.querySelectorAll('.cell')[i]; if(c)c.classList.add('done'); setCount(); }

document.getElementById('start').onclick=start;
recBtn.onclick=toggleRec;
playBtn.onclick=()=>{player.currentTime=0;player.play();};
document.getElementById('next').onclick=()=>go(1);
document.getElementById('prev').onclick=()=>go(-1);
document.addEventListener('keydown',e=>{
  if(document.getElementById('app').style.display==='none')return;
  if(e.code==='Space'){e.preventDefault();toggleRec();}
  else if(e.key==='p'||e.key==='P'){if(!playBtn.disabled){player.currentTime=0;player.play();}}
  else if(e.key==='ArrowRight'){go(1);} else if(e.key==='ArrowLeft'){go(-1);}
});

/* ---------- ZIP export (store method, no external libs → fully offline) ---------- */
const CRCT=(()=>{let t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}return t;})();
function crc32(u8){let c=0xFFFFFFFF;for(let i=0;i<u8.length;i++)c=CRCT[(c^u8[i])&0xFF]^(c>>>8);return (c^0xFFFFFFFF)>>>0;}
function makeZip(files){
  const enc=new TextEncoder(),now=new Date();
  const dt=((now.getHours()&31)<<11)|((now.getMinutes()&63)<<5)|((now.getSeconds()/2)&31);
  const dd=(((now.getFullYear()-1980)&127)<<9)|(((now.getMonth()+1)&15)<<5)|(now.getDate()&31);
  const u16=n=>[n&255,(n>>8)&255], u32=n=>[n&255,(n>>8)&255,(n>>16)&255,(n>>>24)&255];
  let parts=[],central=[],offset=0;
  for(const f of files){ const nb=enc.encode(f.name),crc=crc32(f.data),sz=f.data.length;
    const lh=[].concat(u32(0x04034b50),u16(20),u16(0),u16(0),u16(dt),u16(dd),u32(crc),u32(sz),u32(sz),u16(nb.length),u16(0));
    parts.push(new Uint8Array(lh),nb,f.data);
    const ch=[].concat(u32(0x02014b50),u16(20),u16(20),u16(0),u16(0),u16(dt),u16(dd),u32(crc),u32(sz),u32(sz),u16(nb.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(offset));
    central.push(new Uint8Array(ch),nb); offset+=lh.length+nb.length+sz; }
  let cs=0; for(const c of central) cs+=c.length;
  const eo=[].concat(u32(0x06054b50),u16(0),u16(0),u16(files.length),u16(files.length),u32(cs),u32(offset),u16(0));
  return new Blob([...parts,...central,new Uint8Array(eo)],{type:'application/zip'});
}
document.getElementById('export').onclick=async()=>{
  const info=document.getElementById('exportInfo'); info.textContent="Packing…";
  const files=[]; const man=["key\tword\tenglish\tfile"];
  for(const w of WORDS){ const b=await getClip(w.key); if(!b)continue;
    const ext=extFor(b.type), name=w.key+"."+ext;
    files.push({name, data:new Uint8Array(await b.arrayBuffer())});
    man.push(w.key+"\t"+w.lt+"\t"+w.en+"\t"+name); }
  if(!files.length){info.textContent="Nothing recorded yet.";return;}
  files.push({name:"manifest.tsv", data:new TextEncoder().encode(man.join("\n"))});
  const blob=makeZip(files), url=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=url; a.download="lithuanian_recordings.zip"; a.click();
  info.textContent="Exported "+(files.length-1)+" clips.";
};
</script>
</body></html>"""

html = TEMPLATE.replace("__WORDS__", json.dumps(WORDS, ensure_ascii=False))
out = f"recorder_{LEVEL}.html" if LEVEL else "recorder.html"
open(out, "w", encoding="utf-8").write(html)
print(f"wrote {out} — {len(WORDS)} words, {len(html)//1024} KB")
