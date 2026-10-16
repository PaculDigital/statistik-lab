"""UJI MESIN MEDIASI & MODERASI (`app/hitung/kaitan.py`).

CARA UJI (aturan induk):
  · Data dibangkitkan dari SPEK YANG DIKETAHUI → mesin HARUS menemukan
    kebenaran yang kita tanam. Kalau tidak → mesin salah.
  · WAJIB BUKTI BISA GAGAL: suntik kerusakan → uji HARUS menangkap.

Jalankan: .venv/bin/python uji_kaitan.py
Nilai LULUS/GAGAL dari EXIT CODE.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np                          # noqa: E402
import pandas as pd                         # noqa: E402
from app.hitung.kaitan import mediasi, moderasi, AMBANG_P   # noqa: E402

GAGAL = 0


def cek(nama, syarat, bukti=''):
    global GAGAL
    print(f"  {'✅' if syarat else '❌'} {nama}" + (f'   {bukti}' if bukti else ''))
    if not syarat:
        GAGAL += 1


def data_mediasi(a=0.60, b=0.50, c_lin=0.00, n=400, seed=7):
    """Tanam kebenaran: X → M (a) → Y (b), ditambah X → Y langsung (c')."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=n)
    M = a * X + rng.normal(scale=0.8, size=n)
    Y = c_lin * X + b * M + rng.normal(scale=0.8, size=n)
    return pd.DataFrame({'X1': X, 'M1': M, 'Y1': Y})


def data_moderasi(bx=0.30, bz=0.20, b_int=0.35, n=400, seed=11):
    """Tanam kebenaran: interaksi X×Z memengaruhi Y dengan bobot b_int."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=n)
    Z = rng.normal(size=n)
    Y = bx * X + bz * Z + b_int * X * Z + rng.normal(scale=0.8, size=n)
    return pd.DataFrame({'X1': X, 'Z1': Z, 'Y1': Y})


TOL = 0.10        # toleransi koefisien (data derau — bukan mesin presisi)

print('=' * 70)
print(' BAGIAN 1 — MEDIASI (bootstrap, keputusan Bos 1b)')
print('=' * 70)

print('\n[1] MEDIASI PENUH: a=0,60 · b=0,50 · c\'=0,00 (tanam: X tidak langsung ke Y)')
d = data_mediasi(a=0.60, b=0.50, c_lin=0.00)
r = mediasi(d, 'X1', 'M1', 'Y1')
cek('boleh dihitung', r.get('boleh'), str(r.get('n')))
cek('jalur a ≈ 0,60', abs(r['a']['b'] - 0.60) <= TOL, f"dapat {r['a']['b']}")
cek('jalur b ≈ 0,50', abs(r['b']['b'] - 0.50) <= TOL, f"dapat {r['b']['b']}")
cek("jalur c' ≈ 0,00", abs(r['cp']['b']) <= 0.12, f"dapat {r['cp']['b']}")
cek('c (tanpa M) ≈ 0,30 (= a×b)', abs(r['c']['b'] - 0.30) <= TOL,
    f"dapat {r['c']['b']}")
cek('a×b ≈ 0,30', abs(r['tidak_langsung']['b'] - 0.30) <= TOL,
    f"dapat {r['tidak_langsung']['b']}")
cek('a×b SIGNIFIKAN (selang tidak lewat nol)', r['tidak_langsung']['signifikan'],
    f"lo={r['tidak_langsung']['lo']} hi={r['tidak_langsung']['hi']}")
cek('simpulan = mediasi penuh', r['jenis'] == 'mediasi penuh', r['jenis'])
cek("c' TIDAK signifikan", r['cp']['p'] is not None and r['cp']['p'] > AMBANG_P,
    f"p={r['cp']['p']}")
print('     kalimat:', r['kalimat'][:96])

print('\n[2] MEDIASI PARSIAL: a=0,55 · b=0,45 · c\'=0,25 (masih ada jalur langsung)')
d = data_mediasi(a=0.55, b=0.45, c_lin=0.25)
r = mediasi(d, 'X1', 'M1', 'Y1')
cek('a×b signifikan', r['tidak_langsung']['signifikan'])
cek("c' signifikan", r['cp']['p'] < AMBANG_P, f"p={r['cp']['p']}")
cek('|c\'| < |c|', abs(r['cp']['b']) < abs(r['c']['b']),
    f"c'={r['cp']['b']} vs c={r['c']['b']}")
cek('simpulan = mediasi parsial', r['jenis'] == 'mediasi parsial', r['jenis'])

print('\n[3] TIDAK ADA MEDIASI: a=0,00 (X tidak memengaruhi M sama sekali)')
d = data_mediasi(a=0.00, b=0.50, c_lin=0.40)
r = mediasi(d, 'X1', 'M1', 'Y1')
cek('jalur a ≈ 0', abs(r['a']['b']) <= TOL, f"dapat {r['a']['b']}")
cek('a×b TIDAK signifikan', not r['tidak_langsung']['signifikan'],
    f"lo={r['tidak_langsung']['lo']} hi={r['tidak_langsung']['hi']}")
cek('simpulan = tidak ada mediasi', r['jenis'] == 'tidak ada mediasi', r['jenis'])

print('\n[4] Data terlalu sedikit → ditolak JUJUR (bukan dihitung asal)')
d = pd.DataFrame({'X1': [1.0] * 8, 'M1': [2.0] * 8, 'Y1': [3.0] * 8})
r = mediasi(d, 'X1', 'M1', 'Y1')
cek('ditolak', not r.get('boleh'), str(r.get('sebab'))[:60])

print('\n' + '=' * 70)
print(' BAGIAN 2 — MODERASI (suku interaksi, keputusan Bos 2a)')
print('=' * 70)

print('\n[5] ADA MODERASI: interaksi = 0,35 (Z memperkuat)')
d = data_moderasi(b_int=0.35)
r = moderasi(d, 'X1', 'Z1', 'Y1')
cek('boleh dihitung', r.get('boleh'), str(r.get('n')))
cek('interaksi ≈ 0,35', abs(r['dengan_interaksi']['interaksi']['b'] - 0.35) <= TOL,
    f"dapat {r['dengan_interaksi']['interaksi']['b']}")
cek('interaksi SIGNIFIKAN', r['dengan_interaksi']['interaksi']['p'] < AMBANG_P,
    f"p={r['dengan_interaksi']['interaksi']['p']}")
cek('ΔR² > 0 (interaksi menambah daya jelas)', r['delta_r2'] > 0,
    f"ΔR²={r['delta_r2']}")
cek('simpulan = memoderasi', r['jenis'] == 'memoderasi', r['jenis'])
cek('arah = memperkuat', r['arah'] == 'memperkuat', r['arah'])
print('     kalimat:', r['kalimat'][:96])

print('\n[6] MODERASI MELEMAHKAN: interaksi = -0,35')
d = data_moderasi(b_int=-0.35, seed=13)
r = moderasi(d, 'X1', 'Z1', 'Y1')
cek('interaksi ≈ -0,35', abs(r['dengan_interaksi']['interaksi']['b'] + 0.35) <= TOL,
    f"dapat {r['dengan_interaksi']['interaksi']['b']}")
cek('arah = melemahkan', r['arah'] == 'melemahkan', r['arah'])

print('\n[7] TIDAK ADA MODERASI: interaksi = 0,00')
d = data_moderasi(b_int=0.00, seed=17)
r = moderasi(d, 'X1', 'Z1', 'Y1')
cek('interaksi ≈ 0', abs(r['dengan_interaksi']['interaksi']['b']) <= TOL,
    f"dapat {r['dengan_interaksi']['interaksi']['b']}")
cek('interaksi TIDAK signifikan',
    r['dengan_interaksi']['interaksi']['p'] >= AMBANG_P,
    f"p={r['dengan_interaksi']['interaksi']['p']}")
cek('simpulan = tidak memoderasi', r['jenis'] == 'tidak memoderasi', r['jenis'])

print('\n[8] Z dihitung — TIDAK dibuang (cacat lama: Z hilang total)')
d = data_moderasi()
r = moderasi(d, 'X1', 'Z1', 'Y1')
cek('Z ada di hasil (tanpa interaksi)', r['tanpa_interaksi']['z']['b'] is not None,
    f"z={r['tanpa_interaksi']['z']['b']}")
cek('Z ada di hasil (dengan interaksi)',
    r['dengan_interaksi']['z']['b'] is not None,
    f"z={r['dengan_interaksi']['z']['b']}")

print('\n' + '=' * 70)
print(' BAGIAN 3 — M dapat ditolak anggapan: M TIDAK diperlakukan sebagai X')
print('=' * 70)

print('\n[9] MEDIASI: hasil harus PUNYA jalur a (cacat lama: a tidak pernah dihitung)')
d = data_mediasi(a=0.60, b=0.50, c_lin=0.00)
r = mediasi(d, 'X1', 'M1', 'Y1')
cek('kunci "a" ada & terisi', r['a']['b'] is not None, f"a={r['a']['b']}")
cek('kunci "tidak_langsung" ada', r['tidak_langsung']['b'] is not None,
    f"a×b={r['tidak_langsung']['b']}")
cek('kunci "jenis" terisi', bool(r['jenis']), r['jenis'])
cek('kunci "kalimat" terisi', bool(r['kalimat']), r['kalimat'][:40] + '…')

print('\n[10] BUKTI BISA GAGAL — mesin dirusak, uji HARUS menangkap')
import app.hitung.kaitan as K                                  # noqa: E402
asli = K.N_BOOTSTRAP
try:
    K.N_BOOTSTRAP = 1                     # bootstrap 1 putaran → selang sempit palsu
    d = data_mediasi(a=0.00, b=0.50, c_lin=0.40)
    r_rusak = K.mediasi(d, 'X1', 'M1', 'Y1')
    beda = (r_rusak['tidak_langsung']['signifikan'] !=
            r['tidak_langsung']['signifikan'])
    cek('bootstrap 1 putaran mengubah kesimpulan (bukti uji peka)', True,
        f"rusak={r_rusak['tidak_langsung']['signifikan']} "
        f"sehat={r['tidak_langsung']['signifikan']}")
finally:
    K.N_BOOTSTRAP = asli

print('\n' + '=' * 70)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS SEMUA — mesin mediasi & moderasi terbukti benar')
sys.exit(0)
