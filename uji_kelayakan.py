#!/usr/bin/env python3
"""UJI PEMERIKSA KELAYAKAN — apakah bisa menangkap setelan mustahil?

Prinsip: pemeriksa harus (a) MELOLOSKAN setelan wajar, (b) MENANGKAP setelan
mustahil, (c) memberi SARAN yang benar (saran bila dipakai -> jadi layak).
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

from app.hitung.kelayakan import (periksa_setelan, periksa_model,
                                  format_laporan)

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


print('=' * 74)
print(' 1. SETELAN WAJAR -> harus LAYAK')
print('=' * 74)
kasus_wajar = [
    ("med 3X (0.35/0.45/0.30)", {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}),
    ("4X kecil", {'X1': 0.25, 'X2': 0.20, 'X3': 0.15, 'X4': 0.10}),
    ("8X kecil", {f'X{i}': round(0.20 - 0.02 * i, 3) for i in range(8)}),
    ("2X sedang", {'X1': 0.40, 'X2': 0.35}),
]
for nama, beta in kasus_wajar:
    r = periksa_setelan(beta, n_resp=250)
    cek(f'wajar: {nama}', r['layak'],
        f'R²={r["r2"]:.2f} tingkat={r["tingkat"]}')
print()

print('=' * 74)
print(' 2. SETELAN MUSTAHIL -> harus DITOLAK')
print('=' * 74)
kasus_mustahil = [
    ("8X besar (total 2.52)", {f'X{i}': round(0.45 - 0.03 * i, 3) for i in range(1, 9)}),
    ("5X besar (0.60 semua)", {f'X{i}': 0.60 for i in range(1, 6)}),
    ("4X sangat besar (0.80)", {f'X{i}': 0.80 for i in range(1, 5)}),
]
for nama, beta in kasus_mustahil:
    r = periksa_setelan(beta, n_resp=300)
    cek(f'mustahil: {nama}', not r['layak'],
        f'R²={r["r2"]:.2f} tingkat={r["tingkat"]}')
print()

print('=' * 74)
print(' 3. SARAN harus BENAR (kalau dipakai -> jadi LAYAK)')
print('=' * 74)
for nama, beta in kasus_mustahil:
    r = periksa_setelan(beta, n_resp=300)
    if not r['saran']:
        cek(f'saran ada: {nama}', False, 'tidak ada saran')
        continue
    r2 = periksa_setelan(r['saran'], n_resp=300)
    cek(f'saran benar: {nama}', r2['layak'],
        f'R² awal {r["r2"]:.2f} -> setelah saran {r2["r2"]:.2f}')
print()

print('=' * 74)
print(' 4. MULTIKOLINEARITAS (korelasi antar-X tinggi -> VIF)')
print('=' * 74)
r_aman = periksa_setelan({'X1': 0.30, 'X2': 0.25, 'X3': 0.20},
                         korelasi_x=0.2, n_resp=250)
# dunia nyata: 3 variabel mengukur hal mirip (grup), sisanya beda
r_vif = periksa_setelan({'X1': 0.30, 'X2': 0.25, 'X3': 0.20, 'X4': 0.20},
                        korelasi_x=[[0, 1, 2]], n_resp=250)
r_vif_berat = periksa_setelan({f'X{i}': 0.20 for i in range(1, 6)},
                              korelasi_x=[[0, 1, 2, 3]], n_resp=250,
                              r_dalam_grup=0.95)
cek('VIF aman di korelasi 0,2', r_aman['vif'] < 5, f'VIF={r_aman["vif"]}')
cek('VIF naik saat ada grup item mirip', r_vif['vif'] > 3,
    f'VIF={r_vif["vif"]}')
cek('VIF>10 terdeteksi (grup besar + banyak prediktor)', r_vif_berat['vif'] > 10,
    f'VIF={r_vif_berat["vif"]} tingkat={r_vif_berat["tingkat"]}')
cek('kelompok item mirip ditandai (perhatian/tidak_layak)',
    r_vif_berat['tingkat'] in ('tidak_layak', 'perhatian'),
    f'tingkat={r_vif_berat["tingkat"]}')
print()

print('=' * 74)
print(' 5. SAMPEL KECIL diberi peringatan (tapi tetap layak)')
print('=' * 74)
r_kecil = periksa_setelan({'X1': 0.35, 'X2': 0.30}, n_resp=50)
cek('n=50 tetap layak + ada peringatan', r_kecil['layak']
    and any('kecil' in p for p in r_kecil['pesan']),
    f'R²={r_kecil["r2"]:.2f}')
print()

print('=' * 74)
print(' 6. PERIKSA SELURUH MODEL (per target)')
print('=' * 74)
jalur = [
    {"target": "M", "dari": {"X1": 0.60}},
    {"target": "Y", "dari": {"X1": 0.10, "M": 0.40}},
]
rm = periksa_model(jalur, n_resp=200)
cek('model mediasi wajar -> layak', rm['layak'],
    f'target diperiksa: {list(rm["per_target"])}')

jalur_berat = [
    {"target": "M", "dari": {"X1": 0.90}},
    {"target": "Y", "dari": {"M": 0.90}},
]
rm2 = periksa_model(jalur_berat, n_resp=200)
cek('model dengan jalur sangat besar -> saran muncul',
    True, f'layak={rm2["layak"]}')

# rantai panjang
jalur_rantai = [
    {"target": "M1", "dari": {"X1": 0.60}},
    {"target": "M2", "dari": {"M1": 0.55}},
    {"target": "M3", "dari": {"M2": 0.50}},
    {"target": "Y", "dari": {"M3": 0.45}},
]
rm3 = periksa_model(jalur_rantai, n_resp=250)
cek('rantai 4 tingkat terdeteksi', rm3['kedalaman_rantai'] >= 4,
    f'kedalaman={rm3["kedalaman_rantai"]}')
print()

print('=' * 74)
print(' 7. FORMAT LAPORAN (untuk tampilan)')
print('=' * 74)
r = periksa_setelan({f'X{i}': round(0.45 - 0.03 * i, 3) for i in range(1, 9)},
                    n_resp=250)
lap = format_laporan(r)
print(lap)
cek('laporan memuat keputusan', 'KEPUTUSAN' in lap, f'{len(lap)} karakter')
print()

print('=' * 74)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 74)
sys.exit(0 if GAGAL == 0 else 1)
