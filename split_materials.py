# -*- coding: utf-8 -*-
"""materials.json を materials/ 配下のカテゴリ別ファイルへ分割する（移行用・1回だけ実行）。

Cloudflare Pages の「1ファイル25MiBまで」に引っかかったための対応。
出力:
  materials/index.json   … updatedAt / categories / catTargets / lockedCats / files
  materials/cNN.json     … {"category": 名前, "items": [...]}
  materials/shapes.json  … customShapes（illust-sticker のみ使用）
"""
import json, os, sys, hashlib

SRC = sys.argv[1] if len(sys.argv) > 1 else 'materials.json'
OUT = 'materials'
LIMIT = 25 * 1024 * 1024

d = json.load(open(SRC, encoding='utf-8'))
os.makedirs(OUT, exist_ok=True)

cats = d.get('categories') or list(d.get('materials', {}).keys())
files, hashes, sizes = {}, {}, []

def h(text):
    # illust-sticker 側の admPushToGitHub と同じ作り方（SHA-256の先頭32桁）
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:32]

for i, c in enumerate(cats, 1):
    slug = 'c%02d.json' % i
    body = {'category': c, 'items': d.get('materials', {}).get(c, [])}
    s = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
    open(os.path.join(OUT, slug), 'w', encoding='utf-8').write(s)
    files[c] = slug
    hashes[c] = h(s)
    sizes.append((len(s.encode()), slug, c, len(body['items'])))

shapes = d.get('customShapes', [])
if shapes:
    s = json.dumps(shapes, ensure_ascii=False, separators=(',', ':'))
    open(os.path.join(OUT, 'shapes.json'), 'w', encoding='utf-8').write(s)
    hashes['__shapes'] = h(s)
    sizes.append((len(s.encode()), 'shapes.json', '(customShapes)', len(shapes)))

index = {
    'updatedAt': d.get('updatedAt'),
    'categories': cats,
    'catTargets': d.get('catTargets', {}),
    'lockedCats': d.get('lockedCats', []),
    'files': files,
    'shapes': 'shapes.json' if shapes else None,
    'hashes': hashes,
}
s = json.dumps(index, ensure_ascii=False, indent=2)
open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8').write(s)
sizes.append((len(s.encode()), 'index.json', '(索引)', len(cats)))

print('出力先: %s/' % OUT)
over = 0
for b, f, c, n in sorted(sizes, reverse=True):
    flag = ' ← 25MiB超過' if b > LIMIT else ''
    over += b > LIMIT
    print('  %-12s %-12s %3d件 %7.2f MiB%s' % (f, c, n, b / 1048576, flag))
print('  上限を超えるファイル: %d' % over)
