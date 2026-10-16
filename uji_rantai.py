"""UJI RANTAI PANJANG: 3 & 4 perantara. Tanam koefisien, mesin harus temukan.

Latar: ACC Bos 21Sep26 — *"Rantai lebih 2 perantara belum"*.
Sebelum ini mediasi berjenjang hanya menghitung 2 perantara pertama.

CARA UJI (aturan induk): bangkitkan data dari SPEK YANG DIKETAHUI →
mesin HARUS menemukan kebenaran yang kita tanam. Kalau tidak → uji GAGAL.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')
import numpy as np
import pandas as pd
from app.hitung.kaitan import mediasi_rantai, hitung_kaitan, mediasi_berjenjang

GAGAL = 0
def cek(n, s, b=''):
    global GAGAL
    print(f"  {'✅' if s else '❌'} {n}" + (f'   {b}' if b else ''))
    if not s:
        GAGAL += 1

n = 400
TOL = 0.12

# ── 3 PERANTARA: X → M1(0,60) → M2(0,55) → M3(0,50) → Y(0,45) ──
rng = np.random.default_rng(11)
X = rng.normal(size=n)
M1 = 0.60 * X + rng.normal(scale=0.8, size=n)
M2 = 0.10 * X + 0.55 * M1 + rng.normal(scale=0.8, size=n)
M3 = 0.05 * X + 0.10 * M1 + 0.50 * M2 + rng.normal(scale=0.8, size=n)
Y = 0.03 * X + 0.05 * M1 + 0.08 * M2 + 0.45 * M3 + rng.normal(scale=0.8, size=n)
d3 = pd.DataFrame({'X1': X, 'M1': M1, 'M2': M2, 'M3': M3, 'Y1': Y})

print('=' * 70)
print(' 3 PERANTARA — X → M1 → M2 → M3 → Y')
print('=' * 70)
r = mediasi_rantai(d3, 'X1', ['M1', 'M2', 'M3'], 'Y1')
cek('boleh dihitung', r.get('boleh'), str(r.get('n')))
cek('jumlah_perantara = 3', r.get('jumlah_perantara') == 3)
cek('a1 (X→M1) ≈ 0,60', abs(r['a']['b'] - 0.60) <= TOL, f"dapat {r['a']['b']}")
cek('d1 (M1→M2) ≈ 0,55', abs(r['d_semua'][0]['b'] - 0.55) <= TOL,
    f"dapat {r['d_semua'][0]['b']}")
cek('d2 (M2→M3) ≈ 0,50', abs(r['d_semua'][1]['b'] - 0.50) <= TOL,
    f"dapat {r['d_semua'][1]['b']}")
cek('b3 (M3→Y) ≈ 0,45', abs(r['b']['b'] - 0.45) <= TOL, f"dapat {r['b']['b']}")
cek('ADA 3 jalur tidak langsung', len(r['jalur']) == 3, f"→ {len(r['jalur'])}")
cek('jalur 1: X→M1→Y', r['jalur'][0]['nama'] == 'X1 → M1 → Y1',
    r['jalur'][0]['nama'])
cek('jalur 2: X→M1→M2→Y', r['jalur'][1]['nama'] == 'X1 → M1 → M2 → Y1',
    r['jalur'][1]['nama'])
cek('jalur 3: X→M1→M2→M3→Y',
    r['jalur'][2]['nama'] == 'X1 → M1 → M2 → M3 → Y1', r['jalur'][2]['nama'])
# jalur 3 = 0,60 × 0,55 × 0,50 × 0,45 = 0,07425
cek('jalur 3 ≈ 0,0743 (empat angka dikali)',
    abs(r['jalur'][2]['b'] - 0.0743) <= 0.03, f"dapat {r['jalur'][2]['b']}")
cek('jalur 3 SIGNIFIKAN', r['jalur'][2]['signifikan'] is True,
    f"lo={r['jalur'][2]['lo']} hi={r['jalur'][2]['hi']}")
cek('ada selang di semua jalur', all(j['lo'] is not None for j in r['jalur']))
cek('simpulan terisi', bool(r['jenis']), r['jenis'])
cek('kalimat sebut ketiga perantara',
    all(m in r['kalimat'] for m in ('M1', 'M2', 'M3')), r['kalimat'][:60])
cek('jujur soal tumpang-tindih',
    'tumpang' in str(r['tidak_langsung'].get('ket', '')).lower(),
    str(r['tidak_langsung'].get('ket'))[:60])

# ── 4 PERANTARA ──
print()
print('=' * 70)
print(' 4 PERANTARA — X → M1 → M2 → M3 → M4 → Y')
print('=' * 70)
rng2 = np.random.default_rng(22)
X4 = rng2.normal(size=n)
A = 0.60 * X4 + rng2.normal(scale=0.8, size=n)
B = 0.55 * A + rng2.normal(scale=0.8, size=n)
C = 0.50 * B + rng2.normal(scale=0.8, size=n)
D = 0.45 * C + rng2.normal(scale=0.8, size=n)
Y4 = 0.03 * X4 + 0.40 * D + rng2.normal(scale=0.8, size=n)
d4 = pd.DataFrame({'X1': X4, 'M1': A, 'M2': B, 'M3': C, 'M4': D, 'Y1': Y4})
r4 = mediasi_rantai(d4, 'X1', ['M1', 'M2', 'M3', 'M4'], 'Y1')
cek('4 perantara boleh dihitung', r4.get('boleh'), str(r4.get('n')))
cek('ADA 4 jalur', len(r4['jalur']) == 4, f"→ {len(r4['jalur'])}")
# jalur 4 = 0,60×0,55×0,50×0,45×0,40 = 0,0297
cek('jalur 4 ≈ 0,0297 (lima angka dikali)',
    abs(r4['jalur'][3]['b'] - 0.0297) <= 0.02, f"dapat {r4['jalur'][3]['b']}")
cek('nama jalur 4 benar',
    r4['jalur'][3]['nama'] == 'X1 → M1 → M2 → M3 → M4 → Y1',
    r4['jalur'][3]['nama'])

# ── RANTAI TERPUTUS di tengah (M2→M3 = 0) ──
print()
print('=' * 70)
print(' RANTAI TERPUTUS di tengah (M2→M3 = 0)')
print('=' * 70)
rng3 = np.random.default_rng(33)
Xp = rng3.normal(size=n)
P1 = 0.60 * Xp + rng3.normal(scale=0.8, size=n)
P2 = 0.55 * P1 + rng3.normal(scale=0.8, size=n)
P3 = rng3.normal(scale=0.8, size=n)          # TIDAK nyambung dari P2
Yp = 0.03 * Xp + 0.40 * P3 + rng3.normal(scale=0.8, size=n)
dp = pd.DataFrame({'X1': Xp, 'M1': P1, 'M2': P2, 'M3': P3, 'Y1': Yp})
rp = mediasi_rantai(dp, 'X1', ['M1', 'M2', 'M3'], 'Y1')
cek('d2 (P2→P3) ≈ 0', abs(rp['d_semua'][1]['b']) <= TOL,
    f"dapat {rp['d_semua'][1]['b']}")
cek('jalur 3 (lewat P3) TIDAK signifikan',
    rp['jalur'][2]['signifikan'] is False,
    f"lo={rp['jalur'][2]['lo']} hi={rp['jalur'][2]['hi']}")

# ── LEWAT hitung_kaitan: 3 perantara berjenjang ──
print()
print('=' * 70)
print(' LEWAT hitung_kaitan (pintu gerbang)')
print('=' * 70)
h = hitung_kaitan(d3, ['X1'], 'Y1', kolom_m=['M1', 'M2', 'M3'],
                  bentuk='berjenjang')
cek('bentuk = berjenjang', h['bentuk_mediasi'] == 'berjenjang',
    str(h['bentuk_mediasi']))
cek('hasil pakai rantai panjang', h['mediasi'][0].get('rantai_panjang') is True)
cek('3 jalur dilaporkan', len(h['mediasi'][0]['jalur']) == 3,
    f"→ {len(h['mediasi'][0]['jalur'])}")
cek('TIDAK ada lagi catatan "belum"', 'catatan' not in h['mediasi'][0],
    str(h['mediasi'][0].get('catatan'))[:50])

# ── k=2 lewat rantai harus SAMA dengan mediasi_berjenjang ──
print()
print('[5] k=2 lewat rantai == mediasi_berjenjang (jalur 1 & 2)')
r_old = mediasi_berjenjang(d3, 'X1', 'M1', 'M2', 'Y1')
r_new = mediasi_rantai(d3, 'X1', ['M1', 'M2'], 'Y1')
cek('jalur 1 sama', abs(r_old['jalur'][0]['b'] - r_new['jalur'][0]['b']) < 0.01,
    f"lama {r_old['jalur'][0]['b']} vs baru {r_new['jalur'][0]['b']}")
cek('jalur 2 sama', abs(r_old['jalur'][1]['b'] - r_new['jalur'][1]['b']) < 0.01,
    f"lama {r_old['jalur'][1]['b']} vs baru {r_new['jalur'][1]['b']}")

print()
print('=' * 70)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS SEMUA — rantai 3 & 4 perantara terbukti benar')
sys.exit(0)
