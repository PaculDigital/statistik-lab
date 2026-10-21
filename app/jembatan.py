"""
JEMBATAN EduAi ↔ Statistik Lab — pintu hitung TANPA SESI (Opsi B).

Keputusan Bos (21 Okt 2026, DOKUMENTASI_BAB4_RANCANGAN_FINAL_21OKT2026.md
di repo eduai-publishing §11): data dikirim → langsung dihitung → hasil
pulang. TIDAK ada data yang dititipkan/disimpan di server ini — beda
dengan alur lama /api/diagnosis/* yang menyimpan sesi sementara di
memori untuk pemakai langsung (alur lama TIDAK diubah sama sekali).

Isi modul ini:
  1. `periksa_pra_survei()` — mode berhenti-awal: validitas tiap butir
     (korelasi butir–total terkoreksi vs r kritis) + reliabilitas tiap
     variabel (Cronbach Alpha dari `_alpha` yang SUDAH ada di
     diagnosis.py — rumus tidak diduplikasi).
  2. `buat_router()` — endpoint:
       GET  /api/jembatan/status  (tanpa kunci: cek layanan hidup)
       POST /api/jembatan/hitung  (WAJIB kunci antar-layanan)
     Tahap 'utama' membungkus fungsi murni periksa_spss/periksa_pls
     persis seperti rute lama (termasuk penggabungan peran dan hiasan
     nasihat yang sama, disuntikkan dari main.py agar satu sumber).

Kunci antar-layanan: header `X-Kunci-Layanan`, dibandingkan dengan
variabel lingkungan `JEMBATAN_KUNCI_LAYANAN` di server. Kuncinya milik
EduAi (kredensial layanan baru) — BUKAN meminjam kredensial proyek lain.
Kalau variabel itu belum dipasang, pintu menolak dengan 503 (aman:
tertutup sampai pemilik memasang kunci), bukan terbuka.
"""
from __future__ import annotations

import os
import re
import secrets
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Header, HTTPException

ENV_KUNCI = 'JEMBATAN_KUNCI_LAYANAN'
ALPHA_MIN = 0.60          # batas lazim reliabilitas untuk penelitian sosial
N_MIN_PRA = 10            # saran jumlah responden minimum pra-survei


# ══════════════════════════════════════════════════════════════════════════
# PRA-SURVEI — pemeriksaan instrumen (berhenti awal, tanpa regresi/PLS)
# ══════════════════════════════════════════════════════════════════════════
def _r_kritis(n: int, taraf: float = 0.05) -> float | None:
    """r tabel (dua arah) untuk n responden — dari sebaran t, df = n-2."""
    if n < 4:
        return None
    from scipy import stats
    df = n - 2
    t = float(stats.t.ppf(1 - taraf / 2, df))
    return float(t / np.sqrt(t * t + df))


def _kelompok_dari_awalan(kolom: list[str]) -> dict[str, list[str]]:
    """Kelompokkan butir dari pola nama: 'Kualitas_Produk_1' → 'Kualitas_Produk',
    'KP1' → 'KP'. Pola yang sama dipakai template instrumen EduAi."""
    keluar: dict[str, list[str]] = {}
    for c in kolom:
        m = re.match(r'^(.*?)[_\s]?\d+$', str(c))
        nama = m.group(1) if m else str(c)
        keluar.setdefault(nama, []).append(c)
    return keluar


def periksa_pra_survei(df: pd.DataFrame,
                       konstruk: dict[str, list[str]] | None = None) -> dict[str, Any]:
    """Periksa instrumen dari data pra-survei (responden asli, sedikit).

    konstruk: {nama_variabel: [kolom butir, ...]}. Kalau kosong,
    butir dikelompokkan dari pola nama kolom.
    Keluaran per variabel: alpha + lolos_alpha; per butir: r hitung
    (butir vs total butir LAIN dalam variabelnya), r kritis, lolos.
    """
    from app.diagnosis import _alpha, _f, _r, GagalBaca

    if df is None or df.shape[1] == 0:
        raise GagalBaca('Belum ada data pra-survei yang dikirim.')
    if not konstruk:
        konstruk = _kelompok_dari_awalan([str(c) for c in df.columns])

    variabel: list[dict[str, Any]] = []
    semua_lolos = True
    for nama, cols in konstruk.items():
        ada = [c for c in cols if c in df.columns]
        if len(ada) < 2:
            raise GagalBaca(
                f'Variabel "{nama}" cuma punya {len(ada)} butir yang ada di '
                f'data. Minimal 2 butir supaya bisa diperiksa.')
        item = df[ada].apply(pd.to_numeric, errors='coerce').dropna()
        n = int(len(item))
        if n < 4:
            raise GagalBaca(
                f'Variabel "{nama}" tinggal {n} baris lengkap — terlalu '
                f'sedikit untuk diperiksa (perlu minimal 4, disarankan '
                f'{N_MIN_PRA}+).')
        mat = item.to_numpy(dtype=float)
        alpha = _alpha(mat)
        rk = _r_kritis(n)
        total = mat.sum(axis=1)
        butir: list[dict[str, Any]] = []
        for i, c in enumerate(ada):
            r = _r(mat[:, i], total - mat[:, i])     # butir–total terkoreksi
            lolos = bool(r == r and rk is not None and r >= rk and r > 0)
            semua_lolos = semua_lolos and lolos
            butir.append({'butir': c, 'r': _f(r), 'r_kritis': _f(rk),
                          'lolos': lolos})
        lolos_alpha = bool(alpha == alpha and alpha >= ALPHA_MIN)
        semua_lolos = semua_lolos and lolos_alpha
        variabel.append({
            'nama': nama, 'n': n, 'butir': butir,
            'alpha': _f(alpha), 'alpha_min': ALPHA_MIN,
            'lolos_alpha': lolos_alpha,
            'catatan': ([] if n >= N_MIN_PRA else
                        [f'Responden baru {n} orang — hasil pemeriksaan '
                         f'belum kokoh, disarankan minimal {N_MIN_PRA}.']),
        })
    return {'tahap': 'pra-survei', 'n': int(len(df)),
            'variabel': variabel, 'semua_lolos': semua_lolos}


# ══════════════════════════════════════════════════════════════════════════
# RUTE — dibuat lewat pabrik supaya memakai penolong yang sama dengan
# rute lama di main.py (penggabung peran + penghias hasil): SATU sumber,
# hasil pintu baru dijamin sama dengan alur lama untuk data yang sama.
# ══════════════════════════════════════════════════════════════════════════
def buat_router(gabung_peran, hias_hasil) -> APIRouter:
    router = APIRouter()

    @router.get('/api/jembatan/status')
    async def jembatan_status():
        return {'layanan': 'jembatan-eduai', 'ok': True,
                'kunci_terpasang': bool(os.environ.get(ENV_KUNCI))}

    @router.post('/api/jembatan/hitung')
    async def jembatan_hitung(payload: dict,
                              x_kunci_layanan: str | None = Header(default=None)):
        kunci_server = os.environ.get(ENV_KUNCI) or ''
        if not kunci_server:
            raise HTTPException(status_code=503, detail=(
                'Kunci antar-layanan belum dipasang di server Statistik '
                'Lab. Pemilik server perlu memasangnya dulu.'))
        if not x_kunci_layanan or not secrets.compare_digest(
                x_kunci_layanan, kunci_server):
            raise HTTPException(status_code=401, detail=(
                'Kunci antar-layanan tidak dikenal.'))

        from app.diagnosis import periksa_spss, periksa_pls, GagalBaca

        baris = payload.get('baris')
        if not isinstance(baris, list) or not baris:
            raise HTTPException(status_code=400, detail=(
                'Data kosong — kirim "baris": daftar baris data '
                '(satu objek per responden).'))
        try:
            df = pd.DataFrame(baris)
        except Exception:
            raise HTTPException(status_code=400, detail=(
                'Bentuk data tidak bisa dibaca sebagai tabel.'))

        tahap = str(payload.get('tahap', 'utama'))
        try:
            if tahap == 'pra-survei':
                konstruk = payload.get('konstruk') or None
                if not konstruk and isinstance(payload.get('peran'), dict):
                    kelompok: dict[str, list[str]] = {}
                    for kolom, peran in payload['peran'].items():
                        if peran:
                            kelompok.setdefault(str(peran), []).append(kolom)
                    konstruk = kelompok or None
                return periksa_pra_survei(df, konstruk)

            # ── Tahap utama: jalur yang sama persis dengan rute lama ──
            df2, payload2 = gabung_peran(df, dict(payload))
            mode = str(payload2.get('mode', 'spss'))
            missing = str(payload2.get('missing', 'buang'))
            buang_kosong = 'rata' if missing == 'rata' else 'baris'
            if mode == 'pls':
                r = periksa_pls(df2, payload2.get('konstruk') or {},
                                str(payload2.get('kolom_y_konstruk') or ''))
            else:
                r = periksa_spss(df2, payload2.get('kolom_x') or [],
                                 str(payload2.get('kolom_y') or ''),
                                 kolom_m=payload2.get('kolom_m') or [],
                                 kolom_z=payload2.get('kolom_z') or [],
                                 bentuk_mediasi=payload2.get('bentuk_mediasi'),
                                 buang_kosong=buang_kosong)
            return hias_hasil(r, mode)
        except GagalBaca as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
