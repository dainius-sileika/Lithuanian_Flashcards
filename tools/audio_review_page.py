#!/usr/bin/env python3
"""audio_review_page.py — a listening page for one batch of processed recorder takes, for the owner.

    python3 tools/ingest_takes.py <zip> --process-only OUT/proc          # process, touch nothing else
    python3 tools/audio_review_page.py <zip> OUT/proc OUT/page [--july 0027_suo,1035_karve,0953_arklys]
            [--title "Audio batch 2 check"] [--section "Batch 2"] [--mixed mixed.tsv]
            [--relevel _archive/takes/<relevel run> [--relevel-proc DIR] [--masters-root PROJECT_ROOT]] [--pack MB]
            [--db audio_b2] [--html-only [--packs-from PUBLISHED_PAGE_DIR]]

Writes OUT/page/index.html and OUT/page/media/: for every take the original as recorded (an mp3 listening copy of
the webm, 48 kHz 128 kbit/s, no other change, so Safari plays it too) and the processed mp3 exactly as it will ship,
plus one before/after waveform PNG (original on top with the removed parts shaded and every click marked; the
processed take below, on the same time axis). Flagged takes come first. A few July takes are added as loudness
references. Publish the folder as an artifact (index.html + media/ as files).
  --mixed       the table of tools/check_mixed_takes.py: those takes are marked "re-record" (two recordings in one).
  --pack MB     pack the media into media/pack_NN.json files of about MB megabytes each (base64; the page loads a
                pack when a card scrolls near and plays the clips from blob URLs). A published artifact holds at most 511
                files, so a batch of hundreds of takes (three files each) must be packed; batch 2 (483 takes + 63
                re-levelled) was. The unpacked files are kept in OUT/media_files/.
  --relevel     a run folder of tools/relevel_takes.py: a second section, "July takes re-levelled", with the take as
                it shipped before (media/audio/_history/...) and as re-processed (its dest, or --relevel-proc/<key>.mp3
                before --apply), both drawn on the raw master's time axis, so the owner hears that only the loudness
                changed and sees that nothing was cut into the words.
  --db NAME     the owner answers on the page: every take gets three buttons (processed is good / use the original
                instead: the raw take with loudness only, no cuts / re-record) and a note. Answers are saved in the
                artifact's database, collection NAME, one document per take key {choice, note, updatedAt}, with
                choice "processed" | "original" | "rerecord" | "" (unanswered = ships as processed). Publish with
                capabilities {db: {}, user: {}}; without them (or in a plain browser) answers stay in localStorage.
                Read them back with ArtifactData list on NAME. Default collection: audio_review.
  --html-only   rewrite index.html only, for a page whose media are already published: no ffmpeg, no media copied.
                <zip> may then be the batch's archived manifest.tsv. With --packs-from DIR, the clips are mapped to
                the packs already in DIR/media/pack_NN.json (names read from the packs, nothing re-packed), so the
                page can be republished without its 19 packs.
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


def waveform_relevel(master, old, new, r, png):
    """Old shipped take (top) and re-processed take (bottom), both on the raw master's time axis, own scales."""
    lag, hc, tc = int(r["identity_lag_ms"]), int(r["head_cut_ms"]), int(r["tail_cut_ms"])
    t_old = np.arange(len(old)) / SR * 1000 - lag
    t_new = hc + np.arange(len(new)) / SR * 1000
    dur = max(len(master) / SR * 1000, t_old[-1] if len(old) else 0)
    fig, ax = plt.subplots(2, 1, figsize=(9, 2.6), sharex=True)
    fig.patch.set_alpha(0)
    grey, ink, cut = "#7d8794", "#2f6f8f", "#d9822b"
    for a in ax:
        a.set_facecolor("none")
        for sp in a.spines.values():
            sp.set_visible(False)
        a.tick_params(colors=grey, labelsize=7, length=2)
        a.set_yticks([])
        a.axvspan(int(r["onset_ms"]), int(r["offset_ms"]), color=ink, alpha=0.08, lw=0)
    if len(old):
        ax[0].plot(t_old, old / max(1e-6, float(np.abs(old).max())), color=grey, lw=0.4)
    ax[0].axvspan(min(0, t_old[0] if len(old) else 0), hc, color=cut, alpha=0.28, lw=0)
    ax[0].axvspan(tc, dur, color=cut, alpha=0.28, lw=0)
    ax[0].set_ylim(-1.05, 1.05)
    ax[0].text(t_old[0] if len(old) else 0, 1.0, f"as shipped before ({f(r['shipped_I'])} LUFS, own scale)", color=grey, fontsize=7, va="top")
    if len(new):
        ax[1].plot(t_new, new / max(1e-6, float(np.abs(new).max())), color=ink, lw=0.4)
    ax[1].set_ylim(-1.05, 1.05)
    ax[1].text(t_old[0] if len(old) else 0, 1.0, f"re-levelled ({f(r['out_I'])} LUFS, own scale)", color=grey, fontsize=7, va="top")
    ax[1].set_xlim(min(0, t_old[0] if len(old) else 0), dur)
    ax[1].set_xlabel("ms (time in the raw recording)", color=grey, fontsize=7)
    fig.tight_layout(pad=0.3, h_pad=0.2)
    fig.savefig(png, dpi=110, transparent=True)
    plt.close(fig)


PACK_JS = """<script>
/* media packs: each card's clips and picture are fetched with the pack that holds them, when the card nears the view */
(() => {
  const packs = {};
  const pack = n => packs[n] || (packs[n] = fetch("media/pack_" + n + ".json").then(r => r.json()));
  const load = card => card.querySelectorAll("[data-pack]").forEach(el => {
    pack(el.dataset.pack).then(p => {
      const b64 = p[el.dataset.name];
      if (!b64) return;
      const bin = atob(b64), u = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
      el.src = URL.createObjectURL(new Blob([u], {type: el.tagName === "IMG" ? "image/png" : "audio/mpeg"}));
      el.removeAttribute("data-pack");
    });
  });
  const cards = document.querySelectorAll(".take, .ref");
  if (!("IntersectionObserver" in window)) { cards.forEach(load); return; }
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { io.unobserve(e.target); load(e.target); } }),
                                      {rootMargin: "1200px 0px"});
  cards.forEach(c => io.observe(c));
})();
</script>
"""


def pack_media(out, mb):
    """Rewrite index.html so every media/<file> it plays or shows comes from media/pack_NN.json (base64), in page
    order, about mb MB per pack; the single files move to OUT/media_files/."""
    import base64
    import re
    page = open(os.path.join(out, "index.html"), encoding="utf-8").read()
    pat = re.compile(r'(<(?:audio|img)\b[^>]*?) src="media/([^"]+)"')
    names = []
    for m in pat.finditer(page):
        if m.group(2) not in names:
            names.append(m.group(2))
    where, cur, size, n = {}, {}, 0, 0
    media = os.path.join(out, "media")

    def flush():
        nonlocal cur, size, n
        if cur:
            json.dump(cur, open(os.path.join(media, f"pack_{n:02d}.json"), "w"), separators=(",", ":"))
            n, cur, size = n + 1, {}, 0
    for name in names:
        data = open(os.path.join(media, name), "rb").read()
        if size and size + len(data) > mb * 1e6:
            flush()
        cur[name] = base64.b64encode(data).decode("ascii")
        where[name] = n
        size += len(data)
    flush()
    keep = os.path.join(out, "media_files")
    os.makedirs(keep, exist_ok=True)
    for name in names:
        shutil.move(os.path.join(media, name), os.path.join(keep, name))
    return map_to_packs(out, where), len(names)


def map_to_packs(out, where):
    """Point every media/<file> of index.html at the pack that holds it (where: name -> pack number)."""
    import re
    page = open(os.path.join(out, "index.html"), encoding="utf-8").read()
    pat = re.compile(r'(<(?:audio|img)\b[^>]*?) src="media/([^"]+)"')
    missing = sorted({m.group(2) for m in pat.finditer(page)} - set(where))
    if missing:
        raise SystemExit(f"not in any pack: {', '.join(missing[:10])}{' …' if len(missing) > 10 else ''}")
    page = pat.sub(lambda m: f'{m.group(1)} data-pack="{where[m.group(2)]:02d}" data-name="{m.group(2)}"', page)
    page = page.replace("</main>", "</main>\n" + PACK_JS, 1)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
    return len(set(where.values()))


def packs_in(page_dir):
    """name -> pack number, read from the packs already built in page_dir/media/pack_NN.json."""
    import glob
    where = {}
    for p in sorted(glob.glob(os.path.join(page_dir, "media", "pack_*.json"))):
        n = int(os.path.basename(p)[5:-5])
        for name in json.load(open(p)):
            where[name] = n
    if not where:
        raise SystemExit(f"no media/pack_NN.json in {page_dir}")
    return where


def opt(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    zpath, proc_dir, out = argv[1], argv[2], argv[3]
    july = opt(argv, "--july", "0027_suo,1035_karve,0953_arklys").split(",")
    title = opt(argv, "--title", "Audio batch check")
    section = opt(argv, "--section", "Takes")
    dbname = opt(argv, "--db", "audio_review")
    html_only = "--html-only" in argv
    mixed = {}
    if "--mixed" in argv:
        for m in csv.DictReader(open(opt(argv, "--mixed"), encoding="utf-8"), delimiter="\t"):
            mixed.setdefault(m["mixed_take"], []).append(m)
    media = os.path.join(out, "media")
    os.makedirs(media, exist_ok=True)
    if zpath.endswith(".tsv"):                                  # the archived manifest of an ingested batch
        z, stem = None, os.path.basename(os.path.dirname(os.path.abspath(zpath)))
        mtext = open(zpath, encoding="utf-8").read()
    else:
        z, stem = zipfile.ZipFile(zpath), os.path.splitext(os.path.basename(zpath))[0]
        mtext = z.read("manifest.tsv").decode("utf-8")
    if z is None and not html_only:
        raise SystemExit("a manifest.tsv instead of the ZIP works with --html-only only")
    man = {m["key"]: m for m in csv.DictReader(io.StringIO(mtext), delimiter="\t")}
    rows = list(csv.DictReader(open(os.path.join(proc_dir, "process_log.csv"), encoding="utf-8")))
    tmp = os.path.join(out, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    items = []
    for r in rows:
        k = r["take"]
        r["no_words"] = r.get("onset_ms", "") == ""            # "no speech found": the tool measured nothing more
        for c, v in (("head_cut_ms", "0"), ("tail_cut_ms", r["dur_ms"]), ("onset_ms", "0"), ("offset_ms", "0"),
                     ("head_margin_ms", "0"), ("tail_margin_ms", "0")):
            if r.get(c, "") == "":
                r[c] = v
        if k in mixed:
            r["mixed"] = "; ".join(f"contains the take {m['contains']} at {m['at_ms']} ms (r = {m['r']}): "
                                   "two recordings in one take (recorder bug before the fix), re-record" for m in mixed[k])
        if html_only:
            items.append(r)
            continue
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
    jl = []
    for k in july:
        src = os.path.join(ROOT, "media", "audio", k + ".mp3")
        if os.path.exists(src):
            if not html_only:
                shutil.copyfile(src, os.path.join(media, "july_" + k + ".mp3"))
            i, tp = loud(src)
            jl.append((k, i, tp))
    items.sort(key=lambda r: (not r.get("mixed"), r["status"] == "ok", not r["flags"], r["take"]))
    rel_items = []
    if "--relevel" in argv:
        rdir, rproc = opt(argv, "--relevel"), opt(argv, "--relevel-proc")
        for r in csv.DictReader(open(os.path.join(rdir, "process_log.csv"), encoding="utf-8")):
            if r["status"] != "ok":
                continue
            k = r["take"]
            if html_only:
                rel_items.append(r)
                continue
            old = os.path.join(ROOT, r["history"] or r["dest"])
            new = os.path.join(rproc, k + ".mp3") if rproc else os.path.join(ROOT, r["dest"])
            shutil.copyfile(old, os.path.join(media, "rl_" + k + ".old.mp3"))
            shutil.copyfile(new, os.path.join(media, "rl_" + k + ".new.mp3"))
            master = opt(argv, "--masters-root")
            mpath = os.path.join(master, r["master"]) if master else None
            mx = dec(mpath) if mpath and os.path.exists(mpath) else dec(old)
            waveform_relevel(mx, dec(old), dec(new), r, os.path.join(media, "rl_" + k + ".png"))
            rel_items.append(r)
        rel_items.sort(key=lambda r: (not r["flags"], float(r["shipped_I"])))
    shutil.rmtree(tmp, ignore_errors=True)
    write_html(out, stem, items, man, jl, title, section, rel_items, dbname)
    if html_only and "--packs-from" in argv:
        npk = map_to_packs(out, packs_in(opt(argv, "--packs-from")))
        print(f"clips mapped to the {npk} packs already in {opt(argv, '--packs-from')}/media (not re-packed)")
    elif html_only and "--pack" in argv:
        raise SystemExit("--html-only with --pack needs --packs-from (the published page's folder)")
    elif "--pack" in argv:
        npk, nf = pack_media(out, float(opt(argv, "--pack")))
        print(f"packed {nf} media files into {npk} packs (media/pack_NN.json)")
    print(f"{out}/index.html: {len(items)} takes ({sum(1 for r in items if r['flags'])} flagged, "
          f"{sum(1 for r in items if r.get('mixed'))} mixed), {len(rel_items)} re-levelled, {len(jl)} July references")
    return 0


def f(x, nd=1):
    try:
        return f"{float(x):.{nd}f}".replace("-", "−")
    except (TypeError, ValueError):
        return "–"


CHOICES = (("processed", "Processed is good"), ("original", "Use the original instead"), ("rerecord", "Re-record"))


def answer_block(k, said, can_process=True, july=False):
    """The owner's answer for one take: three buttons and a note. ANSWER_JS saves it."""
    labels = dict(CHOICES)
    if july:
        labels["processed"] = "Re-levelled is good"
    btns = "".join(
        f'<button type="button" data-choice="{c}" aria-pressed="false"'
        f'{" disabled" if c == "processed" and not can_process else ""}>{labels[c]}</button>' for c, _ in CHOICES)
    default = ("ships re-levelled" if july else "ships as processed") if can_process else \
        "the take has no processed file, so it stays on the recording sheet"
    return f"""<div class="answer" data-default="{html.escape(default)}">
    <div class="choices" role="group" aria-label="Your answer for {html.escape(k)}">{btns}</div>
    <label class="notelab">Note (optional)<textarea rows="2" placeholder="e.g. click still audible at the end" aria-label="Note for {html.escape(k)} {html.escape(said)}"></textarea></label>
    <p class="astate" aria-live="polite">Not answered: {html.escape(default)}.</p>
  </div>"""


ANSWER_CSS = """
/* Answers: three plain buttons and a note per take; a sticky bar with the count and the filter. */
.bar { position: sticky; top: 0; z-index: 5; background: var(--bg); border-bottom: 1px solid var(--line);
  margin: 0 -4px; padding: 8px 4px; display: flex; flex-wrap: wrap; align-items: center; gap: 6px 14px; }
.bar .count { font-weight: 600; font-variant-numeric: tabular-nums; }
.bar .count small { font-weight: 400; color: var(--muted); }
.bar .mode { font-size: .8rem; color: var(--muted); flex: 1 1 100%; }
.take, h2 { scroll-margin-top: 8rem; }
.filter { display: flex; flex-wrap: wrap; gap: 4px; }
.filter button { font: 500 .82rem var(--body); padding: 4px 10px; border-radius: 99px; border: 1px solid var(--line);
  background: var(--surface); color: var(--fg); cursor: pointer; }
.filter button[aria-pressed="true"] { background: var(--fg); color: var(--bg); border-color: var(--fg); }
.howto { background: var(--surface); border: 1px solid var(--accent); border-radius: 6px; padding: 12px 16px; display: grid; gap: 6px; }
.howto p { max-width: none; }
.howto dl { margin: 0; display: grid; gap: 2px; font-size: .9rem; }
.howto dt { display: inline; font-weight: 600; }
.howto dd { display: inline; margin: 0; color: var(--muted); }
.answer { display: grid; gap: 8px; border-top: 1px solid var(--line); padding-top: 10px; }
.choices { display: flex; flex-wrap: wrap; gap: 8px; }
.choices button { flex: 1 1 10em; min-height: 40px; padding: 8px 12px; border-radius: 6px; cursor: pointer;
  font: 600 .9rem var(--body); color: var(--fg); background: var(--bg); border: 1px solid var(--line); }
.choices button:hover:not(:disabled) { border-color: var(--accent); }
.choices button:disabled { opacity: .45; cursor: not-allowed; }
.take:not([data-answered]) .choices button[data-choice="processed"]:not(:disabled) { border: 1px dashed var(--accent); }
.choices button[aria-pressed="true"] { color: var(--surface); }
.choices button[data-choice="processed"][aria-pressed="true"] { background: var(--ok); border-color: var(--ok); }
.choices button[data-choice="original"][aria-pressed="true"] { background: var(--flag); border-color: var(--flag); }
.choices button[data-choice="rerecord"][aria-pressed="true"] { background: var(--fail); border-color: var(--fail); }
.notelab { display: grid; gap: 4px; font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.notelab textarea { width: 100%; box-sizing: border-box; resize: vertical; min-height: 2.8em; padding: 6px 8px;
  font: 400 .92rem/1.4 var(--body); text-transform: none; letter-spacing: 0; color: var(--fg); background: var(--bg);
  border: 1px solid var(--line); border-radius: 4px; }
.astate { font-size: .82rem; color: var(--muted); }
.take[data-answered] .astate { color: var(--fg); }
.take[hidden] { display: none; }
"""


ANSWER_JS = r"""<script>
/* Answers. One document per take in the artifact's database (collection COL, id = take key):
   {choice: "processed"|"original"|"rerecord"|"", note, updatedAt}. localStorage keeps a copy on this device and is
   the only store when the database is not available (a plain browser, or a viewer who cannot write). */
(() => {
  const COL = __COL__, LS = "audio_review:" + COL, LSF = LS + ":filter";
  const NAMES = {processed: "Processed is good", original: "Use the original instead", rerecord: "Re-record"};
  const cards = [...document.querySelectorAll("article.take[data-key]")];
  const byKey = new Map(cards.map(c => [c.dataset.key, c]));
  const $ = id => document.getElementById(id);
  let answers = {};
  try { answers = JSON.parse(localStorage.getItem(LS) || "{}") || {}; } catch (e) { answers = {}; }
  const saveLocal = () => { try { localStorage.setItem(LS, JSON.stringify(answers)); } catch (e) { /* private mode */ } };
  let db = null, mode = "connecting";
  const setMode = (m, extra) => {
    mode = m;
    $("ans-mode").textContent = {
      connecting: "Connecting to the page's storage…",
      db: "Answers are saved with this page.",
      local: "Answers are saved in this browser only: the page's own storage is not available here.",
      readonly: "You cannot save answers to this page; they are kept in this browser only.",
    }[m] + (extra ? " " + extra : "");
  };
  const ser = a => JSON.stringify([a.choice || "", a.note || ""]);
  const written = {}, chain = {}, timers = {};

  function render(key) {
    const card = byKey.get(key), a = answers[key] || {}, choice = a.choice || "";
    card.querySelectorAll(".choices button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.choice === choice)));
    const ta = card.querySelector("textarea");
    if (document.activeElement !== ta && ta.value !== (a.note || "")) ta.value = a.note || "";
    if (choice) card.dataset.answered = choice; else delete card.dataset.answered;
    const btn = card.querySelector(`.choices button[data-choice="${choice}"]`);
    card.querySelector(".astate").textContent = choice
      ? "Your answer: " + (btn ? btn.textContent : NAMES[choice]) + "." + (a.note ? " Note saved." : "")
      : "Not answered: " + card.querySelector(".answer").dataset.default + "." + (a.note ? " Note saved." : "");
  }

  function count() {
    let n = 0; const by = {processed: 0, original: 0, rerecord: 0};
    for (const k of byKey.keys()) { const c = (answers[k] || {}).choice; if (c) { n++; by[c] = (by[c] || 0) + 1; } }
    $("ans-n").textContent = n;
    $("ans-by").textContent = n ? ` (${by.processed} good · ${by.original} original · ${by.rerecord} re-record)` : "";
    applyFilter();
  }

  function push(key) {                      // one write at a time per take, only when the answer changed
    if (!db) return;
    chain[key] = (chain[key] || Promise.resolve()).then(async () => {
      const a = answers[key]; if (!a || written[key] === ser(a)) return;
      const body = {choice: a.choice || "", note: a.note || "", updatedAt: a.updatedAt || new Date().toISOString()};
      try {
        await db.collection(COL).doc(key).set(body);
        written[key] = ser(body);
      } catch (e) {
        if (e && e.code === "unavailable") {      // transient: one retry after a short pause
          await new Promise(r => setTimeout(r, 400 + Math.random() * 600));
          try { await db.collection(COL).doc(key).set(body); written[key] = ser(body); return; } catch (e2) { e = e2; }
        }
        if (e && e.code === "invalid_argument") { db = null; setMode("readonly"); }
        else setMode(mode, "Last answer not saved to the page (" + ((e && e.code) || "error") + "); it is kept in this browser.");
      }
    });
  }

  function change(key, patch) {
    answers[key] = Object.assign({choice: "", note: ""}, answers[key], patch, {updatedAt: new Date().toISOString()});
    saveLocal(); render(key); count();
  }

  document.addEventListener("click", e => {
    const b = e.target.closest(".choices button"); if (!b || b.disabled) return;
    const key = b.closest("article.take").dataset.key, cur = (answers[key] || {}).choice || "";
    change(key, {choice: cur === b.dataset.choice ? "" : b.dataset.choice});   // pressing the chosen one again clears it
    push(key);
  });
  document.addEventListener("input", e => {
    if (!e.target.matches(".answer textarea")) return;
    const key = e.target.closest("article.take").dataset.key;
    change(key, {note: e.target.value});
    clearTimeout(timers[key]); timers[key] = setTimeout(() => push(key), 900);
  });
  document.addEventListener("focusout", e => {
    if (!e.target.matches(".answer textarea")) return;
    const key = e.target.closest("article.take").dataset.key;
    if (timers[key]) { clearTimeout(timers[key]); timers[key] = null; push(key); }
  });

  let filter = "all";
  try { filter = localStorage.getItem(LSF) || "all"; } catch (e) { /* ignore */ }
  function applyFilter() {
    let shown = 0;
    for (const [k, card] of byKey) {
      const ans = !!(answers[k] || {}).choice;
      const show = filter === "all" || (filter === "flagged" && card.dataset.flagged === "1") ||
                   (filter === "answered" && ans) || (filter === "unanswered" && !ans);
      card.hidden = !show; if (show) shown++;
    }
    document.querySelectorAll(".filter button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.filter === filter)));
    $("ans-shown").textContent = filter === "all" ? "" : ` · ${shown} shown`;
  }
  document.querySelectorAll(".filter button").forEach(b => b.addEventListener("click", () => {
    filter = b.dataset.filter; try { localStorage.setItem(LSF, filter); } catch (e) { /* ignore */ }
    applyFilter();
  }));

  cards.forEach(c => render(c.dataset.key)); count(); setMode("connecting");

  (async () => {
    let d = null, user = null;
    try { d = window.claude && typeof window.claude.use === "function" ? await window.claude.use("db") : null; } catch (e) { d = null; }
    if (!d) { setMode("local"); return; }
    try { user = await window.claude.use("user"); } catch (e) { user = null; }
    try {
      const snap = await d.collection(COL).get();
      for (const doc of snap.docs) {
        if (!byKey.has(doc.id)) continue;
        const v = doc.data() || {}, mine = answers[doc.id];
        const theirs = {choice: v.choice || "", note: v.note || "", updatedAt: v.updatedAt || ""};
        written[doc.id] = ser(theirs);
        if (!mine || String(theirs.updatedAt) >= String(mine.updatedAt || "")) answers[doc.id] = theirs;
      }
    } catch (e) { setMode("local"); return; }
    let canWrite = null;
    try { canWrite = user && user.can ? await user.can("data.write") : null; } catch (e) { canWrite = null; }
    saveLocal(); cards.forEach(c => render(c.dataset.key)); count();
    if (canWrite === false) { setMode("readonly"); return; }
    db = d; setMode("db");
    for (const k of Object.keys(answers)) if (byKey.has(k) && written[k] !== ser(answers[k])) push(k);   // answered before the page connected
  })();
})();
</script>
"""


def write_html(out, stem, items, man, jl, title="Audio batch check", section="Takes", rel_items=(), dbname="audio_review"):
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
        state = "fail" if r.get("mixed") or r["status"] != "ok" else ("flag" if r["flags"] else "ok")
        label = "re-record" if r.get("mixed") else {"fail": "not processed", "flag": "listen", "ok": "clean"}[state]
        flags = "".join(f"<li>{html.escape(x)}</li>" for x in ((r.get("mixed") or "").split("; ") + r["flags"].split("; ")) if x)
        note = f'<p class="note">{html.escape(r["note"])}</p>' if r.get("note") else ""
        head = (f'cut {r["head_cut_ms"]} ms · {r["head_margin_ms"]} ms before the words' if int(r["head_cut_ms"]) > 0
                else "no head cut")
        tail = (f'cut at {r["tail_cut_ms"]} ms · {r["tail_margin_ms"]} ms after the words'
                if int(r["tail_cut_ms"]) < int(r["dur_ms"]) else f'no tail cut · {r["tail_margin_ms"]} ms after the words')
        proc_audio = (f'<audio controls preload="none" src="media/{k}.mp3"></audio>' if r["status"] == "ok"
                      else '<p class="na">No processed file: the take failed the self-check.</p>')
        cards.append(f"""
<article class="take {state}" id="t{k}" data-key="{k}"{' data-flagged="1"' if state != "ok" else ''}>
  <header>
    <h3><span class="k">{k}</span> <span class="said" lang="lt">{html.escape(said)}</span></h3>
    <span class="pill {state}">{label}</span>
  </header>
  <p class="eng">{html.escape(eng)}</p>
  {('<ul class="flags">' + flags + '</ul>') if flags else ''}
  <div class="players">
    <div><span class="lab">Original (as recorded)</span><audio controls preload="none" src="media/{k}.orig.mp3"></audio></div>
    <div><span class="lab">Processed (what ships)</span>{proc_audio}</div>
  </div>
  <img src="media/{k}.png" alt="Waveform of {k} before and after processing" loading="lazy">
  <dl class="nums">
    <div><dt>Words</dt><dd>{"none found by the tool in " + r["dur_ms"] + " ms" if r.get("no_words") else r["onset_ms"] + "–" + r["offset_ms"] + " ms of " + r["dur_ms"]}</dd></div>
    <div><dt>Head</dt><dd>{"–" if r.get("no_words") else head}</dd></div>
    <div><dt>Tail</dt><dd>{"–" if r.get("no_words") else tail}</dd></div>
    <div><dt>Clicks</dt><dd>{html.escape((r["head_clicks"] + " | " + r["tail_clicks"]).strip(" |") or "none")}{(" · attenuated " + html.escape(r["attenuated"])) if r["attenuated"] else ""}</dd></div>
    <div><dt>Loudness</dt><dd>{f(r["raw_I"])} → {f(r["out_I"])} LUFS · peak {f(r["out_TP"])} dBTP</dd></div>
    <div><dt>Speech energy kept</dt><dd>{f(r["energy_kept_pct"], 3)} %</dd></div>
  </dl>
  {note}
  {answer_block(k, said, can_process=r["status"] == "ok")}
</article>""")
    rel_cards = []
    for r in rel_items:
        k = r["take"]
        flags = "".join(f"<li>{html.escape(x)}</li>" for x in r["flags"].split("; ") if x)
        state = "flag" if r["flags"] else "ok"
        ends = int(r["offset_ms"]) >= int(r["dur_ms"]) - 10
        enote = ('<p class="note">The raw recording ends while the words still sound (the July recorder stopped there); '
                 'the old file only had silence added after it. Listen whether the end of the word is clipped.</p>') if ends else ""
        head = (f'cut {r["head_cut_ms"]} ms · {r["head_margin_ms"]} ms before the words' if int(r["head_cut_ms"]) > 0
                else "no head cut")
        tail = (f'cut at {r["tail_cut_ms"]} ms · {r["tail_margin_ms"]} ms after the words'
                if int(r["tail_cut_ms"]) < int(r["dur_ms"]) else f'no tail cut · the recording ends {r["tail_margin_ms"]} ms after the words')
        rel_cards.append(f"""
<article class="take {state}" id="r{k}" data-key="{k}"{' data-flagged="1"' if state != "ok" else ''}>
  <header>
    <h3><span class="k">{k}</span> <span class="said" lang="lt">{html.escape(r["said"])}</span></h3>
    <span class="pill {state}">{"listen" if r["flags"] else "level only"}</span>
  </header>
  <p class="eng">Raw master {html.escape(r["master"])} (same recording as the shipped take: r = {html.escape(r["identity_r"])})</p>
  {('<ul class="flags">' + flags + '</ul>') if flags else ''}
  <div class="players">
    <div><span class="lab">Before (shipped until now)</span><audio controls preload="none" src="media/rl_{k}.old.mp3"></audio></div>
    <div><span class="lab">Re-levelled (what ships)</span><audio controls preload="none" src="media/rl_{k}.new.mp3"></audio></div>
  </div>
  <img src="media/rl_{k}.png" alt="Waveform of {k} as shipped before and re-levelled" loading="lazy">
  <dl class="nums">
    <div><dt>Words</dt><dd>{r["onset_ms"]}–{r["offset_ms"]} ms of {r["dur_ms"]}</dd></div>
    <div><dt>Head</dt><dd>{head}</dd></div>
    <div><dt>Tail</dt><dd>{tail}</dd></div>
    <div><dt>Loudness</dt><dd>{f(r["shipped_I"])} → {f(r["out_I"])} LUFS · peak {f(r["out_TP"])} dBTP</dd></div>
    <div><dt>Speech energy kept</dt><dd>{f(r["energy_kept_pct"], 3)} %</dd></div>
    <div><dt>Gain</dt><dd>{f(r["gain_db"])} dB, one fixed gain</dd></div>
  </dl>
  {enote}
  {answer_block(k, r["said"], july=True)}
</article>""")
    rel_section = ""
    if rel_items:
        rb = [float(r["shipped_I"]) for r in rel_items]
        ra = [float(r["out_I"]) for r in rel_items]
        rel_section = f"""
  <h2 id="july">July takes re-levelled</h2>
  <section class="how">
    <p>{len(rel_items)} July takes had shipped {f(min(rb))} to {f(max(rb))} LUFS (median {f(med(rb))}), 20–30 dB below the rest of the deck. Each was re-processed from its raw master exactly like a new take: one fixed gain, no limiter, the start click cut away only where 250 ms of silence stays before the words. Median now {f(med(ra))} LUFS. Compare the two players: the words should sound the same, only louder. Here <b>Re-levelled is good</b> keeps the new file; <b>Use the original instead</b> ships the raw July recording with its loudness raised only, no cuts at all. Takes marked <b>listen</b> first: {sum(1 for r in rel_items if r["flags"])} keep a sound the tool could not safely call a click (the July processing had simply cut the first 150 ms of every take; the new one never cuts within 250 ms of the words, so a start click that close now stays). In {sum(1 for r in rel_items if int(r["offset_ms"]) >= int(r["dur_ms"]) - 10)} the raw recording itself ends while the word still sounds.</p>
  </section>
  {''.join(rel_cards)}"""
    page = f"""<meta charset="utf-8">
<title>{html.escape(title)}</title>
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
.eng {{ color: var(--muted); font-size: .9rem; margin-top: -6px; overflow-wrap: anywhere; }}
.take > * {{ min-width: 0; }}
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
{ANSWER_CSS}
</style>
<main>
  <div>
    <h1>{html.escape(title)}</h1>
    <p class="lede">{len(items)} takes from <span class="k">{html.escape(stem)}.zip</span>. Each card has the take as you recorded it and as it will ship. Takes marked <b>re-record</b> (two recordings in one take) or <b>not processed</b> come first, then <b>listen</b>: the tool kept a sound it could not safely call a click.{(' The second section, <a href="#july">July takes re-levelled</a>, has ' + str(len(rel_items)) + ' older takes as they shipped before and as they ship now.') if rel_items else ''}</p>
  </div>
  <section class="howto" aria-label="How to use this page">
    <p><b>How to use this page.</b> For each take: listen to both, then pick one. Unanswered takes ship as processed.</p>
    <dl>
      <div><dt>Processed is good</dt> <dd>— ship the processed take (the default for every take you leave unanswered).</dd></div>
      <div><dt>Use the original instead</dt> <dd>— ship the raw take with its loudness raised only, no cuts.</dd></div>
      <div><dt>Re-record</dt> <dd>— the take goes back on the recording sheet.</dd></div>
    </dl>
    <p class="legend">Add a note if something needs saying. Your answers are saved as you go; press a chosen button again to clear it.</p>
  </section>
  <div class="bar" role="region" aria-label="Answers">
    <span class="count">Answered <span id="ans-n">0</span> of {len(items) + len(rel_items)}<small id="ans-by"></small><small id="ans-shown"></small></span>
    <span class="filter" role="group" aria-label="Show">
      <button type="button" data-filter="all" aria-pressed="true">All</button><button type="button" data-filter="flagged" aria-pressed="false">Flagged</button><button type="button" data-filter="answered" aria-pressed="false">Answered</button><button type="button" data-filter="unanswered" aria-pressed="false">Unanswered</button>
    </span>
    <span class="mode" id="ans-mode">Answers are saved in this browser.</span>
  </div>
  <section class="summary" aria-label="Batch summary">
    <div class="stat"><b>{len(ok)} / {len(items)}</b><span>passed the self-check</span></div>
    <div class="stat"><b>{len(flagged)}</b><span>to listen to</span></div>
    <div class="stat"><b>{sum(1 for r in items if r.get("mixed"))}</b><span>to re-record (two takes in one)</span></div>
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
  <h2 id="batch">{html.escape(section)}</h2>
  {''.join(cards)}{rel_section}
</main>
{ANSWER_JS.replace("__COL__", json.dumps(dbname))}"""
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
