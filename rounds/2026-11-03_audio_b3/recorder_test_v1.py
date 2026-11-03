#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recorder_test_v1.py — headless test of the recorder regenerated after audio batch 3 (2026-11-03).

    python3 rounds/2026-11-03_audio_b3/recorder_test_v1.py recorder_A2.html 1837 > rounds/2026-11-03_audio_b3/recorder_test_v1.txt

Same method as rounds/2026-10-28_naturalness/recorder_test_v1.py (playwright + chromium, fake microphone). Seeds
IndexedDB lt_recorder_A2_afb2ebe2 with clips as the owner's browser holds them after batch 3:
  * 0650_greitai_s stamped with the OLD words "Autobusas atvažiuos greitai." (the sheet now says "Autobusas greitai
    atvažiuos."): must be set aside (superseded/), never lost, and the take must show as a re-take with the old words;
  * 0263_tik "tìk" (failed the self-check, still on the sheet): stays a take;
  * 0650_greitai "greĩtai" (ingested, off the sheet now): kept and exported under off_list/;
  * 0239_orai_s (a v3 rename, old words): still moves to 0239_oras_s; that take was re-recorded in batch 3 and is off
    the sheet now, so the old clip leaves under off_list/ (kept, not lost).
Clicks "Enable microphone & start", presses Export all, lists the ZIP, and checks the take count, the KEY_MAP, no
console errors, the re-take entry, and that every seeded blob comes out exactly once where expected. Exit 1 on a fail.
"""
import asyncio, io, json, os, shutil, subprocess, sys, tempfile, time, zipfile
from playwright.async_api import async_playwright

SEED = [("0650_greitai_s", "Autobusas atvažiuos greitai."), ("0263_tik", "tìk"), ("0650_greitai", "greĩtai"),
        ("0239_orai_s", "Kokie šiandien orai?")]
EXPECT = {"0650_greitai_s": "superseded", "0263_tik": "0263_tik", "0650_greitai": "off_list",
          "0239_orai_s": "off_list"}
PORT = 8767


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
            rt = await pg.evaluate("(WORDS.find(w => w.key === '0650_greitai_s') || {})")
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
    print("0650_greitai_s on the sheet:", json.dumps({k: rt.get(k) for k in ("status", "was", "say")}, ensure_ascii=False))
    if rt.get("status") != "retake" or rt.get("was") != "Autobusas atvažiuos greitai." or rt.get("say") != "Autobusas greitai atvažiuos.":
        fails.append(f"0650_greitai_s is not a re-take with the old words: {rt}")
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
        ok = (hits[0].startswith(where + "/") if where in ("superseded", "off_list")
              else hits[0].split("/")[-1].startswith(where + "."))
        print(f"CHECK {k:32} -> {hits[0]:60} {'ok' if ok else 'UNEXPECTED (expected ' + where + ')'}")
        if not ok:
            fails.append(f"{k}: came out as {hits[0]}, expected {where}")
    for f in fails:
        print("FAIL", f)
    print("RESULT:", "PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1])))
