#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_study_order.py — SUPERSEDED 2026-10-17 by build_study_order_v2.py (repo root),
which now writes study_order.csv. Kept for the record of the v1 rules (unit quotas,
phase-by-phase A2); do not run it, it would overwrite the adopted order. The last v1
output is study_order.csv at commit 2ea6462.

Original docstring:
build_study_order.py — the learning order of the deck, written to study_order.csv.

    python3 build_study_order.py          # regenerates study_order.csv

build_apkg.py reads study_order.csv and gives every note its `order` as the new-card
position (Anki's `due` for new cards), so a fresh import studies the deck in this
sequence. Card keys/GUIDs never change; only the position does.

Why a generated order and not the wordlist number: the 520 follow the Fluent Forever
625 list category by category (all animals, then all vehicles, ...), which is a bad
study order — 59 adjectives in a row, the core verbs at card 363. The order below
mixes categories in units so the learner meets people, food, a few verbs and a few
adjectives together and can form sentences early (Fluent Forever's own advice: the
pictures are the words, the sentences come once ~100 words are in).

Rules, A1 (427 cards + batonas):
  1. Utility first: inside each category cards are ranked by corpus frequency
     (sources/lt_3000_frequency.csv), unranked ones last in wordlist order.
  2. Units of ~36 cards take a quota from each category (people 3, food/drink 4,
     home 3, verbs 7, adjectives 4 pairs, places 3, body 3, nature 3, transport 1,
     animals 1, clothing 1, jobs 2, colours 1, electronics 1, rest 1) so concrete
     everyday vocabulary and the verbs that use it arrive together.
  3. Adjective antonym pairs stay adjacent (ilgas/trumpas …); the colours are one run.
  4. Confusables apart: a second card with the same Lithuanian word (eiti ×2,
     šokti ×2, aukštas ×2, žemas ×2, senas ×2, žemė ×3, pėda ×2, dangus ×2,
     vyras ×2, garsus ×2) is pushed at least 60 positions after the first.
  5. Pinned neighbours: 531_batonas directly after 182_duona.
Rules, A2: the deck's own A2-tagged cards (93) first, same unit mixing; then the A2
list phase by phase (P-A … P-K). P-A (time, numbers) and P-D (phrases) keep their
file order; the other phases are category-mixed the same way.

Hand overrides: edit study_order.csv directly (it is the file build_apkg.py reads);
re-running this script overwrites it, so put lasting rules in here instead.
"""
import csv, os, re, unicodedata
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
A2_LIST = os.environ.get("A2_LIST", "a2_build/a2_wordlist.csv")


def base(s):
    s = unicodedata.normalize("NFD", s.lower())
    return unicodedata.normalize("NFC", "".join(c for c in s if c not in "̀́̃"))


def rd(p):
    return list(csv.DictReader(open(os.path.join(ROOT, p), encoding="utf-8")))


freq = {base(r["lemma"]): int(r["rank"]) for r in rd("sources/lt_3000_frequency.csv")}

# --- category groups and per-unit quotas --------------------------------------
GROUP = {
    "People": "people", "Job": "jobs",
    "Food": "food", "Beverages": "food",
    "Home": "home", "Electronics": "electronics",
    "Verbs": "verbs", "Adjectives": "adjectives", "Color": "colours",
    "Location": "places", "Transportation": "transport",
    "Body": "body", "Nature": "nature", "Animal": "animals", "Clothing": "clothing",
    "Materials": "rest", "Math": "rest", "Misc": "rest", "Art": "rest", "Society": "rest",
    "Pronouns": "rest",
}
QUOTA = OrderedDict([("people", 3), ("food", 4), ("verbs", 7), ("home", 3), ("adjectives", 8),
                     ("places", 3), ("body", 3), ("nature", 3), ("transport", 1), ("animals", 1),
                     ("clothing", 1), ("jobs", 2), ("colours", 1), ("electronics", 1), ("rest", 1)])
# The corpus is press/legal, so its ranks put asmuo, teismas and praeiti before vaikas and
# valgyti. Hand lists fix the head of each group (everyday utility, judged), and DEMOTE
# sends the administrative or abstract words to the end of their group.
CORE = {
 "people": ["103_zmogus", "086_vyras", "087_moteris", "101_vaikas", "099_berniukas", "100_mergaite", "090_seima", "082_motina", "083_tevas", "080_sunus", "081_dukra", "088_brolis", "089_sesuo", "104_draugas", "084_tevai", "092_senele", "091_senelis", "085_kudikis", "098_kaimynas"],
 "food": ["177_vanduo", "182_duona", "178_pienas", "172_kava", "173_arbata", "180_kiausinis", "181_suris", "188_obuolys", "183_sriuba", "206_druska", "205_cukrus", "176_sultys", "175_alus", "202_pusryciai", "203_pietus", "204_vakariene", "208_maistas", "179_gerimas", "198_saukstas", "197_peilis", "199_sakute", "200_lekste", "201_puodelis", "207_butelis"],
 "verbs": ["376_valgyti", "377_gerti", "366_eiti", "363_dirbti", "409_miegoti", "394_matyti", "375_sakyti", "395_ziureti", "390_girdeti", "423_rasyti", "383_pirkti", "384_moketi", "401_sedeti", "402_stoveti", "367_begti", "420_gaminti", "419_plauti", "421_atidaryti", "422_uzdaryti", "424_skambinti", "403_myleti", "387_mokytis", "374_galvoti", "427_mokyti", "380_sypsotis", "381_juoktis", "382_verkti", "410_pabusti", "438_nesti", "434_rasti", "364_zaisti", "365_groti", "408_sokti", "411_dainuoti", "368_vairuoti", "370_plaukti", "369_skristi", "372_sustoti"],
 "home": ["025_namas", "038_kambarys", "209_stalas", "210_kede", "211_lova", "214_durys", "213_langas", "216_virtuve", "217_vonia", "215_miegamasis", "222_knyga", "236_telefonas", "224_raktas", "226_laiskas", "218_piestukas", "219_rasiklis", "230_popierius", "221_muilas", "240_krepsys", "242_dovana", "246_laikrodis", "247_lempa", "251_kompiuteris", "256_televizorius"],
 "adjectives": ["452_didelis", "453_mazas", "460_naujas", "461_senas", "474_grazus", "475_bjaurus", "456_karstas", "457_saltas", "458_siltas", "459_vesus", "484_brangus", "485_pigus", "498_svarus", "499_purvinas", "472_laimingas", "473_liudnas", "462_jaunas", "463_senas", "448_aukstas", "449_zemas", "446_ilgas", "447_trumpas", "455_greitas", "454_letas", "469_sveikas", "468_sergantis"],
 "places": ["024_miestas", "027_gatve", "045_parduotuve", "036_mokykla", "050_turgus", "030_stotis", "048_ligonine", "049_baznycia", "043_parkas", "033_restoranas", "042_baras", "026_butas", "039_miestelis", "028_kelias", "031_tiltas", "055_bankas", "032_viesbutis"],
 "body": ["258_galva", "277_ranka", "276_koja", "263_akis", "264_burna", "266_nosis", "268_ausis", "267_dantis", "262_plaukai", "260_veidas", "279_sirdis", "273_pirstas", "288_kunas"],
 "nature": ["296_saule", "293_lietus", "294_sniegas", "295_medis", "305_gele", "291_upe", "308_ezeras", "289_jura", "300_miskas", "301_dangus", "303_vejas", "297_menulis", "309_zvaigzde", "316_ugnis", "310_zole"],
 "transport": ["016_autobusas", "013_automobilis", "011_traukinys", "015_dviratis", "022_bilietas", "012_lektuvas"],
 "animals": ["001_suo", "002_kate", "004_paukstis", "003_zuvis", "005_karve", "008_arklys", "006_kiaule", "007_pele"],
 "clothing": ["064_batai", "063_kelnes", "061_marskiniai", "066_paltas", "057_kepure", "058_suknele", "060_sijonas"],
 "jobs": ["110_mokytojas", "113_gydytojas", "111_studentas", "115_padavejas", "118_policininkas", "127_darbas"],
 "electronics": ["236_telefonas", "251_kompiuteris", "256_televizorius", "246_laikrodis", "247_lempa", "257_radijas", "255_fotoaparatas"],
}
DEMOTE = {"109_asmuo", "035_teismas", "105_auka", "052_pastatas", "054_kosmosas", "056_vieta", "051_salis", "044_stovykla", "041_klubas", "040_universitetas", "029_oro_uostas", "034_ukis", "023_transportas", "019_padanga", "020_benzinas", "021_variklis", "009_sparnas", "010_gyvunas", "404_praeiti", "373_sekti", "378_zudyti", "386_sauti", "400_sprogti", "398_tirpti", "406_mustis", "442_purtyti", "443_pasirasyti", "418_lenkti", "530_lydyti", "107_sirgalius", "106_zaidejas", "095_karalius", "096_karaliene", "097_prezidentas", "102_suauges", "108_minia", "093_vyras", "094_zmona", "067_deme", "068_drabuziai", "065_kisene", "062_marskineliai", "059_kostiumas", "079_spalva", "283_prakaitas", "281_smegenys", "269_asara", "272_kojos_pirstas", "275_plastaka", "283_prakaitas", "270_liezuvis", "261_barzda", "290_vandenynas", "306_slenis", "307_saknis", "319_kalva", "318_sala", "315_banga", "321_gamta", "304_zeme", "299_zeme", "476_kurcias", "477_aklas", "486_plokscias", "487_islenktas", "488_vyriskas", "489_moteriskas", "490_ankstas", "491_laisvas", "492_aukstas", "493_zemas", "502_negyvas", "503_gyvas", "508_branduolinis"}
CORE_INDEX = {k: (g, i) for g, ks in CORE.items() for i, k in enumerate(ks)}

SEPARATION = 60          # minimum distance between cards that share a Lithuanian word
PIN_AFTER = {"531_batonas": "182_duona"}


def plain(lt):
    return base(re.split(r"[/(]", lt)[0].strip())


def rank(r):
    k = r["key"]
    if k in CORE_INDEX:
        return (0, CORE_INDEX[k][1])
    if k in DEMOTE:
        return (3, int(r["number"]))
    f = freq.get(plain(r["lithuanian"]))
    return (1, f) if f else (2, int(r["number"]))


def order_block(cards, keep_order=False):
    """Round-robin the cards of one block by group quota; returns the ordered list."""
    if keep_order:
        return list(cards)
    groups = defaultdict(list)
    for c in cards:
        groups[GROUP.get(c["category"], "rest")].append(c)
    for g in groups:
        groups[g].sort(key=rank)
    # adjective antonym pairs travel together: FF numbers 446-507 come in pairs
    if "adjectives" in groups:
        adj = groups["adjectives"]; paired = []; seen = set()
        bynum = {int(c["number"]): c for c in adj}
        for c in sorted(adj, key=rank):
            n = int(c["number"])
            if n in seen:
                continue
            partner = bynum.get(n + 1) if n % 2 == 0 else bynum.get(n - 1)
            if partner and 446 <= n <= 507 and int(partner["number"]) not in seen:
                paired += [c, partner]; seen |= {n, int(partner["number"])}
            else:
                paired.append(c); seen.add(n)
        groups["adjectives"] = paired
    if "colours" in groups:          # one run, in wordlist order
        groups["colours"].sort(key=lambda c: int(c["number"]))
        colours = groups.pop("colours")
    else:
        colours = []
    out = []
    while any(groups.values()):
        for g, q in QUOTA.items():
            if g == "colours":
                if colours and len(out) >= 40:      # colours as one run in the second unit
                    out += colours; colours = []
                continue
            take = groups.get(g, [])[:q]
            groups[g] = groups.get(g, [])[q:]
            out += take
        if colours and not any(groups.values()):
            out += colours; colours = []
    return out


def separate_confusables(ordered):
    """Push a later card with the same Lithuanian word at least SEPARATION positions on
    (or to the end of the block if it is shorter than that)."""
    ordered = list(ordered)
    done = set()
    while True:
        first = {}
        move = None
        for i, c in enumerate(ordered):
            w = plain(c["lithuanian"])
            if w in first and i - first[w] < SEPARATION and c["key"] not in done:
                move = (i, first[w] + SEPARATION, c); break
            first.setdefault(w, i)
        if not move:
            return ordered
        i, target, c = move
        ordered.pop(i); ordered.insert(min(len(ordered), target), c); done.add(c["key"])


def regroup_colours(ordered):
    """Confusable pushes can land inside the colour run; gather the colours again."""
    cols = [c for c in ordered if c.get("category") == "Color"]
    if not cols:
        return ordered
    first = ordered.index(cols[0])
    rest = [c for c in ordered if c.get("category") != "Color"]
    return rest[:first] + cols + rest[first:]


def pin(ordered):
    ordered = list(ordered)
    for k, after in PIN_AFTER.items():
        c = next((x for x in ordered if x["key"] == k), None)
        if not c:
            continue
        ordered.remove(c)
        i = next((j for j, x in enumerate(ordered) if x["key"] == after), None)
        ordered.insert(i + 1 if i is not None else len(ordered), c)
    return ordered


def main():
    deck = rd("cards_anki.csv")
    a1 = [c for c in deck if (c.get("level") or "A1") == "A1"]
    a2 = [c for c in deck if (c.get("level") or "A1") == "A2"]
    out = []
    blk = pin(regroup_colours(separate_confusables(order_block(a1))))
    out += [(c["key"], "A1 deck", c["lithuanian"], c["category"]) for c in blk]
    blk = separate_confusables(order_block(a2))
    out += [(c["key"], "A2 deck cards", c["lithuanian"], c["category"]) for c in blk]
    if os.path.exists(os.path.join(ROOT, A2_LIST)):
        rows = rd(A2_LIST)
        for r in rows:            # adapt to the deck row shape
            r["key"] = r["id"]; r["lithuanian"] = r["lithuanian_TARGET"]; r["number"] = r["id"].replace("A2-", "")
        phases = OrderedDict()
        for r in rows:
            phases.setdefault(r["phase"], []).append(r)
        for ph, cards in phases.items():
            blk = order_block(cards, keep_order=(ph in ("P-A", "P-D")))
            if ph not in ("P-A", "P-D"):
                blk = separate_confusables(blk)
            out += [(c["key"], f"A2 list {ph}", c["lithuanian"], c["category"]) for c in blk]
    # sentence cards: each goes right after the last of its words
    sent_path = os.path.join(ROOT, os.environ.get("SENTENCES", "a2_build/sentences/sentences.csv"))
    if os.path.exists(sent_path):
        pos = {k: i for i, (k, *_rest) in enumerate(out)}
        inserts = []
        for r in rd(os.environ.get("SENTENCES", "a2_build/sentences/sentences.csv")):
            words = [w for w in r["words_used"].split() if w in pos]
            after = max((pos[w] for w in words), default=len(out) - 1)
            inserts.append((after, int(r["order"]), (r["id"], "sentences", r["lt"], "Sakiniai")))
        for after, _o, item in sorted(inserts, reverse=True):
            out.insert(after + 1, item)
    with open(os.path.join(ROOT, "study_order.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["order", "key", "block", "lithuanian", "category"])
        for i, (k, b, lt, cat) in enumerate(out, 1):
            w.writerow([i, k, b, lt, cat])
    print(f"study_order.csv: {len(out)} rows ({len(a1)} A1 deck, {len(a2)} A2 deck, the A2 list and the sentence cards)")


if __name__ == "__main__":
    main()
