#!/usr/bin/env python3
"""audio_review_page.py — a listening page for one batch of processed recorder takes, for the owner.

    python3 tools/ingest_takes.py <zip> --process-only OUT/proc          # process, touch nothing else
    python3 tools/audio_review_page.py <zip> OUT/proc OUT/page [--july 0027_suo,1035_karve,0953_arklys]

Writes OUT/page/index.html and OUT/page/media/: for every take the original as recorded (an mp3 listening copy of
the webm, 48 kHz 128 kbit/s, no other change, so Safari plays it too) and the processed mp3 exactly as it will ship,
plus one before/after waveform PNG (original on top with the removed parts shaded and every click marked; the
processed take below, on the same time axis). Flagged takes come first. A few July takes are added as loudness
references. Publish the folder as an artifact (index.html + media/ as files).
"""
import csv
import html
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 24000


def dec(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def spans(s):
    out = []
    for part in (s or "").split():
        a, b = part.split("(")[0].split("-")
        out.append((int(a), int(b)))
    return out


def waveform(orig, proc, r, png):
    t0 = np.arange(len(orig)) / SR * 1000
    hc, tc = int(r["head_cut_ms"]), int(r["tail_cut_ms"])
    t1 = hc + np.arange(len(proc)) / SR * 1000
    dur = max(t0[-1], t1[-1]) if len(proc) else t0[-1]
    fig, ax = plt.subplots(2, 1, figsize=(9, 2.6), sharex=True)
    fig.patch.set_alpha(0)
    grey, ink, cut, mark = "#7d8794", "#2f6f8f", "#d9822b", "#c2410c"
    for a in ax:
        a.set_facecolor("none")
        for sp in a.spines.values():
            sp.set_visible(False)
        a.tick_params(colors=grey, labelsize=7, length=2)
        a.set_yticks([])
    m0 = max(1e-6, float(np.abs(orig).max()))
    ax[0].plot(t0, orig / m0, color=grey, lw=0.4)
    ax[0].axvspan(0, hc, color=cut, alpha=0.28, lw=0)
    ax[0].axvspan(tc, t0[-1], color=cut, alpha=0.28, lw=0)
    ax[0].axvspan(int(r["onset_ms"]), int(r["offset_ms"]), color=ink, alpha=0.08, lw=0)
    for a_, b_ in spans(r["head_clicks"]) + spans(r["tail_clicks"]):
        ax[0].axvspan(a_, b_, color=mark, alpha=0.55, lw=0)
    ax[0].set_ylim(-1.05, 1.05)
    ax[0].text(0, 1.0, "original (own scale)", color=grey, fontsize=7, va="top")
    if len(proc):
        m1 = max(1e-6, float(np.abs(proc).max()))
        ax[1].plot(t1, proc / m1, color=ink, lw=0.4)
    ax[1].set_ylim(-1.05, 1.05)
    ax[1].text(0, 1.0, "processed (own scale)", color=grey, fontsize=7, va="top")
    ax[1].set_xlim(0, dur)
    ax[1].set_xlabel("ms", color=grey, fontsize=7)
    fig.tight_layout(pad=0.3, h_pad=0.2)
    fig.savefig(png, dpi=110, transparent=True)
    plt.close(fig)


def loud(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=print_format=json",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(out[out.rindex("{"):])
    return float(j["input_i"]), float(j["input_tp"])


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    zpath, proc_dir, out = argv[1], argv[2], argv[3]
    july = ["0027_suo", "1035_karve", "0953_arklys"]
    if "--july" in argv:
        july = argv[argv.index("--july") + 1].split(",")
    media = os.path.join(out, "media")
    os.makedirs(media, exist_ok=True)
    z = zipfile.ZipFile(zpath)
    man = {m["key"]: m for m in csv.DictReader(io.StringIO(z.read("manifest.tsv").decode("utf-8")), delimiter="\t")}
    rows = list(csv.DictReader(open(os.path.join(proc_dir, "process_log.csv"), encoding="utf-8")))
    tmp = os.path.join(out, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    items = []
    for r in rows:
        k = r["take"]
        raw = os.path.join(tmp, os.path.basename(r["file"]))
        open(raw, "wb").write(z.read(r["file"]))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ar", "48000", "-ac", "1", "-codec:a", "libmp3lame",
                        "-b:a", "128k", os.path.join(media, k + ".orig.mp3")], check=True)
        pm = os.path.join(proc_dir, k + ".mp3")
        ok = r["status"] == "ok" and os.path.exists(pm)
        if ok:
            shutil.copyfile(pm, os.path.join(media, k + ".mp3"))
        waveform(dec(raw), dec(pm) if ok else np.zeros(0, np.float32), r, os.path.join(media, k + ".png"))
        items.append(r)
    shutil.rmtree(tmp, ignore_errors=True)
    jl = []
    for k in july:
        src = os.path.join(ROOT, "media", "audio", k + ".mp3")
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(media, "july_" + k + ".mp3"))
            i, tp = loud(src)
            jl.append((k, i, tp))
    items.sort(key=lambda r: (r["status"] == "ok", not r["flags"], r["take"]))
    write_html(out, os.path.splitext(os.path.basename(zpath))[0], items, man, jl)
    print(f"{out}/index.html: {len(items)} takes ({sum(1 for r in items if r['flags'])} flagged), {len(jl)} July references")
    return 0


def f(x, nd=1):
    try:
        return f"{float(x):.{nd}f}".replace("-", "−")
    except (TypeError, ValueError):
        return "–"


def write_html(out, stem, items, man, jl):
    ok = [r for r in items if r["status"] == "ok"]
    flagged = [r for r in items if r["flags"]]
    med = lambda v: float(np.median(v)) if v else float("nan")
    out_i = [float(r["out_I"]) for r in ok]
    raw_i = [float(r["raw_I"]) for r in ok]
    rem = [int(r["removed_head_ms"]) + int(r["removed_tail_ms"]) for r in ok]
    hm = [int(r["head_margin_ms"]) for r in ok if int(r["head_cut_ms"]) > 0]
    tm = [int(r["tail_margin_ms"]) for r in ok if int(r["tail_cut_ms"]) < int(r["dur_ms"])]
    july_rows = "".join(
        f'<div class="ref"><span class="k">{html.escape(k)}</span><span class="num">{f(i)} LUFS · {f(tp)} dBTP</span>'
        f'<audio controls preload="none" src="media/july_{html.escape(k)}.mp3"></audio></div>' for k, i, tp in jl)
    cards = []
    for r in items:
        k = r["take"]
        said = man.get(k, {}).get("said", r.get("said", ""))
        eng = man.get(k, {}).get("english", "")
        state = "fail" if r["status"] != "ok" else ("flag" if r["flags"] else "ok")
        label = {"fail": "not processed", "flag": "listen", "ok": "clean"}[state]
        flags = "".join(f"<li>{html.escape(x)}</li>" for x in r["flags"].split("; ") if x)
        note = f'<p class="note">{html.escape(r["note"])}</p>' if r.get("note") else ""
        head = (f'cut {r["head_cut_ms"]} ms · {r["head_margin_ms"]} ms before the words' if int(r["head_cut_ms"]) > 0
                else "no head cut")
        tail = (f'cut at {r["tail_cut_ms"]} ms · {r["tail_margin_ms"]} ms after the words'
                if int(r["tail_cut_ms"]) < int(r["dur_ms"]) else f'no tail cut · {r["tail_margin_ms"]} ms after the words')
        proc_audio = (f'<audio controls preload="none" src="media/{k}.mp3"></audio>' if r["status"] == "ok"
                      else '<p class="na">No processed file: the take failed the self-check.</p>')
        cards.append(f"""
<article class="take {state}" id="t{k}">
  <header>
    <h3><span class="k">{k}</span> <span class="said" lang="lt">{html.escape(said)}</span></h3>
    <span class="pill {state}">{label}</span>
  </header>
  <p class="eng">{html.escape(eng)}</p>
  {('<ul class="flags">' + flags + '</ul>') if flags else ''}
  <div class="players">
    <div><span class="lab">Original, as recorded</span><audio controls preload="none" src="media/{k}.orig.mp3"></audio></div>
    <div><span class="lab">Processed, as it will ship</span>{proc_audio}</div>
  </div>
  <img src="media/{k}.png" alt="Waveform of {k} before and after processing" loading="lazy">
  <dl class="nums">
    <div><dt>Words</dt><dd>{r["onset_ms"]}–{r["offset_ms"]} ms of {r["dur_ms"]}</dd></div>
    <div><dt>Head</dt><dd>{head}</dd></div>
    <div><dt>Tail</dt><dd>{tail}</dd></div>
    <div><dt>Clicks</dt><dd>{html.escape((r["head_clicks"] + " | " + r["tail_clicks"]).strip(" |") or "none")}{(" · attenuated " + html.escape(r["attenuated"])) if r["attenuated"] else ""}</dd></div>
    <div><dt>Loudness</dt><dd>{f(r["raw_I"])} → {f(r["out_I"])} LUFS · peak {f(r["out_TP"])} dBTP</dd></div>
    <div><dt>Speech energy kept</dt><dd>{f(r["energy_kept_pct"], 3)} %</dd></div>
  </dl>
  {note}
</article>""")
    page = f"""<title>Audio batch 1 check</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column; a summary band, then one card per take, takes to listen to first. */
:root {{
  --bg: #f6f7f8; --surface: #ffffff; --fg: #1d2329; --muted: #5d6873; --line: #dde2e7;
  --accent: #2f6f8f; --flag: #b45309; --flag-bg: #fdf3e6; --fail: #b42318; --ok: #2e7d4f;
  --body: "Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #14181c; --surface: #1c2227; --fg: #e4e8ec; --muted: #9aa5b0; --line: #2d353c;
  --accent: #7fb6d1; --flag: #f0a75a; --flag-bg: #2b2117; --fail: #f27b6e; --ok: #6cc596; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #14181c; --surface: #1c2227; --fg: #e4e8ec; --muted: #9aa5b0; --line: #2d353c;
  --accent: #7fb6d1; --flag: #f0a75a; --flag-bg: #2b2117; --fail: #f27b6e; --ok: #6cc596; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.5 var(--body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; }}
main {{ max-width: 860px; margin: 0 auto; display: grid; gap: 20px; }}
h1 {{ font-size: 1.6rem; margin: 0; text-wrap: balance; }}
h2 {{ font-size: 1.05rem; margin: 8px 0 0; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
p {{ margin: 0; max-width: 68ch; }}
.lede {{ color: var(--muted); }}
.summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }}
.stat {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 10px 12px; }}
.stat b {{ display: block; font: 500 1.25rem var(--mono); font-variant-numeric: tabular-nums; }}
.stat span {{ color: var(--muted); font-size: .82rem; }}
.how {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 12px 16px; }}
.how ul {{ margin: 6px 0 0; padding-left: 1.2em; display: grid; gap: 4px; }}
.refs {{ display: grid; gap: 8px; }}
.ref {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; }}
.ref .num {{ font: .82rem var(--mono); color: var(--muted); }}
.take {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; display: grid; gap: 10px; min-width: 0; }}
.take.flag {{ border-left: 4px solid var(--flag); }}
.take.fail {{ border-left: 4px solid var(--fail); }}
.take header {{ display: flex; justify-content: space-between; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
.take h3 {{ margin: 0; font-size: 1.1rem; font-weight: 600; }}
.k {{ font: 500 .85em var(--mono); color: var(--muted); }}
.said {{ font-weight: 700; }}
.eng {{ color: var(--muted); font-size: .9rem; margin-top: -6px; }}
.pill {{ font: 600 .72rem var(--body); text-transform: uppercase; letter-spacing: .07em; padding: 2px 8px; border-radius: 99px; border: 1px solid currentColor; }}
.pill.ok {{ color: var(--ok); }} .pill.flag {{ color: var(--flag); }} .pill.fail {{ color: var(--fail); }}
.flags {{ margin: 0; padding: 8px 12px 8px 28px; background: var(--flag-bg); border-radius: 4px; color: var(--fg); font-size: .9rem; }}
.players {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; }}
.players > div {{ display: grid; gap: 4px; min-width: 0; }}
.lab {{ font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
audio {{ width: 100%; max-width: 100%; height: 36px; }}
.take img {{ width: 100%; height: auto; display: block; border-top: 1px solid var(--line); padding-top: 6px; }}
.nums {{ margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 4px 16px; font-size: .85rem; }}
.nums div {{ display: flex; gap: 8px; min-width: 0; }}
.nums dt {{ color: var(--muted); flex: 0 0 8.5em; }}
.nums dd {{ margin: 0; font-family: var(--mono); font-size: .8rem; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }}
.note, .na {{ font-size: .82rem; color: var(--muted); }}
.legend {{ font-size: .85rem; color: var(--muted); }}
.sw {{ display: inline-block; width: .9em; height: .9em; vertical-align: -.1em; border-radius: 2px; margin-right: 3px; }}
</style>
<main>
  <div>
    <h1>Audio batch 1 check</h1>
    <p class="lede">{len(items)} takes from <span class="k">{html.escape(stem)}.zip</span>. Each card has the take as you recorded it and as it will ship. Takes marked <b>listen</b> come first: the tool kept a sound it could not safely call a click.</p>
  </div>
  <section class="summary" aria-label="Batch summary">
    <div class="stat"><b>{len(ok)} / {len(items)}</b><span>passed the self-check</span></div>
    <div class="stat"><b>{len(flagged)}</b><span>to listen to</span></div>
    <div class="stat"><b>{min(hm) if hm else '–'} ms</b><span>closest head cut to the words</span></div>
    <div class="stat"><b>{min(tm) if tm else '–'} ms</b><span>closest tail cut to the words</span></div>
    <div class="stat"><b>{f(med(raw_i))} → {f(med(out_i))}</b><span>median loudness, LUFS</span></div>
    <div class="stat"><b>{int(med(rem))} ms</b><span>median silence removed per take</span></div>
  </section>
  <section class="how">
    <h2>What was done</h2>
    <ul>
      <li>The key click at the start was cut away with the silence before the words, always leaving 250 ms before the first sound.</li>
      <li>At the end the take was cut 400 ms after the last sound, or just before the closing key click, never closer than 250 ms. A click that could not be cut away was turned down to the background level.</li>
      <li>Nothing between the first and the last sound was touched. A short sound just after the words (a final <i>p</i> or <i>t</i>, or a click) was kept.</li>
      <li>Volume raised with one fixed gain to the July level, at most −17 LUFS with peaks at or below −1.5 dBTP. No compression and no limiter, so very peaky takes stay a little quieter.</li>
    </ul>
    <p class="legend">Waveforms: <span class="sw" style="background:#d9822b66"></span>removed · <span class="sw" style="background:#c2410c"></span>key click · <span class="sw" style="background:#2f6f8f22"></span>words as detected.</p>
  </section>
  <section class="refs">
    <h2>July takes, for loudness</h2>
    {july_rows}
  </section>
  <h2>Takes</h2>
  {''.join(cards)}
</main>
"""
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
