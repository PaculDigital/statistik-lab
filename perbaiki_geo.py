"""Perbaiki: di dalam loop putaran kedua, `geo` harus `geo_awal`
(akses saat ELIPS/LABEL), lalu setelah blok tinggi `geo` baru dipakai.
"""
from pathlib import Path

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
t = p.read_text(encoding='utf-8')

# 1. enumerate(geo) -> enumerate(geo_awal) HANYA di loop putaran kedua
t = t.replace(
    '    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo):\n'
    '        if busur:\n'
    '            continue          # sudah melengkung\n'
    '        for j, (p2, sx2, sy2, ex2, ey2, busur2) in enumerate(geo):',
    '    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo_awal):\n'
    '        if busur:\n'
    '            continue          # sudah melengkung\n'
    '        for j, (p2, sx2, sy2, ex2, ey2, busur2) in enumerate(geo_awal):')

# 2. geo[i] / geo[j] -> geo_awal[i] / geo_awal[j] di loop itu
t = t.replace('                geo[i] = (p, sx, sy, ex, ey, BUSUR_POTONG)\n'
              '                geo[j] = (p2, sx2, sy2, ex2, ey2, -BUSUR_POTONG)',
              '                geo_awal[i] = (p, sx, sy, ex, ey, BUSUR_POTONG)\n'
              '                geo_awal[j] = (p2, sx2, sy2, ex2, ey2, -BUSUR_POTONG)')

p.write_text(t, encoding='utf-8')
print('OK')
