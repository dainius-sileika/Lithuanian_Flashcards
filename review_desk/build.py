import json, shutil, os
L = "/home/claude/lt"
# Reference documents shown under "Documents for review": (id, title, path). Keep ONLY documents
# the owner still has to read; settled ones go (they stay in the repo). Empty list = no section.
docs = []
D = {k: open(p, encoding="utf-8").read() for k, _, p in docs}
# Screenshots (path under build_reports/, caption); same rule: only what is still under review.
shots = []
os.makedirs("img", exist_ok=True)
fig = []
for p, cap in shots:
    name = os.path.basename(p); shutil.copy(f"{L}/build_reports/{p}", f"img/{name}")
    fig.append(f'<figure><img src="img/{name}" alt="{cap}" loading="lazy"><figcaption>{cap}</figcaption></figure>')
t = open("template.html", encoding="utf-8").read()
parts = [f'  <details class="doc" id="doc-{k}"><summary>{title}</summary><div class="body" data-md="{k}"></div></details>' for k, title, _ in docs]
if fig:
    parts.append('  <details class="doc" id="doc-frames"><summary>Screenshots</summary><div class="body"><div class="shots">' + "\n".join(fig) + '</div></div></details>')
doclist = ('  <h2 id="docs">Documents for review</h2>\n' + "\n".join(parts)) if parts else ""
t = t.replace("__DOCLIST__", doclist)
j = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
t = (t.replace("__ITEMS__", j(json.load(open("items.json", encoding="utf-8"))))
      .replace("__DOCS__", j(D)).replace("__UPDATED__", __import__("datetime").datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Vilnius")).strftime("%-d %b %Y, %H:%M")))
open("review_desk.html", "w", encoding="utf-8").write(t)
print(len(t), sorted(os.listdir("img")))
