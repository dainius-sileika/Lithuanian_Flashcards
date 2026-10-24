"""Bubble-free situation renders (2026-10-17, a2_build/RESTAGE_PROPOSAL.md + PILOT_24.md):
every restaged card of situations.py (generated from a2_build/restage_bubbles.csv) drawn
by gen_phrases.build_situation_call -> go_generator.build_prompt(situation=True) on the
production model (gpt-image-2.5-sunburst, medium, 1536x1024) into out_phrases_v3/<id>.png.
374 galvoti goes through its own A1 production path (deck_builder.build_call, which now
passes situation=True for SITUATION_ROWS) and is written as out_phrases_v3/0223_galvoti.png.
The bubble renders in out_phrases/, out_phrases_a2/ and out_deck_f62/0223_galvoti.png are
NOT touched; they move to _superseded/ only after the owner passes the pilot.

    python out_phrases_v3/gen.py 0 0 --plan                                # plan.json only
    ONLY=0356_nieko_tokio,0099_nera_uz_ka timeout 178 python -u out_phrases_v3/gen.py 20 6  # chosen keys
    ONLY=pilot timeout 178 python -u out_phrases_v3/gen.py 20 6            # the 34 of PILOT_24.md
    REROLL=0356_nieko_tokio timeout 178 python -u out_phrases_v3/gen.py 20 2        # old png -> _rerolled/<key>.r<n>.png
    V3_OUT=out_phrases_v3/round2 ONLY=0274_kodel,... timeout 178 python -u out_phrases_v3/gen.py 100 4   # pilot round 2

Append-only ledger/gen_log are kept in ~/a2_work/v3_* (outside the Proton-synced tree) and
copied in once per call. Last ledger row per key = current picture.

Layout since the tidy of 2026-10-24 (spec §13, INDEX.md): this driver lives in media/generation/out_phrases_v3/
with its ledger, plan and QA sheets (round 2's under round2/); pictures go to media/images/<key>.png (the one
current picture per card, where build_apkg looks) and a re-roll moves the old picture to
media/images/_history/<batch>/_rerolled/<key>.r<n>.png. V3_BATCH=out_phrases_v3/round2 (was V3_OUT) selects
round 2's ledger, plan and history folder. Run it from the project root as before:
    python3 media/generation/out_phrases_v3/gen.py ...
"""
import csv, json, os, sys, time, base64, threading
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))              # media/generation/out_phrases_v3
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import go_generator as g, deck_builder as db, gen_phrases as gp
from situations import SITUATIONS, BY_ID, renders

# V3_BATCH=out_phrases_v3/round2 (pilot round 2, 2026-10-17; was V3_OUT before the tidy of 2026-10-24):
# round 2 keeps its own ledger, plan and _history folder and never writes over round 1's records; its
# append-only logs are ~/a2_work/v3_round2_* (TAG below). Pictures of both rounds go to media/images/.
BATCH = os.environ.get("V3_BATCH", os.environ.get("V3_OUT", "out_phrases_v3"))
OUT = "media/images"                                   # the current pictures (build_apkg.IMAGE_DIR)
HIST = f"media/images/_history/{BATCH}/_rerolled"       # previous versions, <key>.r<n>.png
META = f"media/generation/{BATCH}"                      # plan.json, ledger.csv, gen_log.jsonl
TAG = "v3" if BATCH == "out_phrases_v3" else "v3_" + os.path.basename(BATCH.rstrip("/"))
MODEL = g.OPENAI_MODEL
SIZE, QUALITY = "1536x1024", g.OPENAI_QUALITY
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 15
W = int(sys.argv[2]) if len(sys.argv) > 2 else 6
REROLL = [k for k in os.environ.get("REROLL", "").split(",") if k]
PILOT = ("0356_nieko_tokio 0099_nera_uz_ka 0231_kas_tai 0242_kas_tas_zmogus 0110_kur_yra_tualetas 0269_nekalbu_lietuviskai 0565_prasom_uzrasyti 1058_kaip_lietuviskai 0247_man_reikia_pagalbos 0647_iskvieskite_gydytoja 0291_kur_galiu_rasti "
         "0855_kiek_kainuoja_bilietas 0021_labas 0088_sveiki 0077_labas_rytas 0036_laba_diena 0081_labas_vakaras 0025_aciu 0103_atsiprasau 0169_atleiskite 0065_kiek_kainuoja 0755_sekmes "
         "0768_geros_keliones 0191_ar_galite_man_padeti 0215_kas 0204_kur 0428_kada 0150_kaip 0274_kodel 0347_kiek 0238_koks 0217_kuris 0138_kieno "
         "0223_galvoti").split()
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
os.makedirs(OUT, exist_ok=True); os.makedirs(META, exist_ok=True)
json.dump({"model": MODEL, "size": SIZE, "quality": QUALITY, "n": len(jobs), "pilot": PILOT, "jobs": jobs},
          open(f"{META}/plan.json", "w"), indent=1, ensure_ascii=False)
if "--plan" in sys.argv:
    print(len(jobs), "planned; plan.json written"); sys.exit()

os.makedirs(OUT, exist_ok=True)
if REROLL:
    os.makedirs(HIST, exist_ok=True)
    for k in REROLL:
        p = f"{OUT}/{k}.png"
        if os.path.exists(p):
            n = 1
            while os.path.exists(f"{HIST}/{k}.r{n}.png"): n += 1
            os.replace(p, f"{HIST}/{k}.r{n}.png")
    todo = [j for j in jobs if j["key"] in REROLL]
else:
    todo = [j for j in jobs if (not ONLY or j["key"] in ONLY) and not os.path.exists(f"{OUT}/{j['key']}.png")]
print(len(jobs), "planned,", len(todo), "to do", flush=True)

from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI()
t0 = time.time(); lock = threading.Lock()
LOCAL = os.path.expanduser("~/a2_work"); os.makedirs(LOCAL, exist_ok=True)
log = open(f"{LOCAL}/{TAG}_gen_log.jsonl", "a")
lf, lw = g.GOGenerator.open_ledger(f"{LOCAL}/{TAG}_ledger.csv")


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
for name in (f"{TAG}_ledger.csv", f"{TAG}_gen_log.jsonl"):
    for w_try in range(6):
        try:
            shutil.copyfile(f"{LOCAL}/{name}", f"{META}/{name.replace(TAG + '_', '')}"); break
        except OSError:
            time.sleep(2 * (w_try + 1))
left = [j["key"] for j in jobs if (not ONLY or j["key"] in ONLY) and not os.path.exists(f"{OUT}/{j['key']}.png")]
print("remaining", len(left), flush=True)
