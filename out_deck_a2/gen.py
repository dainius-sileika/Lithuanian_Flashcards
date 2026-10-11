"""A2 picture cards (2026-10-11): every IMG row of a2_build/a2_wordlist.csv drawn by
the production prompt path (a2_adapter.build_call_a2 -> go_generator.build_prompt,
the A2 twin of deck_builder.build_call) on the production model
(gpt-image-2.5-sunburst, medium, 1536x1024) into out_deck_a2/<id>.png, where
build_apkg.find_a2_image looks (A2_IMAGE_DIRS).

Resumable: a card is done when out_deck_f62/<key>.png exists. Each device call is
capped at ~180 s, so jobs launch only in the first BUDGET seconds; repeat the call
until "remaining 0".

    timeout 178 python -u out_deck_a2/gen.py 15 30          # launch window, workers
    python out_deck_a2/gen.py 0 0 --plan                     # (re)write plan + cards.csv only
    REROLL=key1,key2 timeout 178 python -u out_deck_a2/gen.py 15 10   # re-roll: moves old png to _rerolled/

Ledger: out_deck_f62/ledger.csv, same columns as deck_builder (key, subject, seed,
backend, size, file, prompt); re-rolls append a new row, so the LAST row per key is
the current picture. gen_log.jsonl records seconds and token usage per image.
"""
import csv, json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import go_generator as g
sys.path.insert(0, os.path.join(ROOT, "out_deck_a2")); import a2_adapter as A
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())

OUT = "out_deck_a2"
MODEL = g.OPENAI_MODEL          # gpt-image-2.5-sunburst
SIZE, QUALITY = "1536x1024", g.OPENAI_QUALITY
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 15
W = int(sys.argv[2]) if len(sys.argv) > 2 else 30
REROLL = [k for k in os.environ.get("REROLL", "").split(",") if k]

rows, staging = A.load_rows(); skipped = []
jobs = []
for r in rows:
    key = r["id"]
    kw, cls = A.build_call_a2(r, staging); kw.pop("filename")
    jobs.append({"key": key, "n": key, "cls": cls, "subject": kw["subject"], "phase": r["phase"],
                 "lt": r["lithuanian_TARGET"], "en": r["english"], "lt_pron": r["lt_pron"],
                 "gender": r["gender"], "category": r["category"], "staged": key in staging,
                 "composition": kw.get("composition"), "setting": kw.get("setting", ""),
                 "exact_text": kw.get("exact_text", ""),
                 "prompt": g.build_prompt(backend="openai", **kw)})
json.dump({"model": MODEL, "size": SIZE, "quality": QUALITY, "n": len(jobs), "skipped": skipped,
           "card_text_rewrites": A.CARD_TEXT_FIXES, "jobs": jobs}, open(f"{OUT}/plan.json", "w"), indent=1, ensure_ascii=False)
with open(f"{OUT}/cards.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["key", "lithuanian", "english", "lt_pron", "gender", "number", "category", "image_file"])
    for j in jobs:
        w.writerow([j["key"], j["lt"], j["en"], j["lt_pron"], j["gender"], j["n"], j["category"], j["key"] + ".png"])
if "--plan" in sys.argv:
    print(len(jobs), "planned; plan.json + cards.csv written"); sys.exit()

if REROLL:
    os.makedirs(f"{OUT}/_rerolled", exist_ok=True)
    for k in REROLL:
        p = f"{OUT}/{k}.png"
        if os.path.exists(p):
            i = 1
            while os.path.exists(f"{OUT}/_rerolled/{k}.r{i}.png"): i += 1
            os.replace(p, f"{OUT}/_rerolled/{k}.r{i}.png")
    todo = [j for j in jobs if j["key"] in REROLL]
else:
    todo = [j for j in jobs if not os.path.exists(f"{OUT}/{j['key']}.png")]
print(len(jobs), "planned,", len(todo), "to do", flush=True)

c = OpenAI()
t0 = time.time(); lock = threading.Lock()
# append-only files are written OUTSIDE the Proton-synced folder (Proton forks
# "(# Edit conflict ...)" copies and locks files with EDEADLK when a file is
# appended to while it syncs); they are copied into OUT once per call, below
LOCAL = os.path.expanduser("~/a2_work"); os.makedirs(LOCAL, exist_ok=True)
log = open(f"{LOCAL}/gen_log.jsonl", "a")
lf, lw = g.GOGenerator.open_ledger(f"{LOCAL}/ledger.csv")

def run(j):
    if time.time() - t0 > BUDGET:
        return
    for a in range(3):
        try:
            t = time.time()
            r = c.images.generate(model=MODEL, prompt=j["prompt"], size=SIZE, quality=QUALITY, n=1)
            data = base64.b64decode(r.data[0].b64_json)
            # Proton Drive throws EDEADLK ([Errno 35]) under many concurrent
            # writes; never re-call the API for a local write hiccup
            for w_try in range(8):
                try:
                    tmp = f"{OUT}/{j['key']}.tmp"
                    with open(tmp, "wb") as fh:
                        fh.write(data)
                    os.replace(tmp, f"{OUT}/{j['key']}.png")
                    break
                except OSError as oe:
                    if w_try == 7:
                        raise
                    time.sleep(1.5 * (w_try + 1))
            u = r.usage.model_dump() if getattr(r, "usage", None) else None
            with lock:
                lw.writerow([j["key"], j["subject"], "", f"openai/{MODEL}", SIZE, j["key"] + ".png", j["prompt"]]); lf.flush()
                log.write(json.dumps({"key": j["key"], "model": MODEL, "s": round(time.time() - t),
                                      "usage": u, "reroll": bool(REROLL), "t": time.strftime("%H:%M:%S")}) + "\n"); log.flush()
                print("OK", j["key"], round(time.time() - t), "s", flush=True)
            return
        except Exception as e:
            with lock:
                print("RETRY" if a < 2 else "ERR", j["key"], str(e)[:160], flush=True)
                log.write(json.dumps({"key": j["key"], "error": str(e)[:300], "t": time.strftime("%H:%M:%S")}) + "\n"); log.flush()
            if "moderation" in str(e).lower() or "safety" in str(e).lower():
                return
            time.sleep(8 * (a + 1))

with ThreadPoolExecutor(W) as ex:
    list(ex.map(run, todo))
lf.close(); log.close()
import shutil
for name in ("ledger.csv", "gen_log.jsonl"):
    for w_try in range(6):
        try:
            shutil.copyfile(f"{LOCAL}/{name}", f"{OUT}/{name}"); break
        except OSError:
            time.sleep(2 * (w_try + 1))
print("remaining", len([j for j in jobs if not os.path.exists(f"{OUT}/{j['key']}.png")]), flush=True)
