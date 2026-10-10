"""Generate the survey's new images from survey_design.json (Fable, 2026-10-10).
Resumable; stops launching new jobs after BUDGET s. usage: python gen_new.py [BUDGET] [WORKERS]"""
import csv, json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.getcwd()); import go_generator as g
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI(); csv.field_size_limit(10**7)
D = "style_lab/2026-10-10_06_blind_survey"; OUT = f"{D}/new"; os.makedirs(OUT, exist_ok=True)
REFS = "style_lab/2026-10-10_04_levers_A_B/style_refs"
REFNOTE = ("The attached images are pages from the same manual. Use them only as style references: "
           "match their illustration style, linework, colouring, palette, printing texture, card frame, and the "
           "way people are drawn and dressed, so the new card looks like another page of the same 1981 "
           "publication. Draw a new subject and composition of your own. The new page: ")
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 120; WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 6
d = json.load(open(f"{D}/survey_design.json")); P = d["new_prompts"]
ledger = {r["key"]: r["prompt"] for r in csv.DictReader(open("out_deck/ledger.csv", encoding="utf-8"))}
def build(img):
    p = ledger[img["card"]]; assert p.startswith(g.CONCEPT_LEAD)
    if img["prompt"] != "shipped":
        pr = P[img["prompt"]]; p = pr["lead"] + p[len(g.CONCEPT_LEAD):] + (" " + pr["suffix"] if pr.get("suffix") else "")
    if img.get("subject_override"):
        i = p.index("Subject:"); j = p.index(". ", i) + 2
        p = p[:i] + img["subject_override"].rstrip() + " " + p[j:]
    return p
todo = [i for i in d["new_images"] if not os.path.exists(f"{OUT}/{i['vid']}.png")]
print(f"{len(d['new_images'])} new images, {len(todo)} to do")
t0 = time.time(); lock = threading.Lock(); log = open(f"{D}/gen_log.jsonl", "a")
def run(img):
    if time.time() - t0 > BUDGET: return
    p = build(img)
    for attempt in range(3):
        try:
            t = time.time()
            if img.get("references"):
                refs = [open(f"{REFS}/{k}.png", "rb") for k in img["references"]]
                r = c.images.edit(model=img["model"], image=refs, prompt=REFNOTE + p, size="1536x1024", quality=img["quality"], n=1)
            else:
                r = c.images.generate(model=img["model"], prompt=p, size="1536x1024", quality=img["quality"], n=1)
            open(f"{OUT}/{img['vid']}.png", "wb").write(base64.b64decode(r.data[0].b64_json))
            u = r.usage.model_dump() if getattr(r, "usage", None) else None
            with lock:
                log.write(json.dumps({**img, "s": round(time.time()-t), "usage": u, "prompt_text": p}) + "\n"); log.flush()
                print("OK", img["vid"], round(time.time()-t), "s")
            return
        except Exception as e:
            with lock: print("RETRY" if attempt < 2 else "ERR", img["vid"], str(e)[:200])
            time.sleep(8 * (attempt + 1))
with ThreadPoolExecutor(WORKERS) as ex: list(ex.map(run, todo))
print("remaining", len([i for i in d["new_images"] if not os.path.exists(f"{OUT}/{i['vid']}.png")]), "after", round(time.time()-t0), "s")
