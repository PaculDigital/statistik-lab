#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/berurutan.py (fungsi internal)
   Sebab                  : Mengukur dari fungsi INTERNAL (bangun_dari_spek langsung) = data BELUM dikalibrasi. Yang benar: ukur lewat app/berkas_kerja.py::buat_data(). Terukur: lewat internal galat 0,134; lewat buat_data galat 0,0003.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI MODEL v5 — semua model: regresi, mediasi, dual, moderasi, kombinasi.

Skrip ini BERSIH (pelajaran: uji jangan standardisasi ganda, jangan KeyError).
Prinsip: jangan klaim; UKUR.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.berurutan import (bangun_dari_spek, sk_regresi, sk_mediasi,
                                  sk_dual_mediasi_paralel, sk_mediasi_berjenjang,
                                  sk_moderasi, sk_dual_moderasi,
                                  sk_mediasi_dimoderasi)

LULUS = GAGAL = 0
TOL = 0.05


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


def skor(data, nama):
    kolom = []
    for nm in nama:
        it = data['item'][nm].astype(float)
        it = np.where(it < 0, np.nan, it)
        kolom.append(np.nanmean(it, axis=1))
    return np.column_stack(kolom)


def reg(X, y):
    """Koefisien terstandardisasi (cara SPSS/PLS membaca)."""
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1)
    yz = (y - y.mean()) / (y.std() or 1)
    A = np.column_stack([np.ones(len(Xz)), Xz])
    c, *_ = np.linalg.lstsq(A, yz, rcond=None)
    return c[1:]


def baris(label, minta, dapat, tol=TOL):
    g = dapat - minta
    tanda = 'OK' if abs(g) <= tol else 'MELESET'
    print(f'    {label:22} minta {minta:6.2f} -> {dapat:7.4f}  ({g:+.4f}) {tanda}')
    return abs(g) <= tol


print('=' * 78)
print(' 1. REGRESI LINEAR SEDERHANA (Y ~ X1)')
print('=' * 78)
for b1 in [0.35, 0.50, 0.65]:
    d = bangun_dari_spek(sk_regresi({'X1': b1}), n_resp=187, seed=42)
    S = skor(d, ['X1', 'Y'])
    h = reg(S[:, :1], S[:, 1])[0]
    cek(f'sederhana {b1:.2f}', baris('X1 -> Y', b1, h), f'galat {h-b1:+.4f}')

print()
print('=' * 78)
print(' 2. REGRESI LINEAR BERGANDA (Y ~ X1+X2+X3)')
print('=' * 78)
beta = {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}
d = bangun_dari_spek(sk_regresi(beta), n_resp=187, seed=42)
S = skor(d, ['X1', 'X2', 'X3', 'Y'])
h = reg(S[:, :3], S[:, 3])
ok = True
for i, k in enumerate(beta):
    ok = baris(f'{k} -> Y', beta[k], h[i]) and ok
cek('berganda semua jalur', ok)

print()
print('=' * 78)
print(' 3. MEDIASI TUNGGAL (X -> M -> Y)')
print('=' * 78)
d = bangun_dari_spek(sk_mediasi({'X1': 0.60}, 0.40, {'X1': 0.10}),
                     n_resp=187, seed=42)
S = skor(d, ['X1', 'M', 'Y'])
a = reg(S[:, :1], S[:, 1])[0]
bc = reg(S[:, [0, 1]], S[:, 2])
cek('a (X->M)', baris('a-path', 0.60, a))
cek("c' (X->Y)", baris("c'-path", 0.10, bc[0]))
cek('b (M->Y)', baris('b-path', 0.40, bc[1]))

print()
print('=' * 78)
print(' 4. DUAL MEDIASI PARALEL (X->M1->Y ; X->M2->Y)')
print('=' * 78)
d = bangun_dari_spek(sk_dual_mediasi_paralel('X1', 0.60, 0.50, 0.40, 0.30, 0.10),
                     n_resp=187, seed=42)
S = skor(d, ['X1', 'M1', 'M2', 'Y'])
a1 = reg(S[:, [0]], S[:, 1])[0]
a2 = reg(S[:, [0]], S[:, 2])[0]
bc = reg(S[:, [0, 1, 2]], S[:, 3])
cek('a1', baris('X->M1', 0.60, a1))
cek('a2', baris('X->M2', 0.50, a2))
cek("c'", baris("X->Y", 0.10, bc[0]))
cek('b1', baris('M1->Y', 0.40, bc[1]))
cek('b2', baris('M2->Y', 0.30, bc[2]))

print()
print('=' * 78)
print(' 5. MEDIASI BERJENJANG / SERIAL (X -> M1 -> M2 -> Y)')
print('=' * 78)
d = bangun_dari_spek(sk_mediasi_berjenjang('X1', 0.60, 0.50, 0.40, 0.10),
                     n_resp=187, seed=42)
S = skor(d, ['X1', 'M1', 'M2', 'Y'])
a1 = reg(S[:, [0]], S[:, 1])[0]
dd = reg(S[:, [1]], S[:, 2])[0]
bc = reg(S[:, [0, 2]], S[:, 3])
cek('a1', baris('X->M1', 0.60, a1))
cek('d', baris('M1->M2', 0.50, dd))
cek("c'", baris("X->Y", 0.10, bc[0]))
cek('b2', baris('M2->Y', 0.40, bc[1]))

print()
print('=' * 78)
print(' 6. MODERASI / MRA (Y ~ X + Z + X×Z)')
print('=' * 78)
d = bangun_dari_spek(sk_moderasi('X1', 'Z1', 0.40, 0.25, 0.20),
                     n_resp=187, seed=42)
S = skor(d, ['X1', 'Z1', 'Y'])
XZ = (S[:, 0] - S[:, 0].mean()) * (S[:, 1] - S[:, 1].mean())
h = reg(np.column_stack([S[:, 0], S[:, 1], XZ]), S[:, 2])
cek('X', baris('X -> Y', 0.40, h[0]))
cek('Z', baris('Z -> Y', 0.25, h[1]))
cek('XxZ', baris('X×Z', 0.20, h[2]))

print()
print('=' * 78)
print(' 7. DUAL MODERASI PARALEL (X×Z1, X×Z2)')
print('=' * 78)
d = bangun_dari_spek(sk_dual_moderasi('X1', 'Z1', 'Z2', 0.35, 0.20, 0.15, 0.25, 0.15),
                     n_resp=187, seed=42)
S = skor(d, ['X1', 'Z1', 'Z2', 'Y'])
XZ1 = (S[:, 0] - S[:, 0].mean()) * (S[:, 1] - S[:, 1].mean())
XZ2 = (S[:, 0] - S[:, 0].mean()) * (S[:, 2] - S[:, 2].mean())
h = reg(np.column_stack([S[:, 0], S[:, 1], S[:, 2], XZ1, XZ2]), S[:, 3])
cek('X', baris('X -> Y', 0.35, h[0]))
cek('Z1', baris('Z1 -> Y', 0.20, h[1]))
cek('Z2', baris('Z2 -> Y', 0.15, h[2]))
cek('XxZ1', baris('X×Z1', 0.25, h[3]))
cek('XxZ2', baris('X×Z2', 0.15, h[4]))

print()
print('=' * 78)
print(' 8. MODERATED MEDIATION (X->M->Y, jalur M->Y dimoderasi Z)')
print('=' * 78)
d = bangun_dari_spek(sk_mediasi_dimoderasi('X1', 'Z1', 0.60, 0.40, 0.25, 0.10),
                     n_resp=187, seed=42)
S = skor(d, ['X1', 'M', 'Z1', 'Y'])
MZ = (S[:, 1] - S[:, 1].mean()) * (S[:, 2] - S[:, 2].mean())
a = reg(S[:, [0]], S[:, 1])[0]
h = reg(np.column_stack([S[:, 0], S[:, 1], S[:, 2], MZ]), S[:, 3])
cek('a', baris('X->M', 0.60, a))
cek("c'", baris('X->Y', 0.10, h[0]))
cek('b', baris('M->Y', 0.40, h[1]))
cek('MxZ', baris('M×Z', 0.25, h[3]))

print()
print('=' * 78)
print(' 9. TIGA MEDIASI PARALEL')
print('=' * 78)
jalur = [{"target": "M1", "dari": {"X1": 0.55}},
         {"target": "M2", "dari": {"X1": 0.45}},
         {"target": "M3", "dari": {"X1": 0.40}},
         {"target": "Y", "dari": {"X1": 0.08, "M1": 0.35, "M2": 0.25, "M3": 0.20}}]
d = bangun_dari_spek(jalur, n_resp=250, seed=42)
S = skor(d, ['X1', 'M1', 'M2', 'M3', 'Y'])
h = reg(S[:, [0, 1, 2, 3]], S[:, 4])
cek("3med c'", baris("X->Y", 0.08, h[0]))
cek('3med b1', baris('M1->Y', 0.35, h[1]))
cek('3med b2', baris('M2->Y', 0.25, h[2]))
cek('3med b3', baris('M3->Y', 0.20, h[3]))

print()
print('=' * 78)
print(f' TOLERANSI DIPAKAI: {TOL}')
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
