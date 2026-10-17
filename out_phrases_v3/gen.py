"""Bubble-free situation renders (2026-10-17, a2_build/RESTAGE_PROPOSAL.md + PILOT_24.md):
every restaged card of situations.py (generated from a2_build/restage_bubbles.csv) drawn
by gen_phrases.build_situation_call -> go_generator.build_prompt(situation=True) on the
production model (gpt-image-2.5-sunburst, medium, 1536x1024) into out_phrases_v3/<id>.png.
374 galvoti goes through its own A1 production path (deck_builder.build_call, which now
passes situation=True for SITUATION_ROWS) and is written as out_phrases_v3/374_galvoti.png.
The bubble renders in out_phrases/, out_phrases_a2/ and out_deck_f62/374_galvoti.png are
NOT touched; they move to _superseded/ only after the owner passes the pilot.

    python out_phrases_v3/gen.py 0 0 --plan                                # plan.json only
    ONLY=A2-0882,A2-0360 timeout 178 python -u out_phrases_v3/gen.py 20 6  # chosen keys
    ONLY=pilot timeout 178 python -u out_phrases_v3/gen.py 20 6            # the 34 of PILOT_24.md
    REROLL=A2-0882 timeout 178 python -u out_phrases_v3/gen.py 20 2        # old png -> _rerolled/<key>.r<n>.png

Append-only ledger/gen_log are kept in ~/a2_work/v3_* (outside the Proton-synced tree) and
copied in once per call. Last ledger row per key = current picture.
"""
import csv, json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import go_generator as g, deck_builder as db, gen_phrases as gp
from situations import SITUATIONS, BY_ID, renders

OUT = "out_phrases_v3"
MODEL = g.OPENAI_MODEL
SIZE, QUALITY = "1536x1024", g.OPENAI_QUALITY
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 15
W = int(sys.argv[2]) if len(sys.argv) > 2 else 6
REROLL = [k for k in os.environ.get("REROLL", "").split(",") if k]
PILOT = ("A2-0882 A2-0360 A2-0896 A2-0897 A2-0898 A2-0900 A2-0903 A2-0905 A2-0906 A2-0907 A2-0909 "
         "A2-0928 A2-0348 A2-0349 A2-0350 A2-0351 A2-0352 A2-0358 A2-0881 A2-0362 A2-0377 A2-0887 "
         "A2-0895 A2-0383 A2-0108 A2-0110 A2-0111 A2-0112 A2-0113 A2-0114 A2-0115 A2-0116 A2-0117 "
         "374_galvoti").split()
_only = os.environ.get("ONLY", "")
ONLY = PILOT if _only == "pilot" else [k for k in _only.split(",") if k]

# --- rows: the A2 list, the sentence cards, the A1 phrase pack, and 374 via deck_builder
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
sent = {r["id"]: r for r in csv.DictReader(open("a2_build/sentences/sentences.csv", encoding="utf-8")) if r.get("id")}
jobs = []
for en, s in SITUATIONS.items():
    if not renders(en):
        continue
    ids = s["ids"] or ["yes_no" if en == "Yes / no" else en]
    i = ids[0]
    if i == "374":
        rows = db.load_rows(db.WORDLIST); work, _ = db.eligible(rows); db.prepare_settings(work)
        key, r, cls = next(w for w in work if w[0].startswith("374_"))
        kw = db.build_call(key, r, cls)
        row = {"id": key, "english": r["english"], "lithuanian_TARGET": r["lithuanian_TARGET"]}
    else:
        row = dict(a2.get(i) or {})
        if i in sent:
            row = {"id": i, "english": sent[i]["en"], "lithuanian_TARGET": sent[i]["lt"].replace("{", "").replace("}", ""),
                   "card_text": sent[i].get("card_text", "")}
        row.setdefault("id", i); row.setdefault("english", en); row.setdefault("lithuanian_TARGET", s["lithuanian"])
        kw = gp.build_situation_call(row)
        key = row["id"]
    kw.pop("filename")
    jobs.append({"key": key, "en": en, "lt": row.get("lithuanian_TARGET", ""), "format": s["format"],
                 "staging": s["scene"], "cue": s["cue"], "confusables": s["confusables"],
                 "subject": kw["subject"], "prompt": g.build_prompt(backend="openai", **kw)})
os.makedirs(OUT, exist_ok=True)
json.dump({"model": MODEL, "size": SIZE, "quality": QUALITY, "n": len(jobs), "pilot": PILOT, "jobs": jobs},
          open(f"{OUT}/plan.json", "w"), indent=1, ensure_ascii=False)
if "--plan" in sys.argv:
    print(len(jobs), "planned; plan.json written"); sys.exit()

if REROLL:
    os.makedirs(f"{OUT}/_rerolled", exist_ok=True)
    for k in REROLL:
        p = f"{OUT}/{k}.png"
        if os.path.exists(p):
            n = 1
            while os.path.exists(f"{OUT}/_rerolled/{k}.r{n}.png"): n += 1
            os.replace(p, f"{OUT}/_rerolled/{k}.r{n}.png")
    todo = [j for j in jobs if j["key"] in REROLL]
else:
    todo = [j for j in jobs if (not ONLY or j["key"] in ONLY) and not os.path.exists(f"{OUT}/{j['key']}.png")]
print(len(jobs), "planned,", len(todo), "to do", flush=True)

from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI()
t0 = time.time(); lock = threading.Lock()
LOCAL = os.path.expanduser("~/a2_work"); os.makedirs(LOCAL, exist_ok=True)
log = open(f"{LOCAL}/v3_gen_log.jsonl", "a")
lf, lw = g.GOGenerator.open_ledger(f"{LOCAL}/v3_ledger.csv")


def run(j):
    if time.time() - t0 > BUDGET:
        return
    for a in range(3):
        try:
            t = time.time()
            r = c.images.generate(model=MODEL, prompt=j["prompt"], size=SIZE, quality=QUALITY, n=1)
            data = base64.b64decode(r.data[0].b64_json)
            for w_try in range(8):            # Proton EDEADLK: never re-call the API for a write hiccup
                try:
                    tmp = f"{OUT}/{j['key']}.tmp"
                    with open(tmp, "wb") as fh:
                        fh.write(data)
                    os.replace(tmp, f"{OUT}/{j['key']}.png")
                    break
                except OSError:
                    if w_try == 7:
                        raise
                    time.sleep(1.5 * (w_try + 1))
            u = r.usage.model_dump() if getattr(r, "usage", None) else None
            with lock:
                lw.writerow([j["key"], j["subject"], "", f"openai/{MODEL}", SIZE, j["key"] + ".png", j["prompt"]]); lf.flush()
                log.write(json.dumps({"key": j["key"], "model": MODEL, "s": round(time.time() - t), "usage": u,
                                      "reroll": bool(REROLL), "t": time.strftime("%H:%M:%S")}) + "\n"); log.flush()
                print("OK", j["key"], round(time.time() - t), "s", flush=True)
            return
        except Exception as e:
            with lock:
                print("RETRY" if a < 2 else "ERR", j["key"], str(e)[:160], flush=True)
                log.write(json.dumps({"key": j["key"], "error": str(e)[:300], "t": time.strftime("%H:%M:%S")}) + "\n"); log.flush()
            if any(x in str(e).lower() for x in ("moderation", "safety", "billing", "insufficient_quota")):
                return
            time.sleep(8 * (a + 1))


with ThreadPoolExecutor(W) as ex:
    list(ex.map(run, todo))
lf.close(); log.close()
import shutil
for name in ("v3_ledger.csv", "v3_gen_log.jsonl"):
    for w_try in range(6):
        try:
            shutil.copyfile(f"{LOCAL}/{name}", f"{OUT}/{name.replace('v3_', '')}"); break
        except OSError:
            time.sleep(2 * (w_try + 1))
left = [j["key"] for j in jobs if (not ONLY or j["key"] in ONLY) and not os.path.exists(f"{OUT}/{j['key']}.png")]
print("remaining", len(left), flush=True)
