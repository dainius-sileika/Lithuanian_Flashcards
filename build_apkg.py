#!/usr/bin/env python3
"""Build the importable Anki deck (Lietuviu_Flashcards.apkg) from cards_anki.csv
+ images/ (webp) + audio/ (mp3) + anki/go_theme.css.

    pip install genanki
    python3 build_apkg.py

Front = card image (question). Back = image + Lithuanian word, audio, gender,
grammatical forms (noun genitive / verb principal parts / adjective feminine),
and the English gloss. Media (webp + mp3) is bundled into the .apkg.

A2 (2026-10-11): the same build also reads the A2 list (A2_LIST, default
a2_build/a2_wordlist.csv; set A2_LIST="" to skip it). Its IMG and PHRASE rows become
picture cards of the same note type once their image exists (looked up by id in
A2_IMAGE_DIRS: images_a2/<id>.webp, out_phrases/<id>.png, ...); its CLOZE and PAIR
rows become native Anki cloze notes ("Lietuvių GO Cloze") built from example_lt,
where the {braces} mark the blank — these need no image. Every A2 note is tagged
with its level, route and phase and goes to the A1/A2 subdeck by its level.
"""
import genanki, csv, hashlib, os

CSS = open("anki/go_theme.css", encoding="utf-8").read()
FRONT = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
         '<span class="plate">{{number}}</span></div>{{image}}'
         '<div class="bar bottom"><span>{{category}}</span><span>?</span></div></div>')
BACK = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
        '<span class="plate">{{number}}</span></div>{{image}}'
        '<div class="answer"><div class="word">{{lithuanian}}</div>'
        '{{#pron}}<div class="pron">{{pron}}</div>{{/pron}}{{audio}}'
        '{{#gender}}<div class="gender">{{gender}}</div>{{/gender}}'
        '{{#gen_sg}}<div class="forms">{{lithuanian}} · {{gen_sg}}</div>{{/gen_sg}}'
        '{{#pres3}}<div class="forms">{{lithuanian}} · {{pres3}} · {{past3}}</div>{{/pres3}}'
        '{{#fem}}<div class="forms">{{lithuanian}} · {{fem}}</div>{{/fem}}'
        '<hr id="answer"><div class="gloss">{{english}}</div></div>'
        '<div class="bar bottom"><span>{{category}}</span><span>{{number}}</span></div></div>')

model = genanki.Model(
    1607392913, "Lietuvių GO",
    fields=[{'name': n} for n in ['key', 'lithuanian', 'english', 'gender', 'gen_sg',
            'pres3', 'past3', 'fem', 'number', 'category', 'image', 'audio', 'pron']],
    templates=[{'name': 'Card', 'qfmt': FRONT, 'afmt': BACK}], css=CSS)

# --- A2 cloze note type -----------------------------------------------------
# Native Anki cloze (model_type CLOZE): the Text field carries {{c1::...}} around the
# target form, so Anki itself blanks and reveals it. The English sentence is shown
# as a hint under the blank; the back adds the headword, stress, gender, forms and gloss.
CLOZE_CSS = CSS + """
.cloze-text { font-size: 1.6em; line-height: 1.35; margin: 1.2em 0.6em 0.4em; text-align: center; }
.cloze { font-weight: bold; text-decoration: underline; }
.hint { font-size: 0.95em; opacity: 0.75; text-align: center; margin-bottom: 0.8em; font-style: italic; }
.word-line { text-align: center; margin-top: 0.6em; }
"""
CLOZE_FRONT = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
               '<span class="plate">{{Number}}</span></div>'
               '<div class="cloze-text">{{cloze:Text}}</div>'
               '<div class="hint">{{SentenceEN}}</div>'
               '<div class="bar bottom"><span>{{Category}}</span><span>?</span></div></div>')
CLOZE_BACK = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
              '<span class="plate">{{Number}}</span></div>'
              '<div class="cloze-text">{{cloze:Text}}</div>'
              '<div class="hint">{{SentenceEN}}</div>'
              '<div class="answer word-line"><div class="word">{{Word}}</div>'
              '{{#Pron}}<div class="pron">{{Pron}}</div>{{/Pron}}{{Audio}}'
              '{{#Gender}}<div class="gender">{{Gender}}</div>{{/Gender}}'
              '{{#Forms}}<div class="forms">{{Forms}}</div>{{/Forms}}'
              '<hr id="answer"><div class="gloss">{{Gloss}}</div></div>'
              '<div class="bar bottom"><span>{{Category}}</span><span>{{Number}}</span></div></div>')
cloze_model = genanki.Model(
    1607392914, "Lietuvių GO Cloze", model_type=genanki.Model.CLOZE,
    fields=[{'name': n} for n in ['Text', 'SentenceEN', 'Word', 'Pron', 'Gender', 'Forms',
            'Gloss', 'Number', 'Category', 'Audio', 'Key']],
    templates=[{'name': 'Cloze', 'qfmt': CLOZE_FRONT, 'afmt': CLOZE_BACK}], css=CLOZE_CSS)

A2_LIST = os.environ.get("A2_LIST", "a2_build/a2_wordlist.csv")
A2_IMAGE_DIRS = ["images_a2", "out_phrases", "out_deck_a2", "images"]
A2_AUDIO_DIR = "audio_a2"

# Images are stored as WebP in the repo (compact). Some Anki clients/older Qt
# builds don't render WebP inside cards, so for the importable deck we transcode
# each image to JPEG (universally supported) into a temp folder. The repo set is
# untouched. Set IMG_FMT="webp" to bundle WebP directly instead.
IMG_FMT = os.environ.get("IMG_FMT", "jpg")
# Anki/AnkiWeb caps a shared deck at 250 MB. Measured on this deck, resolution
# dominates format: full-size WebP still lands ~308 MB at the projected 1365
# cards, while JPEG downscaled to 1024 px comes in at ~179 MB (+~30 MB audio)
# and keeps universal client compatibility — some Anki builds don't render WebP
# inside cards. 1024 px is still more than a card ever displays.
IMG_WIDTH = int(os.environ.get("IMG_WIDTH", "1024"))
TMP = "_apkg_media"
APKG_OUT = os.environ.get("APKG_OUT", "Lietuviu_Flashcards.apkg")   # where to write the deck

def gender_mark(g):
    """1.9 — gender as a symbol, not a letter: blue Mars for masculine, red
    Venus for feminine, with a plural tag beside where the noun is plural-only.
    Returns HTML placed straight into the gender field."""
    g = (g or "").strip()
    if not g or g == "V":
        return ""
    plural = "pl" in g.lower()
    out = []
    if g.upper().startswith("M/F") or g.upper() == "MF":
        out.append('<span class="g m">\u2642</span><span class="g f">\u2640</span>')
    elif g.upper().startswith("M"):
        out.append('<span class="g m">\u2642</span>')
    elif g.upper().startswith("F"):
        out.append('<span class="g f">\u2640</span>')
    elif g.upper().startswith("N"):
        out.append('<span class="g n">\u26b2</span>')
    if plural:
        out.append('<span class="pl">pl.</span>')
    return "".join(out)


def _sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_a2_image(k):
    """First existing <dir>/<id>.webp|png|jpg in A2_IMAGE_DIRS, else None."""
    for d in A2_IMAGE_DIRS:
        for ext in ("webp", "png", "jpg"):
            p = f"{d}/{k}.{ext}"
            if os.path.exists(p):
                return p
    return None


def media_image(k, src=None):
    src = src or f"images/{k}.webp"
    if not os.path.exists(src):
        return None, None
    ext = "webp" if IMG_FMT == "webp" else "jpg"
    dst = f"{TMP}/{k}.{ext}"
    # The transcode cache is keyed by the SOURCE's content hash (and the
    # settings), recorded in a sidecar. Keyed by filename alone, a re-rolled
    # card silently shipped its old picture.
    stamp = f"{_sha1(src)} {ext} {IMG_WIDTH}"
    side = dst + ".src"
    cached = (os.path.exists(dst) and os.path.exists(side)
              and open(side).read().strip() == stamp)
    if not cached:
        from PIL import Image
        im = Image.open(src).convert("RGB")
        if IMG_WIDTH and im.width > IMG_WIDTH:
            im = im.resize((IMG_WIDTH, round(im.height * IMG_WIDTH / im.width)),
                           Image.LANCZOS)
        if ext == "webp":
            im.save(dst, "WEBP", quality=85, method=6)
        else:
            im.save(dst, "JPEG", quality=85, optimize=True, progressive=True)
        with open(side, "w") as fh:
            fh.write(stamp)
    return dst, f"{k}.{ext}"

def cloze_text(example_lt):
    """'Aš {esu} mokytojas.' -> 'Aš {{c1::esu}} mokytojas.' (first braces only; later
    braces become c2, c3 so a sentence may blank two forms)."""
    out, n, i = [], 0, 0
    while True:
        a = example_lt.find("{", i)
        if a < 0:
            out.append(example_lt[i:]); break
        b = example_lt.find("}", a)
        if b < 0:
            out.append(example_lt[i:]); break
        n += 1
        out.append(example_lt[i:a] + "{{c%d::%s}}" % (n, example_lt[a + 1:b]))
        i = b + 1
    return "".join(out), n


def a2_forms(r):
    w = r["lithuanian_TARGET"]
    if r.get("gen_sg"):
        return f"{w} · {r['gen_sg']}"
    if r.get("pres3"):
        return f"{w} · {r['pres3']} · {r.get('past3', '')}"
    if r.get("fem"):
        return f"{w} · {r['fem']}"
    return ""


def add_a2_notes(DECKS, media):
    """Add the A2 list to the decks. Picture rows (IMG, PHRASE) need an image in
    A2_IMAGE_DIRS and use the GO model; CLOZE/PAIR rows need example_lt and use the
    cloze model. Returns counts. Skipped silently: no list, rows without image/sentence."""
    counts = {"image": 0, "cloze": 0, "skipped_no_image": 0, "skipped_no_sentence": 0}
    if not A2_LIST or not os.path.exists(A2_LIST):
        return counts
    os.makedirs(TMP, exist_ok=True)
    for r in csv.DictReader(open(A2_LIST, encoding="utf-8")):
        k = r["id"]; route = r.get("route", "")
        level = (r.get("level") or "A2").strip() or "A2"
        target = DECKS.get(level, DECKS["A2"])
        tags = [level, route, r.get("phase", "").replace("-", "")]
        aud = f"{A2_AUDIO_DIR}/{k}.mp3"
        audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
        if route in ("IMG", "PHRASE"):
            src = find_a2_image(k)
            if not src:
                counts["skipped_no_image"] += 1; continue
            img_path, img_name = media_image(k, src)
            target.add_note(genanki.Note(
                model=model, tags=tags, guid=genanki.guid_for(k),
                fields=[k, r["lithuanian_TARGET"], r["english"], gender_mark(r.get("gender", "")),
                        r.get("gen_sg", ""), r.get("pres3", ""), r.get("past3", ""), r.get("fem", ""),
                        k.replace("A2-", ""), r.get("category", ""),
                        f'<img class="art" src="{img_name}">', audf, r.get("lt_pron", "")]))
            media.append(img_path); counts["image"] += 1
        elif route in ("CLOZE", "PAIR"):
            text, n = cloze_text(r.get("example_lt", ""))
            if not n:
                counts["skipped_no_sentence"] += 1; continue
            target.add_note(genanki.Note(
                model=cloze_model, tags=tags, guid=genanki.guid_for(k),
                fields=[text, r.get("example_en", ""), r["lithuanian_TARGET"], r.get("lt_pron", ""),
                        gender_mark(r.get("gender", "")), a2_forms(r), r["english"],
                        k.replace("A2-", ""), r.get("category", ""), audf, k]))
            counts["cloze"] += 1
        else:
            continue
        if audf:
            media.append(aud)
    return counts


def main():
    os.makedirs(TMP, exist_ok=True)
    # 1.7.9 — one deck, split into CEFR subdecks. Studying the parent studies
    # everything; clicking A1 or A2 studies just that level. Cards also carry an
    # A1/A2 tag so custom filtered decks stay possible.
    DECKS = {
        "A1": genanki.Deck(2059400112, "Lietuvių Flashcards::A1"),
        "A2": genanki.Deck(2059400113, "Lietuvių Flashcards::A2"),
    }
    deck = DECKS["A1"]   # default for rows with no level set
    media = []
    for r in csv.DictReader(open("cards_anki.csv", encoding="utf-8")):
        k = r['key']; aud = f"audio/{k}.mp3"
        img_path, img_name = media_image(k)
        if not img_path:
            continue
        audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
        level = (r.get("level") or "A1").strip() or "A1"
        target = DECKS.get(level, DECKS["A1"])
        target.add_note(genanki.Note(
            model=model,
            tags=[level],
            # STABLE identity: guid derived from the card key, never random, so
            # re-importing an updated deck updates cards in place (keeps study
            # history / scheduling) instead of creating duplicates.
            guid=genanki.guid_for(k),
            fields=[k, r['lithuanian'], r['english'], gender_mark(r['gender']), r['gen_sg'],
                    r['pres3'], r['past3'], r['fem'], r['number'], r['category'],
                    f'<img class="art" src="{img_name}">', audf, r.get('pron', '')]))
        media.append(img_path)
        if os.path.exists(aud):
            media.append(aud)

    a2_counts = add_a2_notes(DECKS, media)

    pkg = genanki.Package(list(DECKS.values())); pkg.media_files = media
    pkg.write_to_file(APKG_OUT)
    counts = {lv: len(d.notes) for lv, d in DECKS.items()}
    print(f"built {APKG_OUT} — {len(media)} media files | "
          f"subdecks: {counts} | A2 list: {a2_counts}")


if __name__ == "__main__":
    main()
