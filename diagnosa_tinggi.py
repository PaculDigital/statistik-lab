"""DIAGNOSA: kenapa tinggi tidak naik? Cetak isi geo_awal saat hitung tinggi."""
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))

# sisipkan pencetakan ke diagram_svg lewat monkeypatch sederhana
import diagram_svg as D

_asli = D.gambar_svg
src = open(DIR / 'diagram_svg.py', encoding='utf-8').read()

# cari nilai butuh_bawah dengan menjalankan potongan:
from resep_model import baca_resep
from uji_pertanyaan_bos import R_BER

m, info = baca_resep(R_BER)
kolom, jml = D.hitung_kolom(m)
baris = D.hitung_baris(m, kolom, jml)
print('kolom:', kolom)
print('baris:', baris)

# jalankan gambar dan tangkap tinggi lewat trace sederhana
import re
svg = D.gambar_svg(m, 'tes')
vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
print('viewBox:', vb)
print()
print('--- semua path/line di SVG ---')
for mm in re.finditer(r'<(path|line)[^>]*d="([^"]*)"[^>]*>', svg):
    print(' ', mm.group(1), mm.group(2)[:70])
print()
# cek: apakah 'geo' yang dipakai menggambar sudah bergeser?
print('--- y label ---')
for mm in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*>([^<]+)</text>',
                      svg):
    print(f'  {mm.group(3)[:28]:30} y={mm.group(2)}')
