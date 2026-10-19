#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_study_order_v3.py — the learning order of the deck, written to study_order.csv.

    python3 build_study_order_v3.py                  # regenerates study_order.csv (and the recording order)
    python3 build_study_order_v3.py --report         # also prints the audit tables for the new order
    python3 build_study_order_v3.py --audit [FILE]   # audits an existing order file (default study_order.csv), writes nothing
    python3 build_study_order_v3.py --apply-retier   # writes the `level` of a2_build/study_order/retier_v3.csv into
                                                     # cards_anki.csv, master_wordlist.csv and a2_build/a2_wordlist.csv
    python3 build_study_order_v3.py --rebuild-subs <lt_full.txt>   # re-derives the subtitle lemma list

Deck v3.0 (2026-10-19). build_apkg.py reads study_order.csv and gives every note its `order` as the
new-card position (Anki `due`). Keys and GUIDs never change; v3.0 is a delete-and-reimport release, so
the whole order may move; from v3.0 on keys and GUIDs are frozen. build_study_order_v2.py stays in the
tree as history (adopted 2026-10-17, superseded by this file); the v2 order is in git.

WHAT V3 CHANGES (the audit of the v2 order is reproducible: `--audit` on any order file)
  1. Dependencies. A reading card (cloze, pair, sentence) waits until every word of its sentence has
     been introduced by an earlier card of the same subdeck (or any card of an earlier subdeck). v2
     had 193 of 1,981 in-deck dependencies pointing forward (a cloze at 144 used manyti, taught at
     1254). Words are matched by surface form and by simplemma lemma against every card's headword and
     listed forms; ne- + a known verb counts as known; sentence-internal capitalised names are ignored.
  2. The A1/A2 split. a2_build/study_order/retier_v3.csv moves a small set of cards between the
     subdecks: A2 words that A1 sentences depend on and that are themselves A1 (manyti, vėluoti, likti …),
     antonym partners split across the subdecks (piktas, abi, linksmas, šiemet), and the rare
     Fluent-Forever leftovers that sat at the A1 tail (plaštaka, lydyti, išlenktas …) which are A2 by any
     CEFR list. `--apply-retier` writes the levels into the data files; the schedule reads the file
     either way, so the order and the data agree.
  3. Pacing. v2's greedy pick left runs at the tail of each subdeck (21 phrases in a row at the end of
     A1, 31 nouns and 119 reading cards in a row at the end of A2) because the per-10 caps were lower
     than the lane's share. v3 adds lane pressure (a lane behind its share is pulled forward, one ahead
     is held back) and derives the reading-card cap from the subdeck's own share of reading cards.
  4. Phrases earlier: the greetings start at position 20, not 40 (Labas on day two at 20 cards a day).
  5. Pairs. Besides the Fluent Forever adjective pairs and PIN_AFTER, the antonym / counterpart pairs
     noted in the A2 list ("pair with …") sit next to each other when both are in one subdeck.
  6. Confusables. Same headword ≥ 60 apart (as v2); look-alikes (edit distance 1, ≥ 4 letters, not a
     pronoun paradigm, not a pair) ≥ 30 apart: kitas/kinas, ausis/sausis, keisti/leisti …
  7. Sentence cards are scheduled inside their own subdeck as reading cards with their words as
     prerequisites (v2 inserted them after their last word, which put A2-level sentences inside the
     A1 block).

THE SCORE (lower = earlier) is v2's, unchanged:
  score = 0.6·ln(subtitle rank) + 0.4·ln(press rank) + tier offset − 0.3 if in the VU A1/A2 lexicon.
  Subtitle rank: OpenSubtitles 2018 Lithuanian (hermitdave/FrequencyWords, CC-BY-SA 4.0) lemmatised with
  simplemma (a2_build/study_order/opensubtitles_lt_lemmas.csv), missing = 30000. Press rank: PERLSI 3000
  (sources/lt_3000_frequency.csv), missing = not penalised. A phrase or sentence ranks as its rarest word.
  Tiers: T0 survival −3.0 (the hand-ORDERED SURVIVAL list and SURVIVAL_PHRASES are placed outright),
  T1 daily −1.5, T2 0, T3 demoted +1.5; +1.0 "Extended patterns", +0.8 phase P-K.

THE SCHEDULE (per subdeck: A1 then A2; greedy, best eligible first)
  - lane cap 3 per trailing 10 (phrases 2 in A1); lane pressure LANE_PULL × (expected − placed), clipped
  - A1: no reading card before 100, no phrase picture before 20, colours one run from 40 on;
    A2: no reading card before 30; reading cap per 10 = clip(ceil(10·share) + 1, 4, 8)
  - prerequisites (rule 1), sequences (one … ten, Monday … Sunday, months, seasons, ordinals, tens, teens),
    PIN_AFTER, PAIRS (partner placed straight after), SEPARATION 60 / LOOKALIKE_SEPARATION 30
  - deadlock at the tail: relax everything except pins and pairs, never place a pinned card before its anchor
Output columns: order, key, block, lithuanian, category, lane, route, tier, sub_rank, press_rank, score,
old_order (position in the study_order.csv this run replaces).
Also written: a2_build/study_order/recording_order_v3.csv — the recorder's order: A1 first, then A2, each
in study order, with the example sentence for cloze cards.
"""
import csv, math, os, re, sys, unicodedata
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
A2_LIST = os.environ.get("A2_LIST", "a2_build/a2_wordlist.csv")
SENTENCES = os.environ.get("SENTENCES", "a2_build/sentences/sentences.csv")
SUBS_LEMMAS = "a2_build/study_order/opensubtitles_lt_lemmas.csv"
RETIER = "a2_build/study_order/retier_v3.csv"
OUT = os.environ.get("STUDY_ORDER_OUT", "study_order.csv")
RECORDING_OUT = "a2_build/study_order/recording_order_v3.csv"

W_SUB, W_PRESS = 0.6, 0.4
MISSING_SUB = 30000
VU_BONUS = 0.3
TIER_OFFSET = {0: -3.0, 1: -1.5, 2: 0.0, 3: 1.5}
EXTENDED_PENALTY, PK_PENALTY = 1.0, 0.8
LANE_CAP, WINDOW = 3, 10
LANE_CAP_OVERRIDE_A1 = {"phrases": 2}
LANE_MIN_GAP_A1 = {"phrases": 4}            # in A1 a phrase picture every 4+ cards, not two in a row
PULL_GAP, PULL_FLOOR = 1.0, -5.0            # a word a reading card needs is pulled to (that card's score + gap)
SENT_AFTER = 0.3                            # a sentence card scores just after the last of its words
LANE_PULL, LANE_PULL_MAX = 0.08, 2.0        # score units per card of lane deficit, clipped
FIRST_CLOZE, FIRST_PHRASE, FIRST_COLOURS = 100, 20, 40
A2_FIRST_CLOZE = 30
READING_CAP_MIN, READING_CAP_MAX = 4, 8
SEPARATION, LOOKALIKE_SEPARATION = 60, 30
READING = ("CLOZE", "PAIR", "SENT")

# Pinned neighbours (a pinned card waits for its anchor, then follows it directly).
PIN_AFTER = {"531_batonas": "182_duona",
             "A2-1898": "082_motina", "A2-1899": "083_tevas", "081_dukra": "080_sunus", "089_sesuo": "088_brolis",
             "092_senele": "091_senelis", "A2-0581": "A2-0582", "094_zmona": "093_vyras",
             "A2-1924": "A2-1923", "A2-1874": "A2-1873", "A2-1891": "A2-1890"}
# Antonym / counterpart pairs by plain headword (the A2 list's "pair with" notes, 2026-10-19); whichever is
# scheduled first pulls the other straight after it. Pairs split across subdecks are reported, not forced.
PAIRS = [("arti", "toli"), ("aukštyn", "žemyn"), ("netyčia", "tyčia"), ("į vidų", "viduje"), ("abi", "abu"),
         ("šiemet", "pernai"), ("leidžiama", "draudžiama"), ("išjungtas", "įjungtas"), ("linksmas", "liūdnas"),
         ("gazuotas vanduo", "negazuotas vanduo"), ("išėjimas", "įėjimas"), ("kvepėti", "smirdėti"),
         ("kvailas", "protingas"), ("sotus", "alkanas"), ("pirkėjas", "pardavėjas"), ("saulėta", "debesuota"),
         ("malonus", "piktas")]
# look-alike separation does not apply inside these categories (a paradigm is learnt as a set)
LOOKALIKE_EXEMPT = {"Pronouns", "Numbers", "Question words"}
# transparent inflections the lemmatiser misses (adverbial cases): a learner who knows namas reads namie
FORM_ALIAS = {"namie": "namas"}


# --- text helpers --------------------------------------------------------------
def base(s):
    s = unicodedata.normalize("NFD", s.lower())
    return unicodedata.normalize("NFC", "".join(c for c in s if c not in "̀́̃"))


def plain(lt):
    """Headword without accents, bracketed glosses or trailing punctuation."""
    s = base(re.split(r"[/(]", lt)[0])
    return re.sub(r"[^\w\s.-]", "", s).strip(" .-").strip()


def tokens(lt):
    return [t for t in re.findall(r"[a-ząčęėįšųūž]+", plain(lt)) if t]


def rd(p):
    return list(csv.DictReader(open(os.path.join(ROOT, p), encoding="utf-8")))


_lemma_cache = {}
try:
    import simplemma
    def lemma(w):
        if w not in _lemma_cache:
            _lemma_cache[w] = simplemma.lemmatize(w, lang="lt").lower()
        return _lemma_cache[w]
except ImportError:
    def lemma(w):
        return w


def rebuild_subs(src):
    """Sum the OpenSubtitles word-form counts per simplemma lemma; keep the top 40k."""
    cnt = Counter()
    for line in open(src, encoding="utf-8"):
        parts = line.split()
        if len(parts) != 2 or not parts[0].isalpha():
            continue
        cnt[lemma(parts[0])] += int(parts[1])
    os.makedirs(os.path.join(ROOT, os.path.dirname(SUBS_LEMMAS)), exist_ok=True)
    with open(os.path.join(ROOT, SUBS_LEMMAS), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["rank", "lemma", "count"])
        for i, (l, n) in enumerate(cnt.most_common(40000), 1):
            w.writerow([i, l, n])
    print(f"{SUBS_LEMMAS}: {min(len(cnt), 40000)} lemmas from {src}")


# --- frequency sources ---------------------------------------------------------
def load_sources():
    sub = {r["lemma"]: int(r["rank"]) for r in rd(SUBS_LEMMAS)} if os.path.exists(os.path.join(ROOT, SUBS_LEMMAS)) else {}
    press = {base(r["lemma"]).strip(): int(r["rank"]) for r in rd("sources/lt_3000_frequency.csv")}
    vu = {base(r["entry"]).strip() for r in rd("sources/vu_a1a2_lexicon.csv")}
    return sub, press, vu


def rank_of(table, tok, forms, missing):
    cands = {lemma(tok)} | {lemma(base(f)) for f in forms if f}
    found = [2 * table[c] for c in cands if c in table]
    if tok in table:
        found.append(table[tok])
    return min(found) if found else missing


def freq(card, sub, press):
    toks = tokens(card["lt"])
    content = [t for t in toks if len(t) > 1] or toks or [plain(card["lt"])]
    forms = card.get("forms", []) if len(content) == 1 else []
    s = [rank_of(sub, t, forms, MISSING_SUB) for t in content]
    p = [rank_of(press, t, forms, None) for t in content]
    return max(s), (max(p) if all(p) else None)


# --- lanes ---------------------------------------------------------------------
LANE = {
    "People": "people", "Job": "work", "Food": "food", "Beverages": "food", "Home": "home",
    "Electronics": "electronics", "Verbs": "verbs", "Adjectives": "adjectives", "Color": "colours",
    "Location": "places", "Transportation": "transport", "Body": "body", "Nature": "nature",
    "Animal": "animals", "Clothing": "clothing", "Materials": "rest", "Math": "rest", "Misc": "rest",
    "Art": "rest", "Society": "society", "Pronouns": "function",
    "Nouns": "nouns", "Adverbs": "adverbs", "Time": "time", "Numbers": "numbers", "Abstract": "abstract",
    "Work & culture": "work", "Work & school": "work", "Jobs": "work", "Prepositions": "function",
    "Conjunctions": "function", "Question words": "function", "Modal & core verbs": "verbs",
    "Getting by": "phrases", "Formulas": "phrases", "Phrases": "phrases", "Basics": "phrases",
    "Core patterns": "phrases", "Extended patterns": "phrases", "Opinion & discourse": "phrases",
    "Transactions": "phrases", "Greetings": "phrases", "Politeness": "phrases", "Functions": "phrases",
    "Feelings": "feelings", "Travel": "transport", "Health": "body", "Technology": "electronics",
    "Shopping": "shopping", "Money & admin": "society", "Nationalities": "rest", "Languages": "rest",
    "Sakiniai": "sentences",
}
TYPE_LANE = {"N": "nouns", "V": "verbs", "A": "adjectives", "ADV": "adverbs", "P": "function",
             "PREP": "function", "CONJ": "function", "Q": "function", "NUM": "numbers",
             "PHRASE": "phrases", "SENTENCE": "phrases"}

# --- tiers (judged; carried over from v2) -----------------------------------------
SURVIVAL = ["103_zmogus", "086_vyras", "087_moteris", "177_vanduo", "182_duona", "376_valgyti", "377_gerti",
            "101_vaikas", "172_kava", "173_arbata", "366_eiti", "452_didelis", "453_mazas", "025_namas", "178_pienas",
            "175_alus", "104_draugas", "090_seima", "045_parduotuve", "363_dirbti", "024_miestas", "188_obuolys",
            "183_sriuba", "064_batai", "016_autobusas", "001_suo", "002_kate",
            "354_taip", "355_ne", "510_as", "511_tu", "512_jis", "513_ji", "515_mes", "516_jus", "517_jie", "514_tai",
            "464_geras", "465_blogas", "133_pinigai", "160_kaina"]
SURVIVAL_INDEX = {k: i for i, k in enumerate(SURVIVAL)}
SURVIVAL_PHRASES = ["Labas", "Ačiū", "Prašau", "Laba diena", "Atsiprašau", "Viso gero", "Iki", "Nesuprantu", "Kiek kainuoja?",
                    "Kur yra…?", "Labas rytas", "Labas vakaras", "Sveiki", "Labai ačiū", "Nėra už ką", "Kur yra tualetas?",
                    "Sąskaitą, prašau", "Norėčiau…", "Ar kalbate angliškai?", "Kaip sekasi?", "Man gerai", "Nežinau",
                    "Mano vardas…", "Aš esu iš…", "Labanakt", "Iki pasimatymo", "Atleiskite", "Malonu susipažinti",
                    "Skanaus", "Į sveikatą!", "Ar galite man padėti?", "Ar galite pakartoti?", "Prašom kalbėti lėčiau"]
SURVIVAL_PHRASE_INDEX = {plain(w): i for i, w in enumerate(SURVIVAL_PHRASES)}
CORE = {
 "people": ["103_zmogus", "086_vyras", "087_moteris", "101_vaikas", "099_berniukas", "100_mergaite", "090_seima", "082_motina", "083_tevas", "080_sunus", "081_dukra", "088_brolis", "089_sesuo", "104_draugas", "084_tevai", "092_senele", "091_senelis", "085_kudikis", "098_kaimynas"],
 "food": ["177_vanduo", "182_duona", "178_pienas", "172_kava", "173_arbata", "180_kiausinis", "181_suris", "188_obuolys", "183_sriuba", "206_druska", "205_cukrus", "176_sultys", "175_alus", "202_pusryciai", "203_pietus", "204_vakariene", "208_maistas", "179_gerimas", "198_saukstas", "197_peilis", "199_sakute", "200_lekste", "201_puodelis", "207_butelis", "185_vistiena", "184_mesa", "186_jautiena", "187_kiauliena", "189_bulve", "190_pomidoras", "191_morka", "192_darzove", "193_vaisius", "194_pyragas", "195_saldainis", "196_ledai"],
 "verbs": ["376_valgyti", "377_gerti", "366_eiti", "363_dirbti", "409_miegoti", "394_matyti", "375_sakyti", "395_ziureti", "390_girdeti", "423_rasyti", "383_pirkti", "384_moketi", "401_sedeti", "402_stoveti", "367_begti", "420_gaminti", "419_plauti", "421_atidaryti", "422_uzdaryti", "424_skambinti", "403_myleti", "387_mokytis", "374_galvoti", "427_mokyti", "380_sypsotis", "381_juoktis", "382_verkti", "410_pabusti", "438_nesti", "434_rasti", "364_zaisti", "365_groti", "408_sokti", "411_dainuoti", "368_vairuoti", "370_plaukti", "369_skristi", "372_sustoti"],
 "home": ["025_namas", "038_kambarys", "209_stalas", "210_kede", "211_lova", "214_durys", "213_langas", "216_virtuve", "217_vonia", "215_miegamasis", "222_knyga", "236_telefonas", "224_raktas", "226_laiskas", "218_piestukas", "219_rasiklis", "230_popierius", "221_muilas", "240_krepsys", "242_dovana", "246_laikrodis", "247_lempa", "251_kompiuteris", "256_televizorius"],
 "adjectives": ["452_didelis", "453_mazas", "460_naujas", "461_senas", "474_grazus", "475_bjaurus", "456_karstas", "457_saltas", "458_siltas", "459_vesus", "484_brangus", "485_pigus", "498_svarus", "499_purvinas", "472_laimingas", "473_liudnas", "462_jaunas", "463_senas", "448_aukstas", "449_zemas", "446_ilgas", "447_trumpas", "455_greitas", "454_letas", "469_sveikas", "468_sergantis", "464_geras", "465_blogas"],
 "places": ["024_miestas", "027_gatve", "045_parduotuve", "036_mokykla", "050_turgus", "030_stotis", "048_ligonine", "049_baznycia", "043_parkas", "033_restoranas", "042_baras", "026_butas", "039_miestelis", "028_kelias", "031_tiltas", "055_bankas", "032_viesbutis"],
 "body": ["258_galva", "277_ranka", "276_koja", "263_akis", "264_burna", "266_nosis", "268_ausis", "267_dantis", "262_plaukai", "260_veidas", "279_sirdis", "273_pirstas", "288_kunas"],
 "nature": ["296_saule", "293_lietus", "294_sniegas", "295_medis", "305_gele", "291_upe", "308_ezeras", "289_jura", "300_miskas", "301_dangus", "303_vejas", "297_menulis", "309_zvaigzde", "316_ugnis", "310_zole"],
 "transport": ["016_autobusas", "013_automobilis", "011_traukinys", "015_dviratis", "022_bilietas", "012_lektuvas"],
 "animals": ["001_suo", "002_kate", "004_paukstis", "003_zuvis"],
 "clothing": ["064_batai", "063_kelnes", "061_marskiniai", "066_paltas", "057_kepure", "058_suknele", "060_sijonas"],
 "jobs": ["110_mokytojas", "113_gydytojas", "111_studentas", "115_padavejas", "118_policininkas", "127_darbas"],
 "electronics": ["236_telefonas", "251_kompiuteris", "256_televizorius", "246_laikrodis", "247_lempa", "257_radijas", "255_fotoaparatas"],
 "society": ["133_pinigai", "160_kaina", "132_vaistai", "152_laikrastis", "155_sportas", "169_muzika", "167_daina", "312_oras", "284_liga", "298_pasaulis", "344_data", "340_puse", "336_kilogramas", "334_metras", "343_temperatura", "464_geras", "465_blogas", "479_piktas"],
}
CORE_T1 = {k for ks in CORE.values() for k in ks}
DEMOTE = {"109_asmuo", "035_teismas", "105_auka", "052_pastatas", "054_kosmosas", "056_vieta", "051_salis", "044_stovykla", "041_klubas", "040_universitetas", "029_oro_uostas", "034_ukis", "023_transportas", "019_padanga", "020_benzinas", "021_variklis", "009_sparnas", "010_gyvunas", "404_praeiti", "373_sekti", "378_zudyti", "386_sauti", "400_sprogti", "398_tirpti", "406_mustis", "442_purtyti", "443_pasirasyti", "418_lenkti", "530_lydyti", "107_sirgalius", "106_zaidejas", "095_karalius", "096_karaliene", "097_prezidentas", "102_suauges", "108_minia", "093_vyras", "094_zmona", "067_deme", "068_drabuziai", "065_kisene", "062_marskineliai", "059_kostiumas", "079_spalva", "283_prakaitas", "281_smegenys", "269_asara", "272_kojos_pirstas", "275_plastaka", "270_liezuvis", "261_barzda", "290_vandenynas", "306_slenis", "307_saknis", "319_kalva", "318_sala", "315_banga", "321_gamta", "304_zeme", "299_zeme", "476_kurcias", "477_aklas", "486_plokscias", "487_islenktas", "488_vyriskas", "489_moteriskas", "490_ankstas", "491_laisvas", "492_aukstas", "493_zemas", "502_negyvas", "503_gyvas", "508_branduolinis",
          "128_religija", "129_dangus", "130_pragaras", "131_mirtis", "134_doleris", "135_banknotas", "136_santuoka", "139_santykiai", "140_rase", "141_seksas", "142_lytis", "143_zmogzudyste", "144_kalejimas", "145_technologija", "146_energija", "147_karas", "148_taika", "149_puolimas", "150_rinkimai", "153_nuodai", "154_ginklas", "156_lenktynes", "161_sutartis", "162_narkotikas", "164_mokslas", "165_dievas", "171_menas", "227_raide", "250_tinklas", "320_karstis", "337_colis", "338_peda", "339_svaras", "341_apskritimas", "342_kvadratas", "346_krastas", "347_kampas", "350_priebalsis", "351_balsis", "362_rastas", "414_melstis", "528_serti", "529_lesinti"}
T0_CATEGORIES = {"Greetings", "Politeness", "Question words", "Basics", "Getting by"}
T0_WORDS = {"nulis", "vienas", "du", "trys", "keturi", "penki", "šeši", "septyni", "aštuoni", "devyni", "dešimt",
            "dvidešimt", "šimtas", "tūkstantis",
            "šiandien", "vakar", "rytoj", "dabar", "valanda", "diena", "būti", "turėti", "galėti", "norėti", "reikėti",
            "mano", "tavo", "jo", "jos", "mūsų", "jūsų", "savo", "šis", "tas", "į", "iš", "su", "ir", "bet", "ar",
            "labai", "čia", "ten", "gerai", "dėkui", "kainuoti", "euras", "kalbėti", "suprasti", "žinoti", "gyventi",
            "mėgti", "patikti", "duoti", "padėti", "važiuoti", "gelbėkit", "sąskaita", "vaistinė"}
T1_CATEGORIES = {"Food", "Beverages", "Home", "Body", "Clothing", "People", "Location", "Transportation", "Travel",
                 "Time", "Numbers", "Health", "Shopping", "Transactions", "Money & admin", "Formulas", "Core patterns",
                 "Modal & core verbs", "Prepositions", "Conjunctions", "Pronouns", "Sakiniai"}
T1_WORDS = {"ateiti", "daryti", "pirkti", "laukti", "grįžti", "ieškoti", "klausti", "atsakyti", "dirbti", "mokytis",
            "skaityti", "rašyti", "klausyti", "prašyti", "vadintis", "eiti", "atvažiuoti", "išeiti", "įeiti", "imti",
            "gauti", "pasakyti", "paimti", "rasti", "žiūrėti", "sėdėti", "gyventi", "jau", "dar", "tik", "daug",
            "mažai", "šiek tiek", "gal", "tikrai", "visada", "niekada", "kartais", "dažnai", "vėl", "taip pat",
            "svarbus", "įdomus", "pilnas", "tuščias", "uždarytas", "atidarytas", "alkanas", "pavargęs",
            "tualetas", "bankomatas", "autobusų stotis", "stotelė", "kasa", "piniginė", "lagaminas", "bilietas",
            "sveikata", "vaistinė", "kelionė", "žmonės", "ponia", "Lietuva", "lietuvis", "lietuvių kalba", "anglų kalba"}


def tier_of(card):
    k, cat, w = card["key"], card["category"], plain(card["lt"])
    if card["source"] == "deck":
        if k in SURVIVAL_INDEX: return 0
        if k in DEMOTE: return 3
        if k in CORE_T1: return 1
        return 2
    if cat in T0_CATEGORIES or w in T0_WORDS: return 0
    if cat in T1_CATEGORIES or w in T1_WORDS: return 1
    return 2


def extra_penalty(card):
    p = 0.0
    if card["category"] == "Extended patterns": p += EXTENDED_PENALTY
    if card.get("phase") == "P-K": p += PK_PENALTY
    return p


SEQUENCES = [
    ["vienas", "du", "trys", "keturi", "penki", "šeši", "septyni", "aštuoni", "devyni", "dešimt"],
    ["vienuolika", "dvylika", "trylika", "keturiolika", "penkiolika", "šešiolika", "septyniolika", "aštuoniolika", "devyniolika"],
    ["dvidešimt", "trisdešimt", "keturiasdešimt", "penkiasdešimt", "šešiasdešimt", "septyniasdešimt", "aštuoniasdešimt", "devyniasdešimt"],
    ["šimtas", "tūkstantis", "milijonas"],
    ["pirmas", "antras", "trečias", "ketvirtas", "penktas", "šeštas", "septintas", "aštuntas", "devintas", "dešimtas"],
    ["pirmadienis", "antradienis", "trečiadienis", "ketvirtadienis", "penktadienis", "šeštadienis", "sekmadienis"],
    ["sausis", "vasaris", "kovas", "balandis", "gegužė", "birželis", "liepa", "rugpjūtis", "rugsėjis", "spalis",
     "lapkritis", "gruodis"],
    ["pavasaris", "vasara", "ruduo", "žiema"],
]


# --- load the cards ------------------------------------------------------------
def load_retier():
    p = os.path.join(ROOT, RETIER)
    return {r["key"]: r["to"] for r in rd(RETIER)} if os.path.exists(p) else {}


def load_cards(old, retier):
    cards = []
    for r in rd("cards_anki.csv"):
        cards.append({"key": r["key"], "lt": r["lithuanian"], "en": r["english"], "category": r["category"],
                      "number": int(r["number"]), "level": (r.get("level") or "A1"), "route": "IMG", "source": "deck",
                      "phase": "", "type": "", "ex": "", "words": "",
                      "forms": [r.get(f, "") for f in ("gen_sg", "pres3", "past3", "fem")]})
    if os.path.exists(os.path.join(ROOT, A2_LIST)):
        for r in rd(A2_LIST):
            cards.append({"key": r["id"], "lt": r["lithuanian_TARGET"], "en": r["english"], "category": r["category"],
                          "number": 10000 + int(re.sub(r"\D", "", r["id"]) or 0),
                          "level": (r.get("level") or "A2").strip() or "A2", "route": r.get("route", ""),
                          "source": "list", "phase": r.get("phase", ""), "type": r.get("type", ""),
                          "ex": r.get("example_lt", "") if r.get("route") in ("CLOZE", "PAIR") else "", "words": "",
                          "forms": [r.get(f, "") for f in ("gen_sg", "pres3", "past3", "fem")]})
    if os.path.exists(os.path.join(ROOT, SENTENCES)):
        for r in rd(SENTENCES):
            cards.append({"key": r["id"], "lt": r["lt"], "en": r["en"], "category": "Sakiniai",
                          "number": 20000 + int(r["order"]), "level": (r.get("level") or "A2").strip() or "A2",
                          "route": "SENT", "source": "sentences", "phase": "", "type": "SENTENCE",
                          "ex": r["lt"], "words": r["words_used"], "forms": []})
    for c in cards:
        c["level"] = retier.get(c["key"], c["level"])
        c["lane"] = LANE.get(c["category"]) or TYPE_LANE.get(c.get("type", ""), "rest")
        c["tier"] = tier_of(c)
        c["old"] = old.get(c["key"], "")
    return cards


def score_cards(cards, sub, press, vu):
    for c in cards:
        s, p = freq(c, sub, press)
        c["sub"], c["press"] = s, p
        w = plain(c["lt"])
        c["vu"] = w in vu or lemma(w) in vu
        f = W_SUB * math.log(s) + W_PRESS * math.log(p) if p else math.log(s)
        c["score"] = f + TIER_OFFSET[c["tier"]] + extra_penalty(c) - (VU_BONUS if c["vu"] else 0)
        if c["key"] in SURVIVAL_INDEX:
            c["score"] = -20 + 0.1 * SURVIVAL_INDEX[c["key"]]
        elif c["source"] == "list" and plain(c["lt"]) in SURVIVAL_PHRASE_INDEX and c["route"] == "PHRASE":
            c["score"] = -19 + 0.1 * SURVIVAL_PHRASE_INDEX[plain(c["lt"])]   # from FIRST_PHRASE on, among the survival words
    by_word = defaultdict(list)
    for c in cards:
        by_word[plain(c["lt"])].append(c)
    for seq in SEQUENCES:
        for lvl in ("A1", "A2"):
            run = [m for w in seq for m in by_word.get(w, []) if m["level"] == lvl and m["lane"] in ("numbers", "time", "nouns")]
            best = -99
            for i, m in enumerate(run):
                m["score"] = max(m["score"], best + 1e-6); best = m["score"]
                m["prev"] = run[i - 1]["key"] if i else None


# --- vocabulary and dependencies -----------------------------------------------
def intro_forms(c):
    """Every surface form and lemma a card teaches: its headword tokens and listed forms."""
    forms = set()
    for t in tokens(c["lt"]):
        forms.add(t); forms.add(lemma(t))
    for f in c["forms"]:
        for t in tokens(f or ""):
            forms.add(t); forms.add(lemma(t))
    return forms


def sentence_tokens(ex):
    """(token, is_name) for the words of a sentence; a name is a capitalised word that does not open the sentence."""
    out = []
    for m in re.finditer(r"[A-Za-zĄČĘĖĮŠŲŪŽąčęėįšųūž]+", re.sub(r"[{}]", "", ex)):
        raw = m.group(0)
        start = m.start() == 0 or re.match(r"^[\s\"„“(]*$", re.sub(r"[{}]", "", ex)[:m.start()]) is not None \
            or re.search(r"[.!?]\s*$", re.sub(r"[{}]", "", ex)[:m.start()]) is not None
        out.append((base(raw), raw[:1].isupper() and not start))
    return out


def build_dependencies(cards):
    """card -> list of dependency groups; each group is the list of keys that would satisfy one word."""
    intro = defaultdict(set)
    for c in cards:
        if c["route"] == "SENT":
            c["intro"] = set(); continue
        c["intro"] = intro_forms(c)
        for f in c["intro"]:
            intro[f].add(c["key"])

    def introducers(t):
        t = FORM_ALIAS.get(t, t)
        ks = set(intro.get(t, ())) | set(intro.get(lemma(t), ()))
        if not ks and t.startswith("ne") and len(t) > 4:           # negation is transparent: nemėgsta <- mėgti
            ks = set(intro.get(t[2:], ())) | set(intro.get(lemma(t[2:]), ()))
        return ks

    for c in cards:
        c["deps"], c["outside"] = [], []
        if c["route"] not in READING:
            continue
        seen = set()
        for t, is_name in sentence_tokens(c["ex"]):
            if is_name or len(t) == 1 or t in seen or t in c["intro"] or lemma(t) in c["intro"]:
                continue
            seen.add(t)
            ks = introducers(t) - {c["key"]}
            if ks:
                c["deps"].append((t, sorted(ks)))
            else:
                c["outside"].append(t)
        for k in c["words"].split():                                 # sentences.csv words_used, when it names a key
            if re.match(r"^(\d{3}_|A2-|S-)", k) and k not in {x for _, ks in c["deps"] for x in ks}:
                c["deps"].append((k, [k]))
    return cards


# --- the scheduler -------------------------------------------------------------
def adjective_partner(card, pool):
    n = card["number"]
    if card["source"] != "deck" or not 446 <= n <= 507:
        return None
    pn = n + 1 if n % 2 == 0 else n - 1
    return next((c for c in pool if c["source"] == "deck" and c["number"] == pn), None)


def lev1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def lookalike_pairs(pool, pairs_by_key):
    """{key: {key}} of single-word cards one edit apart (≥ 4 letters), outside paradigms and pairs."""
    words = [(c["key"], plain(c["lt"]), c["category"]) for c in pool
             if c["route"] in ("IMG", "CLOZE", "PAIR") and " " not in plain(c["lt"]) and len(plain(c["lt"])) >= 4]
    out = defaultdict(set)
    for i, (k, w, cat) in enumerate(words):
        for k2, w2, cat2 in words[i + 1:]:
            if cat in LOOKALIKE_EXEMPT and cat2 in LOOKALIKE_EXEMPT:
                continue
            if k2 in pairs_by_key.get(k, ()) or w == w2:
                continue
            if lev1(w, w2):
                out[k].add(k2); out[k2].add(k)
    return out



def break_cycles(block, keys):
    """Reading cards may need each other's word (kad: 'Manau, kad…'; manyti: 'Manau, kad…'). Inside each
    strongly connected component of that graph the better-scored card goes first and drops its dependency
    on the worse-scored members; a dependency group left empty is waived."""
    bykey = {c["key"]: c for c in block}
    edges = {c["key"]: {k for _t, ks in c["deps"] for k in ks if k in keys and bykey[k]["route"] in READING}
             for c in block if c["route"] in READING}
    index, low, on, stack, sccs, counter = {}, {}, set(), [], [], [0]

    def strong(v):
        index[v] = low[v] = counter[0]; counter[0] += 1
        stack.append(v); on.add(v)
        for w in edges.get(v, ()):
            if w not in index:
                strong(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop(); on.discard(w); comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                sccs.append(comp)
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
    for v in edges:
        if v not in index:
            strong(v)
    for comp in sccs:
        rank = {k: i for i, k in enumerate(sorted(comp, key=lambda k: (bykey[k]["score"], bykey[k]["number"])))}
        for k in comp:
            c = bykey[k]
            c["deps"] = [(t, [x for x in ks if not (x in rank and rank[x] > rank[k])]) for t, ks in c["deps"]]
            c["deps"] = [(t, ks) for t, ks in c["deps"] if ks]


def pull_prerequisites(block, keys, earlier_keys):
    """A word a reading card needs comes a little before that card: the best-scored in-block card of each
    unsatisfied dependency group is pulled to (reading card's score + PULL_GAP), transitively. Sentence
    cards instead score just after the last of their words (SENT_AFTER), as in v2."""
    bykey = {c["key"]: c for c in block}
    changed = True
    while changed:
        changed = False
        for c in block:
            if c["route"] not in READING:
                continue
            if c["route"] == "SENT":
                prereq = []
                for _t, ks in c["deps"]:
                    if any(k in earlier_keys for k in ks):
                        continue
                    inb = [bykey[k]["score"] for k in ks if k in keys]
                    if inb:
                        prereq.append(min(inb))
                if prereq:
                    target = max(prereq) + SENT_AFTER
                    if abs(c["score"] - target) > 1e-9:
                        c["score"] = target; changed = True
                continue
            for _t, ks in c["deps"]:
                if any(k in earlier_keys for k in ks):
                    continue
                inb = [bykey[k] for k in ks if k in keys]
                if not inb:
                    continue
                best = min(inb, key=lambda x: (x["score"], x["number"]))
                target = max(PULL_FLOOR, c["score"] + PULL_GAP)
                if best["score"] > target + 1e-9:
                    best["score"] = target; changed = True
    # sequences stay monotone after the pulls (a pulled Monday must not jump ahead of … nothing; a pulled
    # trečiadienis must not pass antradienis)
    changed = True
    while changed:
        changed = False
        for c in block:
            if c.get("prev") and c["prev"] in bykey and bykey[c["prev"]]["score"] > c["score"]:
                bykey[c["prev"]]["score"] = c["score"] - 1e-6; changed = True


def schedule(block, a1_rules, earlier_keys):
    keys = {c["key"] for c in block}
    break_cycles(block, keys)
    pull_prerequisites(block, keys, earlier_keys)
    pool = sorted(block, key=lambda c: (c["score"], c["number"]))
    n = len(pool)
    placed, out = set(), []
    pos = {}                                                   # key -> position in this block
    last_pos = {}                                              # plain headword -> latest position
    lane_last = {}                                             # lane -> latest position
    colours = [c for c in pool if c["category"] == "Color"]
    colours_done = not colours
    pinned = {k: a for k, a in PIN_AFTER.items() if k in keys and a in keys}
    by_plain = defaultdict(list)
    for c in pool:
        by_plain[plain(c["lt"])].append(c["key"])
    pairs_by_key = defaultdict(set)
    for a, b in PAIRS:
        for ka in by_plain.get(plain(a), []):
            for kb in by_plain.get(plain(b), []):
                pairs_by_key[ka].add(kb); pairs_by_key[kb].add(ka)
    lookalike = lookalike_pairs(pool, pairs_by_key)
    lane_total = Counter(c["lane"] for c in pool)
    lane_done = Counter()
    first_cloze = FIRST_CLOZE if a1_rules else A2_FIRST_CLOZE
    reading_share = sum(1 for c in pool if c["route"] in READING) / max(n, 1)
    reading_cap = min(READING_CAP_MAX, max(READING_CAP_MIN, math.ceil(10 * reading_share) + 1))
    lane_cap_override = LANE_CAP_OVERRIDE_A1 if a1_rules else {}

    def deps_ok(c):
        for _t, ks in c["deps"]:
            if not any(k in placed or (k in earlier_keys) for k in ks):
                if any(k in keys for k in ks):                 # satisfiable inside this block: wait
                    return False
        return True

    def eligible(c, i, strict=True):
        if c["key"] in pinned and pinned[c["key"]] not in placed:
            return False
        if c.get("prev") and c["prev"] not in placed:
            return False
        if not strict:
            return True
        w = plain(c["lt"])
        if w in last_pos and i - last_pos[w] < SEPARATION:
            return False
        if a1_rules and c["lane"] in LANE_MIN_GAP_A1 and c["lane"] in lane_last \
                and i - lane_last[c["lane"]] < LANE_MIN_GAP_A1[c["lane"]]:
            return False
        if any(k in pos and i - pos[k] < LOOKALIKE_SEPARATION for k in lookalike.get(c["key"], ())):
            return False
        window = out[-WINDOW:]
        if sum(1 for x in window if x["lane"] == c["lane"]) >= lane_cap_override.get(c["lane"], LANE_CAP):
            return False
        if c["route"] in READING:
            if i < first_cloze:
                return False
            if sum(1 for x in window if x["route"] in READING) >= reading_cap:
                return False
            if not deps_ok(c):
                return False
        if a1_rules and c["route"] == "PHRASE" and i < FIRST_PHRASE:
            return False
        if c["category"] == "Color" and i < FIRST_COLOURS:
            return False
        return True

    def pressure(c, i):
        expected = lane_total[c["lane"]] * i / n
        d = expected - lane_done[c["lane"]]
        return -max(-LANE_PULL_MAX, min(LANE_PULL_MAX, LANE_PULL * d))

    def put(c):
        out.append(c); placed.add(c["key"]); pos[c["key"]] = len(out) - 1
        lane_done[c["lane"]] += 1
        last_pos[plain(c["lt"])] = lane_last[c["lane"]] = len(out) - 1

    def put_with_followers(c):
        put(c)
        partner = adjective_partner(c, pool)
        followers = [partner] if partner else []
        followers += [next(x for x in pool if x["key"] == k) for k in sorted(pairs_by_key.get(c["key"], ()))]
        followers += [next(x for x in pool if x["key"] == k) for k, after in pinned.items() if after == c["key"]]
        for f in followers:
            if f["key"] not in placed and not (f["key"] in pinned and pinned[f["key"]] not in placed):
                put_with_followers(f)

    while len(placed) < n:
        i = len(out)
        best, best_v = None, None
        for c in pool:
            if c["key"] in placed:
                continue
            if best_v is not None and c["score"] - LANE_PULL_MAX >= best_v:   # sorted by score: nothing further can win
                break
            v = c["score"] + pressure(c, i)
            if (best_v is None or v < best_v) and eligible(c, i):
                best, best_v = c, v
        if best is None:                                       # deadlock at the tail: relax everything but pins
            best = next((c for c in pool if c["key"] not in placed and eligible(c, i, strict=False)), None) \
                or next(c for c in pool if c["key"] not in placed)
        if best["category"] == "Color" and not colours_done:
            for c in sorted(colours, key=lambda c: c["number"]):
                if c["key"] not in placed:
                    put(c)
            colours_done = True
            continue
        put_with_followers(best)
    return out


# --- audit ---------------------------------------------------------------------
TELLING = [("duona", "bread"), ("alus", "beer"), ("vanduo", "water"), ("kava", "coffee"), ("pienas", "milk"), ("obuolys", "apple"),
           ("sriuba", "soup"), ("mėsa", "meat"), ("bulvė", "potato"), ("batai", "shoes"), ("kiaulė", "pig"), ("karvė", "cow"),
           ("šuo", "dog"), ("prezidentas", "president"), ("teismas", "court"), ("asmuo", "person (formal)"),
           ("branduolinis", "nuclear"), ("pragaras", "hell"), ("Labas", "hello"), ("Ačiū", "thank you"), ("Prašau", "please"),
           ("Atsiprašau", "sorry"), ("Kiek kainuoja?", "how much?"), ("Kur yra tualetas?", "where is the toilet?"),
           ("aš", "I"), ("taip", "yes"), ("vienas", "one"), ("šiandien", "today"), ("pirmadienis", "Monday"),
           ("galėti", "can"), ("kalbėti", "speak"), ("suprasti", "understand"), ("važiuoti", "go (by vehicle)"), ("tualetas", "toilet"),
           ("euras", "euro"), ("vaistinė", "pharmacy"), ("manyti", "think"), ("vėluoti", "be late"), ("plaštaka", "palm"),
           ("lydyti", "melt (sth)"), ("antis", "duck")]


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]: j += 1
            for k in range(i, j + 1): r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys); n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = math.sqrt(sum((a - mx) ** 2 for a in rx)); vy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return cov / (vx * vy) if vx and vy else float("nan")


def audit(cards, order, label, verbose=True):
    """Measure an order (key -> position) against the learning criteria. Returns a dict of numbers."""
    bykey = {c["key"] for c in cards}
    pos = {k: p for k, p in order.items() if k in bykey}
    cs = sorted((c for c in cards if c["key"] in pos), key=lambda c: pos[c["key"]])
    blocks = {"A1": [c for c in cs if c["level"] == "A1"], "A2": [c for c in cs if c["level"] == "A2"]}
    res = {"label": label, "n": len(cs)}
    P = print if verbose else (lambda *a, **k: None)
    P(f"\n==== {label}: {len(cs)} positioned cards "
      f"({len(blocks['A1'])} A1, {len(blocks['A2'])} A2; {sum(1 for c in cs if c['route'] == 'SENT')} sentences) ====")
    # coverage
    missing = [c["key"] for c in cards if c["key"] not in order]
    extra = sorted(set(order) - bykey)
    ps = sorted(order.values())
    gaps = ps != list(range(1, len(ps) + 1))
    P(f"coverage: {len(missing)} keys without a position {missing[:8]}; {len(extra)} positions for unknown keys {extra[:8]}; "
      f"{'gaps/duplicates in 1..N' if gaps else 'positions 1..N, no gaps, no duplicates'}")
    res.update(missing=len(missing), extra=len(extra), gaps=gaps)
    # block order: every A1 before every A2
    mixed = sum(1 for c in blocks["A1"] if blocks["A2"] and pos[c["key"]] > min(pos[x["key"]] for x in blocks["A2"]))
    P(f"blocks: {mixed} A1 cards positioned after the first A2 card")
    res["a1_after_a2"] = mixed
    # dependencies
    viol, deps, cross, by_lag = [], 0, [], Counter()
    outside = Counter()
    for c in cs:
        if c["route"] not in READING:
            continue
        for t, ks in c["deps"]:
            ks = [k for k in ks if k in pos]
            if not ks:
                continue
            deps += 1
            best = min(pos[k] for k in ks)
            if best > pos[c["key"]]:
                lag = best - pos[c["key"]]
                viol.append((c, t, min(ks, key=lambda k: pos[k]), lag))
                if c["level"] == "A1" and all(next(x for x in cards if x["key"] == k)["level"] == "A2" for k in ks):
                    cross.append((c, t, ks))
        for t in c["outside"]:
            outside[t] += 1
    for N in (0, 20, 50):
        by_lag[N] = sum(1 for v in viol if v[3] > N)
    P(f"dependencies: {deps} word uses in reading cards point at a deck card; {len(viol)} point FORWARD "
      f"(> 20 later: {by_lag[20]}, > 50 later: {by_lag[50]}); {len(cross)} of them are A1 cards needing a word taught only in A2; "
      f"{sum(outside.values())} uses of words no card teaches ({len(outside)} distinct)")
    res.update(deps=deps, viol=len(viol), viol20=by_lag[20], viol50=by_lag[50], cross=len(cross), outside=sum(outside.values()))
    if verbose and viol:
        P("  forward dependencies (card @pos: word <- teaching card @pos):")
        for c, t, k, lag in sorted(viol, key=lambda v: -v[3])[:60]:
            kc = next(x for x in cards if x["key"] == k)
            P(f"    {c['key']:8} @{pos[c['key']]:5} {c['level']} {c['lt'][:34]:34} {t:16} <- {k:8} {kc['lt'][:22]:22} {kc['level']} @{pos[k]}")
    # pins and pairs
    bad_pins = [(k, a, pos[k] - pos[a]) for k, a in PIN_AFTER.items() if k in pos and a in pos and pos[k] - pos[a] != 1]
    bad_adj = []
    deckn = {c["number"]: c for c in cards if c["source"] == "deck"}
    for nnum, c in deckn.items():
        if 446 <= nnum <= 507 and nnum % 2 == 0 and nnum + 1 in deckn:
            p = deckn[nnum + 1]
            if c["key"] in pos and p["key"] in pos and abs(pos[c["key"]] - pos[p["key"]]) != 1:
                bad_adj.append((c["lt"], p["lt"], abs(pos[c["key"]] - pos[p["key"]]), c["level"], p["level"]))
    by_plain = defaultdict(list)
    for c in cs:
        by_plain[plain(c["lt"])].append(c)
    bad_pairs, split_pairs = [], []
    for a, b in PAIRS:
        for ca in by_plain.get(plain(a), []):
            for cb in by_plain.get(plain(b), []):
                d = abs(pos[ca["key"]] - pos[cb["key"]])
                if ca["level"] != cb["level"]:
                    split_pairs.append((a, b, ca["level"], cb["level"]))
                elif d != 1:
                    bad_pairs.append((a, b, d))
    P(f"pairs: {len(bad_pins)} PIN_AFTER not adjacent {bad_pins}; {len(bad_adj)} FF adjective pairs not adjacent {bad_adj}; "
      f"{len(bad_pairs)} noted pairs not adjacent {bad_pairs}; {len(split_pairs)} pairs split across subdecks {split_pairs}")
    res.update(bad_pins=len(bad_pins), bad_adj=len(bad_adj), bad_pairs=len(bad_pairs), split_pairs=len(split_pairs))
    # confusables
    same = []
    for w, lst in by_plain.items():
        lst = sorted((c for c in lst if c["route"] != "SENT"), key=lambda c: pos[c["key"]])
        for x, y in zip(lst, lst[1:]):
            if pos[y["key"]] - pos[x["key"]] < SEPARATION:
                same.append((w, pos[x["key"]], pos[y["key"]]))
    la = lookalike_pairs(cs, defaultdict(set, {k: set() for k in pos}))
    pairs_plain = {(plain(a), plain(b)) for a, b in PAIRS} | {(plain(b), plain(a)) for a, b in PAIRS}
    close = sorted({(min(k, k2), max(k, k2)) for k, ks in la.items() for k2 in ks
                    if abs(pos[k] - pos[k2]) < LOOKALIKE_SEPARATION})
    close = [(k, k2) for k, k2 in close
             if (plain(next(c for c in cs if c["key"] == k)["lt"]), plain(next(c for c in cs if c["key"] == k2)["lt"])) not in pairs_plain]
    P(f"confusables: {len(same)} same-headword pairs closer than {SEPARATION} {same[:6]}; "
      f"{len(close)} look-alike pairs closer than {LOOKALIKE_SEPARATION}: "
      + ", ".join(f"{next(c for c in cs if c['key'] == k)['lt']}/{next(c for c in cs if c['key'] == k2)['lt']} ({abs(pos[k] - pos[k2])})" for k, k2 in close[:12]))
    res.update(same=len(same), lookalike=len(close))
    # pacing
    for lvl, blk in blocks.items():
        if not blk:
            continue
        def longest(f):
            best, cur, prev = (0, None), 0, None
            for c in blk:
                v = f(c); cur = cur + 1 if v == prev else 1; prev = v
                if cur > best[0]: best = (cur, v)
            return best
        lane_run, route_run = longest(lambda c: c["lane"]), longest(lambda c: c["route"] in READING)
        worst = max((Counter(c["lane"] for c in blk[i:i + 20]).most_common(1)[0] for i in range(0, max(1, len(blk) - 19))), key=lambda t: t[1])
        first_read = next((i + 1 for i, c in enumerate(blk) if c["route"] in READING), None)
        first_phr = next((i + 1 for i, c in enumerate(blk) if c["route"] == "PHRASE"), None)
        wk = Counter(c["lane"] for c in blk[:140]).most_common(6)
        rwk = Counter(c["route"] for c in blk[:140]).most_common()
        P(f"pacing {lvl}: longest same-lane run {lane_run}, longest run of {'reading' if route_run[1] else 'picture'} cards {route_run[0]}, "
          f"densest 20-window {worst}; first reading card at {first_read}, first phrase at {first_phr}; "
          f"first 140 lanes {wk}, routes {rwk}")
        res[f"{lvl}_lane_run"] = lane_run[0]; res[f"{lvl}_read_run"] = route_run[0] if route_run[1] else 0
        res[f"{lvl}_dense20"] = worst[1]; res[f"{lvl}_first_read"] = first_read; res[f"{lvl}_first_phrase"] = first_phr
        greet = [(c["lt"], i + 1) for i, c in enumerate(blk) if c["category"] == "Greetings"][:8]
        if greet:
            P(f"  greetings {lvl}: {greet}")
    # frequency agreement (words only)
    words = [c for c in cs if c["route"] != "SENT"]
    sp_sub = spearman([pos[c["key"]] for c in words], [c["sub"] for c in words])
    wp = [c for c in words if c["press"]]
    sp_press = spearman([pos[c["key"]] for c in wp], [c["press"] for c in wp])
    P(f"frequency: Spearman with subtitle rank {sp_sub:.3f} (n={len(words)}), with press rank {sp_press:.3f} (n={len(wp)}); "
      f"median subtitle rank of the first 100 A1 cards {sorted(c['sub'] for c in blocks['A1'][:100])[50] if blocks['A1'] else '-'}, "
      f"of A1 cards 101-400 {sorted(c['sub'] for c in blocks['A1'][100:400])[150] if len(blocks['A1']) > 400 else '-'}")
    res.update(sp_sub=round(sp_sub, 3), sp_press=round(sp_press, 3))
    return res


def telling(cards, orders):
    """Positions of the TELLING words in several orders ({label: {key: pos}})."""
    by_plain = defaultdict(list)
    for c in cards:
        by_plain[plain(c["lt"])].append(c)
    labels = list(orders)
    print("\n== Telling positions (whole order) ==")
    print(f"{'word':20}{'gloss':22}" + "".join(f"{l:>10}" for l in labels) + "  level")
    for w, g in TELLING:
        cs = [c for c in by_plain.get(plain(w), []) if c["route"] != "SENT"]
        if not cs:
            continue
        c = min(cs, key=lambda c: orders[labels[-1]].get(c["key"], 10 ** 6))
        print(f"{w:20}{g:22}" + "".join(f"{str(o.get(c['key'], '-')):>10}" for o in orders.values()) + f"  {c['level']}")


def first_n(cards, order, lvl, n=60):
    cs = sorted((c for c in cards if c["level"] == lvl and c["key"] in order), key=lambda c: order[c["key"]])[:n]
    return ", ".join(plain(c["lt"]) if c["route"] != "PHRASE" else c["lt"] for c in cs)


# --- outputs -------------------------------------------------------------------
def write_order(out, path):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order", "key", "block", "lithuanian", "category", "lane", "route", "tier", "sub_rank", "press_rank", "score", "old_order"])
        for i, c in enumerate(out, 1):
            c["order"] = i
            w.writerow([i, c["key"], c["block"], c["lt"], c["category"], c["lane"], c["route"], c["tier"], c["sub"],
                        c["press"] or "", f"{c['score']:.3f}", c["old"]])


def write_recording_order(out, path):
    """The recorder's order: A1 first, then A2, each in study order; cloze cards list their sentence too."""
    with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rec_order", "study_order", "key", "level", "route", "lithuanian", "sentence_to_record"])
        i = 0
        for lvl in ("A1", "A2"):
            for c in out:
                if c["level"] != lvl:
                    continue
                i += 1
                sent = re.sub(r"[{}]", "", c["ex"]) if c["route"] in READING else ""
                w.writerow([i, c["order"], c["key"], lvl, c["route"], c["lt"], sent])


def apply_retier(retier):
    """Write the levels of RETIER into the three data files' `level` columns (nothing else changes)."""
    changed = Counter()
    for path, keycol in (("cards_anki.csv", "key"), (A2_LIST, "id")):
        rows = rd(path); fields = list(rows[0].keys())
        for r in rows:
            if r[keycol] in retier and r["level"] != retier[r[keycol]]:
                r["level"] = retier[r[keycol]]; changed[path] += 1
        with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    # master_wordlist.csv is keyed by the A1 number
    num_to_level = {int(k[:3]): v for k, v in retier.items() if re.match(r"^\d{3}_", k)}
    rows = rd("master_wordlist.csv"); fields = list(rows[0].keys())
    for r in rows:
        n = int(r["#"]) if r["#"].isdigit() else None
        if n in num_to_level and r["level"] != num_to_level[n]:
            r["level"] = num_to_level[n]; changed["master_wordlist.csv"] += 1
    with open(os.path.join(ROOT, "master_wordlist.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    sent_keys = {k: v for k, v in retier.items() if k.startswith("S-")}
    if sent_keys and os.path.exists(os.path.join(ROOT, SENTENCES)):
        rows = rd(SENTENCES); fields = list(rows[0].keys())
        for r in rows:
            if r["id"] in sent_keys and r["level"] != sent_keys[r["id"]]:
                r["level"] = sent_keys[r["id"]]; changed[SENTENCES] += 1
        with open(os.path.join(ROOT, SENTENCES), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print("retier applied:", dict(changed) or "nothing to change")


def main():
    if "--rebuild-subs" in sys.argv:
        rebuild_subs(sys.argv[sys.argv.index("--rebuild-subs") + 1]); return
    retier = load_retier()
    if "--apply-retier" in sys.argv:
        apply_retier(retier); return
    old_path = os.environ.get("OLD_ORDER", "study_order.csv")      # the order this run replaces (for the comparison)
    old_rows = rd(old_path) if os.path.exists(os.path.join(ROOT, old_path)) else []
    old = {r["key"]: int(r["order"]) for r in old_rows}
    # the previous order is audited with the subdeck split it was built for (its block column), not today's levels
    old_levels = {r["key"]: r["block"][:2] for r in old_rows if r.get("block", "")[:2] in ("A1", "A2")}
    sub, press, vu = load_sources()
    if "--audit" in sys.argv:
        i = sys.argv.index("--audit")
        path = sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--") else old_path
        order = {r["key"]: int(r["order"]) for r in rd(path)}
        # audit the file against the levels it was built with: the data files' levels, not the retier
        cards = load_cards(old, {})
        score_cards(cards, sub, press, vu); build_dependencies(cards)
        audit(cards, order, path)
        telling(cards, {path: order})
        return
    cards = load_cards(old, retier)
    score_cards(cards, sub, press, vu)
    build_dependencies(cards)
    out, earlier = [], set()
    for lvl, a1_rules in (("A1", True), ("A2", False)):
        blk = schedule([c for c in cards if c["level"] == lvl], a1_rules, earlier)
        for c in blk:
            c["block"] = f"{lvl} subdeck"
        out += blk
        earlier |= {c["key"] for c in blk}
    write_order(out, OUT)
    write_recording_order(out, RECORDING_OUT)
    n1 = sum(1 for c in out if c["level"] == "A1"); n2 = len(out) - n1
    print(f"{OUT}: {len(out)} rows ({n1} A1 subdeck, {n2} A2 subdeck; {sum(1 for c in out if c['route'] == 'SENT')} of them sentence cards); "
          f"{RECORDING_OUT}: recording order")
    if "--report" in sys.argv:
        new = {c["key"]: c["order"] for c in out}
        if old:
            old_cards = load_cards({}, old_levels)
            score_cards(old_cards, sub, press, vu); build_dependencies(old_cards)
            audit(old_cards, old, f"previous {old_path}")
        build_dependencies(cards)            # fresh: the scheduler waived the cyclic ones, the audit must not
        audit(cards, new, f"new {OUT}")
        telling(cards, {"old": old, "v3": new} if old else {"v3": new})
        for lvl in ("A1", "A2"):
            print(f"\n== First 60 of the {lvl} subdeck (v3) ==\n{first_n(cards, new, lvl)}")
        if retier:
            print(f"\nre-tiered: {len(retier)} cards ({Counter(retier.values())})")


if __name__ == "__main__":
    main()
