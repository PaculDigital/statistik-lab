"""Pindahkan blok perhitungan TINGGI (busur) dari baris 156-191
ke SETELAH putaran kedua (~baris 356), karena blok itu butuh `geo_awal`
yang baru terisi di baris 271-321.
"""
from pathlib import Path
import re

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
t = p.read_text(encoding='utf-8')
baris = t.split('\n')

# cari blok mulai dari komentar "TINGGI HARUS MENGHITUNG BUSUR PANAH"
mulai = next(i for i, b in enumerate(baris)
             if 'TINGGI HARUS MENGHITUNG BUSUR PANAH' in b)
# blok berakhir tepat sebelum "s = [f'<svg xmlns"
akhir = next(i for i, b in enumerate(baris)
             if i > mulai and b.startswith("    s = [f'<svg xmlns"))
blok = baris[mulai:akhir]
print(f'blok tinggi: baris {mulai+1}..{akhir} ({len(blok)} baris)')

# buang dari posisi lama
sisa = baris[:mulai] + baris[akhir:]

# sisipkan setelah putaran kedua: cari baris geo[j] = ... -BUSUR_POTONG
target = next(i for i, b in enumerate(sisa) if '-BUSUR_POTONG)' in b)
print(f'sisip setelah baris {target+1}')
baru = sisa[:target + 1] + [''] + blok + sisa[target + 1:]

p.write_text('\n'.join(baru), encoding='utf-8')
print('OK')
