"""UJI MEDIASI BERJENJANG: X → M1 → M2 → Y. Tanam koefisien, mesin harus temukan."""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')
import numpy as np, pandas as pd
from app.hitung.kaitan import mediasi_berjenjang, hitung_kaitan

GAGAL = 0
def cek(n, s, b=''):
    global GAGAL
    print(f"  {'✅' if s else '❌'} {n}" + (f'   {b}' if b else ''))
    if not s: GAGAL += 1

# Tanam: X → M1 (a1=0,60) → M2 (d=0,55) → Y (b2=0,50), plus b1=0,10, c'=0,05
rng = np.random.default_rng(77); n = 400
X  = rng.normal(size=n)
M1 = 0.60*X + rng.normal(scale=0.8, size=n)
M2 = 0.15*X + 0.55*M1 + rng.normal(scale=0.8, size=n)
Y  = 0.05*X + 0.10*M1 + 0.50*M2 + rng.normal(scale=0.8, size=n)
d = pd.DataFrame({'X1': X, 'M1': M1, 'M2': M2, 'Y1': Y})

TOL = 0.12
print('='*70); print(' MEDIASI BERJENJANG (X → M1 → M2 → Y)'); print('='*70)
r = mediasi_berjenjang(d, 'X1', 'M1', 'M2', 'Y1')
cek('boleh dihitung', r.get('boleh'), str(r.get('n')))
cek('ada penanda berjenjang', r.get('berjenjang') is True)
cek('a1 (X→M1) ≈ 0,60', abs(r['a']['b'] - 0.60) <= TOL, f"dapat {r['a']['b']}")
cek('d (M1→M2) ≈ 0,55', abs(r['d']['b'] - 0.55) <= TOL, f"dapat {r['d']['b']}")
cek('b2 (M2→Y) ≈ 0,50', abs(r['b']['b'] - 0.50) <= TOL, f"dapat {r['b']['b']}")
cek("c' (X→Y + keduanya) ≈ 0,05", abs(r['cp']['b']) <= 0.15, f"dapat {r['cp']['b']}")

jr = r['jalur']
cek('ada 2 jalur dilaporkan', len(jr) == 2, f"→ {len(jr)}")
cek('jalur 1: X→M1→Y (a1×b1)', 'M1 → Y1' in jr[0]['nama'], jr[0]['nama'])
cek('jalur 2: X→M1→M2→Y (berjenjang)', jr[1]['nama'].count('→') == 3, jr[1]['nama'])
# jalur 2 = 0,60 × 0,55 × 0,50 = 0,165
cek('jalur 2 ≈ 0,165 (0,60×0,55×0,50)', abs(jr[1]['b'] - 0.165) <= 0.05,
    f"dapat {jr[1]['b']}")
cek('jalur 2 SIGNIFIKAN', jr[1]['signifikan'] is True,
    f"lo={jr[1]['lo']} hi={jr[1]['hi']}")
cek('ada selang kepercayaan jalur 2', jr[1]['lo'] is not None)
cek('simpulan jenis terisi', bool(r['jenis']), r['jenis'])
cek('kalimat menyebut kedua perantara', ('M1' in r['kalimat'] and 'M2' in r['kalimat']), r['kalimat'][:70])

# ── TIDAK BERJENJANG: M1→M2 benar-benar nol ──
print('\n[2] TIDAK BERJENJANG: d (M1→M2) = 0,00 → jalur 2 harus TIDAK signifikan')
rng2 = np.random.default_rng(88)
X2 = rng2.normal(size=n)
N1 = 0.60*X2 + rng2.normal(scale=0.8, size=n)
N2 = 0.00*X2 + 0.00*N1 + rng2.normal(scale=0.8, size=n)   # tidak berhubungan
Y2 = 0.05*X2 + 0.10*N1 + 0.50*N2 + rng2.normal(scale=0.8, size=n)
d2 = pd.DataFrame({'X1': X2, 'M1': N1, 'M2': N2, 'Y1': Y2})
r2 = mediasi_berjenjang(d2, 'X1', 'M1', 'M2', 'Y1')
cek('d ≈ 0', abs(r2['d']['b']) <= TOL, f"dapat {r2['d']['b']}")
cek('jalur berjenjang TIDAK signifikan', r2['jalur'][1]['signifikan'] is False,
    f"lo={r2['jalur'][1]['lo']} hi={r2['jalur'][1]['hi']}")
cek('kalimat JUJUR menyebut tidak meneruskan', 'TIDAK' in r2['kalimat'],
    r2['kalimat'][:60])

# ── Rantai lewat hitung_kaitan (pintu gerbang) ──
print('\n[3] LEWAT hitung_kaitan: bentuk="berjenjang" harus memilih berjenjang')
h = hitung_kaitan(d, ['X1'], 'Y1', kolom_m=['M1','M2'], bentuk='berjenjang')
cek('bentuk_mediasi = berjenjang', h['bentuk_mediasi'] == 'berjenjang',
    str(h['bentuk_mediasi']))
cek('hasil mediasi pakai fungsi berjenjang',
    (h['mediasi'][0] or {}).get('berjenjang') is True)
print('\n[4] LEWAT hitung_kaitan: bentuk="paralel" (atau kosong) → paralel')
h2 = hitung_kaitan(d, ['X1'], 'Y1', kolom_m=['M1','M2'], bentuk='paralel')
cek('bentuk_mediasi = paralel', h2['bentuk_mediasi'] == 'paralel', str(h2['bentuk_mediasi']))
cek('ada 2 hasil (M1 & M2 terpisah)', len(h2['mediasi']) == 2, f"→ {len(h2['mediasi'])}")
h3 = hitung_kaitan(d, ['X1'], 'Y1', kolom_m=['M1','M2'])
cek('tanpa bentuk → aman ke paralel', h3['bentuk_mediasi'] == 'paralel', str(h3['bentuk_mediasi']))

print('\n' + '='*70)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}'); sys.exit(1)
print(' ✅ LULUS SEMUA — mediasi berjenjang terbukti benar')
sys.exit(0)
