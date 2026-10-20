"""Headless test of the recorder's key migration (build_recorder.migrateKeys), 2026-10-20.

    python3 a2_build/rename/recorder_migration_test_v2.py recorder_A2.html > a2_build/rename/recorder_migration_test_v2.txt

Seeds IndexedDB lt_recorder_A2_afb2ebe2 with clips under pre-rename keys (v1 old names, a v2 old name, a chained
name, a conflict with a clip already under the new key, an unstamped clip, an off-list key), clicks
"Enable microphone & start" (fake microphone), dumps both stores, then presses "Export all" and lists the ZIP.
Needs playwright + chromium. Expect: every seeded blob comes out once, under its new key or under superseded/.
"""
import asyncio, json, zipfile, io, subprocess, time, sys, os, shutil, tempfile
from playwright.async_api import async_playwright
SEED = [  # key, said (None = unstamped), payload
 ("A2-0348", "Lãbas"), ("A2-0154_s", "Perku duoną ir pieną."), ("A2-1702_s", "Vakare rakinu duris."),
 ("A2-1193", "Kurì valandà?"), ("1006_veikla", "veiklà · veiklos"), ("A2-0080_s", "Kõks jū́sų ámžius?"),
 ("0514_amzius_s", "Amžius – tik skaičius."), ("A2-0154", None), ("zzz_offlist", "x")]
async def main():
    root = tempfile.mkdtemp(); shutil.copy(sys.argv[1], os.path.join(root, "recorder_A2.html"))
    srv = subprocess.Popen([sys.executable, "-m", "http.server", "8765", "--bind", "127.0.0.1", "-d", root],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"])
            ctx = await b.new_context(accept_downloads=True); await ctx.grant_permissions(["microphone"], origin="http://127.0.0.1:8765")
            pg = await ctx.new_page(); await pg.goto("http://127.0.0.1:8765/recorder_A2.html")
            await pg.evaluate("""async (seed)=>{ await new Promise((res,rej)=>{const r=indexedDB.open('lt_recorder_A2_afb2ebe2',2);
              r.onupgradeneeded=e=>{const d=e.target.result; d.createObjectStore('clips'); d.createObjectStore('meta');};
              r.onsuccess=e=>{const d=e.target.result; const t=d.transaction(['clips','meta'],'readwrite');
                for(const [k,said] of seed){ t.objectStore('clips').put(new Blob(['clip-of-'+k],{type:'audio/webm'}),k);
                  if(said!==null) t.objectStore('meta').put(said,'said:'+k); }
                t.objectStore('meta').put(['A2-0348','zzz_offlist'],'exported');
                t.oncomplete=()=>{d.close();res()}; t.onerror=()=>rej(t.error);}; r.onerror=()=>rej(r.error);});}""", [list(s) for s in SEED])
            await pg.click("#start"); await pg.wait_for_selector("#app", state="visible", timeout=20000)
            info = await pg.inner_text("#storeInfo")
            dump = await pg.evaluate("""async ()=>{ const out={clips:{},meta:{}};
              for(const s of ['clips','meta']){ const t=db.transaction(s,'readonly'); const st=t.objectStore(s);
                const keys=await new Promise(r=>{const q=st.getAllKeys(); q.onsuccess=()=>r(q.result)});
                for(const k of keys){ const v=await new Promise(r=>{const q=db.transaction(s,'readonly').objectStore(s).get(k); q.onsuccess=()=>r(q.result)});
                  if(v instanceof Blob) out[s][k]='BLOB:'+(await v.text());
                  else if(v&&v.blob) out[s][k]={...v, blob:'BLOB:'+(await v.blob.text())};
                  else out[s][k]=v; } }
              return out;}""")
            async with pg.expect_download() as dl:
                await pg.click("#export")
            d = await dl.value; path = await d.path()
            z = zipfile.ZipFile(path); names = z.namelist(); man = z.read("manifest.tsv").decode()
            contents = {n: z.read(n).decode(errors="replace") for n in names if n != "manifest.tsv"}
            print("STOREINFO:", info); print(json.dumps(dump, ensure_ascii=False, indent=1))
            print("ZIP:", json.dumps(contents, ensure_ascii=False, indent=1)); print("MANIFEST:\n" + man)
            await b.close()
    finally:
        srv.terminate()
asyncio.run(main())
