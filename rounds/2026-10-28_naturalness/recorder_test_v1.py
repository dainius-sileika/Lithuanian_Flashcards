#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recorder_test_v1.py — headless test of the recorder regenerated after the naturalness round (2026-10-28).

    python3 rounds/2026-10-28_naturalness/recorder_test_v1.py recorder_A2.html > rounds/2026-10-28_naturalness/recorder_test_v1.txt

Same method as rounds/2026-10-20_rename/recorder_migration_test_v2.py (playwright + chromium, fake microphone).
Seeds IndexedDB lt_recorder_A2_afb2ebe2 with clips as the owner's browser may hold them after this round:
  * under a key that key_map_v3 renamed, with the OLD words (0239_orai_s, 1169_greitai_pasveik): must move to the
    new key and, the words having changed, be set aside (superseded/), never lost;
  * under a renamed key with words still current (1482_ar_yra_laisvas_staliukas, unrecorded so far: a stamp of the
    new words) : must move to 1482_ar_yra_laisvu_staliuku and stay a take;
  * under an unchanged key with old words (0162_jai_s "Padovanojau jai gėlių."): set aside;
  * current clips (0263_tik "tìk", 2435_spustis_s "Centre spūstys."): kept as takes.
Clicks "Enable microphone & start", dumps both stores, presses Export, lists the ZIP, and checks: the page lists
the expected number of takes, no console errors, and every seeded blob comes out exactly once (under its current key
or under superseded/). Exit 1 on a failed check.
"""
import asyncio, io, json, os, shutil, subprocess, sys, tempfile, time, zipfile
from playwright.async_api import async_playwright

SEED = [("0239_orai_s", "Kokie šiandien orai?"), ("1169_greitai_pasveik", "Greitai pasveik!"),
        ("1482_ar_yra_laisvas_staliukas", "Ar yra laisvų staliukų?"), ("0162_jai_s", "Padovanojau jai gėlių."),
        ("0263_tik", "tìk"), ("2435_spustis_s", "Centre spūstys.")]
EXPECT = {"0239_orai_s": "superseded", "1169_greitai_pasveik": "superseded", "0162_jai_s": "superseded",
          "1482_ar_yra_laisvas_staliukas": "1482_ar_yra_laisvu_staliuku", "0263_tik": "0263_tik",
          "2435_spustis_s": "2435_spustis_s"}
PORT = 8766


async def main(html):
    root = tempfile.mkdtemp(); shutil.copy(html, os.path.join(root, "recorder_A2.html"))
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "-d", root],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    errors, fails = [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"])
            ctx = await b.new_context(accept_downloads=True)
            await ctx.grant_permissions(["microphone"], origin=f"http://127.0.0.1:{PORT}")
            pg = await ctx.new_page()
            pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append(str(e)))
            await pg.goto(f"http://127.0.0.1:{PORT}/recorder_A2.html")
            n_words = await pg.evaluate("WORDS.length")
            km = await pg.evaluate("[KEY_MAP['0239_orai_s'], KEY_MAP['1169_greitai_pasveik'], KEY_MAP['1482_ar_yra_laisvas_staliukas']]")
            await pg.evaluate("""async (seed)=>{ await new Promise((res,rej)=>{const r=indexedDB.open('lt_recorder_A2_afb2ebe2',2);
              r.onupgradeneeded=e=>{const d=e.target.result; d.createObjectStore('clips'); d.createObjectStore('meta');};
              r.onsuccess=e=>{const d=e.target.result; const t=d.transaction(['clips','meta'],'readwrite');
                for(const [k,said] of seed){ t.objectStore('clips').put(new Blob(['clip-of-'+k],{type:'audio/webm'}),k);
                  if(said!==null) t.objectStore('meta').put(said,'said:'+k); }
                t.oncomplete=()=>{d.close();res()}; t.onerror=()=>rej(t.error);}; r.onerror=()=>rej(r.error);});}""",
                              [list(s) for s in SEED])
            await pg.click("#start"); await pg.wait_for_selector("#app", state="visible", timeout=20000)
            info = await pg.inner_text("#storeInfo")
            async with pg.expect_download() as dl:
                await pg.click("#export")
            d = await dl.value; path = await d.path()
            z = zipfile.ZipFile(path); names = z.namelist(); man = z.read("manifest.tsv").decode()
            contents = {n: z.read(n).decode(errors="replace") for n in names if n != "manifest.tsv"}
            await b.close()
    finally:
        srv.terminate()
    print("WORDS (takes on the sheet):", n_words)
    print("KEY_MAP 0239_orai_s / 1169_greitai_pasveik / 1482_ar_yra_laisvas_staliukas ->", km)
    print("STOREINFO:", info)
    print("ZIP:", json.dumps(contents, ensure_ascii=False, indent=1))
    print("MANIFEST:\n" + man)
    print("CONSOLE ERRORS:", errors or "none")
    expected_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if expected_n is not None and n_words != expected_n:
        fails.append(f"sheet lists {n_words} takes, expected {expected_n}")
    if km != ["0239_oras_s", "1169_sveik", "1482_ar_yra_laisvu_staliuku"]:
        fails.append(f"KEY_MAP lacks the v3 renames: {km}")
    if errors:
        fails.append(f"{len(errors)} console error(s)")
    for k, where in EXPECT.items():
        hits = [n for n, c in contents.items() if c == "clip-of-" + k]
        if len(hits) != 1:
            fails.append(f"{k}: found {len(hits)} times in the ZIP {hits}")
            continue
        ok = hits[0].startswith("superseded/") if where == "superseded" else hits[0].split("/")[-1].startswith(where + ".")
        print(f"CHECK {k:32} -> {hits[0]:60} {'ok' if ok else 'UNEXPECTED (expected ' + where + ')'}")
        if not ok:
            fails.append(f"{k}: came out as {hits[0]}, expected {where}")
    for f in fails:
        print("FAIL", f)
    print("RESULT:", "PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1])))
