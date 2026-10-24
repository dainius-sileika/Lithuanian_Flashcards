# -*- coding: utf-8 -*-
"""Historical six-render test (a2_build/historical/implementation/test_plan.csv, 2026-10-18).
Builds each test card's production prompt (deck_builder.build_call / a2_adapter.build_call_a2,
which now carry precedent= / likeness= / flag="emblem") and renders it into THIS folder, so the
shipped pictures (out_deck_f62, out_deck_a2) stay untouched until the owner passes the test.
A previous render moves to _rerolled/<key>.r<n>.png. test_ledger.csv records prompt, likeness
(person, period) and any API refusal.
    timeout 170 python3 a2_build/historical/test/render_test.py [KEY ...]     (default: all six)"""
import base64, csv, contextlib, io, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
os.chdir(ROOT); sys.path[:0] = [ROOT, os.path.join(ROOT, "out_deck_a2")]
with contextlib.redirect_stdout(io.StringIO()):
    import go_generator as g, deck_builder as db, a2_adapter as A, historical as H
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
TESTS = {r["key"]: r for r in csv.DictReader(open("a2_build/historical/implementation/test_plan.csv", encoding="utf-8"))}
keys = sys.argv[1:] or list(TESTS)
with contextlib.redirect_stdout(io.StringIO()):
    rows = db.load_rows(db.WORDLIST); work, _ = db.eligible(rows); db.prepare_settings(work)
    a2rows, staging = A.load_rows()
P = {}
for key, r, cls in work:
    if key in keys:
        kw = db.build_call(key, r, cls); kw.pop("filename", None); P[key] = g.build_prompt(backend="openai", **kw)
for r in a2rows:
    if r["id"] in keys:
        kw, cls = A.build_call_a2(r, staging); kw.pop("filename", None); P[r["id"]] = g.build_prompt(backend="openai", **kw)
LA = json.load(open("a2_build/historical/implementation/likeness_args.json", encoding="utf-8"))["cards"]
client = OpenAI(timeout=165, max_retries=0)


def one(key):
    t = time.time(); dest = os.path.join(HERE, key + ".png")
    try:
        r = client.images.generate(model=g.OPENAI_MODEL, prompt=P[key], size="1536x1024", quality=g.OPENAI_QUALITY, n=1)
    except Exception as e:
        return key, "ERR " + type(e).__name__ + ": " + str(e)[:300], round(time.time() - t)
    if os.path.exists(dest):
        os.makedirs(os.path.join(HERE, "_rerolled"), exist_ok=True); n = 1
        while os.path.exists(os.path.join(HERE, "_rerolled", f"{key}.r{n}.png")):
            n += 1
        os.replace(dest, os.path.join(HERE, "_rerolled", f"{key}.r{n}.png"))
    open(dest, "wb").write(base64.b64decode(r.data[0].b64_json))
    return key, "OK", round(time.time() - t)


with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, [k for k in keys if k in P]))
with open(os.path.join(HERE, "test_ledger.csv"), "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for key, status, s in res:
        lk = "; ".join(f"{x['name']} ({x['period']})" for x in LA.get(key, {}).get("likeness", []))
        w.writerow([time.strftime("%Y-%m-%d %H:%M"), TESTS[key]["test"], key, f"openai/{g.OPENAI_MODEL}", status, s, lk, P[key]])
        print(TESTS[key]["test"], key, status, s, "s", flush=True)
