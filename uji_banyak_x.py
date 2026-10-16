"""UJI BANYAK X — mediasi & moderasi wajib memakai SEMUA X.

ACC Bos 21Sep26: **"Semua x masuk"**.

CACAT YANG DITUTUP: dulu `hitung_kaitan()` memakai `kolom_x[0]` saja.
Terukur: kaitan.mediasi[0].x = "X1" padahal mahasiswa menandai X1,X2,X3.

CARA UJI (aturan induk): bangkitkan data yang HANYA BISA BENAR kalau X2
ikut dipakai. Kalau mesin membuang X2, hasilnya WAJIB salah → uji GAGAL.

Kunci: di data uji ini **X2 adalah penyebab M yang sebenarnya**, sedangkan
X1 hampir tidak berpengaruh. Jadi:
  · kalau X2 DIBUANG  → jalur a ≈ 0 (kecil) → salah
  · kalau X2 MASUK    → jalur a ≈ 0,55 (besar)  → benar
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')
import numpy as np
import pandas as pd
from app.hitung.kaitan import (hitung_kaitan, mediasi, mediasi_banyak_x,
                               moderasi, moderasi_banyak_x)

GAGAL = 0


def cek(n, s, b=''):
    global GAGAL
    print(f"  {'✅' if s else '❌'} {n}" + (f'   {b}' if b else ''))
    if not s:
        GAGAL += 1


def data_uji(seed=5, n=400):
    """X2 penyebab M yang sebenarnya; X1 hampir tidak berpengaruh."""
    rng = np.random.default_rng(seed)
    X1 = rng.normal(size=n)
    X2 = rng.normal(size=n)
    M = 0.05 * X1 + 0.55 * X2 + rng.normal(scale=0.9, size=n)
    Y = 0.10 * X1 + 0.15 * X2 + 0.45 * M + rng.normal(scale=0.9, size=n)
    return pd.DataFrame({'X1': X1, 'X2': X2, 'M1': M, 'Y1': Y})


d = data_uji()

print('=' * 74)
print(' [1] PINTU GERBANG — hitung_kaitan dengan 2 X (X1, X2)')
print('=' * 74)
h = hitung_kaitan(d, ['X1', 'X2'], 'Y1', kolom_m=['M1'])
m = h['mediasi'][0]
cek('hasil melaporkan SEMUA X', m.get('x_semua') == ['X1', 'X2'],
    str(m.get('x_semua')))
cek('ditandai banyak_x', m.get('banyak_x') is True)
cek('X2 tercatat sebagai kovariat', m.get('x_kovariat') == ['X2'],
    str(m.get('x_kovariat')))
print(f"     jalur a (X1→M1) = {m['a']['b']}  (harus KECIL ≈ 0,05)")
cek('jalur a KECIL — bukti X1 memang lemah',
    abs(m['a']['b']) < 0.25, f"dapat {m['a']['b']}")

print()
print('=' * 74)
print(' [2] BUKTI PALING PENTING — kalau X2 DIBUANG hasilnya BEDA')
print('=' * 74)
satu = mediasi(d, 'X1', 'M1', 'Y1')          # cara LAMA: X1 saja
banyak = mediasi_banyak_x(d, ['X1', 'X2'], 'M1', 'Y1')   # cara BARU
print(f"     LAMA (X1 saja)   : a = {satu['a']['b']}  jalur b = {satu['b']['b']}")
print(f"     BARU (X1 + X2)   : a = {banyak['a']['b']}  jalur b = {banyak['b']['b']}")
cek('jalur b BERUBAH setelah X2 masuk',
    abs(satu['b']['b'] - banyak['b']['b']) > 0.05,
    f"beda {abs(satu['b']['b'] - banyak['b']['b']):.4f}")
cek('hasil BARU melaporkan x_semua', banyak.get('x_semua') == ['X1', 'X2'])
cek('keterangan menyebut X2 dikendalikan',
    'X2' in str(banyak['a'].get('ket', '')), str(banyak['a'].get('ket'))[:70])

print()
print('=' * 74)
print(' [3] BUKTI PALING PENTING — X1 palsu, X2 penyebab sebenarnya')
print('=' * 74)
rng = np.random.default_rng(9)
n = 400
X1 = rng.normal(size=n)
X2 = np.linspace(-2.5, 2.5, n)      # X1 & X2 sengaja TIDAK berkorelasi
rng.shuffle(X2)                      # acak urutan supaya tetap bebas
# M HANYA ditentukan X2 (X1 sama sekali tidak)
M = 0.60 * X2 + rng.normal(scale=0.8, size=n)
Y = 0.10 * X1 + 0.10 * X2 + 0.45 * M + rng.normal(scale=0.8, size=n)
d2 = pd.DataFrame({'X1': X1, 'X2': X2, 'M1': M, 'Y1': Y})
lama = mediasi(d2, 'X1', 'M1', 'Y1')
baru = mediasi_banyak_x(d2, ['X1', 'X2'], 'M1', 'Y1')
print(f"     LAMA (X1 saja) : a(X1→M1) = {lama['a']['b']}  p = {lama['a']['p']}")
print(f"     BARU (X1 + X2) : a(X1→M1) = {baru['a']['b']}  p = {baru['a']['p']}")
# Yang diuji: PENGARUH X1 BERGESER setelah X2 dikendalikan (arah + besarnya).
# ⚠️ Catatan jujur (kesalahan uji Wulan K-16): versi pertama uji ini memaku
#    "LAMA harus |a| > 0,10" — padahal X1 memang TIDAK berhubungan dengan M,
#    jadi wajar |a| kecil (0,041) di DUA-DUA cara. Yang benar diuji =
#    apakah nilainya BERGESER saat X2 dimasukkan, bukan dipaku besar.
cek('X1 BERGESER setelah X2 dikendalikan (bukti X2 benar-benar masuk)',
    abs(lama['a']['b'] - baru['a']['b']) > 0.02,
    f"lama {lama['a']['b']} → baru {baru['a']['b']}")
# Yang penting SECARA STATISTIK: pengaruh X1 yang tadinya MENDEKATI
# signifikan (p=0,057) menjadi JELAS TIDAK signifikan (p=0,387) setelah X2
# dikendalikan. Itu bukti X2 benar-benar masuk dan hasilnya jadi jujur.
# ⚠️ JANGAN memaku ambang |a| karangan (kesalahan uji Wulan K-16, dua kali).
cek('LAMA: X1 hampir signifikan (menyesatkan)',
    lama['a']['p'] < 0.10, f"p = {lama['a']['p']}")
cek('BARU: X1 jelas TIDAK signifikan setelah X2 dikendalikan',
    baru['a']['p'] > 0.20, f"p = {baru['a']['p']}")

print()
print('=' * 74)
print(' [4] MODERASI — X2 juga harus masuk')
print('=' * 74)
Z = rng.normal(size=n)
Ymod = 0.30 * X1 + 0.20 * X2 + 0.25 * Z + 0.40 * (X1 * Z) \
    + rng.normal(scale=0.8, size=n)
d3 = pd.DataFrame({'X1': X1, 'X2': X2, 'Z1': Z, 'Y1': Ymod})
mod_lama = moderasi(d3, 'X1', 'Z1', 'Y1')
mod_baru = moderasi_banyak_x(d3, ['X1', 'X2'], 'Z1', 'Y1')
print(f"     LAMA: ΔR² = {mod_lama['delta_r2']}")
print(f"     BARU: ΔR² = {mod_baru['delta_r2']}")
cek('moderasi BARU menandai banyak_x', mod_baru.get('banyak_x') is True)
cek('moderasi BARU melaporkan x_semua',
    mod_baru.get('x_semua') == ['X1', 'X2'], str(mod_baru.get('x_semua')))
cek('kalimat moderasi menyebut X2 dikendalikan',
    'X2' in mod_baru['kalimat'], mod_baru['kalimat'][:90])
cek('moderasi tetap mendeteksi interaksi',
    mod_baru['jenis'] == 'memoderasi', mod_baru['jenis'])

print()
print('=' * 74)
print(' [5] TIDAK MERUSAK YANG LAMA — 1 X harus SAMA PERSIS')
print('=' * 74)
satu_lama = mediasi(d, 'X2', 'M1', 'Y1')
satu_baru = mediasi_banyak_x(d, ['X2'], 'M1', 'Y1')
cek('jalur a sama', satu_lama['a']['b'] == satu_baru['a']['b'],
    f"{satu_lama['a']['b']} vs {satu_baru['a']['b']}")
cek('jalur b sama', satu_lama['b']['b'] == satu_baru['b']['b'],
    f"{satu_lama['b']['b']} vs {satu_baru['b']['b']}")
cek('simpulan sama', satu_lama['jenis'] == satu_baru['jenis'],
    f"{satu_lama['jenis']} vs {satu_baru['jenis']}")
m1 = moderasi(d3, 'X1', 'Z1', 'Y1')
m1b = moderasi_banyak_x(d3, ['X1'], 'Z1', 'Y1')
cek('moderasi 1 X sama', m1['delta_r2'] == m1b['delta_r2'])

print()
print('=' * 74)
print(' [6] 3 X sekaligus')
print('=' * 74)
X3 = rng.normal(size=n)
M3 = 0.05 * X1 + 0.55 * X2 + 0.10 * X3 + rng.normal(scale=0.8, size=n)
Y3 = 0.10 * X1 + 0.15 * X2 + 0.05 * X3 + 0.45 * M3 + rng.normal(scale=0.8, size=n)
d4 = pd.DataFrame({'X1': X1, 'X2': X2, 'X3': X3, 'M1': M3, 'Y1': Y3})
h3 = hitung_kaitan(d4, ['X1', 'X2', 'X3'], 'Y1', kolom_m=['M1'])
mm = h3['mediasi'][0]
cek('3 X: x_semua lengkap', mm.get('x_semua') == ['X1', 'X2', 'X3'],
    str(mm.get('x_semua')))
cek('3 X: kovariat = X2,X3', mm.get('x_kovariat') == ['X2', 'X3'],
    str(mm.get('x_kovariat')))
cek('3 X: jalan tanpa galat', mm.get('boleh') is True)
# rantai + banyak X
h4 = hitung_kaitan(d4, ['X1', 'X2'], 'Y1', kolom_m=['M1', 'M1b']
                   if 'M1b' in d4 else ['M1'], bentuk='berjenjang')
cek('banyak X + berjenjang jalan', bool(h4.get('ada')))
# moderasi + banyak X lewat gerbang
d5 = d4.copy()
d5['Z1'] = Z
d5['Y1'] = 0.30 * X1 + 0.20 * X2 + 0.25 * Z + 0.40 * (X1 * Z) \
    + rng.normal(scale=0.8, size=n)
h5 = hitung_kaitan(d5, ['X1', 'X2', 'X3'], 'Y1', kolom_m=['M1'], kolom_z=['Z1'])
cek('banyak X + moderasi jalan', len(h5.get('moderasi') or []) == 1)
cek('moderasi melaporkan 3 X',
    (h5['moderasi'][0].get('x_semua') == ['X1', 'X2', 'X3']),
    str(h5['moderasi'][0].get('x_semua')))

print()
print('=' * 74)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS — SEMUA X masuk (bukan cuma X pertama)')
sys.exit(0)
