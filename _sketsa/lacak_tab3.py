"""Lacak: kenapa #tab-3 tidak membuka tabnya padahal semua elemen ada."""
import re
import sys
sys.path.insert(0, '.')

from app.main import templates, _konteks


class P:
    pass


k = _konteks(P(), 'belajar', 'BELAJAR')
k['batas_beta_rantai'] = 1.2
k['versi_aset'] = '0'
html = templates.get_template('belajar.html').render(**k)
b = html.split('\n')

print('  ── posisi di HALAMAN RENDER ──')
for i, l in enumerate(b):
    if 'const m = (location.hash' in l:
        print(f'    skrip bukaTab      : baris {i+1}')
    if 'id="tab-3"' in l:
        print(f'    panel tab-3        : baris {i+1}')
    if 'id="pa-3"' in l:
        print(f'    tombol pa-3        : baris {i+1}')
    if 'id="tab-1"' in l:
        print(f'    panel tab-1        : baris {i+1}')

print()
print('  "function bukaTab" ada  :', 'function bukaTab' in html)
print('  jumlah <script>         :', len(re.findall(r'<script', html)))

i3 = html.find('id="tab-3"')
z3 = html.find('/tab-3', i3)
print(f'  panel tab-3 panjang     : {z3 - i3} karakter')

# ⚠️ Apakah skrip diletakkan SEBELUM panel? Kalau ya, getElementById gagal
i_skrip = html.find('const m = (location.hash')
print(f'  skrip DI DALAM blok mana? skrip@{i_skrip} vs tab3@{i3}')
print('  → skrip SESUDAH panel?', i_skrip > i3)

print()
print('  ── apakah HTML panel tab-3 rusak (tag tak seimbang)? ──')
seg = html[i3 - 40:z3 + 40]
print('    buka ', repr(seg[:60]))
print('    tutup', repr(seg[-60:]))
print('    <div dalam panel:', seg.count('<div'), ' </div>:', seg.count('</div>'))
