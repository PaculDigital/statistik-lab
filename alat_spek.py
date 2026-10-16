#!/usr/bin/env python3
"""
ALAT BANTU — bangun spek model dari DIAGRAM JALUR.

Pakai:
    .venv/bin/python alat_spek.py contoh          # lihat contoh
    .venv/bin/python alat_spek.py uji model.json  # jalankan dari berkas

Format berkas (JSON):
{
  "nama": "Model saya",
  "n_resp": 250,
  "mode": "presisi",              // "presisi" | "natural"
  "jalur": [
    {"target": "M", "dari": {"X1": 0.60}},
    {"target": "Y", "dari": {"X1": 0.10, "M": 0.40}}
  ]
}

ATURAN: urutkan jalur dari INDUK ke ANAK (X dulu, lalu M, lalu Y).
Kalau urutannya salah, fungsi akan menolak dengan pesan jelas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from app.hitung.kalibrasi_jalur import (bangun_dengan_mode,  # noqa: E402
                                        kalibrasi_per_jalur)

CONTOH = {
    "nama": "Mediasi tunggal (X -> M -> Y)",
    "n_resp": 200,
    "mode": "presisi",
    "jalur": [
        {"target": "M", "dari": {"X1": 0.60}},
        {"target": "Y", "dari": {"X1": 0.10, "M": 0.40}},
    ],
}


def tampilkan_hasil(r: dict, n_resp: int) -> None:
    print(f'  n responden   : {n_resp}')
    print(f'  mode          : {r.get("mode", "presisi")}')
    if "putaran" in r:
        print(f'  putaran       : {r["putaran"]}')
        print(f'  galat maks    : {r["galat_maks"]}')
        print(f'  tercapai      : {r["tercapai"]}')
    print()
    if "hasil" in r:
        print(f'  {"JALUR":26} {"TERUKUR":>9} {"GALAT":>8}')
        for k, v in r["hasil"].items():
            print(f'  {k:26} {v:9.4f} {r["galat"][k]:+8.4f}')
    d = r.get("data", {})
    if d.get("alpha_dipakai"):
        print()
        print('  alpha (reliabilitas) tiap konstruk:')
        for k, v in d["alpha_dipakai"].items():
            print(f'    {k:20} {v:.3f}')
    if d.get("item"):
        print()
        print('  5 baris pertama data (item Likert):')
        nama = list(d["item"].keys())
        print('    ' + ' | '.join(f'{nm:>12}' for nm in nama))
        for i in range(min(5, len(next(iter(d["item"].values()))))):
            baris = []
            for nm in nama:
                it = d["item"][nm][i]
                baris.append(' | '.join(f'{int(v):12d}' for v in it))
            print('    ' + baris[0][:80] + ' ...')


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'contoh'):
        print(__doc__)
        print('=' * 74)
        print(' CONTOH BERKAS SPEK')
        print('=' * 74)
        print(json.dumps(CONTOH, indent=2, ensure_ascii=False))
        if len(sys.argv) >= 2 and sys.argv[1] == 'contoh':
            print()
            print('=' * 74)
            print(' MENJALANKAN CONTOH')
            print('=' * 74)
            r = kalibrasi_per_jalur(CONTOH["jalur"], n_resp=200,
                                    toleransi=0.03, seed=42)
            tampilkan_hasil(r, 200)
        return 0

    berkas = Path(sys.argv[1])
    if not berkas.exists():
        print(f'❌ Berkas tidak ada: {berkas}')
        return 2
    try:
        spek = json.loads(berkas.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f'❌ JSON rusak: {e}')
        return 2

    nama = spek.get("nama", berkas.stem)
    jalur = spek.get("jalur") or []
    n_resp = int(spek.get("n_resp", 250))
    mode = spek.get("mode", "presisi")
    toleransi = float(spek.get("toleransi", 0.03))
    seed = int(spek.get("seed", 42))

    if not jalur:
        print('❌ Spek tidak punya "jalur"')
        return 2

    print('=' * 74)
    print(f' {nama}')
    print('=' * 74)
    print()
    try:
        if mode == "presisi":
            r = kalibrasi_per_jalur(jalur, n_resp=n_resp,
                                    toleransi=toleransi, seed=seed)
            r["mode"] = "presisi"
        else:
            r = bangun_dengan_mode("natural", jalur=jalur, n_resp=n_resp,
                                   seed=seed)
            r["mode"] = "natural"
    except ValueError as e:
        print(f'❌ {e}')
        print('   Pastikan jalur diurutkan dari INDUK ke ANAK.')
        return 1

    tampilkan_hasil(r, n_resp)
    print()
    if r.get("tercapai") is True:
        print('✅ TERCAPAI — semua jalur dalam toleransi')
        return 0
    if mode == "natural":
        print('🌿 MODE NATURAL — hasil bervariasi (memang begitu).')
        print('   Untuk angka persis, pakai mode "presisi".')
        return 0
    print('⚠️  BELUM TERCAPAI — perbesar maks_putaran atau longgarkan toleransi')
    return 1


if __name__ == '__main__':
    sys.exit(main())
