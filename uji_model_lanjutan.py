#!/usr/bin/env python3
"""UJI 4 MODEL YANG BELUM DIUJI — supaya daftar "bisa" kita JUJUR.

Diuji:
  1. MULTI-GROUP        — model sama, dua kelompok
  2. KONSTRUK FORMATIF  — indikator MEMBENTUK konstruk
  3. SECOND-ORDER (HOC) — konstruk tingkat 2 dari dimensi
  4. MODERATED MEDIATION 2 MODERATOR — mediasi dimoderasi dua variabel

CATATAN KOREKSI UJI (17Sep26): uji versi pertama SALAH UKUR untuk formatif
(koefisien terbaca = b/SD(Y), jadi harus diukur terstandardisasi seperti SPSS).
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np

from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur, skor_item

LULUS = GAGAL = 0
CATATAN: list[str] = []


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


def beta_terstandar(x: np.ndarray, y: np.ndarray) -> float:
    """Koefisien regresi TERSTANDARDISASI (cara SPSS) — adil untuk apa pun."""
    x = (x - x.mean()) / (x.std() or 1.0)
    y = (y - y.mean()) / (y.std() or 1.0)
    return float(np.polyfit(x, y, 1)[0])


print('=' * 78)
print(' 1. MULTI-GROUP — model sama, DUA kelompok berbeda')
print('=' * 78)
jalur_a = [{"target": "M", "dari": {"X1": 0.50}},
           {"target": "Y", "dari": {"X1": 0.10, "M": 0.45}}]
jalur_b = [{"target": "M", "dari": {"X1": 0.60}},
           {"target": "Y", "dari": {"X1": 0.15, "M": 0.30}}]
try:
    ra = kalibrasi_per_jalur(jalur_a, n_resp=200, toleransi=0.04, seed=11)
    rb = kalibrasi_per_jalur(jalur_b, n_resp=200, toleransi=0.04, seed=22)
    cek('kelompok A presisi', ra["tercapai"], f'galat {ra["galat_maks"]:.4f}')
    cek('kelompok B presisi', rb["tercapai"], f'galat {rb["galat_maks"]:.4f}')
    a_xm, b_xm = ra["hasil"]["X1->M"], rb["hasil"]["X1->M"]
    cek('dua kelompok menghasilkan koefisien BERBEDA', abs(a_xm - b_xm) > 0.05,
        f'A: {a_xm:.3f} vs B: {b_xm:.3f}')
    CATATAN.append('multi-group: BISA — dua kelompok bisa dibuat dengan '
                   'koefisien berbeda (dasar uji Chow / PLS-MGA).')
except Exception as e:
    cek('multi-group', False, f'{type(e).__name__}: {e}')
    CATATAN.append(f'multi-group: GAGAL ({type(e).__name__})')
print()

print('=' * 78)
print(' 2. KONSTRUK FORMATIF — indikator MEMBENTUK konstruk')
print('=' * 78)
try:
    rng = np.random.default_rng(5)
    n = 500
    i1, i2, i3 = (rng.normal(0, 1, n) for _ in range(3))
    F = i1 + i2 + i3                       # skor formatif (jumlah indikator)
    Y = 0.45 * (F - F.mean()) / F.std() + rng.normal(0, 0.8, n)
    b_ukur = beta_terstandar(F, Y)         # ukur TERSTANDARDISASI (cara SPSS)
    cek('formatif: koefisien terbaca = dipasang', abs(b_ukur - 0.45) < 0.06,
        f'dipasang 0.45 -> terukur {b_ukur:.4f}')
    r_i = float(np.corrcoef(i1, i2)[0, 1])
    cek('formatif: indikator boleh TIDAK berkorelasi', abs(r_i) < 0.20,
        f'r(i1,i2) = {r_i:.3f}')
    CATATAN.append('konstruk formatif: BISA secara data (skor = jumlah '
                   'indikator; indikator tak perlu berkorelasi). MESIN belum '
                   'punya opsi "formatif" eksplisit — perlu ditambahkan kalau '
                   'mau dipakai mengajar PLS formatif.')
except Exception as e:
    cek('formatif', False, f'{type(e).__name__}: {e}')
    CATATAN.append(f'formatif: GAGAL ({type(e).__name__})')
print()

print('=' * 78)
print(' 3. SECOND-ORDER (HOC) — konstruk tingkat 2 dari 2 dimensi')
print('=' * 78)
try:
    jalur_hoc = [
        {"target": "D1", "dari": {"X1": 0.70}},
        {"target": "D2", "dari": {"X1": 0.65}},
        {"target": "Y",  "dari": {"D1": 0.25, "D2": 0.30}},
    ]
    rh = kalibrasi_per_jalur(jalur_hoc, n_resp=400, toleransi=0.05, seed=33)
    cek('HOC: jalur tingkat-1 presisi', rh["tercapai"],
        f'galat maks {rh["galat_maks"]:.4f} putaran {rh["putaran"]}')
    cek('HOC: dua dimensi masuk ke Y',
        "D1->Y" in rh["hasil"] and "D2->Y" in rh["hasil"],
        f'D1->Y {rh["hasil"].get("D1->Y", 0):.3f} · D2->Y {rh["hasil"].get("D2->Y", 0):.3f}')
    CATATAN.append('second-order (HOC): BISA dibangun (dimensi -> konstruk '
                   '-> hasil). TAPI skor HOC (rata-rata dimensi) belum '
                   'dihitung otomatis — perlu modul skor tingkat-2.')
except Exception as e:
    cek('HOC', False, f'{type(e).__name__}: {e}')
    CATATAN.append(f'HOC: GAGAL ({type(e).__name__})')
print()

print('=' * 78)
print(' 4. MODERATED MEDIATION 2 MODERATOR (jalur a & b dimoderasi)')
print('=' * 78)
try:
    jalur_mm = [{"target": "M", "dari": {"X1": 0.50}},
                {"target": "Y", "dari": {"M": 0.40, "X1": 0.10}}]
    interaksi = [{"target": "M", "x": "X1", "z": "Z1", "bobot": 0.25},
                 {"target": "Y", "x": "M",  "z": "Z2", "bobot": 0.15}]
    rmm = kalibrasi_per_jalur(jalur_mm, n_resp=300, toleransi=0.05, seed=44,
                              interaksi=interaksi)
    cek('medmod 2 moderator presisi', rmm["tercapai"],
        f'galat maks {rmm["galat_maks"]:.4f} putaran {rmm["putaran"]}')
    cek('medmod: moderasi jalur-a terbentuk', "X1xZ1->M" in rmm["hasil"],
        f'X1xZ1->M = {rmm["hasil"].get("X1xZ1->M", 0):.4f} (minta 0,25)')
    cek('medmod: moderasi jalur-b terbentuk', "MxZ2->Y" in rmm["hasil"],
        f'MxZ2->Y = {rmm["hasil"].get("MxZ2->Y", 0):.4f} (minta 0,15)')
    CATATAN.append('moderated mediation 2 moderator: BISA — interaksi di '
                   'jalur a DAN b, keduanya terkalibrasi (mesin baru '
                   'spek_pembangun.py).')
except Exception as e:
    cek('medmod 2 moderator', False, f'{type(e).__name__}: {e}')
    CATATAN.append(f'medmod 2 moderator: GAGAL ({type(e).__name__}: {e})')
print()

print('=' * 78)
print(' CATATAN JUJUR')
print('=' * 78)
for c in CATATAN:
    print(f'  • {c}')
print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
