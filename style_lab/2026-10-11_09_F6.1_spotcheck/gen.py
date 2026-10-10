"""F6.1 production spot-check (2026-10-11): 30 cards x 2 models, built with the
PRODUCTION prompt path (deck_builder.build_call -> go_generator.build_prompt),
so what is judged here is exactly what a production run sends.
Strata (Fable, production_spec_F6_1.json model_decision): 10 multi-person /
scene, 10 single-figure verbs & persons, 10 objects / animals / clothing.
usage: python <D>/gen.py BUDGET_S WORKERS"""
import json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.getcwd())
import deck_builder as db, go_generator as g
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI()
D = "style_lab/2026-10-11_09_F6.1_spotcheck"; OUT = f"{D}/img"
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 150; W = int(sys.argv[2]) if len(sys.argv) > 2 else 8
STRATA = {
 "scene":  ["027_gatve", "036_mokykla", "046_teatras", "048_ligonine", "050_turgus", "034_ukis",
            "030_stotis", "363_dirbti", "426_statyti", "408_sokti"],
 "figure": ["367_begti", "118_policininkas", "083_tevas", "117_kunigas", "122_menininkas",
            "114_pacientas", "405_pjauti", "411_dainuoti", "430_maitinti", "368_vairuoti"],
 "object": ["005_karve", "008_arklys", "001_suo", "058_suknele", "064_batai", "059_kostiumas",
            "183_sriuba", "188_obuolys", "236_telefonas", "246_laikrodis"],
}
MODELS = {"G": "gpt-image-2", "S": "gpt-image-2.5-sunburst"}
rows = db.load_rows(db.WORDLIST); work, _ = db.eligible(rows); db.prepare_settings(work)
W_ = {k: (r, cls) for k, r, cls in work}
jobs = []
for stratum, keys in STRATA.items():
    for k in keys:
        r, cls = W_[k]
        kw = db.build_call(k, r, cls); kw.pop("filename")
        p = g.build_prompt(backend="openai", **kw)
        for m, model in MODELS.items():
            jobs.append({"vid": f"{m}_{k}", "card": k, "stratum": stratum, "model": model,
                         "composition": kw.get("composition"), "setting": kw.get("setting", ""), "prompt": p})
if not os.path.exists(f"{D}/plan.json"):
    json.dump({"strata": STRATA, "models": MODELS, "images": jobs}, open(f"{D}/plan.json", "w"), indent=1, ensure_ascii=False)
todo = [j for j in jobs if not os.path.exists(f"{OUT}/{j['vid']}.png")]
print(len(jobs), "planned,", len(todo), "to do")
t0 = time.time(); lock = threading.Lock(); log = open(f"{D}/gen_log.jsonl", "a")
def run(j):
    if time.time() - t0 > BUDGET: return
    for a in range(3):
        try:
            t = time.time()
            r = c.images.generate(model=j["model"], prompt=j["prompt"], size="1536x1024", quality="medium", n=1)
            open(f"{OUT}/{j['vid']}.png", "wb").write(base64.b64decode(r.data[0].b64_json))
            u = r.usage.model_dump() if getattr(r, "usage", None) else None
            with lock: log.write(json.dumps({"vid": j["vid"], "model": j["model"], "s": round(time.time()-t), "usage": u}) + "\n"); log.flush(); print("OK", j["vid"])
            return
        except Exception as e:
            with lock: print("RETRY" if a < 2 else "ERR", j["vid"], str(e)[:200])
            time.sleep(8 * (a + 1))
# Sunburst first (fast), then gpt-image-2
todo.sort(key=lambda j: j["model"] != MODELS["S"])
with ThreadPoolExecutor(W) as ex: list(ex.map(run, todo))
print("remaining", len([j for j in jobs if not os.path.exists(f"{OUT}/{j['vid']}.png")]))
