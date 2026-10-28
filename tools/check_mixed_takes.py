#!/usr/bin/env python3
"""check_mixed_takes.py — find recorder takes that contain a copy of another take (the "two recordings in one take"
bug of the recorder before commit 4832e9b: a fast stop -> start poured the previous take's audio into the next one,
so take N+1 came out as take N followed by take N+1).

    python3 tools/check_mixed_takes.py BATCH.zip [EARLIER.zip ...] [--out mixed.tsv] [--threshold 0.9]

Every clip of BATCH.zip is tested against every clip of BATCH.zip and of the EARLIER ZIPs (the take recorded just
before may sit in the previous export), two ways:
  * whole: clip B is CONTAINED in clip A when A is at least 300 ms longer than B and the normalised cross-correlation
    of B against some stretch of A reaches the threshold;
  * head: the first 400 ms of A (the pre-roll before "SPEAK NOW", where a poured-in END of the previous take would
    sit) found in another clip B at 0.98 or more.
Whole clips use 0.9: two different recordings of the same words stay far below it, the copied chunks of the bug are
the same encoded audio and score ~1.0. The pre-roll needs the stricter 0.98 because it holds little but the Space
press, and two Space presses are alike: in batch 2 the start click of 0129_is_s matched the start of 0126_su at 0.92
(its first 200 ms at 0.93, the silence after it at 0.34), whereas a copied chunk matches in the noise floor as well.
The take that contains the other's audio is the mixed one and must be re-recorded.

Mono, 8 kHz decode (enough for identity; this is not a listening check). Writes one row per mixed take:
kind (whole/head), mixed_take, contains, r, at_ms, mixed_ms, contained_ms. Exit status 0 always (the caller reads the table).
The owner-facing check that complements this (more utterance groups than the card's forms) is in
tools/process_take.py and lands in process_log.csv as a flag.
"""
import argparse
import csv
import io
import os
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
from scipy.signal import fftconvolve

SR = 8000
MIN_EXTRA_MS = 300
HEAD_MS = 400
HEAD_THRESHOLD = 0.98


def decode_bytes(data, tmp, name):
    p = os.path.join(tmp, os.path.basename(name))
    open(p, "wb").write(data)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    os.remove(p)
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x - x.mean() if len(x) else x


def clips(zpath, tmp):
    z = zipfile.ZipFile(zpath)
    man = list(csv.DictReader(io.StringIO(z.read("manifest.tsv").decode("utf-8")), delimiter="\t"))
    out = []
    for m in man:
        name = m["file"].strip()
        if name in z.namelist():
            out.append((m["key"].strip(), os.path.basename(zpath), decode_bytes(z.read(name), tmp, name)))
    return out


def best_match(a, b):
    """max over lags of the normalised correlation of b against a stretch of a (len(a) >= len(b))."""
    n = len(b)
    nb = np.sqrt(np.dot(b, b))
    if nb == 0:
        return 0.0, 0
    num = fftconvolve(a, b[::-1], mode="valid")                 # len(a) - n + 1 lags
    c = np.concatenate([[0.0], np.cumsum(a * a)])
    den = np.sqrt(np.maximum(c[n:] - c[:-n], 1e-20)) * nb
    r = num / den
    i = int(np.argmax(r))
    return float(r[i]), i


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("batch")
    ap.add_argument("earlier", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--threshold", type=float, default=0.9)
    a = ap.parse_args(argv[1:])
    tmp = tempfile.mkdtemp()
    batch = clips(a.batch, tmp)
    pool = batch + [c for z in a.earlier for c in clips(z, tmp)]
    rows = []
    for ka, za, xa in batch:
        for kb, zb, xb in pool:
            if (ka, za) == (kb, zb) or len(xa) < len(xb) + SR * MIN_EXTRA_MS // 1000 or len(xb) < SR // 10:
                continue
            r, lag = best_match(xa, xb)
            if r >= a.threshold:
                rows.append({"kind": "whole", "mixed_take": ka, "contains": kb, "contains_from": zb, "r": round(r, 4),
                             "at_ms": int(lag * 1000 / SR), "mixed_ms": int(len(xa) * 1000 / SR),
                             "contained_ms": int(len(xb) * 1000 / SR)})
        head = xa[:SR * HEAD_MS // 1000]
        for kb, zb, xb in pool:
            if (ka, za) == (kb, zb) or len(xb) < len(head) or len(head) < SR * HEAD_MS // 1000:
                continue
            r, lag = best_match(xb, head)
            if r >= max(a.threshold, HEAD_THRESHOLD):
                rows.append({"kind": "head", "mixed_take": ka, "contains": kb, "contains_from": zb, "r": round(r, 4),
                             "at_ms": int(lag * 1000 / SR), "mixed_ms": int(len(xa) * 1000 / SR),
                             "contained_ms": HEAD_MS})
    # a head hit inside a take that contains the whole clip is the same finding seen from the other side
    whole = {frozenset((r["mixed_take"], r["contains"])) for r in rows if r["kind"] == "whole"}
    rows = [r for r in rows if r["kind"] == "whole" or frozenset((r["mixed_take"], r["contains"])) not in whole]
    fields = ["kind", "mixed_take", "contains", "contains_from", "r", "at_ms", "mixed_ms", "contained_ms"]
    fh = open(a.out, "w", encoding="utf-8", newline="") if a.out else sys.stdout
    w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    if a.out:
        fh.close()
    print(f"{os.path.basename(a.batch)}: {len(batch)} takes checked against {len(pool) - 1} others; "
          f"{len({r['mixed_take'] for r in rows})} contain another take", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
