import json, shutil, os
L = "/home/claude/lt"
docs = {"historical": f"{L}/a2_build/historical/REPORT_historical_places_figures.md",
        "backs": f"{L}/a2_build/BACKS_AUDIT.md", "pilot": f"{L}/a2_build/PILOT_24.md",
        "order": f"{L}/a2_build/study_order/REPORT_study_order.md"}
D = {k: open(v, encoding="utf-8").read() for k, v in docs.items()}
shots = [("frame_preview/phone_183_sriuba.jpg", "Picture card, front and back (sriuba)"),
         ("frame_preview/phone_A2-0907.jpg", "Phrase card (old bubble picture; pilot replaces it)"),
         ("backs_preview/back_069_raudonas.jpg", "Adjective back: both forms (raudonas)"),
         ("backs_preview/back_452_didelis.jpg", "Adjective back (didelis)"),
         ("backs_preview/back_110_mokytojas.jpg", "Job noun back (mokytojas)"),
         ("backs_preview/back_375_sakyti.jpg", "Verb back (sakyti)")]
os.makedirs("img", exist_ok=True)
fig = []
for p, cap in shots:
    name = os.path.basename(p); shutil.copy(f"{L}/build_reports/{p}", f"img/{name}")
    fig.append(f'<figure><img src="img/{name}" alt="{cap}" loading="lazy"><figcaption>{cap}</figcaption></figure>')
t = open("template.html", encoding="utf-8").read()
j = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
t = (t.replace("__ITEMS__", j(json.load(open("items.json", encoding="utf-8"))))
      .replace("__DOCS__", j(D)).replace("__SHOTS__", "\n".join(fig)).replace("__UPDATED__", __import__("datetime").datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Vilnius")).strftime("%-d %b %Y, %H:%M")))
open("review_desk.html", "w", encoding="utf-8").write(t)
print(len(t), sorted(os.listdir("img")))
