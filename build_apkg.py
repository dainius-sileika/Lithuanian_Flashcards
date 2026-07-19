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
         '<span class="plate">{{number}}</span></div><img class="art" src="{{image}}">'
         '<div class="bar bottom"><span>{{category}}</span><span>?</span></div></div>')
BACK = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
        '<span class="plate">{{number}}</span></div><img class="art" src="{{image}}">'
        '<div class="answer"><div class="word">{{lithuanian}}</div>{{audio}}'
        '{{#gender}}<div class="gender {{gender}}">{{gender}}</div>{{/gender}}'
        '{{#gen_sg}}<div class="forms">{{lithuanian}} · {{gen_sg}}</div>{{/gen_sg}}'
        '{{#pres3}}<div class="forms">{{lithuanian}} · {{pres3}} · {{past3}}</div>{{/pres3}}'
        '{{#fem}}<div class="forms">{{lithuanian}} · {{fem}}</div>{{/fem}}'
        '<hr id="answer"><div class="gloss">{{english}}</div></div>'
        '<div class="bar bottom"><span>{{category}}</span><span>{{number}}</span></div></div>')

model = genanki.Model(
    1607392913, "Lietuvių GO",
    fields=[{'name': n} for n in ['key', 'lithuanian', 'english', 'gender', 'gen_sg',
            'pres3', 'past3', 'fem', 'number', 'category', 'image', 'audio']],
    templates=[{'name': 'Card', 'qfmt': FRONT, 'afmt': BACK}], css=CSS)

deck = genanki.Deck(2059400111, "Lietuvių Flashcards")
media = []
for r in csv.DictReader(open("cards_anki.csv")):
    k = r['key']; img = f"images/{k}.webp"; aud = f"audio/{k}.mp3"
    if not os.path.exists(img):
        continue
    audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
    deck.add_note(genanki.Note(model=model, fields=[
        k, r['lithuanian'], r['english'], r['gender'], r['gen_sg'], r['pres3'],
        r['past3'], r['fem'], r['number'], r['category'], f"{k}.webp", audf]))
    media.append(img)
    if os.path.exists(aud):
        media.append(aud)

pkg = genanki.Package(deck); pkg.media_files = media
pkg.write_to_file("Lietuviu_Flashcards.apkg")
print(f"built Lietuviu_Flashcards.apkg — {len(media)} media files")
