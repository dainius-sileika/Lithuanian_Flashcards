# -*- coding: utf-8 -*-
"""build_review.py — build the owner review page for the new cards.

The previous review page inlined every image and clip as a base64 data URI. That
looked convenient and silently broke: opened over `file://`, browsers refuse to
load media from data URIs, so all 18 clips were dead on arrival even though the
bytes in the file were perfectly valid. Media is therefore written as real files
into `review/media/` and referenced relatively, which works in every browser and
keeps the HTML small enough to open instantly.

The page also carries each card's QA verdict, so a defect the machine already
caught is visible next to the picture instead of being rediscovered by eye.

    python3 build_review.py
"""
import csv, html, json, os, shutil, sys

OUT = "review"
MEDIA = os.path.join(OUT, "media")
IMG_W = 620  # downscaled for the page; masters stay full-size


def load_qa():
    """Latest QA verdict per card, if qa_images.py has been run."""
    path = "_qa/qa_phrases.csv"
    if not os.path.exists(path):
        return {}
    return {r["key"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}


def main():
    os.makedirs(MEDIA, exist_ok=True)
    rows = [r for r in csv.DictReader(open("wordlist_a2_pending.csv", encoding="utf-8"))
            if r["status"] == "pending" and r["level"] == "A1"
            and (r["category"] == "Question words" or r["phase"] == "P-G")]
    qa = load_qa()

    try:
        from PIL import Image
    except ImportError:
        Image = None

    cards, n_img, n_aud = [], 0, 0
    for r in rows:
        key = r["id"]
        img = aud = None

        src = f"out_phrases/{key}.png"
        if os.path.exists(src):
            dst = os.path.join(MEDIA, f"{key}.jpg")
            if Image:
                im = Image.open(src).convert("RGB")
                im = im.resize((IMG_W, round(im.height * IMG_W / im.width)), Image.LANCZOS)
                im.save(dst, "JPEG", quality=82, optimize=True)
            else:
                dst = os.path.join(MEDIA, f"{key}.png")
                shutil.copy(src, dst)
            img = "media/" + os.path.basename(dst)
            n_img += 1

        asrc = f"audio/{key}.mp3"
        if os.path.exists(asrc):
            shutil.copy(asrc, os.path.join(MEDIA, f"{key}.mp3"))
            aud = f"media/{key}.mp3"
            n_aud += 1

        fmt = ("question" if r["category"] == "Question words"
               else "exchange" if "exchange" in (r.get("notes") or "")
               else "utterance")
        q = qa.get(key, {})
        cards.append({
            "key": key, "lt": r["lithuanian_TARGET"], "en": r["english"],
            "fmt": fmt, "img": img, "aud": aud,
            "status": q.get("status", ""), "note": q.get("fails") or q.get("warnings", ""),
            "guess": q.get("guess", ""),
        })

    cards.sort(key=lambda c: (c["img"] is None, c["key"]))
    body = []
    for c in cards:
        st = c["status"]
        badge = (f'<span class="qa {st.lower()}">{st}</span>' if st else "")
        note = f'<p class="note">{html.escape(c["note"])}</p>' if c["note"] else ""
        guess = (f'<p class="guess">read cold as: <i>{html.escape(c["guess"])}</i></p>'
                 if c["guess"] else "")
        pic = (f'<img src="{c["img"]}" alt="{html.escape(c["en"])}">' if c["img"]
               else '<div class="pending">image pending</div>')
        au = (f'<audio controls preload="none" src="{c["aud"]}"></audio>' if c["aud"]
              else '<p class="note">no audio</p>')
        body.append(f"""<figure class="card">
  {pic}
  <figcaption>
    <div class="hd"><b>{html.escape(c["lt"])}</b> <span class="fmt">{c["fmt"]}</span> {badge}</div>
    <div class="en">{html.escape(c["en"])}</div>
    {au}{guess}{note}
  </figcaption>
</figure>""")

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>New cards — review</title><style>
:root{{--paper:#e7ddc6;--paper2:#efe7d4;--red:#97301f;--ink:#2c2620;--teal:#3c5e5a;--dun:#8a7d61}}
*{{box-sizing:border-box}}
body{{font-family:Georgia,"Times New Roman",serif;color:var(--ink);background:var(--paper);margin:0}}
header{{background:var(--red);color:var(--paper);padding:12px 18px;font-variant:small-caps;letter-spacing:.12em;font-weight:700}}
.lead{{max-width:900px;margin:16px auto;padding:0 18px;line-height:1.55}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px;padding:18px;max-width:1400px;margin:0 auto}}
.card{{background:var(--paper2);border:2px solid var(--red);margin:0;padding:0;display:flex;flex-direction:column}}
.card img{{width:100%;display:block}}
.pending{{padding:48px 12px;text-align:center;color:var(--dun);font-style:italic;background:#e2d8bf}}
figcaption{{padding:10px 12px 14px}}
.hd{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.hd b{{font-size:1.45rem}}
.fmt{{font-size:.68rem;font-variant:small-caps;letter-spacing:.08em;color:var(--teal);border:1px solid var(--teal);padding:1px 6px;border-radius:2px}}
.qa{{font-size:.68rem;font-variant:small-caps;letter-spacing:.08em;padding:1px 6px;border-radius:2px;color:#fff}}
.qa.pass{{background:#3f7d4f}}.qa.warn{{background:#b7791f}}.qa.fail{{background:#97301f}}
.en{{color:#4a4238;margin:2px 0 8px}}
audio{{width:100%;height:34px}}
.note{{font-size:.82rem;color:#7a4a3a;margin:8px 0 0;line-height:1.4}}
.guess{{font-size:.82rem;color:var(--dun);margin:8px 0 0}}
</style></head><body>
<header>Lietuvių — new cards for review</header>
<div class="lead">
<p><b>{len(cards)} new cards</b> · {n_img} with images · {n_aud} with your audio.
Every clip and picture here is a real file in <code>review/media/</code>, so playback
works when the page is opened straight from disk.</p>
<p>Each card shows its format — <b>question</b> (enquiry scene + bubble),
<b>utterance</b> (one pane + bubble), <b>exchange</b> (two panels, ask then answer) —
and its automated QA verdict. <i>Read cold as</i> is what a vision model guessed the
picture meant without being told the answer; where that misses the gloss, the picture
may not be carrying its own weight.</p>
</div>
<div class="grid">
{"".join(body)}
</div></body></html>"""

    with open(os.path.join(OUT, "new_cards_review.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    size = os.path.getsize(os.path.join(OUT, "new_cards_review.html")) / 1024
    print(f"review/new_cards_review.html  ({size:.0f} KB) · {len(cards)} cards · "
          f"{n_img} images · {n_aud} clips -> review/media/")


if __name__ == "__main__":
    main()
