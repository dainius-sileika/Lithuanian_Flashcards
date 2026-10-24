"""A2 re-base, step 3: add corpus frequency rank (PERLSI 3,000 most frequent
lemmas, from Dadurkevičius 2020, Joint Corpus of Lithuanian; PDF in sources/).

The VU A2 list omits much of the frequent core (laikas, du, prašau, vėl, mūsų
are absent), so "off the A2 list" alone is not a reason to prune: a queue word
in the top 3,000 is still justified. This step makes that visible.

In:  a2_rebase/official_missing_triage.csv, a2_rebase/queue_offlist.csv
Out: same files with a freq_rank column; sources/lt_3000_frequency.csv
Run after coverage.py and overlap.py:  python3 a2_rebase/frequency.py
"""
import csv, re, subprocess, unicodedata
csv.field_size_limit(10**7)

def norm(s):
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    s = "".join(c for c in s if c not in "̀́̃!?…")
    return unicodedata.normalize("NFC", s).strip()

text = subprocess.run(["pdftotext", "-layout", "sources/LT_3000_most_frequent_PERLSI.pdf", "-"],
                      capture_output=True, text=True).stdout
freq = {}
for m in re.finditer(r"^\s*(\d+)\.\s+(\S.*?)\s*$", text, re.M):
    rank, word = int(m.group(1)), m.group(2)
    freq.setdefault(norm(word), (rank, word))
with open("sources/lt_3000_frequency.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["rank", "lemma"])
    w.writerows(sorted(freq.values()))

def rank_of(target):
    t = norm(re.sub(r"\(.*?\)", "", target))
    if t in freq:
        return freq[t][0]
    # multi-word: rank of the rarest content word, so a phrase is no easier than its parts
    parts = [p for p in re.split(r"[\s,]+", t) if len(p) > 2]
    ranks = [freq[p][0] for p in parts if p in freq]
    return max(ranks) if parts and len(ranks) == len(parts) else ""

for path, col in (("a2_rebase/official_missing_triage.csv", "entry"),
                  ("a2_rebase/queue_offlist.csv", "lithuanian_TARGET")):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        r["freq_rank"] = rank_of(r[col])
    cols = [c for c in rows[0] if c != "freq_rank"]
    cols.insert(cols.index(col) + 1, "freq_rank")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

print(f"{len(freq)} lemmas parsed (expect ~3000)")
q = list(csv.DictReader(open("a2_rebase/queue_offlist.csv", encoding="utf-8")))
nva = [r for r in q if r["type"] in ("N", "V", "A", "ADV", "P", "PREP", "NUM")]
top = [r for r in nva if r["freq_rank"] and int(r["freq_rank"]) <= 3000]
print(f"off-list queue words (N/V/A/ADV/P/PREP/NUM): {len(nva)}; of these in top 3,000: {len(top)}; "
      f"not in top 3,000: {len(nva) - len(top)}")
t = list(csv.DictReader(open("a2_rebase/official_missing_triage.csv", encoding="utf-8")))
img = [r for r in t if r["route"] == "IMG"]
print(f"IMG-routed missing entries: {len(img)}; in top 3,000: "
      f"{sum(1 for r in img if r['freq_rank'])}")

# ---- suggested action for each off-list queue row --------------------------
tri = list(csv.DictReader(open("a2_rebase/official_missing_triage.csv", encoding="utf-8")))
swapped = {m.group(1): r["entry"] for r in tri if r["route"] == "SWAP"
           for m in [re.search(r"queue (A2-\d+)", r["note"])] if m}
renamed = {m.group(1): r["entry"] for r in tri if r["route"] == "DUP"
           for m in [re.search(r"queue:(A2-\d+)", r["note"])] if m}
for r in q:
    rk = int(r["freq_rank"]) if r["freq_rank"] else None
    if r["id"] in swapped:
        s = f"SWAP for official '{swapped[r['id']]}'"
    elif r["id"] in renamed:
        s = f"KEEP, retarget to list form '{renamed[r['id']]}'"
    elif r["type"] == "PATTERN":
        s = "DROP (case/tense-name card; fold into cloze)"
    elif r["type"] in ("PHRASE", "SENTENCE"):
        s = "KEEP (phrases are outside a lemma list)"
    elif r["type"] == "NUM":
        s = "KEEP (numerals are core; lemma lists omit them)"
    elif r["type"] == "P":
        s = "KEEP (oblique form of a top-frequency pronoun)"
    elif r["lithuanian_TARGET"] in ("užrakinti", "atrakinti"):
        s = "KEEP (aspect/prefix partner of official 'rakinti')"
    elif rk and rk <= 3000:
        s = f"KEEP (frequency rank {rk})"
    else:
        s = "DEFER (not on A2 list, not in top 3,000; keep, but after list words)"
    r["suggestion"] = s
    r["owner_decision"] = r.get("owner_decision", "")
with open("a2_rebase/queue_offlist.csv", "w", newline="", encoding="utf-8") as f:
    cols = [c for c in q[0] if c not in ("suggestion", "owner_decision")] + ["suggestion", "owner_decision"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(q)
from collections import Counter
print("queue_offlist suggestions:", dict(Counter(r["suggestion"].split(" (")[0].split(" for")[0].split(",")[0] for r in q)))
