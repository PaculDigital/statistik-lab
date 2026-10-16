#!/usr/bin/env python3
"""UJI KALIBRASI PER-JALUR — apakah model kompleks kini presisi?

Diuji: regresi, mediasi, dual mediasi, moderasi, dual moderasi, dan
MODEL JURNAL Bos (9 konstruk / 12 hipotesis / 4 tingkat).
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur, ukur_jalur

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


def tampilkan(judul, r, toleransi):
    print(f'  {judul}')
    print(f'    {"JALUR":30} {"MINTA":>8} {"TERUKUR":>9} {"GALAT":>8}  ')
    for t, js in r["hasil"].items():
        g = r["galat"][t]
        print(f'    {t:30} {"":>8} {js:9.4f} {g:+8.4f}')
    print(f'    putaran = {r["putaran"]} | galat maks = {r["galat_maks"]} '
          f'| tercapai = {r["tercapai"]}')
    print()


print('=' * 78)
print(' 1. REGRESI BERGANDA (Y ~ X1+X2+X3)')
print('=' * 78)
jalur = [{"target": "Y", "dari": {"X1": 0.35, "X2": 0.45, "X3": 0.30}}]
r = kalibrasi_per_jalur(jalur, n_resp=187, toleransi=0.03, seed=42)
print(f'    hasil: {r["hasil"]}  galat maks {r["galat_maks"]}  putaran {r["putaran"]}')
for k, v in r["galat"].items():
    cek(f'berganda {k}', abs(v) <= 0.03, f'{v:+.4f}')
print()

print('=' * 78)
print(' 2. REGRESI SEDERHANA (Y ~ X1)')
print('=' * 78)
jalur = [{"target": "Y", "dari": {"X1": 0.50}}]
r = kalibrasi_per_jalur(jalur, n_resp=187, toleransi=0.03, seed=42)
for k, v in r["galat"].items():
    cek(f'sederhana {k}', abs(v) <= 0.03, f'{v:+.4f} | hasil {r["hasil"][k]}')
print()

print('=' * 78)
print(' 3. MEDIASI (X -> M -> Y)')
print('=' * 78)
jalur = [{"target": "M", "dari": {"X1": 0.60}},
         {"target": "Y", "dari": {"X1": 0.10, "M": 0.40}}]
r = kalibrasi_per_jalur(jalur, n_resp=200, toleransi=0.03, seed=42)
for k, v in r["galat"].items():
    cek(f'mediasi {k}', abs(v) <= 0.03, f'{v:+.4f} | hasil {r["hasil"][k]}')
print()

print('=' * 78)
print(' 4. DUAL MEDIASI PARALEL')
print('=' * 78)
jalur = [{"target": "M1", "dari": {"X1": 0.60}},
         {"target": "M2", "dari": {"X1": 0.50}},
         {"target": "Y", "dari": {"X1": 0.10, "M1": 0.40, "M2": 0.30}}]
r = kalibrasi_per_jalur(jalur, n_resp=200, toleransi=0.03, seed=42)
for k, v in r["galat"].items():
    cek(f'dualmed {k}', abs(v) <= 0.035, f'{v:+.4f} | hasil {r["hasil"][k]}')
print()

print('=' * 78)
print(' 5. MEDIASI BERJENJANG (X -> M1 -> M2 -> Y)')
print('=' * 78)
jalur = [{"target": "M1", "dari": {"X1": 0.60}},
         {"target": "M2", "dari": {"M1": 0.50}},
         {"target": "Y", "dari": {"X1": 0.10, "M2": 0.40}}]
r = kalibrasi_per_jalur(jalur, n_resp=200, toleransi=0.03, seed=42)
for k, v in r["galat"].items():
    cek(f'serial {k}', abs(v) <= 0.035, f'{v:+.4f} | hasil {r["hasil"][k]}')
print()

print('=' * 78)
print(' 6. MODEL JURNAL BOS (9 konstruk, 12 hipotesis, 4 tingkat)')
print('=' * 78)
SE = 'SelfEfficacy'
M1, M2, M3 = 'Mastery', 'PerfApproach', 'PerfAvoid'
PA, DC, DS = 'PosAffect', 'DecConf', 'DecSatis'
Y1, Y2 = 'Loyalty', 'Switching'
jalur = [
    {"target": M1, "dari": {SE: 0.45}},
    {"target": M2, "dari": {SE: 0.35}},
    {"target": M3, "dari": {SE: 0.10}},
    {"target": PA, "dari": {M1: 0.35, M2: 0.20, M3: -0.15}},
    {"target": DC, "dari": {M1: 0.30, M2: 0.25, M3: -0.20}},
    {"target": DS, "dari": {PA: 0.40, DC: 0.35}},
    {"target": Y1, "dari": {DS: 0.50}},
    {"target": Y2, "dari": {DS: -0.30}},
]
r = kalibrasi_per_jalur(jalur, n_resp=250, toleransi=0.04, seed=42)
print(f'    putaran = {r["putaran"]} | galat maks = {r["galat_maks"]} '
      f'| tercapai = {r["tercapai"]}')
print()
print(f'    {"JALUR":30} {"TERUKUR":>9} {"GALAT":>8}')
minta_all = {}
for j in jalur:
    for s, v in j["dari"].items():
        minta_all[f'{s}->{j["target"]}'] = v
for k, v in r["hasil"].items():
    g = r["galat"][k]
    print(f'    {k:30} {v:9.4f} {g:+8.4f}  {"OK" if abs(g)<=0.04 else "MELESET"}')
print()
for k, v in r["galat"].items():
    cek(f'jurnal {k}', abs(v) <= 0.04, f'{v:+.4f}')

print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
