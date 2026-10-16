"""UJI Fornell-Larcker + HTMT — pakai fungsi SUNGGUHAN, data NYATA.

⚠️ ATURAN: uji WAJIB memanggil fungsi asli dari app/, JANGAN menyalin rumus.
Kalau uji menyalin rumus, yang diuji = salinan, bukan mesin.

Jalankan: .venv/bin/python uji_fornell_htmt.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from app.diagnosis import _fornell_htmt, _korelasi_konstruk  # noqa: E402  (fungsi asli)

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, info: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}   {info}')


def bikin_data(benar: bool, n: int = 200, seed: int = 11) -> tuple:
    """Dua konstruk, 3 butir masing-masing.

    benar=True  → tiap konstruk padu, ANTAR konstruk hampir tak berkaitan
    benar=False → kedua konstruk kembar (butirnya saling menyerupai)
    """
    rng = np.random.default_rng(seed)
    A = rng.normal(0, 1, n)
    B = rng.normal(0, 1, n) if benar else A + rng.normal(0, 0.25, n)

    df = pd.DataFrame({
        'A1': A + rng.normal(0, 0.45, n),
        'A2': A + rng.normal(0, 0.45, n),
        'A3': A + rng.normal(0, 0.45, n),
        'B1': B + rng.normal(0, 0.45, n),
        'B2': B + rng.normal(0, 0.45, n),
        'B3': B + rng.normal(0, 0.45, n),
    })
    # konstruk: nama → kolom & ave (hasilnya dari mesin yang sudah ada)
    hasil = []
    for nama, kol in (('Variabel A', ['A1', 'A2', 'A3']),
                      ('Variabel B', ['B1', 'B2', 'B3'])):
        muat = []
        skor = df[kol].sum(axis=1).to_numpy(dtype=float)
        for c in kol:
            v = df[c].to_numpy(dtype=float)
            r = float(np.corrcoef(v, skor)[0, 1])
            muat.append({'butir': c, 'muat': round(r, 4)})
        ave = float(np.mean([m['muat'] ** 2 for m in muat]))
        hasil.append({'nama': nama, 'kolom': kol, 'muat': muat,
                      'ave': round(ave, 4), 'cr': 0.9})
    K = pd.DataFrame({h['nama']: df[h['kolom']].sum(axis=1) for h in hasil})
    return hasil, K, df


def main() -> int:
    print('=' * 74)
    print(' UJI Fornell-Larcker + HTMT (fungsi asli app/diagnosis.py)')
    print('=' * 74)
    print()

    # ── 1. Data BENAR: konstruk terpisah ────────────────────────────────
    print(' ── data BENAR (dua variabel berbeda) ──')
    hasil, K, df = bikin_data(benar=True)
    f, h = _fornell_htmt(hasil, K, df)

    cek('Fornell-Larcker menghasilkan 1 pasangan', len(f) == 1, f'({len(f)})')
    cek('HTMT menghasilkan 1 pasangan', len(h) == 1, f'({len(h)})')
    if f:
        cek('Fornell LULUS (akar AVE > korelasi)', f[0]['lulus'] is True,
            str(f[0]))
        print(f'     korelasi {f[0]["korelasi"]} < batas {f[0]["batas"]}')
    if h:
        cek('HTMT di bawah 0,85 (ketat)', h[0]['lulus_ketat'] is True,
            str(h[0]))
        print(f'     HTMT = {h[0]["nilai"]}')

    # ── 2. Data KEMBAR: konstruk saling menyerupai ──────────────────────
    print()
    print(' ── data KEMBAR (dua variabel nyaris sama) ──')
    hasil2, K2, df2 = bikin_data(benar=False)
    f2, h2 = _fornell_htmt(hasil2, K2, df2)
    if h2:
        cek('HTMT NAIK saat konstruk kembar', h2[0]['nilai'] > (h[0]['nilai'] if h else 0),
            f'kembar={h2[0]["nilai"]} vs benar={h[0]["nilai"] if h else "?"}')
        cek('HTMT kembar MELEBIHI 0,85 → tertangkap', h2[0]['lulus_ketat'] is False,
            str(h2[0]))
        print(f'     HTMT kembar = {h2[0]["nilai"]} (ketat='
              f'{h2[0]["lulus_ketat"]}, longgar={h2[0]["lulus_longgar"]})')

    # ── 3. Tepi: 1 konstruk saja → tidak ada pasangan, TIDAK meledak ────
    print()
    print(' ── tepi: hanya 1 konstruk ──')
    hasil3, K3, df3 = bikin_data(benar=True)
    f3, h3 = _fornell_htmt(hasil3[:1], K3[['Variabel A']], df3)
    cek('1 konstruk → fornell kosong', f3 == [], str(f3))
    cek('1 konstruk → htmt kosong', h3 == [], str(h3))

    # ── 4. Tepi: konstruk 1 butir → HTMT dilewati, TIDAK meledak ────────
    print()
    print(' ── tepi: konstruk hanya 1 butir ──')
    h4 = [{'nama': 'X', 'kolom': ['A1'], 'muat': [{'butir': 'A1', 'muat': 0.9}],
           'ave': 0.81, 'cr': 0.9},
          {'nama': 'Y', 'kolom': ['B1'], 'muat': [{'butir': 'B1', 'muat': 0.9}],
           'ave': 0.81, 'cr': 0.9}]
    K4 = pd.DataFrame({'X': df['A1'], 'Y': df['B1']})
    f4, h4b = _fornell_htmt(h4, K4, df)
    cek('1-butir: Fornell tetap dihitung', len(f4) == 1, str(len(f4)))
    cek('1-butir: HTMT dilewati (tak ada butir dalam)', h4b == [], str(h4b))

    print()
    print('=' * 74)
    print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 74)
    return 1 if GAGAL else 0


if __name__ == '__main__':
    sys.exit(main())
