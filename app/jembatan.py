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
    'KP1' → 'KP'. Pola yang sama dipakai template instrumen EduAi.

    KETAT (temuan review 21 Okt): kolom TANPA nomor butir di ujung
    ('Kualitas', 'Harga') BUKAN butir — jangan digabung/dijadikan
    variabel sendiri diam-diam. Kumpulkan dan laporkan lewat GagalBaca
    supaya pengirim membetulkan nama kolom atau mengirim konstruk
    eksplisit."""
    from app.diagnosis import GagalBaca
    keluar: dict[str, list[str]] = {}
    tak_berpola: list[str] = []
    for c in kolom:
        m = re.match(r'^(.*?)[_\s]?\d+$', str(c))
        if m and m.group(1):
            keluar.setdefault(m.group(1), []).append(c)
        else:
            tak_berpola.append(str(c))
    if tak_berpola:
        raise GagalBaca(
            'Kolom ini tidak mengikuti pola nama butir (Nama_Variabel_Nomor): '
            + ', '.join(tak_berpola)
            + '. Betulkan nama kolomnya, atau kirim pengelompokan "konstruk" '
              'secara eksplisit.')
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


def _grup_butir(kolom: str) -> str:
    """Nama variabel induk dari nama butir: 'Keaslian_2' → 'Keaslian',
    'KP2' → 'KP'. Tanpa pola nomor → kolom itu sendiri."""
    m = re.match(r'^(.*?)[_\s]?\d+$', str(kolom))
    return m.group(1) if m and m.group(1) else str(kolom)


def _cek_belah_variabel(pemilik: dict[str, str], konteks: str) -> None:
    """Satu variabel induk tidak boleh terbelah ke dua pemilik berbeda.

    Ini bolong BUG 3 yang sebenarnya (temuan review kedua, 21 Okt):
    butir-butir SATU variabel (mis. Keaslian_1, Keaslian_2, Keaslian_3)
    bisa ditandai sebagian X dan sebagian Y — sesudah skor digabung,
    variabel yang sama berdiri di dua sisi persamaan dan mesin
    menghitungnya diam-diam. pemilik: {butir: nama pemiliknya}."""
    from app.diagnosis import GagalBaca
    grup: dict[str, str] = {}
    for butir, punya in pemilik.items():
        g = _grup_butir(butir)
        if g in grup and grup[g] != punya:
            raise GagalBaca(
                f'Variabel "{g}" terbelah di {konteks}: sebagian butirnya '
                f'masuk "{grup[g]}", sebagian masuk "{punya}". Satu '
                f'variabel hanya boleh berdiri di satu sisi.')
        grup[g] = punya


def _cek_tumpang_tindih(payload: dict, efektif: bool = False) -> None:
    """Pagar peran — menolak penandaan yang membuat data tidak sah.

    Tiga lapis (temuan review 21 Okt: pagar versi pertama BUTA untuk
    bentuk `peran` karena hanya membaca kolom_x/kolom_y):
      A. Bentuk tunggal — `peran` dan bentuk eksplisit (kolom_x dst /
         konstruk) tidak boleh dicampur dalam satu kiriman; perintah
         yang ambigu ditolak, bukan ditebak.
      B. Belah variabel — pada kiriman `peran`, keluarga peran (huruf
         depan: X/M/Z/Y) satu variabel induk harus satu.
      C. Tumpang tindih persis — satu kolom/butir memegang dua peran
         (SPSS eksplisit) atau masuk dua konstruk (PLS eksplisit,
         termasuk belah variabel antar konstruk).
    Pagar ini dipanggil pada payload MENTAH dan — di penangan — sekali
    lagi pada payload EFEKTIF hasil gabung_peran, yaitu persis yang
    akan dihitung mesin."""
    from app.diagnosis import GagalBaca
    mode = str(payload.get('mode', 'spss'))
    peran = payload.get('peran') or {}
    eksplisit = any(payload.get(k) for k in
                    ('kolom_x', 'kolom_y', 'kolom_m', 'kolom_z', 'konstruk'))

    # A — bentuk tunggal (tidak berlaku untuk panggilan efektif:
    # hasil gabung_peran memang selalu memuat sisa 'peran' + kolom hasil)
    if efektif:
        peran = {}
    if peran and eksplisit:
        raise GagalBaca(
            'Kirim SATU bentuk penandaan saja: "peran" ATAU kolom '
            'eksplisit (kolom_x/kolom_y/konstruk) — jangan dicampur, '
            'perintahnya jadi ambigu.')

    # B — peran: keluarga satu variabel induk harus satu
    if isinstance(peran, dict) and peran:
        pemilik = {str(k): str(v).strip().upper()[:1]
                   for k, v in peran.items() if v not in (None, '', '-')}
        _cek_belah_variabel(pemilik, 'penandaan peran')
        return

    # C — eksplisit
    if mode == 'pls':
        pemilik: dict[str, str] = {}
        for nama, cols in (payload.get('konstruk') or {}).items():
            for c in cols or []:
                if c in pemilik:
                    raise GagalBaca(
                        f'Butir "{c}" masuk dua konstruk sekaligus '
                        f'("{pemilik[c]}" dan "{nama}"). Satu butir hanya '
                        f'boleh milik satu konstruk.')
                pemilik[c] = nama
        _cek_belah_variabel(pemilik, 'konstruk')
        return
    grup = {
        'X': [str(c) for c in (payload.get('kolom_x') or [])],
        'M (perantara)': [str(c) for c in (payload.get('kolom_m') or [])],
        'Z (penguat)': [str(c) for c in (payload.get('kolom_z') or [])],
        'Y': [str(payload['kolom_y'])] if payload.get('kolom_y') else [],
    }
    pemilik2: dict[str, str] = {}
    for nama_peran, cols in grup.items():
        for c in cols:
            if c in pemilik2:
                raise GagalBaca(
                    f'Kolom "{c}" memegang dua peran sekaligus '
                    f'({pemilik2[c]} dan {nama_peran}). Satu kolom hanya '
                    f'boleh satu peran.')
            pemilik2[c] = nama_peran


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

    def _wajib_kunci(x_kunci_layanan: str | None) -> None:
        kunci_server = os.environ.get(ENV_KUNCI) or ''
        if not kunci_server:
            raise HTTPException(status_code=503, detail=(
                'Kunci antar-layanan belum dipasang di server Statistik '
                'Lab. Pemilik server perlu memasangnya dulu.'))
        # BUG (temuan review 21 Okt): compare_digest pada str non-ASCII
        # melempar TypeError → 500. Encode ke bytes dulu supaya kunci
        # aneh apa pun ditolak rapi dengan 401.
        cocok = bool(x_kunci_layanan) and secrets.compare_digest(
            str(x_kunci_layanan).encode('utf-8'),
            kunci_server.encode('utf-8'))
        if not cocok:
            raise HTTPException(status_code=401, detail=(
                'Kunci antar-layanan tidak dikenal.'))

    @router.post('/api/jembatan/hitung')
    async def jembatan_hitung(payload: dict,
                              x_kunci_layanan: str | None = Header(default=None)):
        _wajib_kunci(x_kunci_layanan)

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

            # ── Pagar peran (temuan review 21 Okt): satu kolom tidak
            # boleh memegang dua peran sekaligus (mis. jadi X dan Y) —
            # data seperti itu tidak sah tapi tadinya tetap dihitung.
            _cek_tumpang_tindih(payload)

            # ── Tahap utama: jalur yang sama persis dengan rute lama ──
            df2, payload2 = gabung_peran(df, dict(payload))
            # Pagar diulang pada bentuk EFEKTIF — persis yang dihitung
            # mesin — supaya bentuk kiriman apa pun tidak bisa lolos.
            _cek_tumpang_tindih(payload2, efektif=True)
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

    @router.post('/api/jembatan/simulasi')
    async def jembatan_simulasi(payload: dict,
                                x_kunci_layanan: str | None = Header(default=None)):
        """BUAT DATA untuk simulasi EduAi (Fase 3 sisa, 21 Okt 2026).

        Data latihan TERKALIBRASI per jalur dari mesin BUAT DATA
        (app.berkas_kerja.buat_data_jalur) — AI tidak mengarang angka.
        Tanpa simpan apa pun (Opsi B): data dibuat, dikirim, selesai.

        Kiriman: {model, n, nama: {x/m/z/y/m1/m2: label},
                  params: {a/b/langsung/bx/bz/interaksi/a1/a2/b1/b2/d},
                  konstruk: [{kode: 'X'|'M'|'M1'|'M2'|'Z'|'Y',
                              nama_kolom: 'Keaslian_Streamer', butir: 4}]}
        Balasan: {kolom, baris, laporan: {tercapai, galat_maks, model,
                  diminta}} — kolom diganti nama sesuai peta EduAi dan
        jumlah butir disesuaikan (ditambah dari skor konstruk variabel
        itu sendiri / dipotong) supaya SAMA PERSIS template EduAi.
        """
        _wajib_kunci(x_kunci_layanan)
        from app.berkas_kerja import buat_data_jalur
        model = str(payload.get('model') or '')
        konstruk = payload.get('konstruk') or []
        if not konstruk:
            raise HTTPException(400, 'Daftar konstruk kosong.')
        try:
            r = buat_data_jalur(model, int(payload.get('n') or 120),
                                payload.get('params') or {},
                                payload.get('nama') or {})
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
        except Exception as e:  # noqa: BLE001
            raise HTTPException(502, f'Mesin BUAT DATA gagal: {e}') from e
        item = (r.get('data') or {}).get('item') or {}
        skor = (r.get('data') or {}).get('skor_konstruk') or {}
        import numpy as np
        rng = np.random.default_rng(21)
        kolom: list[str] = []
        per_kolom: list[list[int]] = []
        for k in konstruk:
            kode = str(k.get('kode') or '')
            dasar = str(k.get('nama_kolom') or kode)
            mau = max(1, min(15, int(k.get('butir') or 3)))
            mat = item.get(kode)
            if mat is None:
                raise HTTPException(
                    400, f'Konstruk {kode} tidak dihasilkan mesin '
                         f'untuk model {model}.')
            mat = np.asarray(mat, dtype=float)
            punya = mat.shape[1]
            if mau < punya:
                mat = mat[:, :mau]
            elif mau > punya:
                # Butir tambahan dari pola responden SENDIRI pada
                # konstruk ini (rata-rata butirnya ± riuh kecil) —
                # bukan angka karangan bebas.
                dasar_resp = mat.mean(axis=1, keepdims=True)
                ekstra = np.clip(np.round(
                    dasar_resp + rng.normal(0, 0.45, (mat.shape[0], mau - punya))),
                    1, 5)
                mat = np.hstack([mat, ekstra])
            for j in range(mau):
                kolom.append(f'{dasar}_{j + 1}')
                per_kolom.append([int(x) for x in mat[:, j]])
        baris = [[per_kolom[j][i] for j in range(len(kolom))]
                 for i in range(len(per_kolom[0]) if per_kolom else 0)]
        return {'kolom': kolom, 'baris': baris,
                'laporan': {'model': model, 'n': len(baris),
                            'tercapai': r.get('tercapai'),
                            'galat_maks': r.get('galat_maks'),
                            'diminta': r.get('diminta')}}


    return router
