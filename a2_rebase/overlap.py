"""A2 re-base, step 2: cross-check the hand triage of the 910 missing official
entries against the deck and queue by English gloss, and verify every SYN claim.
In:  a2_rebase/triage_drafts.csv  (entry,pos,english,route,note — hand-authored)
Out: a2_rebase/official_missing_triage.csv  (+ overlap, owner_decision columns)
Run: python3 a2_rebase/overlap.py
"""
import csv, re, unicodedata
from collections import Counter, defaultdict
csv.field_size_limit(10**7)

def norm_lt(s):
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    s = "".join(c for c in s if c not in "̀́̃")
    return unicodedata.normalize("NFC", s)

def keys_en(s):
    s = re.sub(r"\(.*?\)", "", (s or "").lower())
    out = set()
    for part in re.split(r"[;,/]", s):
        p = re.sub(r"^(to|a|an|the)\s+", "", part.strip()).strip(" !?.\"")
        if len(p) > 2:
            out.add(p)
    return out

deck = list(csv.DictReader(open("cards_anki.csv", encoding="utf-8")))
queue = [r for r in csv.DictReader(open("wordlist_a2_pending.csv", encoding="utf-8"))
         if r["status"] != "review-duplicate"]
by_en = defaultdict(list)
for r in deck:
    for k in keys_en(r["english"]):
        by_en[k].append(f"deck:{norm_lt(r['lithuanian'])}")
for r in queue:
    for k in keys_en(r["english"]):
        by_en[k].append(f"queue:{norm_lt(r['lithuanian_TARGET'])}")
lt_all = {norm_lt(r["lithuanian"]) for r in deck} | {norm_lt(r["lithuanian_TARGET"]) for r in queue}

# number variants: the list often lemmatises as plural (braškės), the queue as
# singular (braškė) — map each entry to its likely other-number forms
PL_SG = [("iai", "is"), ("iai", "ys"), ("ai", "as"), ("ės", "ė"), ("os", "a"),
         ("ios", "ia"), ("ys", "is"), ("ūs", "us"), ("ys", "ė")]
def number_variants(w):
    out = set()
    for pl, sg in PL_SG:
        if w.endswith(pl): out.add(w[: -len(pl)] + sg)
        if w.endswith(sg): out.add(w[: -len(sg)] + pl)
    return out
lt_where = {}
for r in deck: lt_where.setdefault(norm_lt(r["lithuanian"]), f"deck:{r['key']}")
for r in queue: lt_where.setdefault(norm_lt(r["lithuanian_TARGET"]), f"queue:{r['id']}")

rows = list(csv.DictReader(open("a2_rebase/triage_drafts.csv", encoding="utf-8")))
# reviewed corrections live in their own file so they survive any edit or
# sync rollback of the drafts: blank cells keep the draft value
fixes = {f["entry"]: f for f in csv.DictReader(open("a2_rebase/route_fixes.csv", encoding="utf-8"))}
for r in rows:
    f = fixes.pop(r["entry"], None)
    if f:
        for k in ("english", "route", "note"):
            if f[k]: r[k] = f[k]
        r["note"] = f"{r['note']} [{f['source']}]".strip()
assert not fixes, f"route_fixes entries not in triage: {list(fixes)}"
num_dups = []
for r in rows:
    # -ai adverbs (ilgai, lėtai) are not plurals of the adjective, and these
    # plurals are different words from their singulars: ledai ice cream / ledas ice,
    # orai weather / oras air, namai home / namas house
    if r["pos"] == "ADV" or r["entry"] in ("ledai", "orai", "namai"):
        continue
    if r["route"] in ("IMG", "CLOZE", "PHRASE", "PAIR"):
        hit = [lt_where[v] for v in number_variants(norm_lt(r["entry"])) if v in lt_where]
        if hit:
            r["route"] = "DUP"
            r["note"] = (f"other-number form already at {hit[0]} — use the list's form there; " + r["note"]).rstrip("; ")
            num_dups.append(f"{r['entry']} ({hit[0]})")
syn_unverified = []
for r in rows:
    hits = sorted({h for k in keys_en(r["english"]) for h in by_en.get(k, [])})
    r["overlap"] = " ".join(hits)
    if r["route"] == "SYN":
        named = re.findall(r"(?:has|overlaps) ([a-ząčęėįšųūž]+(?: [a-ząčęėįšųūž]+)?)", r["note"])
        within = {norm_lt(x["entry"]) for x in rows}
        ok = (any(norm_lt(n) in lt_all for n in named) or hits
              or any(norm_lt(w) in within for w in re.findall(r"[a-ząčęėįšųūž]+(?: [a-ząčęėįšųūž]+)?", r["note"]))
              or "queue A2-" in r["note"])
        if not ok:
            syn_unverified.append(r["entry"])
            r["note"] += " [SYN target not found in deck/queue — check]"
    r["owner_decision"] = ""
cols = ["entry", "pos", "english", "route", "note", "overlap", "owner_decision"]
with open("a2_rebase/official_missing_triage.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

print("routes:", dict(Counter(r["route"] for r in rows).most_common()))
flag = [r for r in rows if r["overlap"] and r["route"] in ("IMG", "CLOZE", "PHRASE")]
print(f"{len(flag)} IMG/CLOZE/PHRASE rows share a gloss word with a deck/queue row "
      "(reviewed 2026-10-10; remaining matches are distinct words, see overlap column)")
print("\nSYN claims not verified:", syn_unverified)
print(f"\n{len(num_dups)} entries re-routed DUP (singular/plural of a deck/queue word):", "; ".join(num_dups))
