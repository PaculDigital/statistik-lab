"""UKUR PETA KALIBRASI BEDA KELOMPOK (MANOVA) — MENGUKUR, bukan menebak.

═══════════════════════════════════════════════════════════════════════════
MASALAH YANG DIUKUR (21Sep26)
  Beda kelompok yang DIPASANG tidak terbaca sama besarnya di skor akhir.
  Terukur: dipasang 0,90 → terbaca 0,66–0,90 (tergantung undian), padahal
  pola bangunnya sudah benar & stabil.

AKAR YANG SUDAH DITUTUP (jangan diulang):
  · JANGAN `_std()` (standardisasi ulang) setelah beda dipasang →
    beda hilang, hasil bergantung undian. (pelajaran berurutan.py putaran 5)
  · Generator acak WAJIB TERPISAH tiap variabel. (putaran 17)
  · Turun ke item: cukup GESER ke tengah skala, jangan standardisasi.

DUGAAN YANG DIUKUR DI SINI (belum diputuskan sebelum ada angka):
  (a) Pembulatan Likert 1–5 meredam beda → makin banyak butir makin halus?
      → diukur: apakah rata-rata 6 butir lebih akurat dari 2 butir?
  (b) Kalau butir bukan akarnya, apakah faktor susut SERAGAM (bisa
      dikalibrasi sekali) atau tergantung besarnya beda?

CARA: sapu (sweep) beda × butir × n × seed, catat rasio terbaca/dipasang,
lalu lihat apakah rasionya STABIL. Kalau stabil → satu faktor cukup.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import statistics
import sys

import numpy as np

sys.path.insert(0, '/opt/data/services/statistik-lab')
from app.hitung.kelompok import buat_data_kelompok  # noqa: E402


def ukur_satu(beda: float, butir: int, n: int, seed: int) -> dict:
    d = buat_data_kelompok(n_per_kelompok=n, nama_kelompok=['A', 'B'],
                           nama_y=['Y'], beda=[beda], seed=seed, butir=butir)
    Y = d['Y'][:, 0]
    kel = d['kelompok']
    terbaca = float(Y[kel == 'B'].mean() - Y[kel == 'A'].mean())
    return {'beda': beda, 'butir': butir, 'n': n, 'seed': seed,
            'terbaca': terbaca, 'rasio': terbaca / beda if beda else 0.0}


def main() -> int:
    baris = []
    for butir in (1, 2, 3, 4, 6, 8):
        for beda in (0.20, 0.50, 0.90, 1.50, 2.50):
            for seed in (7, 33, 99):
                baris.append(ukur_satu(beda, butir, 200, seed))

    print('=' * 76)
    print(' PETA RASIO (terbaca / dipasang) — makin dekat 1,00 makin akurat')
    print('=' * 76)
    print(f'{"butir":>5} ' + ' '.join(f'{b:>6.2f}' for b in (0.2, 0.5, 0.9, 1.5, 2.5)))
    for butir in (1, 2, 3, 4, 6, 8):
        kol = []
        for beda in (0.20, 0.50, 0.90, 1.50, 2.50):
            rs = [q['rasio'] for q in baris
                  if q['butir'] == butir and abs(q['beda'] - beda) < 1e-9]
            kol.append(statistics.mean(rs))
        print(f'{butir:5d} ' + ' '.join(f'{v:6.3f}' for v in kol))

    print()
    print('=' * 76)
    print(' APAKAH RASIONYA STABIL? (kalau stabil → satu faktor cukup)')
    print('=' * 76)
    for butir in (2, 6, 8):
        rs = [q['rasio'] for q in baris if q['butir'] == butir]
        print(f'  butir={butir}: rata {statistics.mean(rs):.4f} · '
              f'sebar {statistics.pstdev(rs):.4f} · '
              f'min {min(rs):.4f} · maks {max(rs):.4f}')

    with open('/tmp/peta_kalibrasi_kelompok.json', 'w') as f:
        json.dump(baris, f, indent=1)
    print('\n  rincian → /tmp/peta_kalibrasi_kelompok.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
