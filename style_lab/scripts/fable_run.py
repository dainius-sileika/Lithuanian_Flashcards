"""Run Fable's style candidates (fable_brief/fable_style_candidates.json) over the
15-card test set. Resumable: skips images that exist. Stops launching new jobs
after BUDGET seconds so each call fits the shell's time limit.
usage: python _proto/fable_run.py [BUDGET_S] [WORKERS]"""
import csv, json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
sys.path.insert(0, os.getcwd()); import go_generator as g
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI(); csv.field_size_limit(10**7)
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 120
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
cands = {x["id"]: x for x in json.load(open("_proto/fable_brief/fable_style_candidates.json"))["candidates"]}
keys = open("_proto/fable_brief/test_keys.txt").read().split()
ledger = {r["key"]: r["prompt"] for r in csv.DictReader(open("out_deck/ledger.csv", encoding="utf-8"))}
jobs = []
for model in ["gpt-image-2.5-sunburst", "gpt-image-2"]:
    for cid in ["F1", "F2", "F3"]:
        for k in keys: jobs.append((cid, model, "medium", k))
for k in keys: jobs.append(("F1", "gpt-image-2.5-sunburst", "low", k))
def outpath(cid, model, q, k): return f"_proto/style_fable/{cid}_{model}_{q}/{k}.png"
todo = [j for j in jobs if not os.path.exists(outpath(*j))]
print(f"{len(jobs)} jobs, {len(todo)} to do")
t0 = time.time(); lock = threading.Lock(); log = open("_proto/style_fable_log.jsonl", "a")
def run(j):
    cid, model, q, k = j
    if time.time() - t0 > BUDGET: return
    p = ledger[k]; assert p.startswith(g.CONCEPT_LEAD), k
    cand = cands[cid]
    p = cand["lead"] + p[len(g.CONCEPT_LEAD):] + ((" " + cand["suffix"]) if cand.get("suffix") else "")
    for attempt in range(3):
        try:
            t = time.time()
            r = c.images.generate(model=model, prompt=p, size="1536x1024", quality=q, n=1)
            os.makedirs(os.path.dirname(outpath(*j)), exist_ok=True)
            open(outpath(*j), "wb").write(base64.b64decode(r.data[0].b64_json))
            u = r.usage.model_dump() if getattr(r, "usage", None) else None
            with lock:
                log.write(json.dumps({"cid": cid, "model": model, "q": q, "key": k, "s": round(time.time()-t), "usage": u}) + "\n"); log.flush()
                print("OK", cid, model, q, k, round(time.time()-t), "s")
            return
        except Exception as e:
            msg = str(e)[:200]
            with lock: print("RETRY" if attempt < 2 else "ERR", cid, model, q, k, msg)
            time.sleep(10 * (attempt + 1))
with ThreadPoolExecutor(WORKERS) as ex: list(ex.map(run, todo))
left = [j for j in jobs if not os.path.exists(outpath(*j))]
print(f"done this call in {round(time.time()-t0)} s; remaining {len(left)}")
