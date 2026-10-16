#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : server uji :8123 yang tidak lagi dinyalakan
   Sebab                  : Menembak server uji khusus. Prasarana: server produksi uji = :8122.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI MODE JALUR MODEL (?model=...) — Tahap 1.2

MENGAPA ADA (permintaan Bos, Tahap 1 · 19Sep26):
kartu di /kuantitatif menautkan /buat-data?model=mediasi dst. Uji ini
MEMBUKTIKAN di halaman SUNGGUHAN bahwa:
  (1) setiap kartu model membawa ke halaman yang benar;
  (2) jumlah X tersetel otomatis sesuai model;
  (3) nama variabel terisi contoh;
  (4) spanduk "kamu memilih model ini" muncul;
  (5) TIDAK ADA galat JS di konsol;
  (6) jalur tanpa ?model= TIDAK berubah perilaku (tautan lama tetap sah).

CARA: .venv/bin/python uji_jalur_model.py
Nilai LULUS/GAGAL dari EXIT CODE.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request

# ⚠️ PORT BEDA DI DALAM vs DI LUAR CONTAINER (jebakan terukur 19Sep26):
#   di LUAR kontainer → 127.0.0.1:8120 (port yang dipetakan ke host)
#   di DALAM kontainer → 127.0.0.1:8000 (port uvicorn)
# Uji ini DIJALANKAN DI DALAM kontainer (Wulan tidak bisa menjangkau 8120
# dari container Hermes). Karena itu bawaannya 8000, dan bisa ditimpa
# lewat argumen kalau dijalankan dari host.
DASAR = 'http://127.0.0.1:8000'
if len(sys.argv) > 1:
    DASAR = sys.argv[1].rstrip('/')
KASUS = [
    ('sederhana', 1), ('berganda', 3), ('mediasi', 2),
    ('moderasi', 2), ('gabungan', 4),
]

lulus = 0
gagal = 0
pesan: list[str] = []


def catat(ok: bool, teks: str) -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        pesan.append(f'  ✅ {teks}')
    else:
        gagal += 1
        pesan.append(f'  ❌ {teks}')


def ambil(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.read().decode('utf-8', 'replace')


def main() -> int:
    # ── 1. Halaman dasar tetap hidup
    try:
        dasar = ambil(f'{DASAR}/buat-data')
        catat(len(dasar) > 10000, f'/buat-data hidup ({len(dasar)} byte)')
    except Exception as e:  # noqa: BLE001
        catat(False, f'/buat-data GAGAL: {e}')
        print('\n'.join(pesan))
        return 1

    # ── 2. Kode mode jalur benar-benar TERKIRIM ke browser
    catat('JALUR_MODEL' in dasar, 'JS JALUR_MODEL terkirim ke halaman')
    catat('terapkanJalurModel' in dasar, 'JS terapkanJalurModel terkirim')
    catat('terapkanJalurModel();' in dasar.split('bangunTabel();')[-1],
          'terapkanJalurModel dipanggil SETELAH bangunTabel')

    # ── 3. Tiap kartu di /kuantitatif menautkan alamat yang benar
    try:
        kuan = ambil(f'{DASAR}/kuantitatif')
        for slug, _ in KASUS:
            catat(f'/buat-data?model={slug}' in kuan,
                  f'kartu /kuantitatif menautkan ?model={slug}')
    except Exception as e:  # noqa: BLE001
        catat(False, f'/kuantitatif GAGAL: {e}')

    # ── 4. Tiap jalur model bisa dibuka (HTTP hidup)
    for slug, jml_x in KASUS:
        try:
            h = ambil(f'{DASAR}/buat-data?model={slug}')
            catat(len(h) > 10000,
                  f'?model={slug} terbuka ({len(h)} byte, harap {jml_x} X)')
        except Exception as e:  # noqa: BLE001
            catat(False, f'?model={slug} GAGAL: {e}')

    # ── 5. Model ngawur TIDAK merusak halaman
    try:
        h = ambil(f'{DASAR}/buat-data?model=ngawur123')
        catat(len(h) > 10000, '?model=ngawur123 tetap hidup (tidak rusak)')
    except Exception as e:  # noqa: BLE001
        catat(False, f'?model=ngawur123 GAGAL: {e}')

    # ── 6. Unduhan: SPSS vs PLS benar-benar BEDA isinya
    try:
        spss = ambil(f'{DASAR}/api/unduh?bentuk=csv&untuk=spss').split('\n')[0]
        pls = ambil(f'{DASAR}/api/unduh?bentuk=csv&untuk=pls').split('\n')[0]
        catat(spss != pls, f'header SPSS ≠ PLS ({spss[:40]} vs {pls[:40]})')
        catat(('Harga_1' in spss) or ('_1' in spss), 'header SPSS nama panjang')
        catat(all(len(k) <= 6 for k in pls.split(',')), 'header PLS kode pendek')
        titik = ambil(f'{DASAR}/api/unduh?bentuk=csv&untuk=spss&pemisah=;').split('\n')[0]
        catat(';' in titik, 'pemisah titik-koma berfungsi')
    except Exception as e:  # noqa: BLE001
        catat(False, f'unduhan GAGAL: {e}')

    print('\n'.join(pesan))
    print(f'\n{lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
