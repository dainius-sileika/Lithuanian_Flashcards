#!/usr/bin/env python3
"""process_take.py — turn one raw recorder take (webm/opus from Chrome) into the deck's mp3: remove the key
clicks at both ends WITHOUT EVER CUTTING SPEECH, and bring the loudness to the July takes.

    python3 tools/process_take.py RAW.webm OUT.mp3 [--said "batònas · batono"] [--json] [--dry-run]
    (normally called by tools/ingest_takes.py for every take of a recorder ZIP)

Why (docs/LESSONS_LEARNED.md, Audio): in July three passes of silence gating cut word-final voiceless fricatives
(karves -> karve) and plosive onsets (dukra without its d), commit d55ec8b; the processing that replaced them was
never committed. This is that processing, written down, with guards. Nothing here is a silence gate: the only
cuts are in the noise floor, at least 250 ms from anything that might be speech.

ANALYSIS (decoded PCM, mono, 48 kHz, 5 ms frames)
  * Two bands: broadband 60 Hz-10 kHz and high 2.5-10 kHz (so a soft voiceless fricative counts on its own).
    Each band's noise floor = its 10th-percentile frame level in this take. A frame is ACTIVE when either band is
    more than 10 dB above its floor (a LOW threshold: soft onsets and devoiced finals are active). Active runs
    closer than 30 ms (hold) are one EVENT. A FLICKER (an event under 30 ms that stays within 20 dB of the floor
    in both bands) is never an anchor.
  * An event's CORE = its frames within 15 dB of its own peak. A key click is a sharp spike whose acoustic decay
    stays above floor + 10 dB for up to ~250 ms, so clicks are judged by the core, not by the extent.
  * HEAD CLICK (the Space press that starts the take; "SPEAK NOW" only shows at 400 ms): an event that starts in
    the first 250 ms, lasts at most 350 ms, has a core of at most 100 ms (the key-down and key-up clicks often
    merge into one event), and is followed by at least 150 ms before the next speech-like event.
  * SPEECH SEEDS: every other event with a core of at least 80 ms and a peak at least 30 dB over the floor.
    Starting from the seeds, every non-click event closer than 350 ms joins the speech (soft onsets, breaths,
    the separate low final -s); onset = start of the first speech event, offset = end of the last.
  * TAIL CLICK (the Space press that stops the take): a transient (core <= 50 ms) after the speech that starts
    at least 250 ms after the previous kept event. A transient closer than 250 ms to the words is NOT treated as a
    click (it may be a word-final release: taip); it is kept, and the take is flagged for listening.
  * Anything else before the onset or after the offset (ticks, a breath far from the words) is NOISE. Short weak
    noise (< 150 ms, peak < floor + 30 dB) may be cut with the floor; anything bigger blocks the cut and is flagged.

CUTS (any doubt -> no cut, and a flag)
  * Head: cut at onset - 250 ms, if > 0 and everything before the cut is clicks, flickers, short weak noise, floor.
  * Tail: cut at min(offset + 400 ms, first tail click or noise after the speech - 5 ms, end), never closer than
    250 ms to the offset; if the first click is closer than that, no tail cut (the click is attenuated, flagged).
  * A click left inside the kept part is attenuated to the noise floor over its own samples (+-5 ms) with 5 ms
    crossfades, only if it is at least 110 ms from the speech; otherwise it is left alone and flagged.
  * 5 ms fades at the cuts only (an uncut end of the file is left exactly as recorded).

SELF-CHECK (a failing take is NOT written; the caller leaves it unprocessed)
  * Identity: the kept signal equals the original sample for sample from onset - 100 ms to offset + 200 ms.
  * Energy: the kept part holds >= 99.5 % of the original's speech-band (60 Hz-10 kHz) energy, clicks excluded.
  * Margins: every cut is >= 250 ms from the speech.

LOUDNESS AND ENCODING (July takes: median -16.7 LUFS, true peak -1.85 dBTP over 512 normalised human takes;
  24 kHz mono CBR 64 kbit/s, libmp3lame — ffprobe of media/audio/0027_suo.mp3)
  * EBU R128 two-pass, LINEAR: pass 1 measures integrated loudness I and true peak TP of the kept, de-clicked
    audio (ffmpeg loudnorm analysis); pass 2 applies ONE static gain = min(-17 - I, -1.5 - TP). No limiter, no
    compression. The mp3 is then measured: one correction up if both limits leave room (0.2 dB kept below the
    ceiling), then down in steps until the mp3's true peak is <= -1.5 dBTP.
  * More loud sound groups (seeds joined across gaps < 350 ms) than forms said is flagged (an extra utterance?).
  * A take that ends below -18.5 LUFS (peaky: the true-peak ceiling limits the gain) gets a note (not a flag:
    nothing to listen for, it is only quieter).

A FLAG means "the owner should listen to this take"; status FAIL means the take was not written.
Returns / prints a dict with every number (cuts in ms, margins, loudness before/after, flags), which
ingest_takes.py writes to _archive/takes/<zip-stem>/process_log.csv.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt

SR = 48000
FRAME_MS = 5
HOP = SR * FRAME_MS // 1000
ACT_DB = 10.0           # activity threshold above the take's own floor (low on purpose)
HOLD_MS = 30            # active runs closer than this are one event
FLICKER_MS, FLICKER_DB = 30, 20.0
CORE_DB = 15.0          # core = frames within this of the event's peak
TRANSIENT_CORE_MS = 50  # a tail click's core is at most this
HEAD_ZONE_MS, HEAD_MAX_MS, HEAD_CORE_MS, HEAD_GAP_MS = 250, 350, 100, 150
SEED_CORE_MS, SEED_DB = 80, 30.0
JOIN_MS = 350           # events closer than this to the speech are speech
TAIL_GAP_MS = 250       # a tail click starts at least this long after the previous kept event
NOISE_MAX_MS, NOISE_MAX_DB = 150, 30.0
LEAD_MS = 250           # head cut = onset - LEAD_MS
TAIL_MS = 400           # tail cut = offset + TAIL_MS at most
MIN_TAIL_MS = 250       # never cut closer than this after the offset
GUARD_MS = 5            # cut this far before a tail click; click attenuation padding
FADE_MS = 5
ID_PRE_MS, ID_POST_MS = 100, 200
ATTEN_MIN_MS = 110      # attenuate a click only this far from the speech
ENERGY_MIN = 0.995
TARGET_I, TARGET_TP = -17.0, -1.5
LOW_I_FLAG = -18.5
MP3_ARGS = ["-ar", "24000", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "64k"]

_BB = butter(4, [60, 10000], btype="band", fs=SR, output="sos")
_HI = butter(4, [2500, 10000], btype="band", fs=SR, output="sos")


def f2ms(frames):
    return int(frames * FRAME_MS)


def s2ms(samples):
    return int(round(samples * 1000 / SR))


def ms2s(t):
    return int(round(t * SR / 1000))


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def frame_db(y):
    m = len(y) // HOP
    e = (y[:m * HOP].reshape(m, HOP) ** 2).mean(1)
    return 10 * np.log10(e + 1e-20)


def analyse(x):
    """Events and their classes (in 5 ms frames), onset/offset, the take's floors."""
    xb = sosfiltfilt(_BB, x)
    b, h = frame_db(xb), frame_db(sosfiltfilt(_HI, x))
    fb, fh = float(np.percentile(b, 10)), float(np.percentile(h, 10))
    act = (b > fb + ACT_DB) | (h > fh + ACT_DB)
    m = len(act)
    ev, i = [], 0
    while i < m:
        if act[i]:
            j = i
            while j < m and act[j]:
                j += 1
            if ev and i - ev[-1]["e"] < HOLD_MS // FRAME_MS:
                ev[-1]["e"] = j
            else:
                ev.append({"s": i, "e": j})
            i = j
        else:
            i += 1
    for e in ev:
        sb, sh = b[e["s"]:e["e"]], h[e["s"]:e["e"]]
        e["peak"] = float(sb.max()) - fb                       # dB over the broadband floor
        e["peak_hi"] = float(sh.max()) - fh
        e["core"] = f2ms(int((sb >= sb.max() - CORE_DB).sum()))
        e["len"] = f2ms(e["e"] - e["s"])
        e["kind"] = "flicker" if (e["len"] < FLICKER_MS and e["peak"] < FLICKER_DB and e["peak_hi"] < FLICKER_DB) else None
    an = [e for e in ev if e["kind"] is None]
    seedlike = lambda e: e["core"] >= SEED_CORE_MS and max(e["peak"], e["peak_hi"]) >= SEED_DB
    # 1. head clicks
    for e in an:
        if f2ms(e["s"]) < HEAD_ZONE_MS and e["len"] <= HEAD_MAX_MS and e["core"] <= HEAD_CORE_MS:
            nxt = [o for o in an if o["s"] >= e["e"] and seedlike(o) and not (f2ms(o["s"]) < HEAD_ZONE_MS and o["len"] <= HEAD_MAX_MS and o["core"] <= HEAD_CORE_MS)]
            if not nxt or f2ms(nxt[0]["s"] - e["e"]) >= HEAD_GAP_MS:
                e["kind"] = "click"
                e["where"] = "head"
    # 2. seeds and the speech span (join everything closer than JOIN_MS)
    for e in an:
        if e["kind"] is None and seedlike(e):
            e["kind"] = "speech"
    sp = [e for e in an if e["kind"] == "speech"]
    if not sp:
        return {"n": len(x), "floor_bb": fb, "floor_hi": fh, "events": ev, "onset": None, "xb": xb, "b": b}
    j = JOIN_MS // FRAME_MS
    changed = True
    while changed:
        changed = False
        lo, hi_ = min(e["s"] for e in sp), max(e["e"] for e in sp)
        for e in an:
            if e["kind"] is None and (lo - j < e["e"] and e["s"] < hi_ + j):
                inside = lo <= e["s"] and e["e"] <= hi_
                # 3. a transient after the words, 250 ms or more after the previous kept event, is a tail click
                if not inside and e["s"] >= hi_ and e["core"] <= TRANSIENT_CORE_MS and f2ms(e["s"] - hi_) >= TAIL_GAP_MS:
                    continue
                e["kind"] = "speech"
                sp.append(e)
                changed = True
    lo, hi_ = min(e["s"] for e in sp), max(e["e"] for e in sp)
    for e in an:
        if e["kind"] is None:
            if e["s"] >= hi_ and e["core"] <= TRANSIENT_CORE_MS:
                prev_end = max([o["e"] for o in an if o["e"] <= e["s"] and o["kind"] in ("speech", "noise")] + [hi_])
                if f2ms(e["s"] - prev_end) >= TAIL_GAP_MS:
                    e["kind"], e["where"] = "click", "tail"
                    continue
            e["kind"] = "noise"
            e["where"] = "head" if e["e"] <= lo else ("tail" if e["s"] >= hi_ else "inside")
    sp.sort(key=lambda e: e["s"])
    groups = []                 # utterance count, for a flag only: the seeds, joined across gaps < 350 ms
    for e in sp:
        if not seedlike(e):
            continue
        if groups and f2ms(e["s"] - groups[-1][1]) < JOIN_MS:
            groups[-1][1] = max(groups[-1][1], e["e"])
        else:
            groups.append([e["s"], e["e"]])
    return {"n": len(x), "floor_bb": fb, "floor_hi": fh, "events": ev, "speech": sp, "groups": groups,
            "clicks": [e for e in an if e["kind"] == "click"], "noise": [e for e in an if e["kind"] == "noise"],
            "onset": lo, "offset": hi_, "xb": xb, "b": b}


def plan(a):
    """Cut points and attenuations in SAMPLES, plus flags."""
    n, flags = a["n"], []
    if a["onset"] is None:
        return None, ["no speech found"]
    onset, offset = a["onset"] * HOP, min(a["offset"] * HOP, n)
    p = {"head": 0, "tail": n, "atten": [], "onset": onset, "offset": offset}
    if a["floor_bb"] > -50:
        flags.append(f"noisy take (floor {a['floor_bb']:.0f} dB): not cut")
        return p, flags
    big = lambda e: e["len"] >= NOISE_MAX_MS or e["peak"] >= NOISE_MAX_DB
    # head
    head = onset - ms2s(LEAD_MS)
    blockers = [e for e in a["noise"] if e["where"] == "head" and big(e)]
    if head <= 0:
        flags.append(f"head: speech starts {s2ms(onset)} ms in (< {LEAD_MS} ms): no head cut")
    elif blockers:
        flags.append("head: sound before the words that is neither a click nor faint noise ("
                     + ", ".join(f"{f2ms(e['s'])}-{f2ms(e['e'])} ms" for e in blockers) + "): no head cut, listen")
    else:
        p["head"] = head
    # tail
    tail = min(offset + ms2s(TAIL_MS), n)
    after = sorted([e for e in a["clicks"] if e["where"] == "tail"] + [e for e in a["noise"] if e["where"] == "tail"], key=lambda e: e["s"])
    if any(big(e) for e in a["noise"] if e["where"] == "tail"):
        tail = n
        flags.append("tail: sound after the words that is neither a click nor faint noise: no tail cut, listen")
    elif after:
        c0 = after[0]["s"] * HOP - ms2s(GUARD_MS)
        if c0 < offset + ms2s(MIN_TAIL_MS):
            tail = n
            flags.append(f"tail: click {s2ms(after[0]['s'] * HOP - offset)} ms after the words: no tail cut, click attenuated")
        else:
            tail = min(tail, c0)
    p["tail"] = tail
    # clicks left inside the kept part
    for c in a["clicks"]:
        s, e = max(c["s"] * HOP - ms2s(GUARD_MS), p["head"]), min(c["e"] * HOP + ms2s(GUARD_MS), p["tail"])
        if e <= s:
            continue
        if s2ms(onset - e) >= ATTEN_MIN_MS or s2ms(s - offset) >= ATTEN_MIN_MS:
            p["atten"].append((s, e, min(a["floor_bb"] - (c["peak"] + a["floor_bb"]), 0.0)))
        else:
            flags.append(f"click at {f2ms(c['s'])} ms too close to the words to attenuate: left in, listen")
    # doubts worth a listen
    sp = sorted(a["speech"], key=lambda e: e["s"])
    last = sp[-1]
    if len(sp) > 1 and last["core"] <= TRANSIENT_CORE_MS:
        prev = max(e["e"] for e in sp[:-1])
        if last["s"] >= prev:
            flags.append(f"transient {f2ms(last['s'] - prev)} ms after the words kept (word-final release or key click?): listen")
    for e in a["events"]:
        if e["kind"] != "click" and f2ms(e["s"]) < HEAD_ZONE_MS and e["kind"] == "speech":
            flags.append(f"head: sound at {f2ms(e['s'])} ms kept as speech (key click too close to the words?): listen")
            break
    return p, flags


def render(x, p):
    """The kept signal (pre-gain, on the ORIGINAL time axis) and its gain envelope."""
    n = len(x)
    env = np.zeros(n)
    env[p["head"]:p["tail"]] = 1.0
    f = ms2s(FADE_MS)
    if p["head"] > 0:
        env[p["head"]:p["head"] + f] *= np.linspace(0, 1, f, endpoint=False)
    if p["tail"] < n:
        env[p["tail"] - f:p["tail"]] *= np.linspace(1, 0, f)
    for s, e, gdb in p["atten"]:
        g = 10 ** (gdb / 20)
        seg = np.full(e - s, g)
        k = min(f, (e - s) // 2)
        if k > 0:
            seg[:k] = np.linspace(1, g, k)
            seg[-k:] = np.linspace(g, 1, k)
        env[s:e] *= seg
    return x * env, env


def self_check(x, xb, y, env, p, a):
    n = len(x)
    res = {}
    i0 = max(0, p["onset"] - ms2s(ID_PRE_MS), p["head"])
    i1 = min(n, p["offset"] + ms2s(ID_POST_MS), p["tail"])
    res["identical_window_ms"] = [s2ms(i0), s2ms(i1)]
    res["identical"] = bool(np.array_equal(y[i0:i1], x[i0:i1]))
    mask = np.ones(n, bool)
    for c in a["clicks"]:
        mask[max(0, c["s"] * HOP - ms2s(GUARD_MS)):min(n, c["e"] * HOP + ms2s(GUARD_MS))] = False
    e_orig = float((xb[mask] ** 2).sum())
    e_kept = float(((xb * env)[mask] ** 2).sum())
    res["energy_kept"] = e_kept / e_orig if e_orig > 0 else 0.0
    hm, tm = s2ms(p["onset"] - p["head"]), s2ms(p["tail"] - p["offset"])
    res["margins_ok"] = bool((p["head"] == 0 or hm >= LEAD_MS) and (p["tail"] == n or tm >= MIN_TAIL_MS))
    res["ok"] = res["identical"] and res["energy_kept"] >= ENERGY_MIN and res["margins_ok"]
    return res


def loudness(path):
    """(integrated LUFS, true peak dBTP, LRA) by ffmpeg's loudnorm analysis pass (EBU R128 / ITU-R BS.1770)."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=print_format=json",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(out[out.rindex("{"):])
    return float(j["input_i"]), float(j["input_tp"]), float(j["input_lra"])


def encode(y, gain_db, out, tmp):
    wav = os.path.join(tmp, "g.wav")
    wavfile.write(wav, SR, (y * 10 ** (gain_db / 20)).astype(np.float32))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav] + MP3_ARGS + [out], check=True)
    return loudness(out)


def process(src, dest, said="", write=True):
    """Process one take. Returns the log dict; writes dest only when the self-check passes (and write=True)."""
    x = decode(src)
    a = analyse(x)
    p, flags = plan(a)
    n = len(x)
    log = {"src": os.path.basename(src), "status": "", "flags": "", "note": "", "dur_ms": s2ms(n),
           "floor_bb_db": round(a["floor_bb"], 1), "floor_hi_db": round(a["floor_hi"], 1)}
    if p is None:
        log.update(status="FAIL", flags="; ".join(flags))
        return log
    forms = len([f for f in said.split("·") if f.strip()]) if said else 0
    if forms and len(a["groups"]) > forms:
        flags.append(f"{len(a['groups'])} loud sound groups for {forms} form(s): an extra utterance? listen")
    y, env = render(x, p)
    chk = self_check(x, a["xb"], y, env, p, a)
    hc = [c for c in a["clicks"] if c["where"] == "head"]
    tc = [c for c in a["clicks"] if c["where"] == "tail"]
    log.update({
        "onset_ms": s2ms(p["onset"]), "offset_ms": s2ms(p["offset"]),
        "head_cut_ms": s2ms(p["head"]), "tail_cut_ms": s2ms(p["tail"]),
        "head_margin_ms": s2ms(p["onset"] - p["head"]), "tail_margin_ms": s2ms(p["tail"] - p["offset"]),
        "removed_head_ms": s2ms(p["head"]), "removed_tail_ms": s2ms(n - p["tail"]), "kept_ms": s2ms(p["tail"] - p["head"]),
        "head_clicks": " ".join(f"{f2ms(c['s'])}-{f2ms(c['e'])}" for c in hc),
        "tail_clicks": " ".join(f"{f2ms(c['s'])}-{f2ms(c['e'])}" for c in tc),
        "noise_cut": " ".join(f"{f2ms(c['s'])}-{f2ms(c['e'])}" for c in a["noise"]
                              if c["e"] * HOP <= p["head"] or c["s"] * HOP >= p["tail"]),
        "attenuated": " ".join(f"{s2ms(s)}-{s2ms(e)}({g:.0f}dB)" for s, e, g in p["atten"]),
        "groups": " ".join(f"{f2ms(g0)}-{f2ms(g1)}" for g0, g1 in a["groups"]),
        "energy_kept_pct": round(chk["energy_kept"] * 100, 4),
        "identical_window_ms": "-".join(map(str, chk["identical_window_ms"])),
        "identical": chk["identical"], "margins_ok": chk["margins_ok"],
    })
    if not chk["ok"]:
        flags.append("SELF-CHECK FAILED: take left unprocessed")
        log.update(status="FAIL", flags="; ".join(flags))
        return log
    kept = y[p["head"]:p["tail"]]
    tmp = tempfile.mkdtemp()
    try:
        w0 = os.path.join(tmp, "k.wav")
        wavfile.write(w0, SR, kept.astype(np.float32))
        i_in, tp_in, _ = loudness(w0)
        i_raw, tp_raw, _ = loudness(src)
        gain = min(TARGET_I - i_in, TARGET_TP - tp_in)
        out = os.path.join(tmp, "o.mp3")
        i_out, tp_out, lra_out = encode(kept, gain, out, tmp)
        step = min(TARGET_I - i_out, TARGET_TP - tp_out - 0.2)    # one correction up, on the mp3 itself
        if step > 0.1:                                            # (resampling and the codec move the true peak)
            gain += step
            i_out, tp_out, lra_out = encode(kept, gain, out, tmp)
        for _ in range(8):                                        # then only down, until the ceiling holds
            if tp_out <= TARGET_TP:
                break
            gain -= (tp_out - TARGET_TP) + 0.15
            i_out, tp_out, lra_out = encode(kept, gain, out, tmp)
        if tp_out > TARGET_TP:
            log.update(status="FAIL", flags="; ".join(flags + [f"true peak {tp_out} dBTP after correction"]))
            return log
        if i_out < LOW_I_FLAG:
            log["note"] = f"loudness {i_out:.1f} LUFS: gain limited by the true-peak ceiling (linear, no limiter)"
        log.update({"raw_I": i_raw, "raw_TP": tp_raw, "kept_I": i_in, "kept_TP": tp_in, "gain_db": round(gain, 2),
                    "out_I": i_out, "out_TP": tp_out, "out_LRA": lra_out})
        if write:
            os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
            shutil.copyfile(out, dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    log.update(status="ok", flags="; ".join(flags))
    return log


def main(argv):
    ap = argparse.ArgumentParser(description="Process one recorder take (see the module docstring).")
    ap.add_argument("src")
    ap.add_argument("dest")
    ap.add_argument("--said", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="analyse, check and measure; write nothing")
    a = ap.parse_args(argv[1:])
    log = process(a.src, a.dest, a.said, write=not a.dry_run)
    print(json.dumps(log, ensure_ascii=False) if a.json else "\n".join(f"{k}: {v}" for k, v in log.items()))
    return 0 if log["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
