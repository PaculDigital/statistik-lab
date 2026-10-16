#!/usr/bin/env python3
"""AUDIT MESIN — buktikan bentuk model APA SAJA yang bisa dibangun.

TUJUAN: menjawab pertanyaan Bos "script/mesin kamu termasuk, belum semua
diimplementasikan ke UI web?" dengan BUKTI TERUKUR, bukan dugaan.

CARA: jalankan 10 bentuk model berbeda lewat bangun_dari_spek(), lalu UKUR
koefisien yang benar-benar keluar (regresi terstandardisasi) dan bandingkan
dengan yang diminta.

Jalankan: .venv/bin/python audit_mesin.py
"""
from __future__ import annotations

import sys
import traceback

import numpy as np

sys.path.insert(0, '.')

from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur, skor_item  # noqa: E402
from app.hitung.kalibrasi_jalur import regresi_terstandar as reg  # noqa: E402


def ukur(data: dict, target: str, sumber: list[str]) -> dict[str, float]:
    """Ukur koefisien target~sumber (regresi terstandardisasi, cara SPSS).

    ⚠️ JEBAKAN (18Sep26): `skor_item(data, nama)` mengembalikan MATRIKS
    bentuk (n, 1) — bukan vektor (n,). Karena itu JANGAN di-`column_stack`
    mentah-mentah lalu dioper ke regresi tanpa `.ravel()`, dan pastikan
    nama yang diminta BENAR-BENAR ada di data (kalau tidak → KeyError).
    """
    tersedia = set(data['item'])
    for nm in sumber + [target]:
        if nm not in tersedia:
            raise KeyError(
                f'{nm!r} tidak ada di data. Yang ada: {sorted(tersedia)}')
    kol = [skor_item(data, [nm]).ravel() for nm in sumber]
    X = np.column_stack(kol)
    y = skor_item(data, [target]).ravel()

    # ⚠️ JEBAKAN (18Sep26): `regresi_terstandar(X, y)` mengembalikan ARRAY
    # koefisien SAJA (bukan tuple 4 nilai seperti dugaan awal Wulan).
    # Terukur: 3 prediktor → array 3 angka. Jadi JANGAN tulis
    # `b, _t, _p, _r = reg(...)` (→ ValueError) dan JANGAN tulis
    # `reg(...)[0]` (→ hanya koefisien pertama, skalar).
    b = np.ravel(reg(X, y))
    return {nm: round(float(v), 4) for nm, v in zip(sumber, b)}


def jalankan(nama: str, spek: dict, periksa: list[tuple]) -> dict:
    """Bangun 1 skenario, ukur, kembalikan ringkasan."""
    kel = kalibrasi_per_jalur(
        spek['jalur'], toleransi=0.02, maks_putaran=40,
        item_per=3, skala=5, alpha_rentang=(0.80, 0.88), seed=7,
        interaksi=spek.get('interaksi'))
    data = kel['data']

    hasil = []
    for target, sumber, diminta in periksa:
        keluar = ukur(data, target, sumber)
        for nm in sumber:
            mau = diminta.get(nm)
            ada = keluar[nm]
            galat = abs(ada - mau) if mau is not None else None
            hasil.append({'target': target, 'dari': nm, 'minta': mau,
                          'keluar': ada, 'galat': galat})
    return {'nama': nama, 'hasil': hasil}


SKENARIO = [
    ('1. Regresi sederhana (1 X → Y)',
     {'jalur': [{'target': 'Y', 'dari': {'X': 0.40}}]},
     [('Y', ['X'], {'X': 0.40})]),

    ('2. Regresi berganda (3 X → Y)',
     {'jalur': [{'target': 'Y', 'dari': {'X1': 0.35, 'X2': 0.25, 'X3': 0.15}}]},
     [('Y', ['X1', 'X2', 'X3'], {'X1': 0.35, 'X2': 0.25, 'X3': 0.15})]),

    ('3. Mediasi tunggal (X → M → Y)',
     {'jalur': [{'target': 'M', 'dari': {'X': 0.55}},
                {'target': 'Y', 'dari': {'M': 0.45, 'X': 0.10}}]},
     [('M', ['X'], {'X': 0.55}), ('Y', ['M', 'X'], {'M': 0.45, 'X': 0.10})]),

    ('4. Dual mediasi PARALEL (X → M1, M2 → Y)',
     {'jalur': [{'target': 'M1', 'dari': {'X': 0.50}},
                {'target': 'M2', 'dari': {'X': 0.40}},
                {'target': 'Y', 'dari': {'M1': 0.35, 'M2': 0.30, 'X': 0.10}}]},
     [('M1', ['X'], {'X': 0.50}), ('M2', ['X'], {'X': 0.40}),
      ('Y', ['M1', 'M2', 'X'], {'M1': 0.35, 'M2': 0.30, 'X': 0.10})]),

    ('5. Mediasi BERJENJANG (X → M1 → M2 → Y)',
     {'jalur': [{'target': 'M1', 'dari': {'X': 0.55}},
                {'target': 'M2', 'dari': {'M1': 0.45}},
                {'target': 'Y', 'dari': {'M2': 0.40, 'X': 0.10}}]},
     [('M1', ['X'], {'X': 0.55}), ('M2', ['M1'], {'M1': 0.45}),
      ('Y', ['M2', 'X'], {'M2': 0.40, 'X': 0.10})]),

    ('6. Moderasi MRA (X, Z, X×Z → Y)',
     {'jalur': [{'target': 'Y', 'dari': {'X': 0.35, 'Z': 0.20}}],
      'interaksi': [{'target': 'Y', 'x': 'X', 'z': 'Z', 'bobot': 0.25}]},
     [('Y', ['X', 'Z'], {'X': 0.35, 'Z': 0.20})]),

    ('7. DUAL moderasi (X×Z1 & X×Z2 → Y)',
     {'jalur': [{'target': 'Y', 'dari': {'X': 0.30, 'Z1': 0.15, 'Z2': 0.15}}],
      'interaksi': [{'target': 'Y', 'x': 'X', 'z': 'Z1', 'bobot': 0.22},
                    {'target': 'Y', 'x': 'X', 'z': 'Z2', 'bobot': 0.18}]},
     [('Y', ['X', 'Z1', 'Z2'], {'X': 0.30, 'Z1': 0.15, 'Z2': 0.15})]),

    ('8. Moderated mediation (X → M → Y, M×Z → Y)',
     {'jalur': [{'target': 'M', 'dari': {'X': 0.55}},
                {'target': 'Y', 'dari': {'M': 0.40, 'X': 0.10, 'Z': 0.05}}],
      'interaksi': [{'target': 'Y', 'x': 'M', 'z': 'Z', 'bobot': 0.20}]},
     [('M', ['X'], {'X': 0.55}),
      ('Y', ['M', 'X', 'Z'], {'M': 0.40, 'X': 0.10, 'Z': 0.05})]),

    ('9. Moderasi di jalur-a (X×Z → M → Y)',
     {'jalur': [{'target': 'M', 'dari': {'X': 0.50, 'Z': 0.10}},
                {'target': 'Y', 'dari': {'M': 0.45, 'X': 0.10}}],
      'interaksi': [{'target': 'M', 'x': 'X', 'z': 'Z', 'bobot': 0.25}]},
     [('M', ['X', 'Z'], {'X': 0.50, 'Z': 0.10}),
      ('Y', ['M', 'X'], {'M': 0.45, 'X': 0.10})]),

    ('10. Model 4 TINGKAT (X → M1 → M2 → Y, 2 keluaran)',
     {'jalur': [{'target': 'M1', 'dari': {'X': 0.60}},
                {'target': 'M2', 'dari': {'X': 0.35, 'M1': 0.30}},
                {'target': 'Y1', 'dari': {'M2': 0.40, 'X': 0.15}},
                {'target': 'Y2', 'dari': {'M2': 0.30, 'X': 0.20}}]},
     [('M1', ['X'], {'X': 0.60}),
      ('M2', ['X', 'M1'], {'X': 0.35, 'M1': 0.30}),
      ('Y1', ['M2', 'X'], {'M2': 0.40, 'X': 0.15}),
      ('Y2', ['M2', 'X'], {'M2': 0.30, 'X': 0.20})]),
]


def main() -> int:
    print('═' * 74)
    print('  AUDIT MESIN — bentuk model apa saja yang BISA dibangun?')
    print('═' * 74)
    lulus = gagal = 0
    rekap = []
    for nama, spek, periksa in SKENARIO:
        print(f'\n▸ {nama}')
        try:
            r = jalankan(nama, spek, periksa)
        except Exception as e:                              # noqa: BLE001
            print(f'   ❌ MESIN MENOLAK: {type(e).__name__}: {e}')
            traceback.print_exc(limit=2)
            gagal += 1
            rekap.append((nama, 'GAGAL-MESIN', 0.0))
            continue
        galat_maks = 0.0
        for h in r['hasil']:
            if h['galat'] is None:
                continue
            tanda = '✅' if h['galat'] <= 0.03 else ('⚠️' if h['galat'] <= 0.06
                                                    else '❌')
            galat_maks = max(galat_maks, h['galat'] or 0)
            print(f'   {tanda} {h["dari"]:>4} → {h["target"]:<4} '
                  f'minta {h["minta"]:.2f}  keluar {h["keluar"]:+.4f}  '
                  f'galat {h["galat"]:.4f}')
        if galat_maks <= 0.03:
            lulus += 1
            rekap.append((nama, 'LULUS', galat_maks))
        else:
            gagal += 1
            rekap.append((nama, 'GALAT BESAR', galat_maks))

    print('\n' + '═' * 74)
    print('  REKAP')
    print('═' * 74)
    for nama, status, g in rekap:
        print(f'  {status:<12} galat maks {g:.4f}  {nama}')
    print(f'\n  {lulus} LULUS / {gagal} GAGAL  (toleransi 0,03)')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
