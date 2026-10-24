#!/usr/bin/env python3
"""Build a self-contained, offline browser recorder (one HTML file). It shows one card at a
time, records one clip per take key from the microphone, keeps the clips in the browser's
IndexedDB (so a session can be resumed), and exports a ZIP of clips named by take key.

    python3 build_recorder.py A2   ->  recorder_A2.html + a2_build/recording_list.csv   (THE sheet)
        Despite the historical name this is the whole-deck sheet: every take the CURRENT
        package still needs, A1 subdeck first, then A2, each in study order (study_order.csv).
        The set is derived from what build_apkg.py emits (same lists, same inclusion rules,
        same audio paths), never from a hand-kept list:
          * one take per note, key = card key: every row -> media/audio/<key>.mp3 (one folder for
            A1, A2-list and sentence cards since the tidy of 2026-10-24; build_apkg.AUDIO_DIR);
          * cloze/pair A2-list rows also take their example sentence, key <id>_s -> media/audio/;
          * a take is listed when audio_source.tsv has no human take for the key ("new"),
            the key still has the synthesized voice ("replace-tts"), or the human take's
            recorded words (`said`) no longer match the card's script, accent-blind ("retake";
            source "superseded" = the old take is withdrawn from the package).
        Merged-away keys (a2_build/merged_keys.csv) and B1 deferrals (a2_build/deferred_B1.csv)
        are not in the lists build_apkg reads; they are checked and skipped here as a guard.
        The page's IndexedDB name is fixed (DECK_SHEET_ID) so takes already in the browser
        survive every regeneration; see a2_build/RECORDING_GUIDE.md.
    python3 build_recorder.py          ->  recorder_all.html   (legacy: cards_anki.csv only)
    python3 build_recorder.py A1 [new] ->  recorder_A1[_new].html (legacy July sheets)

Ingest (owner ZIP -> package): python3 tools/ingest_takes.py <zip> — converts each clip to the
`dest` path in recording_list.csv (ffmpeg ... -codec:a libmp3lame -q:a 4), moves a replaced take to
media/audio/_history/, and writes the key's audio_source.tsv row as  key  human  <dest>  <said>
(said = the ZIP manifest's `said` column), so the next run of this script drops the take from
the sheet. ZIPs exported before the key rename (2026-10-20) name clips by the old keys; the
script maps them through tools/keymap.py. The page itself moves stored clips to their new keys
on start (migrateKeys, KEY_MAP from a2_build/rename/key_map_v*.csv).
"""
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata

SRC = "cards_anki.csv"
QUEUE = "wordlist_a2_pending.csv"
AUDIO_SOURCE = "audio_source.tsv"
LIST_OUT = "a2_build/recording_list.csv"
MERGED = "a2_build/merged_keys.csv"
DEFERRED = "a2_build/deferred_B1.csv"
# The sheet the owner may already have recorded with (2026-10-12): its per-key script, so a
# clip stored in the browser without a script stamp can be recognised as stale.
LEGACY_SHEET = "a2_build/audio/recorder_A2_afb2ebe2_script.json"
# IndexedDB name of the deck sheet = 'lt_recorder_' + DECK_SHEET_ID. NEVER change it: the
# browser keeps the owner's takes under this name, keyed by take key; a new name would hide
# them. (Until 2026-10-19 the id was a hash of the key list and changed on every regeneration.)
DECK_SHEET_ID = "A2_afb2ebe2"


def key_number(k):
    """The number shown on the take ('#21' for 0021_labas): the key's number = the card's plate."""
    return str(int(k[:4])) if k[:4].isdigit() else k


def key_map_for_page():
    """old take key -> current take key, over every a2_build/rename/key_map_v*.csv (chains followed):
    '<old>' -> '<new>' and '<old>_s' -> '<new>_s' for every renamed card and media alias. Embedded in
    the page so clips stored under a pre-rename key move to their new key on start (migrateKeys)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
    import keymap
    out = {}
    for p in keymap.maps():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            old, new = r["old_key"].strip(), (r.get("new_key") or "").strip()
            if not old or not new or old == new or r.get("status") not in ("renamed", "alias"):
                continue
            cur = keymap.canonical(old)
            out[old] = cur
            out[old + "_s"] = cur + "_s"
    return out


def read_script(headword, row):
    """What the speaker should say for this card: the headword, then the forms
    that show the paradigm. Lithuanian stress moves between forms, so hearing
    the genitive / principal parts is the point of recording them."""
    out = [{"label": "", "form": headword}]
    if row.get("gen_sg", "").strip():
        out.append({"label": "gen.", "form": row["gen_sg"].strip()})
    if row.get("pres3", "").strip():
        out.append({"label": "3sg", "form": row["pres3"].strip()})
    if row.get("past3", "").strip():
        out.append({"label": "past", "form": row["past3"].strip()})
    if row.get("fem", "").strip():
        out.append({"label": "fem.", "form": row["fem"].strip()})
    return out


def strip_accents(s):
    """Remove the stress marks (grave, acute, tilde) and the soft-dot that i/j carry under
    an accent (i̇̃), keeping the letters ą č ę ė į š ų ū ž."""
    d = unicodedata.normalize("NFD", s or "")
    out = []
    for ch in d:
        if ch in "̀́̃":
            continue
        if ch == "̇" and out and out[-1] in "iIjJ":
            continue
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out)).strip()


def said_key(s):
    """Comparison key for 'are these the same words?': accent-, case- and punctuation-blind;
    parenthetical glosses dropped."""
    s = re.sub(r"\([^)]*\)", " ", strip_accents(s)).lower()
    s = re.sub(r"[.,!?;:„“”\"«»—–\-·]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def script_text(script):
    return " · ".join(f["form"] for f in script)


def load_audio_source(path=AUDIO_SOURCE):
    """key -> {source, file, said}; reads the 2-column format of July 2026 as well."""
    out = {}
    if not os.path.exists(path):
        return out
    rows = list(csv.reader(open(path, encoding="utf-8"), delimiter="\t"))
    head = rows[0] if rows else []
    for r in rows[1:]:
        if not r:
            continue
        d = dict(zip(head, r))
        out[r[0]] = {"source": d.get("source", ""), "file": d.get("file", ""), "said": d.get("said", "")}
    return out


def ids(path, col="id"):
    return {r[col] for r in csv.DictReader(open(path, encoding="utf-8"))} if os.path.exists(path) else set()


def deck_takes():
    """Every take the current package needs and does not have yet, with its status.
    Returns (takes, stats, warnings)."""
    import build_apkg as B   # same lists, image/sentence inclusion and audio paths as the build
    order = B.load_study_order()
    asrc = load_audio_source()
    skip = ids(MERGED) | ids(DEFERRED)
    warnings, takes = [], []
    lv_rank = {"A1": 0, "A2": 1}

    def add(key, kind, level, sub, lt, en, pron, script, dest, cat, number):
        pos = order.get(key[:-2] if key.endswith("_s") else key)
        if pos is None:
            warnings.append(f"{key}: not in {B.STUDY_ORDER} (sorted last)")
        say = script_text(script)
        a = asrc.get(key)
        status, was = None, ""
        if a and a["source"] == "superseded":
            status, was = "retake", a["said"]
        elif a and a["source"].startswith("human"):
            if a["file"] and a["file"] != dest:
                warnings.append(f"{key}: human take at {a['file']}, but the build reads {dest}")
            if not os.path.exists(a["file"] or dest):
                warnings.append(f"{key}: audio_source says human, file missing -> listed as new")
                status = "new"
            elif not a["said"]:
                warnings.append(f"{key}: human take without a `said` record, assumed current")
            elif said_key(a["said"]) != said_key(say):
                status, was = "retake", a["said"]
        elif a and a["source"].startswith("azure"):
            status = "replace-tts"
        elif os.path.exists(dest):
            warnings.append(f"{key}: {dest} exists but has no audio_source.tsv row, assumed current")
        else:
            status = "new"
        if status:
            takes.append({"key": key, "number": number, "lt": lt, "en": en, "pron": pron,
                          "cat": cat, "kind": kind, "level": level, "status": status, "was": was,
                          "say": say, "script": script, "dest": dest,
                          "order": pos if pos is not None else "",
                          "_sort": (lv_rank.get(level, 9), pos if pos is not None else 10**6, sub)})

    # 1. cards_anki.csv (the 520 + batonas base), only rows the build finds a picture for
    for r in csv.DictReader(open(SRC, encoding="utf-8")):
        k = r["key"]
        if not B.find_image(k, B.A1_IMAGE_DIRS):
            continue
        level = (r.get("level") or "A1").strip() or "A1"
        pron = r.get("pron", "") or r["lithuanian"]
        add(k, "word", level, 0, r["lithuanian"], r["english"], r.get("pron", ""),
            read_script(pron, r), f"{B.AUDIO_DIR}/{k}.mp3", r["category"], key_number(k))
    # 2. the A2 list (IMG/PHRASE with a picture, CLOZE/PAIR with a cloze sentence)
    for r in csv.DictReader(open(B.A2_LIST, encoding="utf-8")):
        k, route = r["id"], r.get("route", "")
        if k in skip:
            warnings.append(f"{k}: merged/deferred key still in {B.A2_LIST} (skipped here)")
            continue
        if route in ("IMG", "PHRASE"):
            if not B.find_a2_image(k):
                continue
        elif route in ("CLOZE", "PAIR"):
            if not B.cloze_text(r.get("example_lt", ""))[1]:
                continue
        else:
            continue
        level = (r.get("level") or "A2").strip() or "A2"
        head = re.sub(r"\s*\(.*\)", "", r["lithuanian_TARGET"]).strip()
        pron = r.get("lt_pron", "") or head
        add(k, "word", level, 0, head, r["english"], r.get("lt_pron", ""), read_script(pron, r),
            f"{B.A2_AUDIO_DIR}/{k}.mp3", r["category"] + " · " + route.lower(), key_number(k))
        if route in ("CLOZE", "PAIR"):
            sent = r["example_lt"].replace("{", "").replace("}", "")
            add(k + "_s", "sentence", level, 1, sent, r.get("example_en", ""), "",
                [{"label": "", "form": sent}], f"{B.A2_AUDIO_DIR}/{k}_s.mp3", "sentence for " + head, key_number(k) + " s")
    # 3. sentence cards
    if B.SENTENCES and os.path.exists(B.SENTENCES):
        for r in csv.DictReader(open(B.SENTENCES, encoding="utf-8")):
            if not B.cloze_text(r["lt"])[1]:
                continue
            sent = r["lt"].replace("{", "").replace("}", "")
            level = (r.get("level") or "A2").strip() or "A2"
            add(r["id"], "sentence", level, 2, sent, r["en"], "", [{"label": "", "form": sent}],
                f"{B.A2_AUDIO_DIR}/{r['id']}.mp3", "sentence card", key_number(r["id"]))
    takes.sort(key=lambda t: t["_sort"])
    for n, t in enumerate(takes, 1):
        t["n"] = n
        del t["_sort"]
    # browser clips recorded with the 2026-10-12 sheet carry no script stamp: name the keys
    # whose script has changed since, so the page sets those clips aside instead of using them
    legacy = {}
    if os.path.exists(LEGACY_SHEET):
        legacy = json.load(open(LEGACY_SHEET, encoding="utf-8"))["said"]
    for t in takes:
        old = legacy.get(t["key"])
        t["legacy_stale"] = bool(old is not None and said_key(old) != said_key(t["say"]))
    stats = {}
    for t in takes:
        stats[(t["level"], t["status"])] = stats.get((t["level"], t["status"]), 0) + 1
    return takes, stats, warnings


def write_list(takes, path=LIST_OUT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["take", "file_name", "dest", "level", "kind", "status", "study_order",
                    "lithuanian", "english", "pron", "say", "was"])
        for t in takes:
            w.writerow([t["n"], t["key"] + ".mp3", t["dest"], t["level"], t["kind"], t["status"],
                        t["order"], t["lt"], t["en"], t["pron"], t["say"], t["was"]])


def legacy_words(level, only_new):
    """The July sheets: cards_anki.csv (+ confirmed queue rows), optionally only keys
    without a human take."""
    human = {k for k, a in load_audio_source().items() if a["source"].startswith("human")} if only_new else set()
    words = [
        {"key": r["key"], "number": r["number"], "lt": r["lithuanian"],
         "en": r["english"], "pron": r.get("pron", ""), "cat": r["category"],
         "script": read_script(r.get("pron") or r["lithuanian"], r)}
        for r in csv.DictReader(open(SRC, encoding="utf-8"))
        if r["lithuanian"].strip() and (not level or r.get("level", "A1") == level)
        and not (only_new and r["key"] in human)]
    if os.path.exists(QUEUE):
        for r in csv.DictReader(open(QUEUE, encoding="utf-8")):
            if r.get("status") != "pending" or (level and r.get("level") != level):
                continue
            if "verify" in (r.get("notes", "") or "").lower() or not r["lithuanian_TARGET"].strip():
                continue
            if only_new and r["id"] in human:
                continue
            words.append({"key": r["id"], "number": r["id"], "lt": r["lithuanian_TARGET"],
                          "en": r["english"], "pron": r.get("lt_pron", ""),
                          "cat": r["category"] + " (new)",
                          "script": read_script(r.get("lt_pron") or r["lithuanian_TARGET"], r)})
    for w in words:
        w["say"] = script_text(w["script"])
    return words


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
  .script{margin:14px auto 0;padding:12px 14px;background:#f6f1e2;border:1px dashed var(--red);max-width:560px}
  .script .lead{font-variant:small-caps;letter-spacing:.1em;font-size:.72rem;color:var(--dun);display:block;margin-bottom:6px}
  .script b{font-size:1.9rem;display:inline-block;margin:0 .35em}
  .script .lab{font-size:.7rem;color:var(--teal);font-variant:small-caps;vertical-align:super;margin-right:2px}
  .script .sep{color:var(--dun);font-size:1.4rem}
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
  .script.sentence b{font-size:1.5rem;line-height:1.3}
  @media (max-width:600px){
    .wrap{padding:8px} .card{padding:16px 10px} .word{font-size:2.3rem} .pron{font-size:1.2rem}
    button{padding:14px 16px;font-size:1.05rem;min-width:44%} .controls button.rec{min-width:100%}
    .grid{display:none} .jump{display:flex}
  }
  .badge{display:inline-block;font-variant:small-caps;letter-spacing:.08em;font-size:.78rem;padding:1px 8px;border:1px solid var(--dun);margin:0 3px;color:var(--dun)}
  .badge.lvA1{border-color:var(--teal);color:var(--teal)} .badge.lvA2{border-color:var(--red);color:var(--red)}
  .badge.retake{background:var(--red);color:var(--paper);border-color:var(--red)}
  .badge.tts{background:var(--teal);color:var(--paper);border-color:var(--teal)}
  .was{font-size:.9rem;color:var(--red);margin-top:6px}
  .jump{display:none;gap:8px;justify-content:center;margin-top:10px;align-items:center}
  .jump input{font-size:1rem;padding:8px;width:7em;border:1px solid var(--dun);background:var(--paper2)}
</style></head>
<body>
<header><span>Lietuvių — voice recorder</span><span id="count">0 / 0</span></header>
<div class="wrap">

  <div id="setup" class="card">
    <p style="font-size:1.1rem">For each card, read <b>every form shown in the dashed box</b> — the headword, then its genitive / principal parts — one clear breath apart.<br>One clip is saved per card; no editing needed.</p>
    <p class="hint">Your recordings are saved in this browser as you go, so you can close the tab and resume later: same computer, same browser. When finished (or partway), click <b>Export new takes</b> and put the ZIP where the guide says (a2_build/RECORDING_GUIDE.md).</p>
    <div class="controls"><button class="rec big" id="start">Enable microphone &amp; start</button></div>
    <p class="status" id="setupStatus"></p>
  </div>

  <div id="app" style="display:none">
    <div class="card">
      <div class="meta"><span id="badges"></span> <span id="numcat"></span></div>
      <div class="word" id="lt"></div>
      <div class="pron" id="pron" title="stressed form: say it this way"></div>
      <div class="en" id="en"></div>
      <div class="was" id="was"></div>
      <div class="script" id="script"></div>
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
        <button id="exportNew" class="big">⬇ Export new takes</button>
        <button id="export">⬇ Export all</button>
      </div>
      <p class="hint" id="exportInfo"></p>
      <p class="hint" id="storeInfo"></p>
      <p class="hint">On a phone each export is one ZIP of the takes recorded since the last export — send it on and carry on; the batches add up. Files are named by card key.</p>
      <div class="jump"><label class="hint">go to take</label><input id="jumpTo" type="number" min="1"><button id="jumpBtn">Go</button></div>
      <div class="grid" id="grid"></div>
    </div>
  </div>

</div>
<script>
const WORDS = __WORDS__;
const SHEET_ID = "__SHEET_ID__";        // IndexedDB name suffix; fixed for the deck sheet (never change)
// old take key -> current take key (the key rename of 2026-10-20, a2_build/rename/key_map_v*.csv)
const KEY_MAP = __KEY_MAP__;
document.getElementById('count').textContent = "0 / " + WORDS.length;

/* ---------- IndexedDB (persist clips so a long session can resume) ----------
   DB 'lt_recorder_'+SHEET_ID, stores 'clips' (take key -> Blob) and 'meta'. Same scheme as the
   2026-10-12 sheet, so its clips are found again. New meta keys: 'said:<key>' (the words a clip
   was recorded for), 'superseded:<key>:<ms>' (a stale clip set aside, never deleted). */
let db;
function openDB(){return new Promise((res,rej)=>{const r=indexedDB.open('lt_recorder_'+SHEET_ID,2);
  r.onupgradeneeded=e=>{const d=e.target.result;
    if(!d.objectStoreNames.contains('clips'))d.createObjectStore('clips');
    if(!d.objectStoreNames.contains('meta'))d.createObjectStore('meta');};
  r.onsuccess=e=>{db=e.target.result;res()};r.onerror=()=>rej(r.error);});}
function putClip(k,b){return new Promise((res,rej)=>{const t=db.transaction('clips','readwrite');
  t.objectStore('clips').put(b,k);t.oncomplete=res;t.onerror=()=>rej(t.error);});}
function getClip(k){return new Promise(res=>{const t=db.transaction('clips','readonly');
  const q=t.objectStore('clips').get(k);q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null);});}
function delClip(k){return new Promise(res=>{const t=db.transaction('clips','readwrite');
  t.objectStore('clips').delete(k);t.oncomplete=res;t.onerror=res;});}
function getMeta(k){return new Promise(res=>{try{const t=db.transaction('meta','readonly');const q=t.objectStore('meta').get(k);q.onsuccess=()=>res(q.result===undefined?null:q.result);q.onerror=()=>res(null);}catch(e){res(null)}});}
function putMeta(k,v){return new Promise(res=>{try{const t=db.transaction('meta','readwrite');t.objectStore('meta').put(v,k);t.oncomplete=res;t.onerror=res;}catch(e){res()}});}
function storeKeys(s){return new Promise(res=>{const t=db.transaction(s,'readonly');
  const q=t.objectStore(s).getAllKeys();q.onsuccess=()=>res(q.result||[]);q.onerror=()=>res([]);});}

/* A stored clip counts as a take only if it was recorded for the take's CURRENT words.
   Stamped clips ('said:<key>') compare the stamp; an unstamped clip comes from the 2026-10-12
   sheet and is stale when that sheet's words differed (w.ls). Stale clips move to meta
   'superseded:<key>:<ms>' and leave with "Export all" (folder superseded/). */
async function setAsideStale(){
  let n=0;
  for(const w of WORDS){
    const b=await getClip(w.key); if(!b) continue;
    const said=await getMeta('said:'+w.key);
    const stale = said==null ? !!w.ls : said!==w.say;
    if(stale){ await putMeta('superseded:'+w.key+':'+Date.now(), {blob:b, said:said||'(sheet of 2026-10-12)'});
      await delClip(w.key); n++; }
  }
  return n;
}

/* The key rename (2026-10-20, spec §12): a clip stored under a card's old key (an A2-list id, a
   three-digit base key, a sentence id, and their '_s' sentence takes) MOVES to its new key, with its 'said:' stamp; a
   'migrated:<old>' meta records the move. If a clip already exists under the new key (recorded
   after the rename) the old one is set aside as 'superseded:<old>:<ms>' and leaves with Export all
   under its new name. Nothing is dropped (the superseded rule). Runs before setAsideStale(). */
async function migrateKeys(){
  let moved=0, aside=0;
  for(const k of await storeKeys('clips')){
    const nk=KEY_MAP[k]; if(!nk||nk===k) continue;
    const b=await getClip(k); if(!b) continue;
    const said=await getMeta('said:'+k);
    if(!(await getClip(nk))){
      await putClip(nk,b);
      if(!(await getClip(nk))) continue;               // write not confirmed: leave the old clip alone
      if(said!=null) await putMeta('said:'+nk,said);
      await putMeta('migrated:'+k,{to:nk,at:Date.now(),said:said});
      await delClip(k); moved++;
    } else {
      await putMeta('superseded:'+k+':'+Date.now(),{blob:b,said:said||'(recorded under the old key '+k+')',to:nk});
      await putMeta('migrated:'+k,{to:nk,at:Date.now(),superseded:true});
      await delClip(k); aside++;
    }
  }
  const ex=(await getMeta('exported'))||[];
  const ex2=[...new Set(ex.map(k=>KEY_MAP[k]||k))];
  if(ex2.length!==ex.length||ex2.some((k,i)=>k!==ex[i])) await putMeta('exported',ex2);
  return {moved,aside};
}

/* ---------- recording ---------- */
let stream,rec,chunks=[],MIME='',idx=0,done=new Set();
const POS={}; WORDS.forEach((w,i)=>POS[w.key]=i);
function pickMime(){for(const m of ['audio/webm;codecs=opus','audio/webm','audio/mp4','audio/ogg']){
  if(window.MediaRecorder&&MediaRecorder.isTypeSupported(m))return m;}return '';}
function extFor(type){if(!type)return 'webm';if(type.includes('mp4')||type.includes('m4a')||type.includes('aac'))return 'm4a';
  if(type.includes('ogg'))return 'ogg';return 'webm';}

async function start(){
  const s=document.getElementById('setupStatus');
  try{stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:false}});}
  catch(e){s.textContent="Could not access the microphone: "+e.message;return;}
  MIME=pickMime();
  await openDB();
  const mig=await migrateKeys();
  const stale=await setAsideStale();
  const keys=await storeKeys('clips');
  done=new Set(keys.filter(k=>k in POS));
  const off=keys.length-done.size;
  document.getElementById('setup').style.display='none';
  document.getElementById('app').style.display='block';
  buildGrid();
  document.getElementById('storeInfo').textContent=
    (mig.moved?mig.moved+" takes carried over from the old card keys. ":"")+
    (mig.aside?mig.aside+" old-key clips had a newer take under the new key: set aside (in Export all). ":"")+
    (done.size?done.size+" takes already in this browser. ":"")+
    (stale?stale+" older clips were recorded for words that have since changed: set aside (in Export all). ":"")+
    (off?off+" clips for cards no longer on the list are kept (in Export all).":"");
  // jump to first not-yet-recorded take
  let f=WORDS.findIndex(w=>!done.has(w.key)); idx=f<0?0:f;
  render();
}

function startRec(){
  chunks=[]; rec=new MediaRecorder(stream, MIME?{mimeType:MIME}:undefined);
  const w=WORDS[idx];
  rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
  rec.onstop=async()=>{
    const blob=new Blob(chunks,{type:MIME||'audio/webm'});
    await putClip(w.key, blob); await putMeta('said:'+w.key, w.say); done.add(w.key);
    // a re-recorded take must leave with the next "Export new" even if its key went before
    const ex=new Set((await getMeta('exported'))||[]); if(ex.delete(w.key)) await putMeta('exported',[...ex]);
    updateCell(POS[w.key]); if(WORDS[idx]===w) setPlayer(blob); setCount();
    document.getElementById('status').textContent="Recorded ✓ ("+Math.round(blob.size/1024)+" KB)";
    recBtn.classList.remove('recording'); recBtn.textContent='● Re-record';
    if(document.getElementById('auto').checked&&WORDS[idx]===w) setTimeout(()=>go(1),350);
  };
  rec.start(); recBtn.classList.add('recording'); recBtn.textContent='■ Stop';
  // pre-roll: the mic is live but we ask for silence first, so every take begins
  // with clean lead-in and no plosive onset is clipped at capture.
  document.getElementById('status').textContent="… wait …";
  setTimeout(()=>{ if(rec&&rec.state==='recording')
      document.getElementById('status').textContent="SPEAK NOW"; }, 400);
}
function toggleRec(){ if(rec&&rec.state==='recording'){rec.stop();} else {startRec();} }

/* ---------- UI ---------- */
const recBtn=document.getElementById('recBtn'), playBtn=document.getElementById('playBtn'), player=document.getElementById('player');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function setPlayer(blob){ player.src=URL.createObjectURL(blob); player.style.display='block'; playBtn.disabled=false; }
async function render(){
  const w=WORDS[idx];
  let b='';
  if(w.level) b+='<span class="badge lv'+w.level+'">'+w.level+'</span>';
  if(w.status==='retake') b+='<span class="badge retake">re-take</span>';
  if(w.status==='replace-tts') b+='<span class="badge tts">replaces synthetic voice</span>';
  document.getElementById('badges').innerHTML=b;
  document.getElementById('numcat').textContent = "#"+w.number+"  ·  "+w.cat+"   ("+(idx+1)+" of "+WORDS.length+")";
  document.getElementById('lt').textContent=w.lt;
  document.getElementById('pron').textContent=w.pron||'';
  document.getElementById('en').textContent=w.en;
  document.getElementById('was').textContent=w.was?("the old take said: "+w.was+" (now different)"):'';
  const sc=w.script&&w.script.length?w.script:[{label:'',form:w.pron||w.lt}];
  document.getElementById('script').className='script'+(w.kind==='sentence'?' sentence':'');
  document.getElementById('script').innerHTML =
    '<span class="lead">'+(w.kind==='sentence'?'read the sentence once, naturally':'say all of this, one breath apart')+'</span>' +
    sc.map(f=>(f.label?'<span class="lab">'+esc(f.label)+'</span>':'')+'<b>'+esc(f.form)+'</b>')
      .join('<span class="sep">·</span>');
  recBtn.classList.remove('recording');
  const clip=await getClip(w.key);
  if(clip){ recBtn.textContent='● Re-record'; setPlayer(clip); document.getElementById('status').textContent="Recorded ✓"; }
  else { recBtn.textContent='● Record'; player.style.display='none'; playBtn.disabled=true; document.getElementById('status').textContent="Not recorded yet"; }
  document.querySelectorAll('.cell').forEach((c,i)=>c.classList.toggle('cur',i===idx));
  const curCell=document.querySelectorAll('.cell')[idx]; if(curCell) curCell.scrollIntoView({block:'nearest'});
}
function go(d){ idx=Math.min(WORDS.length-1,Math.max(0,idx+d)); render(); }
const NA1=WORDS.filter(w=>w.level==='A1').length;
function setCount(){ document.getElementById('count').textContent=done.size+" / "+WORDS.length;
  document.getElementById('progress').style.width=(100*done.size/WORDS.length)+"%";
  const a1=WORDS.filter(w=>w.level==='A1'&&done.has(w.key)).length;
  document.getElementById('exportInfo').textContent=done.size+" recorded, "+(WORDS.length-done.size)+" remaining"+
    (NA1?" · A1: "+a1+" of "+NA1:""); }
function buildGrid(){ const g=document.getElementById('grid'); g.innerHTML='';
  WORDS.forEach((w,i)=>{ const c=document.createElement('div'); c.className='cell'+(done.has(w.key)?' done':'');
    c.textContent=w.n||(i+1); c.title=w.key+' '+w.lt; c.onclick=()=>{idx=i;render();}; g.appendChild(c); });
  setCount(); }
function updateCell(i){ const c=document.querySelectorAll('.cell')[i]; if(c)c.classList.add('done'); setCount(); }

document.getElementById('start').onclick=start;
recBtn.onclick=toggleRec;
playBtn.onclick=()=>{player.currentTime=0;player.play();};
document.getElementById('next').onclick=()=>go(1);
document.getElementById('prev').onclick=()=>go(-1);
document.addEventListener('keydown',e=>{
  if(document.getElementById('app').style.display==='none')return;
  if(e.target&&e.target.tagName==='INPUT')return;
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
    const lh=[].concat(u32(0x04034b50),u16(20),u16(0x0800),u16(0),u16(dt),u16(dd),u32(crc),u32(sz),u32(sz),u16(nb.length),u16(0));
    parts.push(new Uint8Array(lh),nb,f.data);
    const ch=[].concat(u32(0x02014b50),u16(20),u16(20),u16(0x0800),u16(0),u16(dt),u16(dd),u32(crc),u32(sz),u32(sz),u16(nb.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(offset));
    central.push(new Uint8Array(ch),nb); offset+=lh.length+nb.length+sz; }
  let cs=0; for(const c of central) cs+=c.length;
  const eo=[].concat(u32(0x06054b50),u16(0),u16(0),u16(files.length),u16(files.length),u32(cs),u32(offset),u16(0));
  return new Blob([...parts,...central,new Uint8Array(eo)],{type:'application/zip'});
}
document.getElementById('jumpBtn').onclick=()=>{const n=parseInt(document.getElementById('jumpTo').value,10); if(n>=1&&n<=WORDS.length){idx=n-1;render();}};
const tsv=s=>String(s==null?'':s).replace(/[\t\n\r]/g,' ');
async function doExport(onlyNew){
  const info=document.getElementById('exportInfo'); info.textContent="Packing…";
  const exported=new Set((await getMeta('exported'))||[]);
  const files=[]; const man=["key\tdest\tlevel\tstatus\tsaid\tenglish\tfile"]; const shipped=[];
  for(const w of WORDS){ if(onlyNew&&exported.has(w.key))continue; const b=await getClip(w.key); if(!b)continue; shipped.push(w.key);
    const ext=extFor(b.type), name=w.key+"."+ext;
    files.push({name, data:new Uint8Array(await b.arrayBuffer())});
    man.push([w.key,w.dest,w.level,w.status,(await getMeta('said:'+w.key))||w.say,w.en,name].map(tsv).join("\t")); }
  if(!onlyNew){
    // everything else in this browser: clips for cards no longer on the list, and set-aside stale clips
    for(const k of await storeKeys('clips')){ if(k in POS) continue; const b=await getClip(k); if(!b) continue;
      const name="off_list/"+k+"."+extFor(b.type); files.push({name,data:new Uint8Array(await b.arrayBuffer())});
      man.push([k,'','','off-list',(await getMeta('said:'+k))||'','',name].map(tsv).join("\t")); }
    for(const mk of await storeKeys('meta')){ if(typeof mk!=='string'||!mk.startsWith('superseded:')) continue;
      const v=await getMeta(mk); if(!v||!v.blob) continue; const p=mk.split(':'); const sk=KEY_MAP[p[1]]||p[1];
      const name="superseded/"+sk+"."+p[2]+"."+extFor(v.blob.type); files.push({name,data:new Uint8Array(await v.blob.arrayBuffer())});
      man.push([sk,'','','superseded',v.said||'','',name].map(tsv).join("\t")); }
  }
  if(!files.length){info.textContent=onlyNew?"Nothing new since the last export.":"Nothing recorded yet.";return;}
  files.push({name:"manifest.tsv", data:new TextEncoder().encode(man.join("\n")+"\n")});
  const stamp=new Date().toISOString().replace(/[:T]/g,'-').slice(0,16);
  const blob=makeZip(files), url=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=url; a.download="lt_"+SHEET_ID.split('_')[0]+"_takes_"+stamp+(onlyNew?"_batch":"_all")+".zip"; a.click();
  for(const k of shipped) exported.add(k); await putMeta('exported',[...exported]);
  info.textContent="Exported "+(files.length-1)+" clips ("+exported.size+" exported in all).";
}
document.getElementById('export').onclick=()=>doExport(false);
document.getElementById('exportNew').onclick=()=>doExport(true);
</script>
</body></html>"""


def write_html(words, sheet_id, out, key_map=None):
    html = (TEMPLATE.replace("__WORDS__", json.dumps(words, ensure_ascii=False))
                    .replace("__KEY_MAP__", json.dumps(key_map or {}, ensure_ascii=False, separators=(",", ":")))
                    .replace("__SHEET_ID__", sheet_id))
    open(out, "w", encoding="utf-8").write(html)
    return len(html)


def main(argv):
    level = argv[1] if len(argv) > 1 else ""
    only_new = len(argv) > 2 and argv[2].lower() == "new"
    if level.upper() == "A2":
        takes, stats, warnings = deck_takes()
        write_list(takes)
        fields = ("key", "number", "lt", "en", "pron", "cat", "kind", "level",
                  "status", "was", "say", "script", "dest", "n")
        words = []
        for t in takes:
            w = {k: t[k] for k in fields}
            if t["legacy_stale"]:
                w["ls"] = 1          # a clip from the 2026-10-12 sheet is stale for this take
            words.append(w)
        kmap = key_map_for_page()
        size = write_html(words, DECK_SHEET_ID, "recorder_A2.html", kmap)
        print(f"wrote recorder_A2.html ({size // 1024} KB) + {LIST_OUT}: {len(takes)} takes, "
              f"IndexedDB lt_recorder_{DECK_SHEET_ID}; key map {len(kmap)} old take keys")
        for lv in ("A1", "A2"):
            parts = {s: n for (l, s), n in stats.items() if l == lv}
            print(f"  {lv}: {sum(parts.values())}  " + ", ".join(f"{s} {n}" for s, n in sorted(parts.items())))
        print(f"  kinds: word {sum(1 for t in takes if t['kind'] == 'word')}, "
              f"example sentence {sum(1 for t in takes if t['key'].endswith('_s'))}, "
              f"sentence card {sum(1 for t in takes if t['kind'] == 'sentence' and not t['key'].endswith('_s'))}")
        for lv in ("A1",):
            a = [t for t in takes if t["level"] == lv]
            print(f"  {lv} takes by kind: word {sum(1 for t in a if t['kind'] == 'word')}, "
                  f"example sentence {sum(1 for t in a if t['key'].endswith('_s'))}, "
                  f"sentence card {sum(1 for t in a if t['kind'] == 'sentence' and not t['key'].endswith('_s'))}")
        for w in warnings:
            print("  warning:", w)
        return
    words = legacy_words(level, only_new)
    sheet_id = (level or "all") + ("_new" if only_new else "") + "_" + \
        hashlib.md5(",".join(w["key"] for w in words).encode()).hexdigest()[:8]
    out = "recorder_" + (level or "all") + ("_new" if only_new else "") + ".html"
    size = write_html(words, sheet_id, out)
    print(f"wrote {out} — {len(words)} words, {size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv)
