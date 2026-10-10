"""Unblind standalone-survey results from friends.
Put each returned go-survey-<name>.json (or pasted results text saved as .json) in results/friends/,
then run from the project root:  python3 style_lab/2026-10-10_06_blind_survey/results/ingest_friends.py
Writes results/friends_unblinded.json and prints each respondent's ranking per round."""
import json, glob, os
D = "style_lab/2026-10-10_06_blind_survey"
key = json.load(open(f"{D}/web_key.json"))
out = []
for f in sorted(glob.glob(f"{D}/results/friends/*.json")):
    r = json.load(open(f, encoding="utf-8"))
    who = r.get("respondent") or os.path.basename(f)
    rounds = []
    for rd in r["rounds"]:
        rows = [{"rank": i + 1, "variant": key[c]["variant"], "ship": c in rd["ship"], "comment": rd["comments"].get(c, ""),
                 "initial_pos": rd["initial"].index(c) + 1} for i, c in enumerate(rd["order"])]
        rounds.append({"round": rd["round"], "card": key[rd["order"][0]]["card"], "done": rd["done"],
                       "unchanged_from_initial": rd["order"] == rd["initial"], "note": rd.get("note", ""), "ranking": rows})
    out.append({"respondent": who, "file": os.path.basename(f), "started": r.get("started"), "finished": r.get("finished"),
                "general": r.get("general", ""), "rounds": rounds})
    print(f"\n=== {who} ({sum(x['done'] for x in rounds)}/13 rounds done)")
    for x in rounds:
        print(f" R{x['round']:>2} {x['card']:<14} " + " > ".join(("*" if y["ship"] else "") + y["variant"] for y in x["ranking"]))
json.dump(out, open(f"{D}/results/friends_unblinded.json", "w"), indent=1, ensure_ascii=False)
print(f"\n{len(out)} respondent(s) -> {D}/results/friends_unblinded.json")
