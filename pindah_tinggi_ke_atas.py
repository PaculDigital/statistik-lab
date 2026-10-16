"""Pindahkan blok TINGGI ke SEBELUM pembangunan SVG (baris 156).

AKAR terukur 18Sep26: blok tinggi Wulan dipasang di baris ~333-364,
yaitu SETELAH `s = [f'<svg ... viewBox ... {tinggi}...']` di baris 156.
Akibatnya viewBox dibuat dengan tinggi LAMA (170) walau `tinggi`
diupdate jadi 241 setelahnya → gambar terpotong (label H4 hilang).
"""
from pathlib import Path

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
baris = p.read_text(encoding='utf-8').split('\n')

# 1) cari blok tinggi di bawah (mulai dari komentar penanda)
mulai = next(i for i, b in enumerate(baris)
             if 'TINGGI HARUS MENGHITUNG BUSUR PANAH' in b)
# berakhir sebelum baris kosong diikuti komentar "tentukan posisi label"
akhir = next(i for i, b in enumerate(baris)
             if i > mulai and 'tentukan posisi label' in b)
blok = baris[mulai:akhir]
print(f'blok tinggi baris {mulai+1}..{akhir} ({len(blok)} baris)')

# 2) buang dari posisi lama
sisa = baris[:mulai] + baris[akhir:]

# 3) sisipkan tepat SEBELUM baris `s = [f'<svg xmlns`
target = next(i for i, b in enumerate(sisa)
              if b.startswith("    s = [f'<svg xmlns"))
print(f'sisip sebelum baris {target+1}')
baru = sisa[:target] + blok + sisa[target:]

p.write_text('\n'.join(baru), encoding='utf-8')
print('OK')
