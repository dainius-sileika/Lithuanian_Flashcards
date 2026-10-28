#!/usr/bin/env python3
"""Stress marks for the forms shown on the backs (gen_sg, fem, pres3, past3) and for a few
multi-word prons, read from ONE source: English Wiktionary's Lithuanian entries, as the
Wiktextract dump at https://kaikki.org/dictionary/Lithuanian/kaikki.org-dictionary-Lithuanian.jsonl
(spec §7: stress marks are sourced, never generated).

    python3 rounds/2026-10-28_stress_forms/match_kaikki_v2.py [path/to/lt.jsonl]
    -> proposals_v2.csv (every unstressed form, with the decision) and OWNER_LIST.csv

What v2 reads that v1 did not (v1: rounds/2026-10-28_stress_forms/match_kaikki_v1.py):
  1. the headword line's groups: a `canonical` form (with its `stress-pattern-N` tag) and the
     `feminine` / `plural` / third-person forms that follow it; an entry with two stress patterns
     has two groups (raudónas 1: raudóna; raudónas 3: raudonà);
  2. the declension / conjugation tables, split at their `table-tags` rows; each table's own
     nominative singular is the headword it belongs to (ener̃gija / enèrgija have one table each);
  3. the form-of entries (tėvų̃ "genitive plural of tė́vas"); 13,000 of them carry a stressed head;
  4. paradigm neighbours: any table in which our lemma word is the nominative row (batai, tėvai,
     mobilusis, grynieji, miegamasis) gives the genitive / feminine row of the same number and gender;
  5. multi-word lemmas (mobilusis telefonas -> mobiliojo telefono) word by word, every word sourced;
     a one-word form of a multi-word lemma (važiuoti dviračiu -> važiuoja) through the word it inflects.
Case-only duplicates (Žẽmės / žẽmės) collapse: the entry whose spelling matches ours wins and the
candidate takes the case of our form. Wiktionary's dotted stressed i (i̇̀) is written the way every
pron in the data writes it (ì).

Decision per form (column `how`):
  unique              one stressed form in the source (and its headword agrees with the card's pron,
                      or the source gives no stressed headword to compare)
  chosen-by-headword  several sourced variants; the one whose headword (the entry's canonical form,
                      the table's nominative, or the stress-pattern group) equals the card's own
                      sourced pron is taken: selection among sourced forms, not generation
  owner               nothing sourced, or the headword does not decide, or the source's headword
                      contradicts ours (`conflict`, reported separately) -> unmarked, OWNER_LIST.csv
  project-pron        (prons only) the same word's sourced pron elsewhere in the data
Nothing is derived from accent rules or any accentuator.
"""
import csv
import collections
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DUMP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "lt.jsonl")
FETCHED = "2026-10-28"
MARKS = "̀́̃"          # grave, acute, tilde
_DOT = re.compile("(?<=[ijIJ])̨?̇(?=[" + MARKS + "])")


def strip(s):
    """Remove stress marks and the soft dot i/j carry under a mark (i̇̃ -> i)."""
    d = unicodedata.normalize("NFD", s or "")
    out = []
    for ch in d:
        if ch in MARKS:
            continue
        if ch == "̇" and out and (out[-1] in "iIjJ" or (out[-1] == "̨" and len(out) > 1 and out[-2] in "iIjJ")):
            continue
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def stressed(s):
    return any(c in MARKS for c in unicodedata.normalize("NFD", s or ""))


def nfc(s):
    """NFC in the project's spelling of a stressed i/j/į: Wiktionary writes i̇̀ (dotted i + mark),
    the data writes ì (every pron in the data): the dot goes, the ogonek stays."""
    d = unicodedata.normalize("NFD", s or "")
    d = _DOT.sub(lambda m: "̨" if m.group(0).startswith("̨") else "", d)
    return unicodedata.normalize("NFC", d)


def match_case(cand, ours):
    """Žẽmės for Žemės, žẽmės for žemės: the candidate takes the case of our first letter."""
    if not cand or not ours:
        return cand
    if ours[0].islower() and cand[0].isupper():
        return cand[0].lower() + cand[1:]
    if ours[0].isupper() and cand[0].islower():
        return cand[0].upper() + cand[1:]
    return cand


def clean_lemma(s):
    """'nekęsti (+gen)' -> 'nekęsti'; 'slėpti(s)' -> 'slėpti'; 'dvivietis (kambarys)' -> 'dvivietis'."""
    s = re.sub(r"\([^)]*\)", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def head_token(s, lemma):
    """A canonical form sometimes carries the rest of the headword line ('traukinỹs m stress pattern
    3ᵃ'): keep as many words as the lemma has."""
    n = max(1, len((lemma or "").split()))
    return " ".join(nfc(s).split()[:n])


def page(word):
    return "https://en.wiktionary.org/wiki/" + word.replace(" ", "_") + "#Lithuanian"


def is_formof(e):
    """A pure form-of entry (tėvų "genitive plural of tėvas"): no inflection table of its own.
    A diminutive such as berniùkas is tagged form-of too but has a full table: it is a lemma."""
    return any("form-of" in (s.get("tags") or []) for s in e.get("senses", [])) \
        and not any("table-tags" in f.get("tags", []) for f in e.get("forms", []))


# ----------------------------------------------------------------------------- the dump
class Source:
    """The Wiktextract dump, indexed: lemma entries by spelling, form-of entries by spelling,
    and every table row by spelling (for paradigm neighbours)."""

    NEED = {                      # tags a table row / form-of sense must carry for each field
        "gen_sg": {"genitive", "singular"},
        "gen_pl": {"genitive", "plural"},
        "fem": {"feminine", "nominative", "singular"},
        "pres3": {"present", "third-person"},
        "past3": {"past", "third-person"},
    }
    EXCLUDE = {"comparative", "superlative", "error-unrecognized-form", "dual", "vocative", "alternative"}
    POS = {
        "gen_sg": {"noun", "name", "adj", "pron", "num", "det", "verb"},
        "gen_pl": {"noun", "name", "adj"},
        "fem": {"adj", "num", "pron", "det", "verb", "noun"},
        "pres3": {"verb"},
        "past3": {"verb"},
    }

    def __init__(self, path):
        self.by_word = collections.defaultdict(list)       # strip(word) (case kept) -> entries
        self.by_lower = collections.defaultdict(list)
        self.formof = collections.defaultdict(list)        # strip(word) -> form-of entries
        self.rows = collections.defaultdict(list)          # strip(row).lower() -> [(entry id, table idx)]
        self.entries = []
        self._tables = {}
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh):
                e = json.loads(line)
                e["_id"] = n
                self.entries.append(e)
                w = strip(e["word"])
                if is_formof(e):
                    self.formof[w].append(e)
                self.by_word[w].append(e)
                self.by_lower[w.lower()].append(e)
                for ti, tb in enumerate(self.tables(e)):
                    for f, t in tb["forms"]:
                        if "nominative" in t and not t & self.EXCLUDE:
                            self.rows[strip(f).lower()].append((n, ti))

    # --- structure of one entry -------------------------------------------------------------
    @staticmethod
    def groups(e):
        """Headword-line groups: [{'canonical': str, 'pattern': 'N'|None, 'forms': [(form, tags)]}]."""
        out, cur = [], None
        for f in e.get("forms", []):
            if f.get("source"):
                continue
            t = f.get("tags", [])
            if "canonical" in t:
                if f["form"] in ("or", "and"):
                    continue
                pat = next((x.split("-")[-1] for x in t if x.startswith("stress-pattern-")), None)
                cur = {"canonical": head_token(f["form"], e["word"]), "pattern": pat, "forms": []}
                out.append(cur)
            elif cur is not None and "alternative" not in t:
                cur["forms"].append((nfc(f["form"]), set(t)))
        return out

    def tables(self, e):
        """Inflection tables: [{'template', 'pattern', 'nom': stressed nominative (sg masc) or None,
        'forms': [(form, tags)]}]; split at the dump's `table-tags` rows."""
        if e["_id"] in self._tables:
            return self._tables[e["_id"]]
        out, cur = [], None
        for f in e.get("forms", []):
            if not f.get("source"):
                continue
            t = f.get("tags", [])
            if "table-tags" in t:
                cur = {"template": "", "pattern": None, "nom": None, "forms": []}
                out.append(cur)
                continue
            if cur is None:
                cur = {"template": "", "pattern": None, "nom": None, "forms": []}
                out.append(cur)
            if "inflection-template" in t:
                cur["template"] = f["form"]
                m = re.search(r"-(\d)$", f["form"])
                cur["pattern"] = m.group(1) if m else None
                continue
            cur["forms"].append((nfc(f["form"]), set(t)))
        for tb in out:
            for f, t in tb["forms"]:
                if {"nominative", "singular"} <= t and "feminine" not in t and not t & self.EXCLUDE \
                        and strip(f).lower() == strip(e["word"]).lower() and stressed(f):
                    tb["nom"] = f
                    break
        self._tables[e["_id"]] = out
        return out

    def canonicals(self, e):
        return [g["canonical"] for g in self.groups(e)] or [nfc(e["word"])]

    def lemma_entries(self, lemma, poses):
        """Non-form-of entries for this spelling; exact case first, then any case."""
        k = strip(lemma)
        es = [e for e in self.by_word.get(k, []) if e["pos"] in poses and not is_formof(e)]
        if not es:
            es = [e for e in self.by_lower.get(k.lower(), []) if e["pos"] in poses and not is_formof(e)]
        return es

    # --- candidates ---------------------------------------------------------------------------
    def candidates(self, lemma, field, form, plural=False):
        """Stressed candidates for `form` (the `field` form of `lemma`), each
        {'form', 'canonical', 'pattern', 'page', 'via'}; `via` says where in the page it was read;
        `canonical` is the stressed headword the candidate belongs to (for the check against our pron)."""
        key = "gen_pl" if (field == "gen_sg" and plural) else field
        need = self.NEED[key]
        target = strip(form).lower()
        out = []

        def take(e, cand, canonical, pattern, via):
            if strip(cand).lower() != target or not stressed(cand):
                return
            out.append({"form": match_case(nfc(cand), form), "canonical": canonical, "pattern": pattern,
                        "page": page(e["word"]), "via": via, "entry": e["_id"]})

        def row_ok(t):
            if t & self.EXCLUDE or not need <= t:
                return False
            if ("plural" in t and "singular" in need) or ("singular" in t and "plural" in need):
                return False
            if key in ("gen_sg", "gen_pl") and "feminine" in t and "masculine" not in t \
                    and self.entries[cur_entry]["pos"] in ("adj", "verb", "pron", "num", "det"):
                return False      # an adjective's feminine genitive is not our (masculine) genitive
            return True

        # 1. the lemma's own entries: headword line, then the tables
        for e in self.lemma_entries(lemma, self.POS[key]):
            cur_entry = e["_id"]
            gs = self.groups(e)
            for g in gs:
                for f, t in g["forms"]:
                    if field == "fem" and t == {"feminine"}:
                        take(e, f, g["canonical"], g["pattern"], "headword line")
                    elif field in ("pres3", "past3") and self.NEED[field] <= t:
                        take(e, f, g["canonical"], g["pattern"], "headword line")
            pats = {g["pattern"]: g["canonical"] for g in gs if g["pattern"]}
            single = gs[0]["canonical"] if len(gs) == 1 else None
            for tb in self.tables(e):
                canon = tb["nom"] or single or pats.get(tb["pattern"]) or (gs[0]["canonical"] if gs else None)
                for f, t in tb["forms"]:
                    if row_ok(t):
                        take(e, f, canon, tb["pattern"], "table")

        # 2. paradigm neighbours: a table whose nominative row is our lemma word (the nominative
        #    plural of batas for batai; the definite nominative of mobilus for mobilusis)
        lemma_key = strip(lemma).lower()
        for eid, ti in self.rows.get(lemma_key, []):
            e = self.entries[eid]
            cur_entry = eid
            if e["pos"] not in self.POS[key] and e["pos"] not in ("adj", "verb"):
                continue
            tb = self.tables(e)[ti]
            heads = [(f, t) for f, t in tb["forms"] if "nominative" in t and strip(f).lower() == lemma_key
                     and not t & self.EXCLUDE and ("feminine" not in t or "masculine" in t or e["pos"] in ("noun", "name"))]
            own = strip(e["word"]).lower() == lemma_key      # the lemma's own table (a plurale tantum
            for hf, ht in heads:                               # such as sùltys has one column, which the
                number = "plural" if "plural" in ht else "singular"   # dump tags "singular")
                if field == "fem":
                    if number != "singular" or "feminine" in ht:
                        continue
                    want = {"feminine", "nominative", "singular"}
                elif field == "gen_sg":
                    if plural and number != "plural" and not own:
                        continue
                    want = {"genitive"} if (plural and own) else {"genitive", number}
                else:
                    continue
                for f, t in tb["forms"]:
                    if t & self.EXCLUDE or not want <= t:
                        continue
                    if field == "gen_sg" and ("feminine" in t) != ("feminine" in ht) and e["pos"] != "noun":
                        continue
                    if field == "gen_sg" and not (plural and own) and ("plural" in t) != (number == "plural"):
                        continue
                    take(e, f, hf if stressed(hf) else None, tb["pattern"], f"table of {strip(e['word'])}")

        # 3. form-of entries: the inflected form's own page, "genitive plural of tė́vas"
        lemma_heads = {lemma_key}
        for eid, ti in self.rows.get(lemma_key, []):
            lemma_heads.add(strip(self.entries[eid]["word"]).lower())
        for e in self.formof.get(strip(form), []) + \
                [x for x in self.formof.get(strip(form).lower(), []) if strip(x["word"]) != strip(form)]:
            cur_entry = e["_id"]
            canon = self.canonicals(e)
            if len(canon) != 1 or not stressed(canon[0]):
                continue
            for s in e.get("senses", []):
                t = set(s.get("tags") or [])
                if "form-of" not in t or not need <= t or t & self.EXCLUDE:
                    continue
                if "plural" in t and "singular" in need and "singular" not in t:
                    continue
                if "singular" in t and "plural" in need and "plural" not in t:
                    continue
                if key in ("gen_sg", "gen_pl") and "feminine" in t and "masculine" not in t and e["pos"] != "noun":
                    continue
                heads = {strip(x.get("word", "")).lower() for x in (s.get("form_of") or [])}
                if not heads & lemma_heads:
                    continue
                lem_canon = self.headword_of(lemma)
                take(e, canon[0], lem_canon, None, "form-of entry")
                break
        return out

    def headword_of(self, lemma):
        """The one stressed headword of `lemma` in the source, or None (several / none / unstressed):
        the lemma's own canonical form, or the stressed row that spells our lemma in some table."""
        heads = set()
        for e in self.lemma_entries(lemma, {"noun", "name", "adj", "verb", "pron", "num", "det"}):
            for c in self.canonicals(e):
                if stressed(c):
                    heads.add(c.lower())
        if not heads:
            for eid, ti in self.rows.get(strip(lemma).lower(), []):
                for f, t in self.tables(self.entries[eid])[ti]["forms"]:
                    if "nominative" in t and strip(f).lower() == strip(lemma).lower() and stressed(f):
                        heads.add(f.lower())
        return next(iter(heads)) if len(heads) == 1 else None

    def headword(self, lemma, poses=("noun", "name", "adj", "verb", "pron", "num", "det", "adv",
                                      "particle", "conj", "prep", "intj")):
        """Stressed canonical forms of the lemma's entries (for the pron fixes and fixed attributes)."""
        out = []
        for e in self.lemma_entries(lemma, set(poses)):
            for c in self.canonicals(e):
                if stressed(c) and c not in out:
                    out.append(c)
        if not out:
            for e in self.formof.get(strip(lemma), []):
                for c in self.canonicals(e):
                    if stressed(c) and c not in out:
                        out.append(c)
        return out


# ----------------------------------------------------------------------------- decisions
def same_head(a, b):
    return nfc(a).lower() == nfc(b).lower()


def decide(cands, pron, form):
    """-> (how, chosen, reason, options). One sourced form -> unique, unless the source's headword
    contradicts our pron; several -> the one whose headword equals our pron; else owner."""
    forms = collections.OrderedDict()
    for c in cands:
        forms.setdefault(c["form"], []).append(c)
    opts = " / ".join(forms)
    if not forms:
        return "owner", "", "not in source", ""
    pron = nfc(pron or "")
    pron_known = stressed(pron)

    def head_agrees(cs):
        heads = [c["canonical"] for c in cs if c["canonical"] and stressed(c["canonical"])]
        if not heads or not pron_known:
            return None
        return any(same_head(h, pron) for h in heads)

    if len(forms) == 1:
        f, cs = next(iter(forms.items()))
        agrees = head_agrees(cs)
        if agrees is False:
            heads = sorted({c["canonical"] for c in cs if c["canonical"]})
            return "owner", "", f"conflict: source headword {' / '.join(heads)} ≠ card pron {pron}", opts
        return "unique", f, ("headword agrees" if agrees else "headword not compared"), opts
    if not pron_known:
        return "owner", "", "ambiguous in source; card pron unstressed", opts
    keep = [f for f, cs in forms.items() if head_agrees(cs)]
    if len(keep) == 1:
        return "chosen-by-headword", keep[0], "headword decides", opts
    if not keep:
        return "owner", "", f"conflict: no source headword matches card pron {pron}", opts
    return "owner", "", "ambiguous in source; headword identical for both", opts


# ----------------------------------------------------------------------------- the cards
def load_cards():
    """[{key, level, file, lemma, pron, gender, forms}], the A1 base then the A2 list."""
    out = []
    for r in csv.DictReader(open(os.path.join(ROOT, "data/cards_anki.csv"), encoding="utf-8")):
        out.append(dict(key=r["key"], level=r.get("level") or "A1", file="data/cards_anki.csv",
                        lemma=r["lithuanian"], pron=r.get("pron", ""), gender=r.get("gender", ""),
                        forms={f: r.get(f, "") for f in ("gen_sg", "fem", "pres3", "past3")}))
    skip = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "data/merged_keys.csv"), encoding="utf-8"))}
    skip |= {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "data/deferred_B1.csv"), encoding="utf-8"))}
    for r in csv.DictReader(open(os.path.join(ROOT, "data/a2_wordlist.csv"), encoding="utf-8")):
        if r["id"] in skip:
            continue
        out.append(dict(key=r["id"], level=r.get("level") or "A2", file="data/a2_wordlist.csv",
                        lemma=r["lithuanian_TARGET"], pron=r.get("lt_pron", ""), gender=r.get("gender", ""),
                        forms={f: r.get(f, "") for f in ("gen_sg", "fem", "pres3", "past3")}))
    return out


def study_pos():
    return {r["key"]: int(r["order"])
            for r in csv.DictReader(open(os.path.join(ROOT, "data/study_order.csv"), encoding="utf-8"))}


# the multi-word prons the lead listed: one word of the pron carries no mark
PRON_FIXES = ["2013_asmens_tapatybes_kortele", "2424_nuolaidu_kortele", "0736_ne_vienas",
              "0527_kas_nors", "0602_ar_galetumete"]


def resolve_part(src, lw, fw, pw, field, plural):
    """One (lemma word, form word, pron word) -> the part's decision dict."""
    if strip(lw).lower() == strip(fw).lower():
        # a fixed attribute inside the lemma (kojos pirštas -> kojos piršto): the word itself
        if stressed(pw) and strip(pw).lower() == strip(fw).lower():
            cands = [{"form": nfc(pw), "canonical": nfc(pw), "pattern": None,
                      "page": "the card's own pron (same word, its pron_src)", "via": "card pron"}]
        else:
            cands = [{"form": match_case(h, fw), "canonical": h, "pattern": None, "page": page(lw),
                      "via": "headword line"} for h in src.headword(lw)]
    else:
        cands = src.candidates(lw, field, fw, plural=plural)
    how, chosen, why, opts = decide(cands, pw, fw)
    pages = sorted({x["page"] for x in cands if x["form"] == chosen}) if chosen \
        else sorted({x["page"] for x in cands}) or [page(lw)]
    vias = sorted({x["via"] for x in cands if x["form"] == chosen}) if chosen else []
    return dict(how=how, chosen=chosen, why=why, opts=opts, pages=pages, vias=vias, word=fw)


def main():
    src = Source(DUMP)
    cards = load_cards()
    order = study_pos()
    proposals, owner, conflicts = [], [], []

    for c in cards:
        lemma = clean_lemma(c["lemma"])
        pron = clean_lemma(c["pron"])
        plural = "pl" in (c["gender"] or "").lower()
        for field, form in c["forms"].items():
            form = (form or "").strip()
            if not form or stressed(form):
                continue
            results = []
            for alt in [a.strip() for a in form.split(",")]:          # alternates "a, b"
                lw, fw, pw = lemma.split(), alt.split(), pron.split()
                if len(pw) != len(lw):
                    pw = [""] * len(lw)
                if len(fw) > 1 and len(lw) == len(fw):
                    parts = [resolve_part(src, l, f, p, field, plural and field == "gen_sg")
                             for l, f, p in zip(lw, fw, pw)]
                elif len(fw) == 1 and len(lw) > 1:
                    # a one-word form of a multi-word lemma (važiuoti dviračiu -> važiuoja):
                    # the word it inflects is the one the source gives it for
                    tries = [resolve_part(src, l, fw[0], p, field, plural and field == "gen_sg")
                             for l, p in zip(lw, pw)]
                    found = [t for t in tries if t["how"] != "owner" or t["opts"]]
                    parts = [found[0]] if len(found) == 1 else [tries[0] if not found else
                                                                  dict(tries[0], how="owner", why="several words of the lemma have this form in the source", chosen="")]
                else:
                    parts = [resolve_part(src, lemma, alt, pron, field, plural and field == "gen_sg")]
                results.append(parts)
            hows = [p["how"] for parts in results for p in parts]
            if all(h in ("unique", "chosen-by-headword") for h in hows):
                how = "chosen-by-headword" if "chosen-by-headword" in hows else "unique"
                proposed = ", ".join(" ".join(p["chosen"] for p in parts) for parts in results)
            else:
                how, proposed = "owner", ""
            why = "; ".join(f"{p['word']}: {p['why']}" if len(hows) > 1 else p["why"]
                            for parts in results for p in parts)
            opts = " | ".join(p["opts"] for parts in results for p in parts if p["opts"])
            pages = sorted({pg for parts in results for p in parts for pg in p["pages"]})
            vias = sorted({v for parts in results for p in parts for v in p["vias"]})
            row = dict(key=c["key"], level=c["level"], field=field, current=form, proposed=proposed, how=how,
                       source=" ; ".join(pages) + (f" (via kaikki.org Wiktextract, fetched {FETCHED})"
                                                   if any(pg.startswith("http") for pg in pages) else ""),
                       read_from=", ".join(vias), options=opts, reason=why, file=c["file"],
                       lemma=c["lemma"], pron=c["pron"], order=order.get(c["key"], 10**6))
            proposals.append(row)
            if how == "owner":
                owner.append(row)
                if "conflict" in why:
                    conflicts.append(row)

    # the five prons
    pron_rows = []
    by_key = {c["key"]: c for c in cards}
    project_prons = collections.defaultdict(set)     # a sourced pron of the same word elsewhere in the data
    for c in cards:
        p = clean_lemma(c["pron"])
        if " " not in p and stressed(p):
            project_prons[strip(p).lower()].add((p, c["key"]))
    for k in PRON_FIXES:
        c = by_key.get(k)
        if not c:
            continue
        new, hows, pages, whys = [], [], [], []
        for w in c["pron"].split():
            core = re.sub(r"[^\w]", "", strip(w))
            if stressed(w) or not core:
                new.append(w)
                continue
            heads = src.headword(core)
            if len(heads) == 1:
                new.append(w.replace(core, match_case(heads[0], core)))
                hows.append("unique"); pages.append(page(core)); whys.append(f"{core}: headword line")
            elif len(heads) > 1:
                new.append(w); hows.append("owner"); whys.append(f"{core}: ambiguous {' / '.join(heads)}")
            else:
                pp = project_prons.get(core.lower(), set())
                if len({x[0].lower() for x in pp}) == 1:
                    sp, sk = sorted(pp)[0]
                    new.append(w.replace(core, match_case(sp, core)))
                    hows.append("project-pron")
                    pages.append(f"data card {sk}, its pron and pron_src")
                    whys.append(f"{core}: not in en.wiktionary; the project's own sourced pron of the same word ({sk})")
                else:
                    new.append(w); hows.append("owner"); whys.append(f"{core}: not in source")
        how = "owner" if "owner" in hows else ("project-pron" if "project-pron" in hows else "unique")
        row = dict(key=k, level=c["level"], field="pron", current=c["pron"],
                   proposed=" ".join(new) if how != "owner" else "", how=how,
                   source=" ; ".join(pages) + (f" (via kaikki.org Wiktextract, fetched {FETCHED})"
                                               if any(p.startswith("http") for p in pages) else ""),
                   read_from="headword line", options="", reason="; ".join(whys), file=c["file"],
                   lemma=c["lemma"], pron=c["pron"], order=order.get(k, 10**6))
        pron_rows.append(row)
        if how == "owner":
            owner.append(row)
    proposals += pron_rows

    cols = ["key", "level", "field", "current", "proposed", "how", "source", "read_from", "options", "reason", "file"]
    with open(os.path.join(HERE, "proposals_v2.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(proposals)
    owner.sort(key=lambda r: ({"A1": 0}.get(r["level"], 1), r["order"], r["key"], r["field"]))
    with open(os.path.join(HERE, "OWNER_LIST.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["key", "level", "word", "pron", "field", "form", "why", "source_options", "file"])
        w.writeheader()
        for r in owner:
            w.writerow(dict(key=r["key"], level=r["level"], word=r["lemma"], pron=r["pron"], field=r["field"],
                            form=r["current"], why=r["reason"], source_options=r["options"], file=r["file"]))

    # report
    cnt = collections.Counter((r["level"], r["how"]) for r in proposals)
    print("forms:", len(proposals))
    for k in sorted(cnt):
        print(" ", k, cnt[k])
    print("by field:", sorted(collections.Counter((r["field"], r["how"]) for r in proposals).items()))
    print("owner reasons:", collections.Counter(re.sub(r"[:;].*", "", r["reason"]).strip()[:60] for r in owner).most_common(12))
    print("read from:", collections.Counter(r["read_from"] for r in proposals if r["proposed"]).most_common(12))
    print("\nCONFLICTS (source headword ≠ card pron):")
    for r in conflicts:
        print(" ", r["key"], r["field"], r["current"], "|", r["reason"], "|", r["options"])
    print("\nchosen-by-headword:")
    for r in proposals:
        if r["how"] == "chosen-by-headword":
            print(" ", r["key"], r["field"], r["current"], "->", r["proposed"], "| pron", r["pron"], "| from", r["options"])
    print("\nprons:")
    for r in pron_rows:
        print(" ", r["key"], r["current"], "->", r["proposed"] or "(owner)", "|", r["reason"])


if __name__ == "__main__":
    main()
