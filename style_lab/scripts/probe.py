"""Re-run shipped ledger prompts through another image model, for style probes.
usage: python _proto/probe.py KEY[,KEY...] [MODEL]   (default gpt-image-2)
Writes _proto/<MODEL>/<KEY>.png and appends usage to _proto/<MODEL>/probe.log."""
import csv, sys, os, base64, time, json
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI()
csv.field_size_limit(10**7)
keys = sys.argv[1].split(",")
model = sys.argv[2] if len(sys.argv) > 2 else "gpt-image-2"
out = f"_proto/{model}"
os.makedirs(out, exist_ok=True)
last = {}
for r in csv.DictReader(open("out_deck/ledger.csv", encoding="utf-8")):
    last[r["key"]] = r
log = open(f"{out}/probe.log", "a")
for k in keys:
    r = last[k]
    t = time.time()
    try:
        raw = c.images.with_raw_response.generate(model=model, prompt=r["prompt"],
                                                  size="1536x1024", quality="medium", n=1)
        resp = raw.parse()
        open(f"{out}/{k}.png", "wb").write(base64.b64decode(resp.data[0].b64_json))
        log.write(json.dumps({"key": k, "model": model, "ok": True, "s": round(time.time()-t),
                              "usage": getattr(resp, "usage", None) and resp.usage.model_dump()}) + "\n")
        print("OK", model, k, round(time.time()-t), "s")
    except Exception as e:
        log.write(json.dumps({"key": k, "model": model, "ok": False, "err": str(e)[:300]}) + "\n")
        print("ERR", model, k, str(e)[:300])
    log.flush()
