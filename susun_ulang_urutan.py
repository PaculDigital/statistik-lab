"""Solusi: pindahkan PEMBUKAAN SVG (baris `s = [f'<svg ...`) ke bawah,
yaitu TEPAT SETELAH blok tinggi (yang ada di akhir perhitungan panah),
sebelum penggambaran panah.

Urutan yang benar:
  1. posisi elips
  2. geo_awal dihitung + busur + putaran kedua
  3. blok tinggi (butuh geo_awal)
  4. PEMBUKAAN SVG (butuh tinggi final)
  5. gambar panah, label, elips
"""
from pathlib import Path

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
baris = p.read_text(encoding='utf-8').split('\n')

# ── 1. ambil blok pembukaan SVG + <defs> ──
mulai_svg = next(i for i, b in enumerate(baris)
                 if b.startswith("    s = [f'<svg xmlns"))
# berakhir tepat sebelum komentar judul ("if judul:")
akhir_svg = next(i for i, b in enumerate(baris)
                 if i > mulai_svg and b.strip().startswith('if judul:'))
blok_svg = baris[mulai_svg:akhir_svg]
print(f'blok SVG baris {mulai_svg+1}..{akhir_svg} ({len(blok_svg)} baris)')

sisa = baris[:mulai_svg] + baris[akhir_svg:]

# ── 2. pindahkan blok TINGGI (kembali ke atas) ──
mulai_t = next(i for i, b in enumerate(sisa)
               if 'TINGGI HARUS MENGHITUNG BUSUR PANAH' in b)
akhir_t = next(i for i, b in enumerate(sisa)
               if i > mulai_t and 'tentukan posisi label' in b)
blok_t = sisa[mulai_t:akhir_t]
print(f'blok tinggi baris {mulai_t+1}..{akhir_t} ({len(blok_t)} baris)')
sisa2 = sisa[:mulai_t] + sisa[akhir_t:]

# ── 3. sisipkan: blok tinggi + blok SVG, setelah perhitungan panah ──
#     penanda akhir perhitungan panah = baris geo_awal[j] = ... -BUSUR_POTONG
tanda = next(i for i, b in enumerate(sisa2) if '-BUSUR_POTONG)' in b
             and 'geo_awal[j]' in b)
print(f'sisip setelah baris {tanda+1} (akhir putaran kedua)')
baru = sisa2[:tanda + 1] + [''] + blok_t + [''] + blok_svg + sisa2[tanda + 1:]

p.write_text('\n'.join(baru), encoding='utf-8')
print('OK')
