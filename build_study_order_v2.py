#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_study_order_v2.py — the learning order of the deck, written to study_order.csv.

    python3 build_study_order_v2.py                 # regenerates study_order.csv
    python3 build_study_order_v2.py --report        # also prints the audit tables
    python3 build_study_order_v2.py --rebuild-subs <lt_full.txt>
                                                    # re-derives the subtitle lemma list

Adopted 2026-10-17 (owner: "adopt the order, yes; deck coherence is more important than
whatever studying someone has done with it"). build_apkg.py reads study_order.csv and
gives every note its `order` as the new-card position (Anki's `due`), so a fresh import
studies the deck in this sequence. Keys and GUIDs never change; only the position does.
The previous generator is deprecated/build_study_order_v1.py; the previous order is in
git (study_order.csv before this date). Re-running overwrites study_order.csv, so put
lasting rules in the lists below, not in the CSV.

WHY A V2
  v1 ordered A1 well (utility lists per category, unit mixing) but stacked the rest
  phase by phase: all of P-A, then P-B, ... so "Labas" (P-D) was card ~1007, the
  core verbs kalbėti/žinoti (P-F) ~1210, mėsa (P-H) ~1536, and the A2 subdeck
  opened with the Fluent Forever "Society" leftovers (pragaras, žmogžudystė,
  branduolinis) because the 93 A2-tagged deck cards came before the A2 list.
  Neither frequency corpus can fix this on its own: press (PERLSI/Dadurkevičius
  2020) ranks teismas 76 and duona 1992; film subtitles rank prezidentas 567 and
  duona 2044. Bread never beats president by counting, so a judged utility tier
  sits on top of the counts.

THE SCORE  (lower = earlier)
  score = 0.6*ln(subtitle rank) + 0.4*ln(press rank) + tier offset − 0.3 if in the
          VU A1/A2 lexicon
  * subtitle rank: OpenSubtitles 2018 Lithuanian word list (hermitdave/FrequencyWords,
    CC-BY-SA 4.0), lemmatised with simplemma and summed per lemma, stored in
    a2_build/study_order/opensubtitles_lt_lemmas.csv. Spoken register, so it is
    weighted above press. Missing lemma = rank 30000.
  * press rank: sources/lt_3000_frequency.csv (PERLSI 3000, from Dadurkevičius 2020,
    Joint Corpus of Lithuanian). A word missing there is only "not in the top
    3000", and the list has little food or household vocabulary, so a missing
    press rank is not a penalty: the subtitle rank then carries the whole weight.
  * phrases: the rank of the rarest word ("Kur yra tualetas?" ranks as tualetas).
  * tier: T0 survival. For the deck's own cards this is a hand-ORDERED list
    (SURVIVAL: žmogus, vyras, moteris, vaikas, vanduo, duona, kava ... eat, drink,
    go, big/small, good/bad, yes/no, the pronouns) placed first in that order;
    counting cannot put bread before president, so the first ~40 words are judged
    outright. The greetings and getting-by phrases are likewise a hand-ordered list
    (SURVIVAL_PHRASES), fed in from position FIRST_PHRASE on. For the A2 list T0
    (−3.0) covers greetings, politeness, yes/no, question words, 0–10,
    today/tomorrow/yesterday/now, the modal verbs, money, price, the "getting by"
    phrases. T1 daily (−1.5): food & drink, home, body, clothing, people, places,
    transport, time, numbers, health, shopping, the v1 CORE lists. T2 (0): the
    rest. T3 demoted (+1.5): v1 DEMOTE (asmuo, teismas, prezidentas, auka ...) and
    the abstract Society leftovers; +1.0 for "Extended patterns" (conditionals,
    reported speech); +0.8 for phase P-K (the project's own "deferred, low
    frequency" shelf). Tier lists are judged; edit them freely, they are the point.

THE SCHEDULE  (per subdeck: the A1 subdeck first, then the A2 subdeck)
  Which subdeck a card belongs to is the `level` column of cards_anki.csv and of the
  A2 list (a2_build/study_order/retag_A1.csv records the 62 survival items moved to
  A1 on 2026-10-17). Cards are placed greedily by score, best eligible first, under
  these rules:
  1. Mixing: at most LANE_CAP (3) cards of the same lane (people, food, verbs,
     function words, phrases ...) in any trailing WINDOW (10). Frequency drives,
     mixing only throttles — unlike v1's fixed quota per unit, which forced one
     animal per 36 cards whether or not the animal was useful.
  2. Pictures first: in the A1 subdeck no cloze/pair card before position
     FIRST_CLOZE (100) — Fluent Forever's "sentences once ~100 words are in" —
     and never more than CLOZE_CAP (4) reading cards per trailing 10 afterwards.
     Phrase pictures wait until position FIRST_PHRASE (40) and are capped at 2
     per 10 (LANE_CAP_OVERRIDE) so chunks trickle in among the words.
  3. Sequences keep their order: 0,1,2 ... 10, 11 ...; Monday ... Sunday; January
     ... December; a later member never jumps an earlier one.
  4. Adjective antonym pairs (FF 446–507) stay adjacent; the A1 colours are one
     run, not before position 40.
  5. Confusables: a second card with the same Lithuanian headword waits at least
     SEPARATION (60) positions.
  6. Pinned neighbours: 531_batonas directly after 182_duona.
  7. Sentence cards go right after the last of their words (as v1), but not before
     the cloze gate (rule 2).
  Rows in a2_build/deferred_B1.csv are no longer in the A2 list, so they get no
  position; build_apkg.py does not emit them either.

Output columns: order, key, block, lithuanian, category, lane, tier, sub_rank,
press_rank (blank when outside the press top 3000), score, old_order (the key's
position in the study_order.csv this run replaces, for the comparison).
"""
import csv, math, os, re, sys, unicodedata
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
A2_LIST = os.environ.get("A2_LIST", "a2_build/a2_wordlist.csv")
SENTENCES = os.environ.get("SENTENCES", "a2_build/sentences/sentences.csv")
SUBS_LEMMAS = "a2_build/study_order/opensubtitles_lt_lemmas.csv"
OUT = os.environ.get("STUDY_ORDER_OUT", "study_order.csv")

W_SUB, W_PRESS = 0.6, 0.4
MISSING_SUB, MISSING_PRESS = 30000, None      # None: no press rank -> subtitle rank alone
VU_BONUS = 0.3
TIER_OFFSET = {0: -3.0, 1: -1.5, 2: 0.0, 3: 1.5}
EXTENDED_PENALTY, PK_PENALTY = 1.0, 0.8
LANE_CAP, WINDOW = 3, 10
LANE_CAP_OVERRIDE = {"phrases": 2}
FIRST_CLOZE, CLOZE_CAP, FIRST_PHRASE, FIRST_COLOURS = 100, 4, 40, 40
SEPARATION = 60
PIN_AFTER = {"531_batonas": "182_duona"}


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
except ImportError:                      # the stored lemma list still works; only
    def lemma(w):                        # headword-form lookups lose the fallback
        return w


def rebuild_subs(src):
    """Sum the OpenSubtitles word-form counts per simplemma lemma; keep the top 40k."""
    from collections import Counter
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
    """Rank of a token: the headword itself if the table has it; otherwise its lemma or
    the lemma of one of the card's own inflected forms, at twice the rank (a derived
    form — labiau from labai, galima from galėti — is rarer than its lemma)."""
    cands = {lemma(tok)} | {lemma(base(f)) for f in forms if f}
    found = [2 * table[c] for c in cands if c in table]
    if tok in table:                      # a direct entry can be a residue the lemmatiser
        found.append(table[tok])          # left behind (mano -> aš), so it does not win outright
    return min(found) if found else missing


def freq(card, sub, press):
    toks = tokens(card["lt"])
    content = [t for t in toks if len(t) > 1] or toks or [plain(card["lt"])]
    forms = card.get("forms", []) if len(content) == 1 else []
    s = [rank_of(sub, t, forms, MISSING_SUB) for t in content]
    p = [rank_of(press, t, forms, None) for t in content]
    # a phrase is as hard as its rarest word: "Kur yra tualetas?" ranks as tualetas
    return max(s), (max(p) if all(p) else None)


# --- lanes (coarse groups for the mixing rule) --------------------------------
LANE = {
    # deck categories
    "People": "people", "Job": "work", "Food": "food", "Beverages": "food", "Home": "home",
    "Electronics": "electronics", "Verbs": "verbs", "Adjectives": "adjectives", "Color": "colours",
    "Location": "places", "Transportation": "transport", "Body": "body", "Nature": "nature",
    "Animal": "animals", "Clothing": "clothing", "Materials": "rest", "Math": "rest", "Misc": "rest",
    "Art": "rest", "Society": "society", "Pronouns": "function",
    # A2 list categories
    "Nouns": "nouns", "Adverbs": "adverbs", "Time": "time", "Numbers": "numbers", "Abstract": "abstract",
    "Work & culture": "work", "Work & school": "work", "Jobs": "work", "Prepositions": "function",
    "Conjunctions": "function", "Question words": "function", "Modal & core verbs": "verbs",
    "Getting by": "phrases", "Formulas": "phrases", "Phrases": "phrases", "Basics": "phrases",
    "Core patterns": "phrases", "Extended patterns": "phrases", "Opinion & discourse": "phrases",
    "Transactions": "phrases", "Greetings": "phrases", "Politeness": "phrases", "Feelings": "feelings",
    "Travel": "transport", "Health": "body", "Technology": "electronics", "Shopping": "shopping",
    "Money & admin": "society", "Nationalities": "rest", "Languages": "rest",
}
TYPE_LANE = {"N": "nouns", "V": "verbs", "A": "adjectives", "ADV": "adverbs", "P": "function",
             "PREP": "function", "CONJ": "function", "Q": "function", "NUM": "numbers",
             "PHRASE": "phrases", "SENTENCE": "phrases"}

# --- tiers (judged) ------------------------------------------------------------
# A1 deck keys. CORE and DEMOTE are v1's owner-reviewed lists, carried over.
SURVIVAL = ["103_zmogus", "086_vyras", "087_moteris", "177_vanduo", "182_duona", "376_valgyti", "377_gerti",
            "101_vaikas", "172_kava", "173_arbata", "366_eiti", "452_didelis", "453_mazas", "025_namas", "178_pienas",
            "175_alus", "104_draugas", "090_seima", "045_parduotuve", "363_dirbti", "024_miestas", "188_obuolys",
            "183_sriuba", "064_batai", "016_autobusas", "001_suo", "002_kate",
            # retagged A1 on 2026-10-17 (a2_build/study_order/retag_A1.csv); they follow the first words
            "354_taip", "355_ne", "510_as", "511_tu", "512_jis", "513_ji", "515_mes", "516_jus", "517_jie", "514_tai",
            "464_geras", "465_blogas", "133_pinigai", "160_kaina"]
SURVIVAL_INDEX = {k: i for i, k in enumerate(SURVIVAL)}
# The same for the phrase cards, by headword: a greeting made of one rare-ish word
# ("Labas", subtitle rank 85) must not lose to a chunk of frequent function words
# ("Ar yra…?"). Placed in this order from FIRST_PHRASE on, two per ten cards.
SURVIVAL_PHRASES = ["Labas", "Ačiū", "Prašau", "Laba diena", "Atsiprašau", "Viso gero", "Iki", "Nesuprantu", "Kiek kainuoja?",
                    "Kur yra…?", "Labas rytas", "Labas vakaras", "Sveiki", "Labai ačiū", "Nėra už ką", "Kur yra tualetas?",
                    "Sąskaitą, prašau", "Norėčiau…", "Ar kalbate angliškai?", "Kaip sekasi?", "Man gerai", "Nežinau",
                    "Mano vardas…", "Aš esu iš…", "Labanakt", "Iki pasimatymo", "Atleiskite", "Malonu susipažinti",
                    "Skanaus", "Į sveikatą!", "Ar galite man padėti?", "Ar galite pakartoti?", "Kalbėkite lėčiau, prašau"]
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
          # the Society/Math/Misc leftovers that opened the A2 subdeck in v1
          "128_religija", "129_dangus", "130_pragaras", "131_mirtis", "134_doleris", "135_banknotas", "136_santuoka", "139_santykiai", "140_rase", "141_seksas", "142_lytis", "143_zmogzudyste", "144_kalejimas", "145_technologija", "146_energija", "147_karas", "148_taika", "149_puolimas", "150_rinkimai", "153_nuodai", "154_ginklas", "156_lenktynes", "161_sutartis", "162_narkotikas", "164_mokslas", "165_dievas", "171_menas", "227_raide", "250_tinklas", "320_karstis", "337_colis", "338_peda", "339_svaras", "341_apskritimas", "342_kvadratas", "346_krastas", "347_kampas", "350_priebalsis", "351_balsis", "362_rastas", "414_melstis", "528_serti", "529_lesinti"}

# A2 list: matched on the plain headword (ids may shift while the list is being merged).
T0_CATEGORIES = {"Greetings", "Politeness", "Question words", "Basics", "Getting by"}
T0_WORDS = {"nulis", "vienas", "du", "trys", "keturi", "penki", "šeši", "septyni", "aštuoni", "devyni", "dešimt",
            "dvidešimt", "šimtas", "tūkstantis",
            "šiandien", "vakar", "rytoj", "dabar", "valanda", "diena", "būti", "turėti", "galėti", "norėti", "reikėti",
            "mano", "tavo", "jo", "jos", "mūsų", "jūsų", "savo", "šis", "tas", "į", "iš", "su", "ir", "bet", "ar",
            "labai", "čia", "ten", "gerai", "dėkui", "kainuoti", "euras", "kalbėti", "suprasti", "žinoti", "gyventi",
            "mėgti", "patikti", "duoti", "padėti", "važiuoti", "gelbėkit", "sąskaita", "vaistinė"}
T1_CATEGORIES = {"Food", "Beverages", "Home", "Body", "Clothing", "People", "Location", "Transportation", "Travel",
                 "Time", "Numbers", "Health", "Shopping", "Transactions", "Money & admin", "Formulas", "Core patterns",
                 "Modal & core verbs", "Prepositions", "Conjunctions", "Pronouns"}
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


# --- sequences that must keep their order ----------------------------------------
SEQUENCES = [            # nulis is left out: zero is rare and must not hold back one to ten;
    # the teens, the tens and 100/1000 are separate runs so that twenty need not wait for nineteen
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
def load_cards(old):
    cards = []
    for r in rd("cards_anki.csv"):
        cards.append({"key": r["key"], "lt": r["lithuanian"], "category": r["category"], "number": int(r["number"]),
                      "level": (r.get("level") or "A1"), "route": "IMG", "source": "deck", "phase": "",
                      "forms": [r.get(f, "") for f in ("gen_sg", "pres3", "past3", "fem")]})
    if os.path.exists(os.path.join(ROOT, A2_LIST)):
        for r in rd(A2_LIST):
            cards.append({"key": r["id"], "lt": r["lithuanian_TARGET"], "category": r["category"],
                          "number": 10000 + int(re.sub(r"\D", "", r["id"]) or 0), "level": (r.get("level") or "A2").strip() or "A2",
                          "route": r.get("route", ""), "source": "list", "phase": r.get("phase", ""), "type": r.get("type", ""),
                          "forms": [r.get(f, "") for f in ("gen_sg", "pres3", "past3", "fem")]})
    for c in cards:
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
        if c["key"] in SURVIVAL_INDEX:                  # judged head of the deck, in list order
            c["score"] = -20 + 0.1 * SURVIVAL_INDEX[c["key"]]
        elif c["source"] == "list" and plain(c["lt"]) in SURVIVAL_PHRASE_INDEX and c["route"] == "PHRASE":
            c["score"] = -15 + 0.1 * SURVIVAL_PHRASE_INDEX[plain(c["lt"])]
    # sequences: a later member never scores better than an earlier one
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


# --- the scheduler -------------------------------------------------------------
def adjective_partner(card, pool):
    n = card["number"]
    if card["source"] != "deck" or not 446 <= n <= 507:
        return None
    pn = n + 1 if n % 2 == 0 else n - 1
    return next((c for c in pool if c["source"] == "deck" and c["number"] == pn), None)


def schedule(block, a1_rules):
    pool = sorted(block, key=lambda c: (c["score"], c["number"]))
    placed, out = set(), []
    first_pos = {}                                  # plain headword -> first position
    colours = [c for c in pool if c["category"] == "Color"]
    colours_done = not colours
    pinned = {k: a for k, a in PIN_AFTER.items() if any(c["key"] == k for c in pool)}

    def eligible(c, i):
        if c["key"] in pinned and pinned[c["key"]] not in placed:
            return False
        if c.get("prev") and c["prev"] not in placed:
            return False
        w = plain(c["lt"])
        if w in first_pos and i - first_pos[w] < SEPARATION:
            return False
        window = out[-WINDOW:]
        if sum(1 for x in window if x["lane"] == c["lane"]) >= LANE_CAP_OVERRIDE.get(c["lane"], LANE_CAP):
            return False
        if c["route"] in ("CLOZE", "PAIR"):
            if a1_rules and i < FIRST_CLOZE:
                return False
            if sum(1 for x in window if x["route"] in ("CLOZE", "PAIR")) >= CLOZE_CAP:
                return False
        if a1_rules and c["route"] == "PHRASE" and i < FIRST_PHRASE:
            return False
        if c["category"] == "Color" and (i < FIRST_COLOURS):
            return False
        return True

    def put(c):
        out.append(c); placed.add(c["key"])
        first_pos.setdefault(plain(c["lt"]), len(out) - 1)

    while len(placed) < len(pool):
        pick = next((c for c in pool if c["key"] not in placed and eligible(c, len(out))), None)
        if pick is None:                            # constraints deadlock at the tail: relax
            pick = next(c for c in pool if c["key"] not in placed)
        if pick["category"] == "Color" and not colours_done:
            for c in sorted(colours, key=lambda c: c["number"]):
                if c["key"] not in placed:
                    put(c)
            colours_done = True
            continue
        put(pick)
        partner = adjective_partner(pick, pool)
        if partner and partner["key"] not in placed:
            put(partner)
        for k, after in pinned.items():
            if after == pick["key"] and k not in placed:
                put(next(c for c in pool if c["key"] == k))
    return out


def insert_sentences(out):
    p = os.path.join(ROOT, SENTENCES)
    if not os.path.exists(p):
        return out
    pos = {c["key"]: i for i, c in enumerate(out)}
    inserts = []
    for r in rd(SENTENCES):
        words = [w for w in r["words_used"].split() if w in pos]
        after = max((pos[w] for w in words), default=len(out) - 1)
        after = max(after, FIRST_CLOZE - 1)          # a sentence is a reading card: not before the cloze gate
        inserts.append((after, int(r["order"]), {"key": r["id"], "lt": r["lt"], "category": "Sakiniai", "block": "sentences",
                                                  "lane": "sentences", "tier": "", "sub": "", "press": "", "score": "", "old": ""}))
    out = list(out)
    for after, _o, item in sorted(inserts, key=lambda t: (t[0], t[1]), reverse=True):
        out.insert(after + 1, item)
    return out


# --- audit ---------------------------------------------------------------------
TELLING = [("duona", "bread"), ("alus", "beer"), ("vanduo", "water"), ("kava", "coffee"), ("pienas", "milk"), ("obuolys", "apple"),
           ("sriuba", "soup"), ("mėsa", "meat"), ("bulvė", "potato"), ("batai", "shoes"), ("kiaulė", "pig"), ("karvė", "cow"),
           ("pelė", "mouse"), ("šuo", "dog"), ("prezidentas", "president"), ("teismas", "court"), ("asmuo", "person (formal)"),
           ("branduolinis", "nuclear"), ("pragaras", "hell"), ("Labas", "hello"), ("Ačiū", "thank you"), ("Prašau", "please"),
           ("Kiek kainuoja?", "how much?"), ("aš", "I"), ("taip", "yes"), ("vienas", "one"), ("šiandien", "today"), ("pirmadienis", "Monday"),
           ("galėti", "can"), ("kalbėti", "speak"), ("suprasti", "understand"), ("važiuoti", "go (by vehicle)"), ("tualetas", "toilet"),
           ("euras", "euro"), ("vaistinė", "pharmacy"), ("višta", "hen"), ("antis", "duck")]


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


def report(rows, cards):
    by_lt = defaultdict(list)
    for r in rows:
        by_lt[plain(r["lt"])].append(r)
    print("\n== Telling words: position in the whole order (previous study_order.csv -> this run) ==")
    print(f"{'word':18}{'gloss':18}{'old':>6}{'new':>6}{'subs':>7}{'press':>7}  tier block")
    for w, g in TELLING:
        for r in by_lt.get(plain(w), [])[:1]:
            print(f"{w:18}{g:18}{str(r['old']):>6}{r['order']:>6}{str(r['sub']):>7}{str(r['press']):>7}  T{r['tier']}   {r['block']}")
    words = [r for r in rows if r["block"] != "sentences"]
    print("\n== Spearman rank correlation of the order with each source (words only) ==")
    for name, key in (("old order", "old"), ("v2 order", "order")):
        xs = [r for r in words if r[key] != ""]
        xp = [r for r in xs if r["press"]]
        print(f"{name:10} vs subtitle rank {spearman([int(r[key]) for r in xs], [r['sub'] for r in xs]):.3f} (n={len(xs)})"
              f" | vs press rank {spearman([int(r[key]) for r in xp], [r['press'] for r in xp]):.3f} (n={len(xp)}, words in the press top 3000)")
    xs = [r for r in words if r["old"] != ""]
    print(f"v2 order vs old order {spearman([int(r['order']) for r in xs], [int(r['old']) for r in xs]):.3f}")
    for blk in ("A1 subdeck", "A2 subdeck"):
        first = [r for r in rows if r["block"] == blk][:100]
        print(f"\n== First 100 of the {blk} ==")
        print(", ".join(f"{r['lt']}" + ("*" if r["route"] in ("CLOZE", "PAIR") else "") for r in first))
    print("\n(* = cloze/pair reading card)")


def main():
    if "--rebuild-subs" in sys.argv:
        rebuild_subs(sys.argv[sys.argv.index("--rebuild-subs") + 1]); return
    old = {r["key"]: int(r["order"]) for r in rd("study_order.csv")} if os.path.exists(os.path.join(ROOT, "study_order.csv")) else {}
    sub, press, vu = load_sources()
    cards = load_cards(old)
    score_cards(cards, sub, press, vu)
    out = []
    for lvl, a1_rules in (("A1", True), ("A2", False)):
        blk = schedule([c for c in cards if c["level"] == lvl], a1_rules)
        for c in blk:
            c["block"] = f"{lvl} subdeck"
        out += blk
    out = insert_sentences(out)
    rows = []
    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order", "key", "block", "lithuanian", "category", "lane", "tier", "sub_rank", "press_rank", "score", "old_order"])
        for i, c in enumerate(out, 1):
            c["order"] = i
            w.writerow([i, c["key"], c["block"], c["lt"], c["category"], c["lane"], c["tier"], c["sub"], c["press"] or "",
                        f"{c['score']:.3f}" if c["score"] != "" else "", c["old"]])
            rows.append(c)
    n1 = sum(1 for c in out if c["block"] == "A1 subdeck"); n2 = sum(1 for c in out if c["block"] == "A2 subdeck")
    print(f"{OUT}: {len(out)} rows ({n1} A1 subdeck, {n2} A2 subdeck, {len(out) - n1 - n2} sentences)")
    if "--report" in sys.argv:
        report(rows, cards)


if __name__ == "__main__":
    main()
