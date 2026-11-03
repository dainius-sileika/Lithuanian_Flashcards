#!/usr/bin/env python3
"""review_page_test_v1.py — headless test of an audio review page (tools/audio_review_page.py --pack --db) before it
is handed to the owner (lessons: "Test anything the owner will use in a headless browser").

    python3 rounds/2026-11-03_audio_b3/review_page_test_v1.py PAGE_DIR [--col audio_b3] > review_page_test_v1.txt

Serves PAGE_DIR (index.html + media/pack_NN.json) on 127.0.0.1 and, in Chromium at 390 px and 1280 px wide:
  * no horizontal page scroll; no console errors; every waveform image is full width of its card;
  * the first flagged card's clips arrive from their pack (blob: src) and the processed clip plays (duration > 0);
  * the "Not shipped" section (--kept) is there and its original clip loads;
  * the last card's pack loads after scrolling to it;
  * answer buttons: choose, the counter says 1, choose again clears, a note is kept; the Flagged filter shows only
    flagged cards; the answer survives a reload (localStorage);
  * with a mock window.claude (db + user), a click writes exactly {choice, note, updatedAt} to collection COL, doc = take
    key, and a seeded answer from the db is shown.
Exit 1 on a failed check.
"""
import asyncio
import json
import os
import subprocess
import sys
import time

from playwright.async_api import async_playwright

PORT = 8771
MOCK = """
window.__writes = [];
const seed = {docs: [{id: "__SEED__", data: () => ({choice: "original", note: "seeded", updatedAt: "2099-01-01T00:00:00Z"})}]};
const coll = name => ({
  get: async () => (name === "__COL__" ? seed : {docs: []}),
  doc: id => ({set: async body => { window.__writes.push({col: name, id, body}); }}),
});
window.claude = {use: async n => n === "db" ? {collection: coll} : n === "user" ? {can: async () => true} : null};
"""


def check(fails, ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


async def run(page_dir, col):
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "-d", page_dir],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    url = f"http://127.0.0.1:{PORT}/index.html"
    fails = []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
            for width in (390, 1280):
                print(f"== {width} px")
                ctx = await b.new_context(viewport={"width": width, "height": 900})
                pg = await ctx.new_page()
                errors = []
                pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errors.append(str(e)))
                await pg.goto(url)
                await pg.wait_for_timeout(1500)
                sw = await pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
                check(fails, sw[0] <= sw[1], f"no horizontal scroll (scrollWidth {sw[0]} <= {sw[1]})")
                first = await pg.evaluate("""() => { const c = document.querySelector('article.take[data-flagged="1"]');
                    return c ? c.dataset.key : null }""")
                check(fails, bool(first), f"a flagged card comes first: {first}")
                await pg.evaluate("document.querySelector('article.take').scrollIntoView()")   # packs load as cards near the view
                await pg.wait_for_function("""() => { const c = document.querySelector('article.take');
                    return [...c.querySelectorAll('audio, img')].every(e => (e.src || '').startsWith('blob:') || !e.dataset.pack) }""",
                                           timeout=20000)
                srcs = await pg.evaluate("[...document.querySelector('article.take').querySelectorAll('audio,img')].map(e => (e.getAttribute('src')||'').slice(0,5))")
                check(fails, all(s == "blob:" for s in srcs), f"first card's clips and picture come from the pack: {srcs}")
                card = "article.take:not(.fail)"
                dur = await pg.evaluate(f"""async () => {{ const a = document.querySelectorAll('{card} audio')[1];
                    a.scrollIntoView(); for (let i = 0; i < 100 && !(a.src||'').startsWith('blob:'); i++) await new Promise(r => setTimeout(r, 100));
                    try {{ await a.play(); }} catch (e) {{ return 'play failed: ' + e; }}
                    await new Promise(r => setTimeout(r, 400)); a.pause(); return a.duration; }}""")
                check(fails, isinstance(dur, (int, float)) and dur > 0, f"a processed clip plays (duration {dur})")
                iw = await pg.evaluate(f"""() => {{ const c = document.querySelector('{card}'), i = c.querySelector('img');
                    return [Math.round(i.getBoundingClientRect().width), Math.round(c.getBoundingClientRect().width)] }}""")
                check(fails, iw[0] >= iw[1] - 40, f"waveform spans its card ({iw[0]} of {iw[1]} px)")
                kept = await pg.evaluate("""async () => { const s = document.getElementById('kept'); if (!s) return null;
                    s.scrollIntoView(); const a = s.querySelector('audio');
                    for (let i = 0; i < 100 && !(a.src||'').startsWith('blob:'); i++) await new Promise(r => setTimeout(r, 100));
                    return [s.querySelectorAll('.ref').length, (a.src||'').slice(0,5)] }""")
                check(fails, kept and kept[0] >= 1 and kept[1] == "blob:", f"'Not shipped' section with its original clip: {kept}")
                last = await pg.evaluate("""async () => { const cs = document.querySelectorAll('article.take'); const c = cs[cs.length-1];
                    c.scrollIntoView(); const a = c.querySelector('audio');
                    for (let i = 0; i < 150 && !(a.src||'').startsWith('blob:'); i++) await new Promise(r => setTimeout(r, 100));
                    return [cs.length, c.dataset.key, (a.src||'').slice(0,5)] }""")
                check(fails, last[2] == "blob:", f"last card ({last[1]}, {last[0]} cards) loads from its pack")
                # answers
                await pg.evaluate("window.scrollTo(0,0)")
                btn = f"article.take[data-key='{first}'] .choices button[data-choice='rerecord']"
                await pg.click(btn)
                n = await pg.text_content("#ans-n")
                check(fails, n == "1", f"choosing an answer counts it (Answered {n})")
                await pg.click(btn)
                n = await pg.text_content("#ans-n")
                check(fails, n == "0", f"choosing it again clears it (Answered {n})")
                await pg.click(btn)
                await pg.fill(f"article.take[data-key='{first}'] textarea", "test note")
                await pg.click("button[data-filter='flagged']")
                vis = await pg.evaluate("""() => [...document.querySelectorAll('article.take')].filter(c => !c.hidden)
                    .every(c => c.dataset.flagged === '1')""")
                shown = await pg.text_content("#ans-shown")
                check(fails, vis, f"the Flagged filter shows only flagged cards ({shown.strip(' ·')})")
                await pg.click("button[data-filter='all']")
                await pg.reload()
                await pg.wait_for_timeout(800)
                st = await pg.evaluate(f"""() => {{ const c = document.querySelector("article.take[data-key='{first}']");
                    return [c.dataset.answered || '', c.querySelector('textarea').value, document.getElementById('ans-n').textContent] }}""")
                check(fails, st == ["rerecord", "test note", "1"], f"answer and note survive a reload (localStorage): {st}")
                check(fails, not errors, f"no console errors ({errors[:3]})")
                await ctx.close()
            # the db path, with a mock window.claude
            print("== db (mock window.claude)")
            ctx = await b.new_context(viewport={"width": 1280, "height": 900})
            pg = await ctx.new_page()
            keys = None
            await pg.goto(url)
            keys = await pg.evaluate("[...document.querySelectorAll('article.take:not(.fail)')].map(c => c.dataset.key)")
            seed_key, click_key = keys[1], keys[0]
            await ctx.add_init_script(MOCK.replace("__COL__", col).replace("__SEED__", seed_key))
            await pg.goto(url)
            await pg.wait_for_timeout(1500)
            mode = await pg.text_content("#ans-mode")
            seeded = await pg.evaluate(f"document.querySelector(\"article.take[data-key='{seed_key}']\").dataset.answered || ''")
            check(fails, seeded == "original", f"a seeded db answer is shown ({seed_key}: {seeded}); mode: {mode.strip()}")
            await pg.click(f"article.take[data-key='{click_key}'] .choices button[data-choice='processed']")
            await pg.wait_for_timeout(500)
            w = await pg.evaluate("window.__writes")
            ok = (len(w) == 1 and w[0]["col"] == col and w[0]["id"] == click_key
                  and sorted(w[0]["body"]) == ["choice", "note", "updatedAt"] and w[0]["body"]["choice"] == "processed")
            check(fails, ok, f"a click writes {{choice, note, updatedAt}} to {col}/{click_key}: {json.dumps(w, ensure_ascii=False)[:200]}")
            await ctx.close()
            await b.close()
    finally:
        srv.terminate()
    print("PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    col = a[a.index("--col") + 1] if "--col" in a else "audio_review"
    sys.exit(asyncio.run(run(os.path.abspath(a[0]), col)))
