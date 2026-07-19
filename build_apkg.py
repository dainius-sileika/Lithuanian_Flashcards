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
        '{{#gender}}<div class="gender {{gender}}">{{gender}}</div>{{/gender}}'
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
TMP = "_apkg_media"; os.makedirs(TMP, exist_ok=True)

def media_image(k):
    src = f"images/{k}.webp"
    if not os.path.exists(src):
        return None, None
    if IMG_FMT == "webp":
        return src, f"{k}.webp"
    dst = f"{TMP}/{k}.jpg"
    if not os.path.exists(dst):
        from PIL import Image
        Image.open(src).convert("RGB").save(dst, "JPEG", quality=86, optimize=True)
    return dst, f"{k}.jpg"

deck = genanki.Deck(2059400111, "Lietuvių Flashcards")
media = []
for r in csv.DictReader(open("cards_anki.csv")):
    k = r['key']; aud = f"audio/{k}.mp3"
    img_path, img_name = media_image(k)
    if not img_path:
        continue
    audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
    deck.add_note(genanki.Note(
        model=model,
        # STABLE identity: guid derived from the card key, never random, so
        # re-importing an updated deck updates cards in place (keeps study
        # history / scheduling) instead of creating duplicates.
        guid=genanki.guid_for(k),
        fields=[k, r['lithuanian'], r['english'], r['gender'], r['gen_sg'],
                r['pres3'], r['past3'], r['fem'], r['number'], r['category'],
                f'<img class="art" src="{img_name}">', audf, r.get('pron', '')]))
    media.append(img_path)
    if os.path.exists(aud):
        media.append(aud)

pkg = genanki.Package(deck); pkg.media_files = media
pkg.write_to_file("Lietuviu_Flashcards.apkg")
print(f"built Lietuviu_Flashcards.apkg — {len(media)} media files")
