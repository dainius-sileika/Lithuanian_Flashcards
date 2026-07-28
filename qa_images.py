#!/usr/bin/env python3
"""qa_images.py — automated QA gate for generated cards.

Two rules have governed this deck from the start, and both were being checked by
eye, which is why breaches kept surfacing a batch late:

  1. NO TEXT IN THE ART. The model cannot spell Lithuanian; worse, when it does
     spell the target word correctly it hands the learner the answer and the card
     stops teaching. Any lettering beyond a card's declared `card_text` budget is
     a defect. The target word appearing is a *hard* failure.
  2. GUESSABILITY. If you didn't already know the word, the picture alone should
     get you there. An image can be text-free and still fail by being unreadable,
     off-concept, or simply weird.

Rule 1 is mechanical. Rule 2 is a judgement call, and OCR cannot make it —
tesseract was tried first and is unusable here: the painterly, textured ground
produces pages of hallucinated words while missing a 400-pixel question mark.
So QA asks a vision model to do what a reviewer does — read the image cold,
without being told the answer, and say what it sees.

The guessability check is deliberately blind: the model is never shown the target
word before it guesses. Only afterwards is the guess compared to the gloss. A
model that was told the answer would confirm it every time.

    python3 qa_images.py out_phrases                 # QA a folder
    python3 qa_images.py out_phrases --csv qa.csv     # write a report
    python3 qa_images.py images --budget 300          # stop after 5 minutes
    python3 qa_images.py out_phrases --recheck        # ignore the cache

Results are cached in `_qa/qa_cache.json`, keyed by file content hash, so a
re-run only pays for images that actually changed. Exit code is non-zero if any
card fails, so this can gate a generation run.
"""
import base64, csv, hashlib, json, os, re, sys, time, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai")

MODEL = "gpt-5-mini"
CACHE = "_qa/qa_cache.json"
STRESS = {0x0300, 0x0301, 0x0303}

# Metadata sources, in priority order. Each maps id -> row.
SOURCES = ["wordlist_a2_pending.csv", "master_wordlist.csv", "cards_anki.csv"]

PROMPT = """You are inspecting an illustration from a language-learning flashcard deck.
Answer ONLY about what is actually visible. Do not speculate about intent.

Return strict JSON with these keys:
  "lettering":  array of every piece of readable text/lettering in the image,
                transcribed exactly. Include single letters and words on signs,
                labels, packaging, book spines, and inside speech bubbles.
                Do NOT include punctuation-only marks here. [] if none.
  "punctuation": array of standalone punctuation glyphs shown as graphic
                elements (e.g. "?", "!"). [] if none.
  "guess":      your best guess, in English, at the single word or short phrase
                this picture is trying to teach. Guess from the picture alone.
  "confidence": "high" | "medium" | "low" — how clearly the picture points at
                one specific meaning rather than several.
  "problems":   array of short strings describing anything visually wrong:
                garbled or nonsense lettering, malformed hands or faces, duplicated
                or fused limbs, incoherent objects, elements that contradict each
                other, or anything a careful reviewer would call an error. [] if none.
"""


def plain(s):
    """Lowercase, strip stress marks — so 'kodėl' and 'kodė́l' compare equal."""
    s = (s or "").replace("i̇", "i")
    d = unicodedata.normalize("NFD", s)
    d = "".join(c for c in d if ord(c) not in STRESS)
    return unicodedata.normalize("NFC", d).lower().strip()


def words_of(s):
    return [w for w in re.split(r"[^\wĀ-ſ]+", plain(s)) if len(w) >= 3]


def file_hash(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_meta():
    meta = {}
    for src in SOURCES:
        if not os.path.exists(src):
            continue
        for r in csv.DictReader(open(src, encoding="utf-8")):
            for k in ("id", "key", "number"):
                if r.get(k):
                    meta.setdefault(str(r[k]).strip(), r)
                    break
    return meta


def describe(client, path):
    """Ask the vision model what it sees. Returns the parsed dict."""
    b = base64.b64encode(open(path, "rb").read()).decode()
    r = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": PROMPT},
            {"type": "input_image", "image_url": f"data:image/png;base64,{b}"}]}],
    )
    txt = (r.output_text or "").strip()
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise ValueError(f"no JSON in reply: {txt[:200]}")
    return json.loads(m.group(0))


def is_question(row):
    """Canonical test — imported by gen_phrases.py so the generator and the QA
    gate cannot drift apart. They did once: full sentences like 'Kas tai?' are
    questions by their punctuation but sit outside the 'Question words' category,
    so the generator drew the mark correctly and QA then failed the card for it."""
    if row.get("category") == "Question words":
        return True
    if "question" in (row.get("flags") or "") or (row.get("type") or "").upper() == "Q":
        return True
    return ((row.get("lithuanian_TARGET") or "").strip().endswith("?")
            or (row.get("english") or "").strip().endswith("?"))


def judge(seen, row):
    """Turn a vision reading + the card's metadata into pass/fail findings."""
    target = row.get("lithuanian_TARGET") or row.get("lithuanian") or row.get("word") or ""
    gloss = row.get("english") or row.get("english_gloss") or row.get("gloss") or ""
    allowed = row.get("card_text") or ""
    is_q = is_question(row)

    fails, warns = [], []
    allow_words = set(words_of(allowed)) | {plain(x) for x in re.split(r"[,;/]", allowed) if x.strip()}
    tgt_words = set(words_of(target))

    for piece in seen.get("lettering", []) or []:
        p = plain(piece)
        if not p:
            continue
        # Bare numerals are illustration, not answer-leakage — clock faces,
        # prices, and rulers all carry them and none of them spell a word.
        if re.fullmatch(r"[\d\s.,:%-]+", p):
            continue
        pw = set(words_of(piece)) or {p}
        if pw & tgt_words:
            fails.append(f"TARGET WORD IN ART: {piece!r}")
        elif allowed and (p in allow_words or pw <= allow_words):
            pass  # declared and permitted
        elif allowed and p in plain(allowed):
            pass
        else:
            fails.append(f"undeclared text: {piece!r}")

    puncts = [p for p in (seen.get("punctuation") or []) if p.strip()]
    has_q = any("?" in p for p in puncts)
    if has_q and not is_q:
        fails.append("stray '?' — this card is not a question")
    if is_q and not has_q:
        warns.append("question card shows no '?'")

    # Guessability gate — blind guess vs. the actual gloss.
    #
    # Exempt for question words: their grammar is one deliberately uniform
    # enquiry scene where only a small bubble pictogram changes, so a cold
    # reading returns the props ("wrench", "cup") and never "how" or "what kind
    # of". The card teaches through the cloze sentence on the back, not the
    # picture, so scoring it on guessability would flag the design as a bug.
    if not is_q:
        guess, gw = seen.get("guess", ""), set(words_of(seen.get("guess", "")))
        glw = set(words_of(gloss))
        if gloss and gw and glw and not (gw & glw):
            warns.append(f"guessed {guess!r}, card teaches {gloss!r}")
        if (seen.get("confidence") or "").lower() == "low":
            warns.append("picture points at no single meaning (low confidence)")

    for p in seen.get("problems", []) or []:
        warns.append(str(p))

    return fails, warns


def main():
    args = sys.argv[1:]
    folder = next((a for a in args if not a.startswith("--")), "out_phrases")
    out_csv = args[args.index("--csv") + 1] if "--csv" in args else None
    budget = float(args[args.index("--budget") + 1]) if "--budget" in args else 1e9
    recheck = "--recheck" in args

    if not os.getenv("OPENAI_API_KEY") and os.path.exists(".openai_key.txt"):
        os.environ["OPENAI_API_KEY"] = open(".openai_key.txt").read().strip()
    client = OpenAI()

    os.makedirs("_qa", exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) and not recheck else {}
    meta = load_meta()

    files = sorted(f for f in os.listdir(folder)
                   if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg")))
    todo = []
    for f in files:
        path = os.path.join(folder, f)
        key = os.path.splitext(f)[0]
        ck = f"{key}:{file_hash(path)}"
        if ck in cache:
            continue
        todo.append((key, path, ck))

    print(f"{len(files)} images | {len(files)-len(todo)} cached | {len(todo)} to inspect")
    t0 = time.time()
    done = 0
    if todo:
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(describe, client, p): (k, ck) for k, p, ck in todo}
            for fut in as_completed(futs):
                k, ck = futs[fut]
                try:
                    cache[ck] = fut.result()
                except Exception as e:
                    cache[ck] = {"error": str(e)[:200]}
                done += 1
                if time.time() - t0 > budget:
                    print(f"  budget reached — {done}/{len(todo)} inspected; rerun to continue")
                    for g in futs:
                        g.cancel()
                    break
        json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)

    rows, nfail, nwarn = [], 0, 0
    for f in files:
        key = os.path.splitext(f)[0]
        ck = f"{key}:{file_hash(os.path.join(folder, f))}"
        seen = cache.get(ck)
        if not seen:
            continue
        row = meta.get(key) or meta.get(key.split("_")[0]) or {}
        if seen.get("error"):
            fails, warns = [f"QA error: {seen['error']}"], []
        else:
            fails, warns = judge(seen, row)
        status = "FAIL" if fails else ("WARN" if warns else "PASS")
        nfail += bool(fails)
        nwarn += bool(warns and not fails)
        word = row.get("lithuanian_TARGET") or row.get("lithuanian") or ""
        rows.append({"key": key, "word": word, "status": status,
                     "fails": " | ".join(fails), "warnings": " | ".join(warns),
                     "guess": seen.get("guess", ""),
                     "lettering": " | ".join(seen.get("lettering") or [])})
        if status != "PASS":
            print(f"  {status}  {key:12} {word[:22]:24} {' | '.join(fails + warns)[:80]}")

    print(f"\n{len(rows)} checked · {nfail} FAIL · {nwarn} WARN · {len(rows)-nfail-nwarn} PASS")
    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["key", "word", "status", "fails",
                                               "warnings", "guess", "lettering"])
            w.writeheader()
            w.writerows(rows)
        print(f"report -> {out_csv}")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
