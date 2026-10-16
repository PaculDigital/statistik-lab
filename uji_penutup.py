#!/usr/bin/env python3
"""UJI LENGKAP — dua mode (Presisi & Natural) pada model jurnal Bos
dan pada sampel kecil (50/100/150/200) yang sering dipakai mahasiswa S1.

Ini uji PENUTUP: membuktikan mesin selesai & menjawab pertanyaan Bos.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.kalibrasi_jalur import (bangun_dengan_mode, kalibrasi_per_jalur,
                                        ukur_jalur)

LULUS = GAGAL = 0
SE, M1, M2, M3 = 'SelfEfficacy', 'Mastery', 'PerfApproach', 'PerfAvoid'
PA, DC, DS = 'PosAffect', 'DecConf', 'DecSatis'
Y1, Y2 = 'Loyalty', 'Switching'

JALUR = [
    {"target": M1, "dari": {SE: 0.45}},
    {"target": M2, "dari": {SE: 0.35}},
    {"target": M3, "dari": {SE: 0.10}},
    {"target": PA, "dari": {M1: 0.35, M2: 0.20, M3: -0.15}},
    {"target": DC, "dari": {M1: 0.30, M2: 0.25, M3: -0.20}},
    {"target": DS, "dari": {PA: 0.40, DC: 0.35}},
    {"target": Y1, "dari": {DS: 0.50}},
    {"target": Y2, "dari": {DS: -0.30}},
]
MINTA = {}
for j in JALUR:
    for s, v in j["dari"].items():
        MINTA[f'{s}->{j["target"]}'] = v


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


print('=' * 78)
print(' 1. MODE PRESISI — MODEL JURNAL BOS (n=250)')
print('=' * 78)
r = kalibrasi_per_jalur(JALUR, n_resp=250, toleransi=0.04, seed=42)
print(f'  putaran {r["putaran"]} | galat maks {r["galat_maks"]} | tercapai {r["tercapai"]}')
for k, v in r["hasil"].items():
    g = r["galat"][k]
    print(f'    {k:30} minta {MINTA[k]:6.2f} -> {v:7.4f}  ({g:+.4f})')
cek('presisi: semua jalur <= 0,04', r["tercapai"], f'galat maks {r["galat_maks"]}')
print()

print('=' * 78)
print(' 2. MODE NATURAL — MODEL JURNAL BOS (n=250)')
print('=' * 78)
rn = bangun_dengan_mode("natural", jalur=JALUR, n_resp=250, seed=42)
S = None
d = rn["data"]
nama_semua = [SE, M1, M2, M3, PA, DC, DS, Y1, Y2]
kolom = []
for nm in nama_semua:
    it = d["item"][nm].astype(float)
    it = np.where(it < 0, np.nan, it)
    kolom.append(np.nanmean(it, axis=1))
S = np.column_stack(kolom)
idx = {nm: i for i, nm in enumerate(nama_semua)}
gal = []
for k, mi in MINTA.items():
    s, t = k.split('->')
    # ukur dengan sumber lain di target yang sama juga dimasukkan
    sumber = [x for x in MINTA if x.endswith('->' + t)]
    sumber = [x.split('->')[0] for x in sumber]
    h = ukur_jalur(d, t, sumber)
    got = h[sumber.index(s)]
    gal.append(abs(got - mi))
    print(f'    {k:30} minta {mi:6.2f} -> {got:7.4f}  ({got-mi:+.4f})')
print(f'  galat maks natural = {max(gal):.4f}')
print()
print('  ⚠ CATATAN JUJUR: Mode Natural TIDAK dikalibrasi — memang bervariasi.')
print('    Gunanya justru itu: mengajar GALAT PENSAMPELAN & bahwa hasil')
print('    lapangan tak pernah sama dengan harapan peneliti.')
print('    Untuk angka yang harus tepat -> pakai Mode Presisi.')
# Mode Natural diuji: (a) arah SEMUA jalur benar, (b) galat < 0,50.
arah_benar = True
for k, mi in MINTA.items():
    s, t = k.split('->')
    sumber = [x.split('->')[0] for x in MINTA if x.endswith('->' + t)]
    h = ukur_jalur(d, t, sumber)
    got = h[sumber.index(s)]
    if (mi > 0) != (got > 0):
        arah_benar = False
cek('natural: arah semua jalur benar', arah_benar, 'positif tetap positif')
cek('natural: galat < 0,50 (wajar tanpa kalibrasi)', max(gal) < 0.50,
    f'{max(gal):.4f}')
print()

print('=' * 78)
print(' 3. SAMPEL KECIL (mahasiswa S1) — apa yang DIJAMIN?')
print('=' * 78)
print(f'  {"n":>5} {"mode":>9} {"galat maks":>11} {"SIGNIFIKANSI":>14}')
print('  ' + '-' * 46)
for n in [50, 100, 150, 200]:
    rp = kalibrasi_per_jalur(JALUR, n_resp=n, toleransi=0.03, seed=42,
                             maks_putaran=30)
    gm = rp["galat_maks"]
    # cek signifikansi: jalur kuat harus signifikan, jalur NH (0,10) tidak
    d2 = rp["data"]
    sig_ok = True
    for k, mi in MINTA.items():
        s, t = k.split('->')
        sumber = [x.split('->')[0] for x in MINTA if x.endswith('->' + t)]
        S2 = np.column_stack([np.nanmean(np.where(d2["item"][x] < 0, np.nan,
                                                  d2["item"][x].astype(float)),
                                         axis=1) for x in sumber + [t]])
        y = S2[:, -1]
        Xz = (S2[:, :-1] - S2[:, :-1].mean(0)) / np.where(S2[:, :-1].std(0) > 0,
                                                          S2[:, :-1].std(0), 1)
        A = np.column_stack([np.ones(len(Xz)), Xz])
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - A @ c
        s2 = (resid @ resid) / (len(y) - A.shape[1])
        varb = s2 * np.linalg.pinv(A.T @ A).diagonal()
        se = np.sqrt(np.abs(varb))
        tval = c / np.where(se > 0, se, 1)
        # harapan: |minta| > 0,25 -> signifikan ; |minta| < 0,15 -> tidak
        if abs(mi) > 0.25 and abs(tval[sumber.index(s) + 1]) < 1.96:
            sig_ok = False
        if abs(mi) < 0.15 and abs(tval[sumber.index(s) + 1]) > 2.5:
            sig_ok = False
    print(f'  {n:5} {"presisi":>9} {gm:11.4f} {"BENAR" if sig_ok else "ADA SALAH":>14}')
    cek(f'n={n}: signifikansi benar', sig_ok, 'jalur kuat signifikan, jalur NH tidak')

print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
