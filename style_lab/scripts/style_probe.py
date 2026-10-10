"""Style-drift probe (2026-10-10). Two levers against the new models' drift toward
detailed naturalism: A = GO register paragraph replacing the 'botanical plate /
realistic proportions' opening; B = the owner's three favourite 1.5 masters sent
as style references. usage: python _proto/style_probe.py KEY[,KEY] MODEL A|B|AB"""
import csv, sys, os, base64, time, json
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
c = OpenAI(); csv.field_size_limit(10**7)
keys, model, lever = sys.argv[1].split(","), sys.argv[2], sys.argv[3]
REGISTER = (
 "An illustration for a Lithuanian-language learning flashcard, printed as a page of a "
 "fictional 1981 Lithuanian civil-defence (GO) instructional manual. Draw it the way those "
 "Voenizdat wall posters were drawn: economical flat gouache with confident, even black "
 "outlines; each object filled with one or two flat matte colours and a single simple shadow "
 "tone; simplified, legible shapes with little interior detail, as if the illustrator had ten "
 "minutes per figure; generous empty cream paper around everything; four-colour offset "
 "lithography on cheap absorbent paper with faint halftone dots and slightly soft colour "
 "registration; a restrained palette of blue-grey teal, tan, dun and charcoal with a sparing "
 "brick-orange accent. Figures are generic types, not individuals: only as many as the scene "
 "needs, drawn with simple standard faces and calm neutral expressions, like the anonymous "
 "citizens of a procedure diagram. Period appearance, Lithuania 1981: men with short "
 "side-parted hair in plain wool jackets, flat cloth caps and wide-collared shirts; women with "
 "short permed hair or headscarves, knee-length A-line dresses and mid-calf coats; children in "
 "school uniform; boxy Zhiguli and Moskvich cars, Ikarus buses.")
REFNOTE = ("The attached images are pages from the same manual. Use them only as style "
           "references: match their illustration style, linework, flat colouring, palette, "
           "printing texture, card frame, and the way people are drawn and dressed, so the new "
           "card looks like another page of the same 1981 publication. Do not copy their "
           "subjects or compositions. The new page: ")
last = {r["key"]: r for r in csv.DictReader(open("out_deck/ledger.csv", encoding="utf-8"))}
out = f"_proto/style_probe/{model}_{lever}"; os.makedirs(out, exist_ok=True)
log = open("_proto/style_probe/probe.log", "a")
for k in keys:
    p = last[k]["prompt"]
    if "A" in lever:
        cut = p.index("aged cream-paper offset-print feel.") + len("aged cream-paper offset-print feel.")
        p = REGISTER + p[cut:]
    t = time.time()
    try:
        if "B" in lever:
            refs = [open(f"_proto/style_refs/{f}", "rb") for f in sorted(os.listdir("_proto/style_refs"))]
            raw = c.images.with_raw_response.edit(model=model, image=refs, prompt=REFNOTE + p,
                                                  size="1536x1024", quality="medium", n=1)
        else:
            raw = c.images.with_raw_response.generate(model=model, prompt=p, size="1536x1024",
                                                      quality="medium", n=1)
        resp = raw.parse()
        open(f"{out}/{k}.png", "wb").write(base64.b64decode(resp.data[0].b64_json))
        u = resp.usage.model_dump() if getattr(resp, "usage", None) else None
        log.write(json.dumps({"key": k, "model": model, "lever": lever, "s": round(time.time()-t), "usage": u}) + "\n")
        print("OK", model, lever, k, round(time.time()-t), "s", u and (u["input_tokens"], u["output_tokens"]))
    except Exception as e:
        print("ERR", model, lever, k, str(e)[:400]); log.write(json.dumps({"key": k, "model": model, "lever": lever, "err": str(e)[:400]}) + "\n")
    log.flush()
