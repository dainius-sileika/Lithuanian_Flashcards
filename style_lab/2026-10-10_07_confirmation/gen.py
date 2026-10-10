"""Confirmation run for F5/F5D (Fable, 2026-10-10). Arms: A = gpt-image-2 text-only; B = + 3 reference masters
(images.edit); C = Sunburst. Per-card staging notes go right after the subject sentence. Resumable.
usage: python gen.py [BUDGET_S] [WORKERS] [PLANFILE]"""
import csv, json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.getcwd()); import go_generator as g
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI(); csv.field_size_limit(10**7)
D = "style_lab/2026-10-10_07_confirmation"; OUT = f"{D}/img"
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 120; W = int(sys.argv[2]) if len(sys.argv) > 2 else 7
plan = json.load(open(sys.argv[3] if len(sys.argv) > 3 else f"{D}/plan.json"))
P = {x["id"]: x for x in json.load(open("style_lab/2026-10-10_06_blind_survey/results/f5_candidates.json"))["candidates"]}
P.update({x["id"]: x for x in plan.get("extra_prompts", [])})
REFS = "style_lab/2026-10-10_04_levers_A_B/style_refs"
REFNOTE = ("The attached images are pages from the same manual. Use them only as references for layout, card frame "
           "and legibility of the subject; follow the written description below for colour, paper and people. "
           "Draw a new subject and composition of your own. The new page: ")
ledger = {r["key"]: r["prompt"] for r in csv.DictReader(open("out_deck/ledger.csv", encoding="utf-8"))}
def build(img):
    p = ledger[img["card"]]; pr = P[img["prompt"]]
    p = pr["lead"] + p[len(g.CONCEPT_LEAD):] + " " + pr["suffix"]
    note = plan["staging"].get(img["card"])
    if note:
        i = p.index("Subject:"); j = p.index(". ", i) + 2
        p = p[:j] + note + " " + p[j:]
    return p
todo = [i for i in plan["images"] if not os.path.exists(f"{OUT}/{i['vid']}.png")]
print(len(plan["images"]), "planned,", len(todo), "to do")
t0 = time.time(); lock = threading.Lock(); log = open(f"{D}/gen_log.jsonl", "a")
def run(img):
    if time.time() - t0 > BUDGET: return
    p = build(img)
    for a in range(3):
        try:
            t = time.time()
            if img["refs"]:
                refs = [open(f"{REFS}/{k}.png", "rb") for k in ("024_miestas", "036_mokykla", "041_klubas")]
                r = c.images.edit(model=img["model"], image=refs, prompt=REFNOTE + p, size="1536x1024", quality="medium", n=1)
            else:
                r = c.images.generate(model=img["model"], prompt=p, size="1536x1024", quality="medium", n=1)
            open(f"{OUT}/{img['vid']}.png", "wb").write(base64.b64decode(r.data[0].b64_json))
            u = r.usage.model_dump() if getattr(r, "usage", None) else None
            with lock: log.write(json.dumps({**img, "s": round(time.time()-t), "usage": u, "prompt_text": p}) + "\n"); log.flush(); print("OK", img["vid"])
            return
        except Exception as e:
            with lock: print("RETRY" if a < 2 else "ERR", img["vid"], str(e)[:200])
            time.sleep(8 * (a + 1))
with ThreadPoolExecutor(W) as ex: list(ex.map(run, todo))
print("remaining", len([i for i in plan["images"] if not os.path.exists(f"{OUT}/{i['vid']}.png")]))
