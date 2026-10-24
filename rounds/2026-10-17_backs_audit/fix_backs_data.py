# -*- coding: utf-8 -*-
"""Back-of-card data fixes (a2_build/backs_audit/data_errors.csv, high-severity rows plus the
owner's 2026-10-17 adjective rule). Data only: no template or back-design change.
Idempotent; writes a log of every changed field to backs_audit/data_fixes_applied.csv.

    python3 a2_build/src/fix_backs_data.py

Sources: every new form was checked against kirtis.info's analyser
(https://kirtis.info/api/krc/<form>; e.g. "vizos" -> dktv. mot.gim. vnsk. K.), 2026-10-17.

A2 (a2_wordlist.csv and deferred_B1.csv)
  - GEN_SG: the 118 feminine -a nouns whose rule engine wrote -as (vizas -> vizos), plus five
    other rule-derived genitives kirtis rejects: kulkšnis -> kulkšnies, rugsėjis -> rugsėjo,
    priežastis -> priežasties, pėstysis -> pėsčiojo, nepažįstamasis -> nepažįstamojo.
    The other 690 noun genitives were confirmed as they stand; 8 more are not in kirtis and
    stay unconfirmed (listed in the log as "unconfirmed").
  - GENDER: kulkšnis M -> F, priežastis M -> F, dėdė F -> M (masculine in -ė), metai '' -> M pl.
  - ADJECTIVES keep both gender forms (owner): every type-A row with a feminine gets gender
    "M/F"; feminines verified (123 as they stand, ordinals as kirtis numerals); veikiantis
    feminine veikiantė -> veikianti; added tokia pat, kitokia, tam tikra. Feminine-only or
    indeclinable rows stay without a pair (nėščia, ištekėjusi, netekėjusi, atidaryta,
    draudžiama, leidžiama, užsienio, vidutinio amžiaus, saulėta).
A1 (cards_anki.csv `pron`, master_wordlist.csv `lt_pron`)
  - stress for the 9 prons without a mark (kirtis): minià, taikà, kortẽlė, datà, lė̃tas,
    seklùs, jì, jū̃s, jiẽ.
  - the 10 colours carried a noun genitive (raudono) in gen_sg: now fem = raudona … and no
    gen_sg; ♂♀ stays (gender M/F). Job nouns with M/F are untouched.
Both decks: the i + U+0307 + accent sequences (tėvai̇̃, karei̇̃vis, praei̇̃ti, gami̇̀nti, i̇̀lgas,
i̇lgaĩ) normalised to precomposed ì/í/ĩ (or plain i) in every pron field.
"""
import csv, os, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
P = lambda *a: os.path.join(ROOT, *a)
LOG = []

GEN = {
    "A2-0033": ("rugsėjio", "rugsėjo"),
    "A2-0211": ("vizas", "vizos"),
    "A2-0228": ("sveikatas", "sveikatos"),
    "A2-0236": ("slaugytojas", "slaugytojos"),
    "A2-0245": ("algas", "algos"),
    "A2-0246": ("kolegas", "kolegos"),
    "A2-0250": ("pamokas", "pamokos"),
    "A2-0283": ("nuomas", "nuomos"),
    "A2-0298": ("nuostabas", "nuostabos"),
    "A2-0319": ("baterijas", "baterijos"),
    "A2-0327": ("audras", "audros"),
    "A2-0329": ("šalnas", "šalnos"),
    "A2-0332": ("balas", "balos"),
    "A2-0339": ("politikas", "politikos"),
    "A2-0340": ("ekonomikas", "ekonomikos"),
    "A2-0341": ("problemas", "problemos"),
    "A2-0343": ("priežasčio", "priežasties"),
    "A2-0581": ("tetas", "tetos"),
    "A2-0585": ("dukterėčias", "dukterėčios"),
    "A2-0590": ("nepažįstamasio", "nepažįstamojo"),
    "A2-0595": ("poras", "poros"),
    "A2-0605": ("kulkšnio", "kulkšnies"),
    "A2-0623": ("lentynas", "lentynos"),
    "A2-0625": ("spintas", "spintos"),
    "A2-0627": ("užuolaidas", "užuolaidos"),
    "A2-0643": ("šluotas", "šluotos"),
    "A2-0660": ("perėjas", "perėjos"),
    "A2-0666": ("ambasadas", "ambasados"),
    "A2-0675": ("dešras", "dešros"),
    "A2-0694": ("uogas", "uogos"),
    "A2-0703": ("slyvas", "slyvos"),
    "A2-0716": ("sagas", "sagos"),
    "A2-0732": ("avarijas", "avarijos"),
    "A2-0738": ("pievas", "pievos"),
    "A2-0746": ("šakas", "šakos"),
    "A2-0756": ("ožkas", "ožkos"),
    "A2-0757": ("vištas", "vištos"),
    "A2-0775": ("pelėdas", "pelėdos"),
    "A2-0776": ("profesijas", "profesijos"),
    "A2-0796": ("lentas", "lentos"),
    "A2-0805": ("klaidas", "klaidos"),
    "A2-0808": ("istorijas", "istorijos"),
    "A2-0813": ("parodas", "parodos"),
    "A2-0824": ("pradžias", "pradžios"),
    "A2-0825": ("pabaigas", "pabaigos"),
    "A2-0827": ("akimirkas", "akimirkos"),
    "A2-0834": ("idėjas", "idėjos"),
    "A2-0839": ("progas", "progos"),
    "A2-0843": ("tvarkas", "tvarkos"),
    "A2-0848": ("tiesas", "tiesos"),
    "A2-0857": ("pagalbas", "pagalbos"),
    "A2-0858": ("paslaugas", "paslaugos"),
    "A2-0859": ("informacijas", "informacijos"),
    "A2-0866": ("monetas", "monetos"),
    "A2-0869": ("paskolas", "paskolos"),
    "A2-0870": ("skolas", "skolos"),
    "A2-0875": ("anketas", "anketos"),
    "A2-0878": ("registracijas", "registracijos"),
    "A2-1215": ("alėjas", "alėjos"),
    "A2-1221": ("auditorijas", "auditorijos"),
    "A2-1232": ("biologijas", "biologijos"),
    "A2-1235": ("chemijas", "chemijos"),
    "A2-1254": ("ekskursijas", "ekskursijos"),
    "A2-1255": ("elektras", "elektros"),
    "A2-1272": ("injekcijas", "injekcijos"),
    "A2-1280": ("katedras", "katedros"),
    "A2-1288": ("kirpyklas", "kirpyklos"),
    "A2-1290": ("klaviatūras", "klaviatūros"),
    "A2-1301": ("lašišas", "lašišos"),
    "A2-1315": ("mėsas", "mėsos"),
    "A2-1317": ("operacijas", "operacijos"),
    "A2-1318": ("optikas", "optikos"),
    "A2-1325": ("paskaitas", "paskaitos"),
    "A2-1335": ("registratūras", "registratūros"),
    "A2-1344": ("sankryžas", "sankryžos"),
    "A2-1357": ("skulptūras", "skulptūros"),
    "A2-1358": ("sofas", "sofos"),
    "A2-1378": ("tvoras", "tvoros"),
    "A2-1379": ("uniformas", "uniformos"),
    "A2-1389": ("valgyklas", "valgyklos"),
    "A2-1395": ("vazas", "vazos"),
    "A2-1397": ("vilnas", "vilnos"),
    "A2-1487": ("akademijas", "akademijos"),
    "A2-1488": ("akcijas", "akcijos"),
    "A2-1489": ("alergijas", "alergijos"),
    "A2-1498": ("baudas", "baudos"),
    "A2-1505": ("deklaracijas", "deklaracijos"),
    "A2-1511": ("fizikas", "fizikos"),
    "A2-1513": ("garantijas", "garantijos"),
    "A2-1517": ("gimnazijas", "gimnazijos"),
    "A2-1519": ("gramatikas", "gramatikos"),
    "A2-1524": ("instrukcijas", "instrukcijos"),
    "A2-1527": ("kalbas", "kalbos"),
    "A2-1548": ("madas", "mados"),
    "A2-1549": ("matematikas", "matematikos"),
    "A2-1551": ("merginas", "merginos"),
    "A2-1560": ("netiesas", "netiesos"),
    "A2-1567": ("paras", "paros"),
    "A2-1568": ("partijas", "partijos"),
    "A2-1573": ("pensijas", "pensijos"),
    "A2-1575": ("pertraukas", "pertraukos"),
    "A2-1576": ("picas", "picos"),
    "A2-1578": ("poliklinikas", "poliklinikos"),
    "A2-1592": ("reklamas", "reklamos"),
    "A2-1598": ("slogas", "slogos"),
    "A2-1600": ("sumas", "sumos"),
    "A2-1604": ("tradicijas", "tradicijos"),
    "A2-1614": ("valiutas", "valiutos"),
    "A2-1727": ("bėdas", "bėdos"),
    "A2-1728": ("jėgas", "jėgos"),
    "A2-1748": ("pasakas", "pasakos"),
    "A2-1749": ("giras", "giros"),
    "A2-1752": ("pižamas", "pižamos"),
    "A2-1755": ("gėdas", "gėdos"),
    "A2-1756": ("nuotaikas", "nuotaikos"),
    "A2-1768": ("Lietuvas", "Lietuvos"),
    "A2-1784": ("kopas", "kopos"),
    "A2-1785": ("perkūnijas", "perkūnijos"),
    "A2-1799": ("ponias", "ponios"),
    "A2-1802": ("kultūras", "kultūros"),
    "A2-1804": ("televizijas", "televizijos"),
    "A2-1805": ("vėliavas", "vėliavos"),
    "A2-1807": ("pėstysio", "pėsčiojo")
}
GENDER = {"A2-0605": "F", "A2-0343": "F", "A2-0582": "M", "A2-0008": "M pl"}
FEM_SET = {"A2-1477": "veikianti", "A2-0536": "tokia pat", "A2-0537": "kitokia", "A2-1474": "tam tikra"}
A1_PRON = {"108_minia": "minià", "148_taika": "taikà", "243_kortele": "kortẽlė", "344_data": "datà",
           "454_letas": "lė̃tas", "497_seklus": "seklùs", "513_ji": "jì", "516_jus": "jū̃s", "517_jie": "jiẽ"}
COLOUR_FEM = {"069_raudonas": "raudona", "070_zalias": "žalia", "071_melynas": "mėlyna", "072_geltonas": "geltona",
              "073_rudas": "ruda", "074_rozinis": "rožinė", "075_oranzinis": "oranžinė", "076_juodas": "juoda",
              "077_baltas": "balta", "078_pilkas": "pilka"}


def norm_i(s):
    """i + U+0307 (+ accent) -> precomposed: 'i̇̀lgas' -> 'ìlgas', 'i̇lgaĩ' -> 'ilgaĩ'."""
    if "\u0307" not in (s or ""):
        return s
    d = unicodedata.normalize("NFD", s)
    out = []
    for i, ch in enumerate(d):
        if ch == "\u0307" and i and d[i - 1] in "iI":
            continue
        out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f); return r.fieldnames, list(r)


def write(p, cols, rows):
    with open(p + ".tmp", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    os.replace(p + ".tmp", p)


def setf(deck, key, r, field, new, why):
    if r.get(field, "") != new:
        LOG.append([deck, key, field, r.get(field, ""), new, why]); r[field] = new


def fix_a2(path):
    cols, rows = read(path)
    for r in rows:
        k = r["id"]
        if k in GEN and r["gen_sg"].split()[-1:] == [GEN[k][0]]:
            setf("A2", k, r, "gen_sg", " ".join(r["gen_sg"].split()[:-1] + [GEN[k][1]]), "kirtis.info K. vnsk.")
        if k in GENDER:
            setf("A2", k, r, "gender", GENDER[k], "kirtis.info gender")
        if k in FEM_SET:
            setf("A2", k, r, "fem", FEM_SET[k], "kirtis.info mot.gim. vnsk. V.")
        if r["type"] == "A" and r["fem"].strip() and not r["gender"].strip():
            setf("A2", k, r, "gender", "M/F", "adjective keeps both forms (owner 2026-10-17)")
        for f in ("lt_pron", "lithuanian_TARGET"):
            setf("A2", k, r, f, norm_i(r[f]), "precomposed accent")
    write(path, cols, rows)


def fix_a1():
    cols, rows = read(P("cards_anki.csv"))
    for r in rows:
        k = r["key"]
        if k in A1_PRON:
            setf("A1", k, r, "pron", A1_PRON[k], "kirtis.info stress"); setf("A1", k, r, "pron_src", "kirtis.info", "")
        if k in COLOUR_FEM:
            setf("A1", k, r, "fem", COLOUR_FEM[k], "kirtis.info bdvr. mot.gim. vnsk. V.")
            setf("A1", k, r, "gen_sg", "", "colour is an adjective: feminine, not a noun genitive")
        setf("A1", k, r, "pron", norm_i(r["pron"]), "precomposed accent")
    write(P("cards_anki.csv"), cols, rows)
    cols, rows = read(P("master_wordlist.csv"))
    bykey = {k.split("_")[0].lstrip("0"): v for k, v in A1_PRON.items()}
    for r in rows:
        n = r["#"]
        if n in bykey:
            setf("A1-master", n, r, "lt_pron", bykey[n], "kirtis.info stress")
        setf("A1-master", n, r, "lt_pron", norm_i(r["lt_pron"]), "precomposed accent")
    write(P("master_wordlist.csv"), cols, rows)


fix_a2(P("a2_build", "a2_wordlist.csv"))
if os.path.exists(P("a2_build", "deferred_B1.csv")):
    fix_a2(P("a2_build", "deferred_B1.csv"))
fix_a1()
logp = P("a2_build", "backs_audit", "data_fixes_applied.csv")
old = read(logp)[1] if os.path.exists(logp) else []
with open(logp, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["deck", "key", "field", "old", "new", "source"])
    for r in old: w.writerow([r["deck"], r["key"], r["field"], r["old"], r["new"], r["source"]])
    w.writerows(LOG)
print(len(LOG), "field changes this run")
