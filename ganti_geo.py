from pathlib import Path

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
t = p.read_text(encoding='utf-8')
t = t.replace('    geo = []\n',
              '    geo_awal = []   # daftar ruas panah (sebelum digeser)\n', 1)
t = t.replace('        geo.append((p, sx, sy, ex, ey, busur))',
              '        geo_awal.append((p, sx, sy, ex, ey, busur))', 1)
# loop putaran kedua membaca geo -> geo_awal
t = t.replace(
    '    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo):\n'
    '        if busur:\n'
    '            continue          # sudah melengkung\n'
    '        for j,',
    '    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo_awal):\n'
    '        if busur:\n'
    '            continue          # sudah melengkung\n'
    '        for j,')
p.write_text(t, encoding='utf-8')
print('OK')
