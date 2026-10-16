#!/usr/bin/env python3
"""UJI TUNTAS — variabel >3 dan mediasi/moderasi kompleks.

Jawaban untuk pertanyaan Bos:
  (1) apakah bisa menangani variabel lebih dari 3?
  (2) apakah bisa mediasi & moderasi dengan kombinasi kompleks?

Setiap skenario DIUKUR. Yang gagal DITULIS gagal, bukan disembunyikan.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur
from app.hitung.kelayakan import periksa_setelan


def jalan(nama, jalur, n=250, tol=0.05, interaksi=None, seed=7, item=4):
    try:
        r = kalibrasi_per_jalur(jalur, n_resp=n, toleransi=tol, seed=seed,
                                interaksi=interaksi, item_per=item)
        tanda = 'OK ' if r['tercapai'] else '~~~'
        print(f'  {tanda} {nama:52} galat {r["galat_maks"]:.4f} '
              f'({r["putaran"]} putaran)')
        return r
    except Exception as e:
        print(f'  ERR {nama:52} {type(e).__name__}: {str(e)[:50]}')
        return None


print('=' * 80)
print(' 1. VARIABEL LEBIH DARI 3 — X banyak ke satu Y')
print('=' * 80)
b3 = {f'X{i}': 0.26 for i in range(1, 4)}
b4 = {'X1': 0.30, 'X2': 0.26, 'X3': 0.22, 'X4': 0.18}
b5 = {'X1': 0.28, 'X2': 0.25, 'X3': 0.22, 'X4': 0.19, 'X5': 0.16}
b6 = {'X1': 0.26, 'X2': 0.24, 'X3': 0.22, 'X4': 0.20, 'X5': 0.18, 'X6': 0.15}
b7 = {f'X{i}': 0.22 - 0.01 * i for i in range(1, 8)}
b8 = {f'X{i}': 0.20 - 0.008 * i for i in range(1, 9)}
for nama, b in [('3 X -> Y', b3), ('4 X -> Y', b4), ('5 X -> Y', b5),
                ('6 X -> Y', b6), ('7 X -> Y', b7), ('8 X -> Y', b8)]:
    jalan(nama, [{'target': 'Y', 'dari': b}])
print()
print('  Catatan: R² = jumlah kuadrat β (kalau X saling bebas) — mesin menghitung.')
for nama, b in [('4 X', b4), ('6 X', b6), ('8 X', b8)]:
    k = periksa_setelan(b, korelasi_x=0.2, n_resp=250)
    print(f'    {nama}: total β = {k["total_beta"]:.2f} -> R² = {k["r2"]:.3f} '
          f'({"LAYAK" if k["layak"] else "TIDAK LAYAK"})')

print()
print('=' * 80)
print(' 2. MEDIASI — dari sederhana sampai kompleks')
print('=' * 80)
jalan('Mediasi tunggal (X->M->Y)', [
    {'target': 'M', 'dari': {'X1': 0.55}},
    {'target': 'Y', 'dari': {'M': 0.45, 'X1': 0.10}}])
jalan('Dual mediasi PARALEL (M1,M2)', [
    {'target': 'M1', 'dari': {'X1': 0.50}},
    {'target': 'M2', 'dari': {'X1': 0.40}},
    {'target': 'Y', 'dari': {'M1': 0.30, 'M2': 0.25, 'X1': 0.08}}])
jalan('Triple mediasi PARALEL (M1,M2,M3)', [
    {'target': 'M1', 'dari': {'X1': 0.50}},
    {'target': 'M2', 'dari': {'X1': 0.42}},
    {'target': 'M3', 'dari': {'X1': 0.35}},
    {'target': 'Y', 'dari': {'M1': 0.28, 'M2': 0.22, 'M3': 0.18, 'X1': 0.10}}])
jalan('Mediasi BERJENJANG (X->M1->M2->Y)', [
    {'target': 'M1', 'dari': {'X1': 0.60}},
    {'target': 'M2', 'dari': {'M1': 0.50}},
    {'target': 'Y', 'dari': {'M2': 0.45, 'X1': 0.10}}])
jalan('Rantai 4 tingkat (X->M1->M2->M3->Y)', [
    {'target': 'M1', 'dari': {'X1': 0.60}},
    {'target': 'M2', 'dari': {'M1': 0.50}},
    {'target': 'M3', 'dari': {'M2': 0.45}},
    {'target': 'Y', 'dari': {'M3': 0.40, 'X1': 0.08}}])
jalan('Mediasi 2 X (X1,X2 -> M -> Y)', [
    {'target': 'M', 'dari': {'X1': 0.40, 'X2': 0.30}},
    {'target': 'Y', 'dari': {'M': 0.45, 'X1': 0.10, 'X2': 0.08}}])
jalan('Mediasi 3 X (X1,X2,X3 -> M -> Y)', [
    {'target': 'M', 'dari': {'X1': 0.35, 'X2': 0.28, 'X3': 0.22}},
    {'target': 'Y', 'dari': {'M': 0.42, 'X1': 0.10, 'X2': 0.08, 'X3': 0.06}}])
jalan('2 X -> 2 M paralel -> Y', [
    {'target': 'M1', 'dari': {'X1': 0.45, 'X2': 0.25}},
    {'target': 'M2', 'dari': {'X1': 0.30, 'X2': 0.38}},
    {'target': 'Y', 'dari': {'M1': 0.28, 'M2': 0.22, 'X1': 0.08, 'X2': 0.06}}])
jalan('3 X -> 3 M paralel -> Y', [
    {'target': 'M1', 'dari': {'X1': 0.42, 'X2': 0.20, 'X3': 0.15}},
    {'target': 'M2', 'dari': {'X1': 0.18, 'X2': 0.40, 'X3': 0.18}},
    {'target': 'M3', 'dari': {'X1': 0.15, 'X2': 0.20, 'X3': 0.38}},
    {'target': 'Y', 'dari': {'M1': 0.24, 'M2': 0.20, 'M3': 0.16, 'X1': 0.06}}])

print()
print('=' * 80)
print(' 3. MODERASI — tunggal sampai berlapis')
print('=' * 80)
jalan('Moderasi tunggal (X1 x Z1 -> Y)', [
    {'target': 'Y', 'dari': {'X1': 0.30, 'Z1': 0.20}}],
    interaksi=[{'target': 'Y', 'x': 'X1', 'z': 'Z1', 'bobot': 0.25}])
jalan('DUAL moderasi paralel (X1xZ1, X1xZ2)', [
    {'target': 'Y', 'dari': {'X1': 0.30, 'Z1': 0.15, 'Z2': 0.12}}],
    interaksi=[{'target': 'Y', 'x': 'X1', 'z': 'Z1', 'bobot': 0.22},
               {'target': 'Y', 'x': 'X1', 'z': 'Z2', 'bobot': 0.18}])
jalan('TRIPLE moderasi paralel', [
    {'target': 'Y', 'dari': {'X1': 0.28, 'Z1': 0.12, 'Z2': 0.10, 'Z3': 0.08}}],
    interaksi=[{'target': 'Y', 'x': 'X1', 'z': 'Z1', 'bobot': 0.22},
               {'target': 'Y', 'x': 'X1', 'z': 'Z2', 'bobot': 0.18},
               {'target': 'Y', 'x': 'X1', 'z': 'Z3', 'bobot': 0.14}])

print()
print('=' * 80)
print(' 4. MEDIASI + MODERASI (kombinasi)')
print('=' * 80)
jalan('Moderasi jalur-a (X1xZ1 -> M)', [
    {'target': 'M', 'dari': {'X1': 0.50}},
    {'target': 'Y', 'dari': {'M': 0.45, 'X1': 0.10}}],
    interaksi=[{'target': 'M', 'x': 'X1', 'z': 'Z1', 'bobot': 0.25}])
jalan('Moderasi jalur-b (MxZ1 -> Y)', [
    {'target': 'M', 'dari': {'X1': 0.50}},
    {'target': 'Y', 'dari': {'M': 0.40, 'X1': 0.10}}],
    interaksi=[{'target': 'Y', 'x': 'M', 'z': 'Z1', 'bobot': 0.25}])
jalan('Moderated mediation 2 moderator (a & b)', [
    {'target': 'M', 'dari': {'X1': 0.50}},
    {'target': 'Y', 'dari': {'M': 0.40, 'X1': 0.10}}],
    interaksi=[{'target': 'M', 'x': 'X1', 'z': 'Z1', 'bobot': 0.25},
               {'target': 'Y', 'x': 'M', 'z': 'Z2', 'bobot': 0.20}])
jalan('Dual mediasi + moderasi jalur-a & b', [
    {'target': 'M1', 'dari': {'X1': 0.45}},
    {'target': 'M2', 'dari': {'X1': 0.35}},
    {'target': 'Y', 'dari': {'M1': 0.28, 'M2': 0.22, 'X1': 0.08}}],
    interaksi=[{'target': 'M1', 'x': 'X1', 'z': 'Z1', 'bobot': 0.22},
               {'target': 'Y', 'x': 'M2', 'z': 'Z2', 'bobot': 0.18}])
jalan('Mediasi berjenjang + moderasi jalur-b', [
    {'target': 'M1', 'dari': {'X1': 0.55}},
    {'target': 'M2', 'dari': {'M1': 0.48}},
    {'target': 'Y', 'dari': {'M2': 0.42, 'X1': 0.08}}],
    interaksi=[{'target': 'Y', 'x': 'M2', 'z': 'Z1', 'bobot': 0.20}])

print()
print('=' * 80)
print(' 5. MODEL BESAR — 9 konstruk (model jurnal Bos, 12 hipotesis)')
print('=' * 80)
jalan('Model jurnal 4 tingkat (n=250)', [
    {'target': 'Mastery', 'dari': {'SE': 0.45}},
    {'target': 'PerfApp', 'dari': {'SE': 0.35}},
    {'target': 'PerfAvo', 'dari': {'SE': 0.10}},
    {'target': 'PosAff', 'dari': {'Mastery': 0.35, 'PerfApp': 0.20, 'PerfAvo': -0.15}},
    {'target': 'DecConf', 'dari': {'Mastery': 0.30, 'PerfApp': 0.25, 'PerfAvo': -0.20}},
    {'target': 'DecSatis', 'dari': {'PosAff': 0.40, 'DecConf': 0.35}},
    {'target': 'Loyalty', 'dari': {'DecSatis': 0.50}},
    {'target': 'Switching', 'dari': {'DecSatis': -0.30}}],
    tol=0.04)

print()
print('=' * 80)
print(' SELESAI — semua di atas diukur, bukan diklaim')
print('=' * 80)
