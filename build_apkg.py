#!/usr/bin/env python3
"""Build the importable Anki deck (Lietuviu_Flashcards.apkg) from cards_anki.csv
+ images/ (webp) + audio/ (mp3) + anki/go_theme.css.

    pip install genanki
    python3 build_apkg.py

Front = card image (question). Back = image + Lithuanian word, audio, gender,
grammatical forms (noun genitive / verb principal parts / adjective feminine),
and the English gloss. Media (webp + mp3) is bundled into the .apkg.
"""
import genanki, csv, os

CSS = open("anki/go_theme.css").read()
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
TMP = "_apkg_media"; os.makedirs(TMP, exist_ok=True)

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


def media_image(k):
    src = f"images/{k}.webp"
    if not os.path.exists(src):
        return None, None
    ext = "webp" if IMG_FMT == "webp" else "jpg"
    dst = f"{TMP}/{k}.{ext}"
    if not os.path.exists(dst):
        from PIL import Image
        im = Image.open(src).convert("RGB")
        if IMG_WIDTH and im.width > IMG_WIDTH:
            im = im.resize((IMG_WIDTH, round(im.height * IMG_WIDTH / im.width)),
                           Image.LANCZOS)
        if ext == "webp":
            im.save(dst, "WEBP", quality=85, method=6)
        else:
            im.save(dst, "JPEG", quality=85, optimize=True, progressive=True)
    return dst, f"{k}.{ext}"

# 1.7.9 — one deck, split into CEFR subdecks. Studying the parent studies
# everything; clicking A1 or A2 studies just that level. Cards also carry an
# A1/A2 tag so custom filtered decks stay possible.
DECKS = {
    "A1": genanki.Deck(2059400112, "Lietuvių Flashcards::A1"),
    "A2": genanki.Deck(2059400113, "Lietuvių Flashcards::A2"),
}
deck = DECKS["A1"]   # default for rows with no level set
media = []
for r in csv.DictReader(open("cards_anki.csv")):
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

pkg = genanki.Package(list(DECKS.values())); pkg.media_files = media
pkg.write_to_file("Lietuviu_Flashcards.apkg")
counts = {lv: len(d.notes) for lv, d in DECKS.items()}
print(f"built Lietuviu_Flashcards.apkg — {len(media)} media files | "
      f"subdecks: {counts}")
