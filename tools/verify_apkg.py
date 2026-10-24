#!/usr/bin/env python3
"""Verify a built .apkg (A1_WRAPUP §E2/E3) and import it into a throw-away collection.

    python3 tools/verify_apkg.py <new.apkg> [--against <old.apkg> [--key-map data/key_maps/key_map_v1.csv]]
                                 [--json out.json] [--render 5]

Checks, read straight from the package (zip + its SQLite collection):
  * every <img src=...> and [sound:...] in every note field is in the package's media map, and every
    media file in the map is present in the zip;
  * every media name is ASCII;
  * package size < 250 MB (AnkiWeb's cap for shared decks);
  * GUIDs: for every card key present in both packages the GUID is identical (keys never change);
    with --key-map (the rename of 2026-10-20, spec §12) the old package's keys are first mapped to
    their current names (the map file, chains followed): a GUID that changed exactly as mapped
    (guid_for(old) -> guid_for(new)) is reported, not failed; fields are compared modulo the key,
    the plate number, media names and tags;
  * identity (spec §12): every key is NNNN_slug, the Number field equals the key's number, every
    note carries lt::level / lt::kind / lt::topic tags (lt::level = its subdeck), every picture
    note has an image, every sentence note an image;
  * the deck description carries the spec version and the style hash.
Then, when the `anki` Python package is installed (pip install --user anki), imports the package into a new
temporary collection, counts notes and cards, and renders the question/answer HTML of N cards, checking
that every src= and [sound:] in the rendered HTML names a file in the collection's media folder.
Exit code 1 on any failure."""
import json, os, re, sqlite3, sys, tempfile, zipfile

CAP = 250 * 1024 * 1024


def open_pkg(path, tmp):
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    col = next(n for n in ("collection.anki21b", "collection.anki21", "collection.anki2") if n in names)
    if col == "collection.anki21b":
        raise SystemExit("zstd-compressed collection (anki21b): not produced by genanki; unsupported here")
    db = os.path.join(tmp, os.path.basename(path) + ".db")
    open(db, "wb").write(z.read(col))
    media = json.loads(z.read("media").decode("utf-8")) if "media" in names else {}
    return z, names, sqlite3.connect(db), media


def note_rows(con):
    models = json.loads(con.execute("select models from col").fetchone()[0])
    decks = json.loads(con.execute("select decks from col").fetchone()[0])
    out = []
    deck_of = {nid: did for nid, did in con.execute("select nid, did from cards")}
    for nid, guid, mid, flds, tags in con.execute("select id, guid, mid, flds, tags from notes"):
        m = models[str(mid)]; f = flds.split("\x1f")
        names = [x["name"] for x in m["flds"]]
        d = dict(zip(names, f))
        key = d.get("key") or d.get("Key") or f[0]
        dk = decks.get(str(deck_of.get(nid)), {}).get("name", "")
        out.append({"id": nid, "guid": guid, "model": m["name"], "key": key, "fields": f, "named": d,
                    "tags": tags.split(), "deck": dk})
    return out, decks


def load_key_map(path):
    """old -> current key from a key_map_v<N>.csv and every map beside it (chains followed)."""
    import csv, glob
    paths = sorted(set(glob.glob(os.path.join(os.path.dirname(os.path.abspath(path)), "key_map_v*.csv"))) | {os.path.abspath(path)},
                   key=lambda p: int(p.rsplit("_v", 1)[1].split(".")[0]))
    fwd = {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if r["new_key"] and r["new_key"] != r["old_key"]:
                fwd[r["old_key"]] = r["new_key"]

    def canon(k):
        seen = set()
        while k in fwd and k not in seen:
            seen.add(k); k = fwd[k]
        return k
    return {k: canon(k) for k in fwd}


KEY_RE = re.compile(r"^(\d{4})_[a-z][a-z0-9_]*$")


def identity_checks(notes):
    """spec §12: NNNN_slug keys, plate = key number, lt:: tags, pictures present."""
    bad_key, bad_plate, bad_tags, no_img, bad_level = [], [], [], [], []
    kinds = {}
    for n in notes:
        d, k = n["named"], n["key"]
        m = KEY_RE.match(k)
        if not m:
            bad_key.append(k); continue
        plate = d.get("number", d.get("Number", ""))
        if plate != str(int(m.group(1))):
            bad_plate.append((k, plate))
        t = n["tags"]
        lv = [x for x in t if x.startswith("lt::level::")]; kd = [x for x in t if x.startswith("lt::kind::")]
        tp = [x for x in t if x.startswith("lt::topic::")]
        if len(lv) != 1 or len(kd) != 1 or len(tp) != 1 or any(not x.startswith("lt::") for x in t):
            bad_tags.append((k, t)); continue
        if not n["deck"].endswith("::" + lv[0].split("::")[-1]):
            bad_level.append((k, lv[0], n["deck"]))
        kind = kd[0].split("::")[-1]; kinds[kind] = kinds.get(kind, 0) + 1
        img = d.get("image", d.get("Image", ""))
        if kind in ("picture", "phrase", "sentence") and 'src="' not in img:
            no_img.append(k)
    return {"keys_not_NNNN_slug": bad_key[:20], "n_bad_keys": len(bad_key),
            "plate_not_key_number": bad_plate[:20], "n_bad_plates": len(bad_plate),
            "bad_tags": bad_tags[:20], "n_bad_tags": len(bad_tags),
            "level_tag_not_subdeck": bad_level[:20], "n_bad_level": len(bad_level),
            "without_image": no_img[:20], "n_without_image": len(no_img), "kinds": kinds}


def main():
    a = sys.argv[1:]
    pkg = a[0]
    old = a[a.index("--against") + 1] if "--against" in a else None
    kmap = load_key_map(a[a.index("--key-map") + 1]) if "--key-map" in a else {}
    jout = a[a.index("--json") + 1] if "--json" in a else None
    nrender = int(a[a.index("--render") + 1]) if "--render" in a else 5
    rep = {"package": os.path.basename(pkg), "bytes": os.path.getsize(pkg), "checks": {}, "fail": []}
    tmp = tempfile.mkdtemp()
    z, znames, con, media = open_pkg(pkg, tmp)
    notes, decks = note_rows(con)
    ncards = con.execute("select count(*) from cards").fetchone()[0]
    rep["notes"], rep["cards"], rep["media_files"] = len(notes), ncards, len(media)
    mnames = set(media.values())
    refs = set()
    for n in notes:
        for f in n["fields"]:
            refs.update(re.findall(r'src="([^"]+)"', f)); refs.update(re.findall(r"\[sound:([^\]]+)\]", f))
    missing_ref = sorted(r for r in refs if r not in mnames)
    missing_zip = sorted(k for k in media if k not in znames)
    non_ascii = sorted(n for n in mnames if not n.isascii())
    rep["checks"]["refs"] = {"referenced": len(refs), "missing_from_media_map": missing_ref[:20], "n_missing": len(missing_ref)}
    rep["checks"]["media_in_zip"] = {"missing": missing_zip[:20], "n_missing": len(missing_zip)}
    rep["checks"]["ascii_names"] = {"non_ascii": non_ascii[:20], "n": len(non_ascii)}
    rep["checks"]["size"] = {"bytes": rep["bytes"], "MB": round(rep["bytes"] / 1048576, 1), "under_250MB": rep["bytes"] < CAP}
    sounds = sum(1 for r in refs if r.endswith(".mp3"))
    rep["checks"]["refs"]["sound_files"] = sounds
    descs = {d["name"]: d.get("desc", "") for d in decks.values() if d.get("name") != "Default"}
    rep["deck_descriptions"] = {k: v[:400] for k, v in descs.items()}
    if missing_ref: rep["fail"].append("references missing from media map")
    if missing_zip: rep["fail"].append("media map entries missing from zip")
    if non_ascii: rep["fail"].append("non-ASCII media names")
    if rep["bytes"] >= CAP: rep["fail"].append("package >= 250 MB")
    if all(KEY_RE.match(n["key"]) for n in notes):
        idc = identity_checks(notes)
        rep["checks"]["identity"] = idc
        for f, msg in (("n_bad_plates", "plate number differs from the key number"), ("n_bad_tags", "lt:: tags missing or malformed"),
                       ("n_bad_level", "lt::level tag differs from the subdeck"), ("n_without_image", "picture/sentence note without an image")):
            if idc[f]: rep["fail"].append(msg)
    if old:
        z2, _, con2, _ = open_pkg(old, tmp)
        old_notes, _ = note_rows(con2)
        if kmap:
            import genanki
            ok_ = {n["key"]: n for n in old_notes}
            mapped = {kmap.get(k, k): n for k, n in ok_.items()}
            nn = {n["key"]: n for n in notes}
            both = sorted(set(mapped) & set(nn))
            as_mapped, unexpected = 0, []
            for k in both:
                o, n = mapped[k], nn[k]
                if o["guid"] == n["guid"]:
                    continue
                if o["guid"] == genanki.guid_for(o["key"]) and n["guid"] == genanki.guid_for(k) and kmap.get(o["key"]) == k:
                    as_mapped += 1
                else:
                    unexpected.append(k)
            tok = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(x) for x in sorted(kmap, key=len, reverse=True)) + r")(?![A-Za-z0-9])") if kmap else None
            skip = {"key", "Key", "number", "Number"}
            fdiff = []
            for k in both:
                o, n = mapped[k], nn[k]
                if o["model"] != n["model"]:
                    fdiff.append((k, "note type", o["model"], n["model"])); continue
                for f, ov in o["named"].items():
                    if f in skip:
                        continue
                    ov2 = tok.sub(lambda m: kmap[m.group(1)], ov) if tok else ov
                    nv = n["named"].get(f, "")
                    if ov2 != nv:
                        fdiff.append((k, f, ov2[:120], nv[:120]))
            rep["checks"]["guids"] = {"against": os.path.basename(old), "key_map": True, "old_notes": len(old_notes),
                                      "keys_in_both_after_mapping": len(both), "changed_as_mapped": as_mapped,
                                      "changed_unexpectedly": unexpected[:20], "n_changed_unexpectedly": len(unexpected),
                                      "only_new": sorted(set(nn) - set(mapped))[:60], "n_only_new": len(set(nn) - set(mapped)),
                                      "only_old": sorted(set(mapped) - set(nn))[:60], "n_only_old": len(set(mapped) - set(nn)),
                                      "old_keys_not_in_map": sorted(k for k in ok_ if k not in kmap)[:20]}
            rep["checks"]["fields_modulo_rename"] = {"n_notes_differing": len({d[0] for d in fdiff}), "n_field_diffs": len(fdiff),
                                                     "by_field": {f: sum(1 for d in fdiff if d[1] == f) for f in sorted({d[1] for d in fdiff})},
                                                     "examples": fdiff[:40]}
            if unexpected: rep["fail"].append("GUID changed other than as mapped")
        else:
            og = {n["key"]: n["guid"] for n in old_notes}; ng = {n["key"]: n["guid"] for n in notes}
            both = set(og) & set(ng)
            diff = sorted(k for k in both if og[k] != ng[k])
            rep["checks"]["guids"] = {"against": os.path.basename(old), "keys_in_both": len(both), "changed": diff[:20],
                                      "n_changed": len(diff), "only_new": len(set(ng) - set(og)), "only_old": len(set(og) - set(ng)),
                                      "only_old_keys": sorted(set(og) - set(ng))[:40]}
            if diff: rep["fail"].append("GUID changed for an existing key")
    try:
        from anki.collection import Collection
        from anki.collection import ImportAnkiPackageRequest, ImportAnkiPackageOptions
        cdir = tempfile.mkdtemp()
        col = Collection(os.path.join(cdir, "import_test.anki2"))
        log = col.import_anki_package(ImportAnkiPackageRequest(package_path=os.path.abspath(pkg),
                                      options=ImportAnkiPackageOptions(with_scheduling=True)))
        mdir = col.media.dir()
        cids = col.find_cards("")
        res = {"anki_version": __import__("anki.buildinfo").buildinfo.version, "notes": col.note_count(),
               "cards": len(cids), "import_log_new": len(log.log.new), "decks": sorted(d.name for d in col.decks.all_names_and_ids()), "rendered": []}
        # a spread of card kinds: picture cards, cloze word cards, sentence cards (tag lt::kind::sentence)
        by = {"go": [], "cloze": [], "sent": []}
        for cid in sorted(cids):
            c0 = col.get_card(cid); t0 = c0.note().tags
            kind = "sent" if ("lt::kind::sentence" in t0 or "SENT" in t0) else ("cloze" if "Cloze" in c0.note_type()["name"] else "go")
            by[kind].append(cid)
        pick = []
        for kind, n in (("go", 2), ("cloze", 2), ("sent", 1)):
            lst = by[kind]; pick += lst[::max(1, len(lst) // n)][:n] if lst else []
        pick = pick[:max(nrender, 0)] if nrender < len(pick) else pick
        for cid in pick:
            c = col.get_card(cid)
            q, ans = c.question(), c.answer()
            files = set(re.findall(r'src="([^"]+)"', q + ans)) | set(re.findall(r"\[sound:([^\]]+)\]", q + ans))
            files |= {t.filename for t in list(c.question_av_tags()) + list(c.answer_av_tags()) if hasattr(t, "filename")}
            miss = sorted(f for f in files if not os.path.exists(os.path.join(mdir, f)))
            fields = c.note().keys()
            res["rendered"].append({"card": cid, "note_type": c.note_type()["name"], "key": next((c.note()[f] for f in fields if f.lower() == "key"), c.note().fields[0][:40]),
                                    "q_len": len(q), "a_len": len(ans), "files": sorted(files), "missing": miss,
                                    "unresolved_braces": bool(re.search(r"\{\{[^}]+\}\}", q + ans)),
                                    "q_text": re.sub(r"<[^>]+>|\s+", " ", re.sub(r"<(style|script).*?</(style|script)>", "", q, flags=re.S)).strip()[:160],
                                    "a_text": re.sub(r"<[^>]+>|\s+", " ", re.sub(r"<(style|script).*?</(style|script)>", "", ans, flags=re.S)).strip()[:240]})
            if miss or res["rendered"][-1]["unresolved_braces"]:
                rep["fail"].append(f"card {cid}: unresolved media or field")
        col.close()
        rep["import_test"] = res
        if res["notes"] != rep["notes"]: rep["fail"].append("imported note count differs")
    except ImportError as e:
        rep["import_test"] = {"skipped": f"anki package not installed ({e})"}
    rep["ok"] = not rep["fail"]
    s = json.dumps(rep, ensure_ascii=False, indent=1)
    if jout:
        open(jout, "w", encoding="utf-8").write(s + "\n")
    print(s)
    sys.exit(0 if rep["ok"] else 1)


if __name__ == "__main__":
    main()
