#!/usr/bin/env python3
"""Apply proposals_v2.csv (how = unique / chosen-by-headword / project-pron) to the two live lists,
changing only the gen_sg / fem / pres3 / past3 fields (and the pron of the five listed cards),
and noting the source in the row's own source/check column the way the files already do it
(`notes` in data/cards_anki.csv, `check` in data/a2_wordlist.csv). CSV quoting and the CRLF line
ends are kept (csv round trip is byte-identical, checked before writing).

    python3 rounds/2026-10-28_stress_forms/apply_v2.py [--dry-run]

Writes applied.csv (key, file, field, before, after, how) beside this script.
"""
import csv
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATE = "2026-10-28"
DRY = "--dry-run" in sys.argv

FILES = {
    "data/cards_anki.csv": dict(id="key", note="notes", pron="pron"),
    "data/a2_wordlist.csv": dict(id="id", note="check", pron="lt_pron"),
}


def read_csv(path):
    raw = open(path, encoding="utf-8", newline="").read()
    rows = list(csv.reader(io.StringIO(raw, newline="")))
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(rows)
    if buf.getvalue() != raw:
        sys.exit(f"{path}: csv round trip is not byte-identical; refusing to rewrite it")
    return rows


def write_csv(path, rows):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(rows)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())


def note_for(fields_how):
    """One clause per way the forms were read, e.g.
    'gen_sg stress: en.wiktionary 2026-10-28' / 'fem stress: en.wiktionary, chosen by headword 2026-10-28'."""
    out = []
    by_how = {}
    for f, how in fields_how:
        by_how.setdefault(how, []).append(f)
    for how, fs in by_how.items():
        if how == "unique":
            out.append(f"{', '.join(fs)} stress: en.wiktionary {DATE}")
        elif how == "chosen-by-headword":
            out.append(f"{', '.join(fs)} stress: en.wiktionary, chosen by headword {DATE}")
        elif how == "project-pron":
            out.append(f"{', '.join(fs)}: kortẽlė as 0771_kortele (kirtis.info) {DATE}")
    return "; ".join(out)


def main():
    props = [r for r in csv.DictReader(open(os.path.join(HERE, "proposals_v2.csv"), encoding="utf-8"))
             if r["proposed"] and r["how"] in ("unique", "chosen-by-headword", "project-pron")]
    by_file = {}
    for r in props:
        by_file.setdefault(r["file"], {}).setdefault(r["key"], []).append(r)
    applied = []
    for rel, cols in FILES.items():
        path = os.path.join(ROOT, rel)
        rows = read_csv(path)
        head = rows[0]
        ix = {h: i for i, h in enumerate(head)}
        todo = by_file.get(rel, {})
        seen = set()
        for row in rows[1:]:
            k = row[ix[cols["id"]]]
            if k not in todo:
                continue
            seen.add(k)
            fields_how = []
            for p in todo[k]:
                col = cols["pron"] if p["field"] == "pron" else p["field"]
                before = row[ix[col]]
                if before.strip() != p["current"].strip():
                    sys.exit(f"{rel} {k} {col}: file has {before!r}, proposal expects {p['current']!r}")
                row[ix[col]] = p["proposed"]
                fields_how.append((p["field"], p["how"]))
                applied.append(dict(key=k, file=rel, field=col, before=before, after=p["proposed"], how=p["how"]))
            note = note_for(fields_how)
            old = row[ix[cols["note"]]]
            row[ix[cols["note"]]] = (old + "; " + note) if old.strip() else note
        missing = set(todo) - seen
        if missing:
            sys.exit(f"{rel}: keys not found: {sorted(missing)[:10]}")
        if not DRY:
            write_csv(path, rows)
        print(f"{rel}: {len(seen)} rows, {sum(len(v) for kk, v in todo.items())} fields" + (" (dry run)" if DRY else ""))
    with open(os.path.join(HERE, "applied.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["key", "file", "field", "before", "after", "how"])
        w.writeheader()
        w.writerows(applied)
    print("applied:", len(applied))


if __name__ == "__main__":
    main()
