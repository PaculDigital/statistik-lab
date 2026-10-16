"""Pindahkan PEMBUKAAN SVG ke bawah (setelah panah dihitung), dan
letakkan blok TINGGI tepat sebelum pembukaan SVG.

Struktur akhir di dalam gambar_svg():
  1. posisi elips + tinggi_konten
  2. [KOMENTAR penunjuk]
  3. geo_awal: hitung ruas + busur + putaran kedua   <- butuh pusat
  4. blok TINGGI (baca geo_awal)                     <- butuh geo_awal
  5. PEMBUKAAN SVG + <defs>                           <- butuh tinggi final
  6. judul, panah, label, elips
"""
from pathlib import Path

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
baris = p.read_text(encoding='utf-8').split('\n')

# ── potong blok PEMBUKAAN SVG + defs (dari `s = [f'<svg xmlns` s.d. sebelum `if judul:`) ──
a = next(i for i, b in enumerate(baris)
         if b.startswith("    s = [f'<svg xmlns"))
b_ = next(i for i, b in enumerate(baris)
          if i > a and b.strip().startswith('if judul:'))
blok_svg = baris[a:b_]
print(f'blok SVG: baris {a+1}..{b_} ({len(blok_svg)} baris)')
sisa = baris[:a] + baris[b_:]

# ── titik sisip: setelah `geo_awal[j] = ... -BUSUR_POTONG)` (akhir putaran kedua) ──
tanda = next(i for i, b in enumerate(sisa)
             if 'geo_awal[j] = (p2' in b)
print(f'sisip setelah baris {tanda+1}')

blok_tinggi = '''    # ── 🚨 TINGGI (dipindah ke sini) ──
    #    AKAR terukur 18Sep26: mediasi berjenjang menghasilkan viewBox
    #    890×170 padahal busur X1→Y puncaknya di y=233 → label H4 (y=233)
    #    DI LUAR gambar → seolah "H4 hilang" (temuan vision).
    #    Sebab: tinggi dulu hanya dihitung dari posisi ELIPS.
    #    ⚠️ Blok ini WAJIB di sini (setelah panah dihitung, SEBELUM SVG
    #       dibuka) — kalau ditaruh di atas panah, `geo_awal` belum ada;
    #       kalau di bawah pembukaan SVG, `tinggi` sudah terlanjur dipakai
    #       (viewBox dibuat dengan tinggi lama → gambar terpotong).
    _kandidat_y = [0.0, tinggi_konten]
    for (_p2, _sx2, _sy2, _ex2, _ey2, _busur2) in geo_awal:
        _kandidat_y.append(_sy2)
        _kandidat_y.append(_ey2)
        if _busur2:
            # RUMUS PUNCAK KURVA KUADRATIK (Bézier t=0,5):
            # titik kontrol dulu, lalu puncak = (sy + 2*cy + ey) / 4.
            # (Wulan pernah SALAH pakai (sy+ey)/2 + dx/L*busur → puncak
            #  diperkirakan 165 padahal nyata 233.)
            _dx2, _dy2 = _ex2 - _sx2, _ey2 - _sy2
            _L2 = (_dx2 * _dx2 + _dy2 * _dy2) ** 0.5 or 1
            _nx2, _ny2 = -_dy2 / _L2, _dx2 / _L2
            _cx2 = (_sx2 + _ex2) / 2 + _nx2 * _busur2
            _cy2 = (_sy2 + _ey2) / 2 + _ny2 * _busur2
            _kandidat_y.append(_cy2)
            _kandidat_y.append((_sy2 + 2 * _cy2 + _ey2) / 4)
    _lo, _hi = min(_kandidat_y), max(_kandidat_y)

    geser_y = PINGGIR - _lo if _lo < PINGGIR else 0.0
    butuh_bawah = _hi + PINGGIR
    if butuh_bawah > tinggi:
        tinggi = butuh_bawah
    if geser_y:
        tinggi += geser_y
        pusat = {k: (x, y + geser_y) for k, (x, y) in pusat.items()}
        geo = [(p2, sx2, sy2 + geser_y, ex2, ey2 + geser_y, busur2)
               for (p2, sx2, sy2, ex2, ey2, busur2) in geo_awal]
    else:
        geo = geo_awal
'''.split('\n')

baru = sisa[:tanda + 1] + [''] + blok_tinggi + [''] + blok_svg + sisa[tanda + 1:]
p.write_text('\n'.join(baru), encoding='utf-8')
print('OK')
