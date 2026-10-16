#!/usr/bin/env python3
"""UJI MODEL JURNAL — Goal-Directed Student Decision Quality (12 hipotesis).

MEMAKAI MESIN FINAL: kalibrasi_per_jalur() (bukan bangun_dari_spek).
Model: 9 konstruk, 12 hipotesis, 4 tingkat, 1 jalur NH, 2 keluaran paralel.

Struktur (dari diagram Bos):
  Self-efficacy (X) -> Mastery (M1)          [H1]
                    -> Perf-Approach (M2)    [H2]
                    -> Perf-Avoidance (M3)   [NH — TIDAK dihipotesis]
  M1,M2,M3 -> Positive Affect (PA)           [H3, H4, H5]
  M1,M2,M3 -> Decision Confidence (DC)       [H6, H7, H8]
  PA,DC    -> Decision Satisfaction (DS)     [H9, H10]
  DS -> Attitudinal Loyalty Intention (Y1)   [H11]
  DS -> Switching Likelihood (Y2)            [H12]
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur, ukur_jalur

TOLERANSI = 0.04
LULUS = GAGAL = 0

SE = 'SelfEfficacy'
M1, M2, M3 = 'Mastery', 'PerfApproach', 'PerfAvoid'
PA, DC, DS = 'PosAffect', 'DecConf', 'DecSatis'
Y1, Y2 = 'Loyalty', 'Switching'

JALUR = [
    {"target": M1, "dari": {SE: 0.45}},                        # H1
    {"target": M2, "dari": {SE: 0.35}},                        # H2
    {"target": M3, "dari": {SE: 0.10}},                        # NH
    {"target": PA, "dari": {M1: 0.35, M2: 0.20, M3: -0.15}},   # H3 H4 H5
    {"target": DC, "dari": {M1: 0.30, M2: 0.25, M3: -0.20}},   # H6 H7 H8
    {"target": DS, "dari": {PA: 0.40, DC: 0.35}},              # H9 H10
    {"target": Y1, "dari": {DS: 0.50}},                        # H11
    {"target": Y2, "dari": {DS: -0.30}},                       # H12
]


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


print('=' * 78)
print(' MODEL JURNAL: 9 konstruk, 12 hipotesis, 4 tingkat, 2 keluaran paralel')
print('=' * 78)
print()

r = kalibrasi_per_jalur(JALUR, n_resp=250, toleransi=TOLERANSI, seed=42)
print(f'  n = 250 | toleransi = {TOLERANSI} | putaran = {r["putaran"]} '
      f'| galat maks = {r["galat_maks"]} | tercapai = {r["tercapai"]}')
print()

# setelan asli (minta)
minta = {}
for j in JALUR:
    for s, v in j["dari"].items():
        minta[f'{s}->{j["target"]}'] = v

# urutan tampil mengikuti gambar Bos
URUT = [f'{SE}->{M1}', f'{SE}->{M2}', f'{SE}->{M3}',
        f'{M1}->{PA}', f'{M2}->{PA}', f'{M3}->{PA}',
        f'{M1}->{DC}', f'{M2}->{DC}', f'{M3}->{DC}',
        f'{PA}->{DS}', f'{DC}->{DS}',
        f'{DS}->{Y1}', f'{DS}->{Y2}']
LABEL = {f'{SE}->{M1}': 'H1  SE -> Mastery',
         f'{SE}->{M2}': 'H2  SE -> PerfApproach',
         f'{SE}->{M3}': 'NH  SE -> PerfAvoid',
         f'{M1}->{PA}': 'H3  Mastery -> PositiveAffect',
         f'{M2}->{PA}': 'H4  PerfApproach -> PositiveAffect',
         f'{M3}->{PA}': 'H5  PerfAvoid -> PositiveAffect',
         f'{M1}->{DC}': 'H6  Mastery -> DecisionConf',
         f'{M2}->{DC}': 'H7  PerfApproach -> DecisionConf',
         f'{M3}->{DC}': 'H8  PerfAvoid -> DecisionConf',
         f'{PA}->{DS}': 'H9  PositiveAffect -> DecSatis',
         f'{DC}->{DS}': 'H10 DecisionConf -> DecSatis',
         f'{DS}->{Y1}': 'H11 DecSatis -> Loyalty',
         f'{DS}->{Y2}': 'H12 DecSatis -> Switching'}

print(f'  {"HIPOTESIS":38} {"MINTA":>7} {"TERUKUR":>9} {"GALAT":>8}  STATUS')
print('  ' + '-' * 74)
for k in URUT:
    got = r["hasil"][k]
    g = r["galat"][k]
    print(f'  {LABEL[k]:38} {minta[k]:7.2f} {got:9.4f} {g:+8.4f}  '
          f'{"OK" if abs(g) <= TOLERANSI else "MELESET"}')
    cek(LABEL[k].split()[0], abs(g) <= TOLERANSI, f'{g:+.4f}')

print()
print(f'  galat maksimum = {r["galat_maks"]}')
print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
