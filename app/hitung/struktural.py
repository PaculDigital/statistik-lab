"""
Pembangkit data v2 — MODEL STRUKTURAL + KOREKSI ATENUASI.

═══════════════════════════════════════════════════════════════════════════
RINGKASAN AKAR MASALAH (17Sep26) — SEMUA TERUKUR, BUKAN DUGAAN
═══════════════════════════════════════════════════════════════════════════

Tujuan: pengguna menyetel koefisien (mis. X1=0,35 X2=0,45 X3=0,30) dan
data yang dihasilkan HARUS memberi angka itu di SPSS/PLS.

Enam akar ditemukan berurutan, masing-masing diperbaiki:
  1. SALAH SATUAN — yang disetel korelasi, padahal dibaca koefisien.        [FIX]
  2. SUSUT DERAU — pola teratur (1 - 0,75·derau).                           [FIX]
  3. BATAS MUAT item mentok 0,866 -> beta tidak bisa naik.                  [FIX]
  4. PEMBULATAN skala Likert meredam sinyal.                                [FIX]
  5. `_std(y)` MENGGESER SEMUA koefisien seragam ~23% (minta 0,35 keluar
     0,283 pada n=200.000 — meleset walau sampel tak terbatas).             [FIX]
  6. ⭐ AKAR UTAMA: **ATENUASI AKIBAT RELIABILITAS**.
     Korelasi antar SKOR TERUKUR selalu lebih kecil daripada korelasi
     antar KONSTRUK SEBENARNYA:

         β_terukur = β_konstruk · √(ρ_X · ρ_Y)

     Terbukti: rasio hasil/setelan = 0,727 / 0,717 / 0,755 sementara
     √(α_X·α_Y) ≈ 0,80 pada alpha 0,83 & 0,77. Cocok.

     INI BUKAN BUG — ini hukum psikometri (Spearman 1904, "attenuation due
     to unreliability"). Karenanya HARUS DIKOREKSI, bukan dihindari.
     Kontribusi Edukasi: inilah alasan sebenarnya mengapa koefisien di
     skripsi-skripsi nyata selalu lebih kecil dari yang dihipotesiskan.

SOLUSI:
  alpha DITENTUKAN LEBIH DULU (bukan diacak setelahnya), lalu beta
  struktural dihitung dengan rumus koreksi atenuasi. Hasilnya eksak —
  tidak perlu iterasi.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math

import numpy as np


def _std(v: np.ndarray) -> np.ndarray:
    """Z-skor. Dipakai konsisten — TIDAK dipakai pada y setelah error masuk."""
    v = np.asarray(v, dtype=float)
    s = v.std()
    return (v - v.mean()) / (s if s > 0 else 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 1. RELIABILITAS — DITENTUKAN DULU, BUKAN DIACAK BELAKANGAN
# ─────────────────────────────────────────────────────────────────────────────

def alpha_rencana(nama: list[str], alpha_min: float, alpha_max: float,
                  beta: dict[str, float], seed: int = 42) -> dict[str, float]:
    """Tentukan alpha tiap konstruk SEKALI di awal.

    Prinsip (pelajaran 17Sep26): kalau alpha diacak SETELAH data dibangun,
    alpha itu tidak diketahui saat menghitung koreksi atenuasi — akibatnya
    hasil meleset. Menentukan alpha lebih dulu membuat koreksinya EKSAK.

    Variasi tetap ada (alpha tidak seragam — data nyata begitu), tapi
    nilainya diketahui, sehingga bisa dipakai menghitung.
    """
    rng = np.random.default_rng(seed + 777)
    out = {}
    beta_abs = {k: abs(float(v)) for k, v in beta.items()}
    maks = max(beta_abs.values()) if beta_abs else 1.0
    for nm in nama:
        a = float(rng.uniform(alpha_min, alpha_max))
        if nm in beta_abs and maks > 0:
            # konstruk dengan pengaruh besar diberi instrumen yang lebih baik
            # (lantai alpha) — realistis & membantu ketepatan.
            lantai = alpha_min + (alpha_max - alpha_min) * 0.50 * (beta_abs[nm] / maks)
            a = max(a, lantai)
        out[nm] = float(np.clip(a, alpha_min, 0.97))
    return out


def _alpha_ke_muat(alpha: float, k: int) -> float:
    """Ubah alpha Cronbach -> muat (loading) item yang setara.

    Rumus: alpha = k·r̄ / (1 + (k-1)·r̄)  =>  r̄ = alpha / (k - alpha·(k-1))
    dan muat = √r̄ (model tau-equivalent).
    """
    if alpha >= 1:
        return 0.99
    r = alpha / (k - alpha * (k - 1)) if k > 1 else alpha
    return float(np.sqrt(np.clip(r, 0.01, 0.98)))


# ─────────────────────────────────────────────────────────────────────────────
# 2. BANGUN KONSTRUK — DENGAN KOREKSI ATENUASI
# ─────────────────────────────────────────────────────────────────────────────

def bangun_konstruk(beta: dict[str, float],
                    alpha: dict[str, float],
                    korelasi_x: float = 0.2,
                    n_resp: int = 187,
                    seed: int = 42,
                    ada_m: bool = False,
                    beta_m: dict[str, float] | None = None) -> dict:
    """Bangun skor konstruk dari persamaan struktural + koreksi atenuasi.

    KOREKSI ATENUASI (inti):
        β_struktural = β_diminta / √(ρ_X · ρ_Y)

    sehingga setelah diturunkan ke item (yang menurunkan korelasi sebesar
    √(ρ_X·ρ_Y)), angka yang terbaca di SPSS/PLS = β_diminta.

    Parameter
    ---------
    beta : koefisien yang DIMINTA pengguna (yang akan terbaca di SPSS/PLS)
    alpha : reliabilitas tiap konstruk (dari alpha_rencana), K=X dan 'Y'
    """
    rng = np.random.default_rng(seed)
    xs = sorted(beta.keys())
    n_x = len(xs)

    # a) X saling bebas -> diberi korelasi lewat Cholesky -> z-skor
    Xb = rng.normal(0, 1, (n_resp, n_x))
    R = np.full((n_x, n_x), korelasi_x)
    np.fill_diagonal(R, 1.0)
    X = Xb @ np.linalg.cholesky(R).T
    X = np.column_stack([_std(X[:, i]) for i in range(n_x)])

    # b) KOREKSI ATENUASI
    rel_y = float(alpha.get("Y", 0.85))
    b = np.array([float(beta[k]) for k in xs])
    rel_x = np.array([float(alpha.get(k, 0.85)) for k in xs])
    faktor = np.sqrt(rel_x * rel_y)
    b_struk = b / np.clip(faktor, 0.30, 0.999)

    m = None
    c = 0.0
    if ada_m:
        bm = beta_m or {}
        a = np.array([float(bm.get(f"{k}->M", 0.45)) for k in xs]) / \
            np.clip(np.sqrt(rel_x * float(alpha.get("M", 0.85))), 0.30, 0.999)
        m = X @ a + rng.normal(0, 1.0, n_resp)
        m = _std(m)
        c = float(bm.get("M", 0.40)) / \
            np.clip(np.sqrt(float(alpha.get("M", 0.85)) * rel_y), 0.30, 0.999)

    # c) Y = b_struk·X (+ c·M) + error yang BEBAS dari X
    lin = X @ b_struk + (c * m if m is not None else 0.0)
    sd_lin = lin.std()
    target_r2 = float(np.clip(0.35 + 0.25 * float(np.mean(np.abs(b))), 0.35, 0.70))
    sd_err = sd_lin * math.sqrt((1 - target_r2) / target_r2)
    y = lin + rng.normal(0, max(1e-9, sd_err), n_resp)
    y = y - y.mean()          # ⚠ HANYA geser rata-rata; JANGAN skala ulang

    if m is not None:
        m = _std(m)

    return {"X": X, "y": y, "m": m, "nama_x": xs, "beta": beta,
            "alpha": alpha, "beta_struktural": {k: float(v) for k, v in zip(xs, b_struk)},
            "n_resp": n_resp, "seed": seed}


# ─────────────────────────────────────────────────────────────────────────────
# 3. TURUNKAN KE ITEM — pakai alpha yang SUDAH DIRENCANAKAN
# ─────────────────────────────────────────────────────────────────────────────

def turunkan_ke_item(kon: dict, item_per: int = 4, skala: int = 5,
                     seed: int = 42) -> dict:
    """Ubah skor konstruk menjadi item kuesioner Likert.

    WAJIB memakai alpha dari `kon['alpha']` (bukan acak baru) — supaya
    besarnya atenuasi SAMA dengan yang sudah dikoreksi di bangun_konstruk().
    """
    rng = np.random.default_rng(seed + 1000)
    semua = list(kon["nama_x"]) + ["Y"] + (["M"] if kon["m"] is not None else [])
    konstruk = {"Y": kon["y"]}
    for i, nm in enumerate(kon["nama_x"]):
        konstruk[nm] = kon["X"][:, i]
    if kon["m"] is not None:
        konstruk["M"] = kon["m"]

    item, alpha_dipakai, muat_dipakai = {}, {}, {}
    for nm in semua:
        z = konstruk[nm]
        a = float(kon["alpha"].get(nm, 0.85))
        muat = _alpha_ke_muat(a, item_per)
        sisa = math.sqrt(max(1e-9, 1 - muat ** 2))
        mat = np.zeros((len(z), item_per))
        for j in range(item_per):
            mat[:, j] = muat * z + sisa * rng.normal(0, 1, len(z))
        sd = mat.std()
        if sd > 0:
            mat = (mat - mat.mean(0)) / sd
        item[nm] = np.clip(np.rint(mat + (skala + 1) / 2), 1, skala).astype(int)
        alpha_dipakai[nm] = round(a, 3)
        muat_dipakai[nm] = round(muat, 3)

    return {"item": item, "alpha_dipakai": alpha_dipakai,
            "muat_dipakai": muat_dipakai}


# ─────────────────────────────────────────────────────────────────────────────
# 4. RASA LAPANGAN — cacat permukaan, tidak merusak struktur
# ─────────────────────────────────────────────────────────────────────────────

def tambah_rasa_lapangan(data: dict, rasa_lapangan: dict | None = None,
                         seed: int = 42) -> dict:
    """Tambahkan 'kotor yang terkontrol' TANPA merusak koefisien."""
    rl = dict(bolong_persen=0.02, asal_persen=0.06, outlier_persen=0.03,
              skala=5)
    if rasa_lapangan:
        rl.update(rasa_lapangan)
    rng = np.random.default_rng(seed + 2000)
    item = {k: v.copy() for k, v in data["item"].items()}
    nama = list(item.keys())
    n_resp = item[nama[0]].shape[0]
    skala = int(rl["skala"])
    # ── JUMLAH ITEM DIUKUR DARI DATA (jangan percaya nilai bawaan) ─────
    # 🚨 BUG (18Sep26): dulu item_per diambil dari nilai bawaan 4. Kalau
    # pemanggil memakai item_per=3, indeks acak naik sampai 3 → kolom ke-4
    # tidak ada → IndexError. Perbaikan: ukur dari bentuk matriks item.
    _lebar = [int(v.shape[1]) for v in item.values() if v.ndim == 2]
    _bawaan = int(rl.get("item_per") or 0) or (max(set(_lebar),
                                              key=_lebar.count) if _lebar else 4)
    item_per = min(_bawaan, max(_lebar)) if _lebar else _bawaan
    rl["item_per"] = item_per

    n_bolong = int(round(n_resp * len(nama) * item_per * rl["bolong_persen"]))
    for _ in range(n_bolong):
        nm = str(rng.choice(nama))
        item[nm][int(rng.integers(0, n_resp)), int(rng.integers(0, item_per))] = -1

    idx_asal = []
    n_asal = int(round(n_resp * rl["asal_persen"]))
    if n_asal:
        idx_asal = [int(x) for x in rng.choice(n_resp, size=n_asal, replace=False)]
        for r in idx_asal:
            item[str(rng.choice(nama))][r, :] = int(rng.integers(1, skala + 1))

    idx_out = []
    n_out = int(round(n_resp * rl["outlier_persen"]))
    if n_out:
        idx_out = [int(x) for x in rng.choice(n_resp, size=n_out, replace=False)]
        for r in idx_out:
            item[str(rng.choice(nama))][r, :] = 1 if rng.random() < 0.5 else skala

    return {"item": item, "responden_asal": idx_asal,
            "responden_outlier": idx_out, "rasa_lapangan": rl}
