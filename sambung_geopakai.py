from pathlib import Path
p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
t = p.read_text(encoding='utf-8')

a = "    for (p, sx, sy, ex, ey, busur) in geo:\n        if not p['label']:"
b = "    for (p, sx, sy, ex, ey, busur) in geo_pakai:\n        if not p['label']:"
print('label loop:', a in t)
t = t.replace(a, b, 1)

c = "    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo):\n        # ── gaya garis per jenis panah"
d = "    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo_pakai):\n        # ── gaya garis per jenis panah"
print('gambar loop:', c in t)
t = t.replace(c, d, 1)

p.write_text(t, encoding='utf-8')
print('OK')
