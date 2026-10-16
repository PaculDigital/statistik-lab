#!/usr/bin/env python3
"""SISIP Normalitas + tombol pintasan hetero ke belajar.html (20Sep26).

ATURAN BOS: JANGAN patch buta. Skrip ini:
  1. BACA berkas utuh dulu, HITUNG penanda (tag <script>, {% block %}, <div>)
  2. CADANGKAN berkas asli
  3. SISIP blok lewat PENANDA TEKS yang unik (kalau penanda tidak ketemu → BATAL)
  4. VERIFIKASI seimbang (tag/kurung) + ast.parse tidak berlaku (HTML),
     jadi dipakai: hitung <script>, </script>, {% block %}, {% endblock %}

Pakai: .venv/bin/python _sketsa/sisip_normalitas.py
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BERKAS = BASE / 'app' / 'templates' / 'belajar.html'
CADANGAN = BASE / 'app' / 'templates' / 'belajar.html.cadangan_normalitas'

# ══════════════════════════════════════════════════════════════════════════
# 1. BACA UTUH + HITUNG PENANDA
# ══════════════════════════════════════════════════════════════════════════
asli = BERKAS.read_text(encoding='utf-8')


def hitung(teks: str) -> dict:
    return {
        '<script': len(re.findall(r'<script', teks)),
        '</script>': len(re.findall(r'</script>', teks)),
        '{% block': len(re.findall(r'\{%\s*block', teks)),
        '{% endblock': len(re.findall(r'\{%\s*endblock', teks)),
        '<svg': len(re.findall(r'<svg', teks)),
        '</svg>': len(re.findall(r'</svg>', teks)),
        '<div': len(re.findall(r'<div', teks)),
        '</div>': len(re.findall(r'</div>', teks)),
    }


sebelum = hitung(asli)
print('═══ PENANDA SEBELUM ═══')
for k, v in sebelum.items():
    print(f'  {k:12} = {v}')

# ══════════════════════════════════════════════════════════════════════════
# 2. PENANDA TEKS — kalau salah satu tidak ketemu, BATAL (jangan tebak)
# ══════════════════════════════════════════════════════════════════════════
P_TOMBOL_UJIT = ("    <button class=\"kamus-tombol\" data-k=\"ujit\">"
                 "{{ ikon('alert-circle', 15) }} Uji t: signifikan kok negatif?</button>\n")
P_BIJI_TAB1 = ('    {{ ikon(\'book-open\', 15) }} Materi &amp; Kamus '
               '<span class="biji">9</span>')
P_MEDAN = ('''    <div class="medan renggang">
      <label id="label-slider" for="slider">Seberapa tidak rata sebarannya?</label>
      <input type="range" id="slider" min="0" max="100" value="35">''')

for nama, pola in [('tombol ujit', P_TOMBOL_UJIT),
                   ('biji tab 1', P_BIJI_TAB1),
                   ('medan slider', P_MEDAN)]:
    ada = asli.count(pola)
    print(f'  penanda {nama:14} ditemukan {ada}×', end='')
    if ada != 1:
        print('  ❌ BATAL — harus tepat 1')
        sys.exit(1)
    print('  ✅')

# ══════════════════════════════════════════════════════════════════════════
# 3. CADANGKAN
# ══════════════════════════════════════════════════════════════════════════
shutil.copy2(BERKAS, CADANGAN)
print(f'\n✅ cadangan: {CADANGAN.name} ({CADANGAN.stat().st_size} byte)')

baru = asli

# ══════════════════════════════════════════════════════════════════════════
# 4a. JUDUL TOMBOL UJI t
# ══════════════════════════════════════════════════════════════════════════
baru = baru.replace(
    P_TOMBOL_UJIT,
    "    <button class=\"kamus-tombol\" data-k=\"ujit\">"
    "{{ ikon('alert-circle', 15) }} Uji t: masalah uji t</button>\n"
    # tombol BARU: Normalitas (entri ke-8)
    "    <button class=\"kamus-tombol\" data-k=\"normalitas\">"
    "{{ ikon('bell', 15) }} Normalitas</button>\n",
    1)
print('✅ 4a. tombol uji t diganti + tombol Normalitas ditambah')

# ══════════════════════════════════════════════════════════════════════════
# 4b. BIJI PITA TAB 1 (jumlah tombol kamus 7 → 8)
# ══════════════════════════════════════════════════════════════════════════
baru = baru.replace(P_BIJI_TAB1,
                    P_BIJI_TAB1.replace('<span class="biji">9</span>',
                                        '<span class="biji">8</span>'), 1)
print('✅ 4b. biji pita tab Material & Kamus: 9 → 8')

# ══════════════════════════════════════════════════════════════════════════
# 4c. TOMBOL PINTASAN di atas slider (hetero)
# ══════════════════════════════════════════════════════════════════════════
PINTASAN = '''    {# ⚠️ PINTASAN SEHAT/SAKIT (20Sep26, ACC Bos) — 2 tombol cepat di ATAS
       slider. Slider TETAP ADA (keputusan Bos: variasi B) supaya user masih
       bisa menggeser bebas; tombol cuma jalan pintas satu klik. Tombol
       menyala sendiri saat slider mentok (diatur di JS fungsi pintasanNyalakan).
       Alasan penting (temuan Bos): mahasiswa sering menyangka "tidak ada corong
       = tidak ada hasil". Dua tombol ini membuat keadaan SEHAT bisa dilihat
       langsung, bukan cuma disimpulkan. #}
    <div class="pintasan-baris" id="pintasan-baris" hidden>
      <button type="button" class="pintasan" id="pintasan-sehat">Contoh sehat</button>
      <button type="button" class="pintasan" id="pintasan-sakit">Contoh sakit</button>
    </div>

'''
baru = baru.replace(P_MEDAN, PINTASAN + P_MEDAN, 1)
print('✅ 4c. tombol pintasan ditambah di atas slider')

# ══════════════════════════════════════════════════════════════════════════
# 5. VERIFIKASI SEIMBANG
# ══════════════════════════════════════════════════════════════════════════
sesudah = hitung(baru)
print('\n═══ PENANDA SESUDAH ═══')
selisih = {}
for k in sebelum:
    d = sesudah[k] - sebelum[k]
    selisih[k] = d
    tanda = '✅' if d == 0 else f'({d:+d})'
    print(f'  {k:12} = {sesudah[k]:4}  {tanda}')

# aturan: div/hijau blok baru harus seimbang (2 div buka, 2 div tutup)
if sesudah['<div'] - sesudah['</div>'] != sebelum['<div'] - sebelum['</div>']:
    print('\n❌ BATAL — tag <div> tidak seimbang')
    sys.exit(1)
if sesudah['{% block'] != sesudah['{% endblock']:
    print('\n❌ BATAL — blok Jinja tidak seimbang')
    sys.exit(1)

BERKAS.write_text(baru, encoding='utf-8')
print(f'\n✅ BERKAS DITULIS: {len(asli)} → {len(baru)} byte  ({len(baru)-len(asli):+d})')
