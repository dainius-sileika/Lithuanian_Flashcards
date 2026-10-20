"""Per-card list of an A1 package: due key plate level kind pos topic note_type guid image audio audio_source.
usage: python3 tools/apkg_keys_list.py <pkg.apkg> audio_source.tsv build_reports/builds/<name>.tsv
(2026-10-20; reproduces v3.0_A1_keys_rc2.tsv byte for byte from the rc2 package.)"""
import zipfile, sqlite3, tempfile, json, re, csv, sys
pkg, asrc, out = sys.argv[1:4]
t = tempfile.mkdtemp(); z = zipfile.ZipFile(pkg)
n = next(x for x in ('collection.anki21', 'collection.anki2') if x in z.namelist())
open(t + '/c.db', 'wb').write(z.read(n)); db = sqlite3.connect(t + '/c.db')
models = json.loads(db.execute('select models from col').fetchone()[0])
src = {r['key']: r['source'] for r in csv.DictReader(open(asrc, encoding='utf-8'), delimiter='\t')}
rows = []
for mid, guid, tags, flds, due in db.execute("select n.mid,n.guid,n.tags,n.flds,c.due from cards c join notes n on n.id=c.nid"):
    m = models[str(mid)]; f = dict(zip([x['name'].lower() for x in m['flds']], flds.split('\x1f')))
    tg = dict(x.split('::')[1:3] for x in tags.split() if x.startswith('lt::') and x.count('::') == 2)
    img = re.findall(r'src="([^"]+)"', f.get('image', ''))
    snd = re.findall(r'\[sound:([^\]]+)\]', f.get('audio', ''))
    key = f['key']
    rows.append([due, key, f['number'], tg.get('level', ''), tg.get('kind', ''), tg.get('pos', ''), tg.get('topic', ''),
                 m['name'], guid, img[0] if img else '', snd[0] if snd else '',
                 (src.get(key, '?') if snd else 'silent')])
rows.sort(key=lambda r: r[0])
with open(out, 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t', lineterminator='\n')
    w.writerow(['due', 'key', 'plate', 'level', 'kind', 'pos', 'topic', 'note_type', 'guid', 'image', 'audio', 'audio_source'])
    w.writerows(rows)
print(out, len(rows))
