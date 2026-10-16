#!/usr/bin/env python3
"""ALAT UKUR UJI — pembuat data SAKIT + pemeriksa terpisah dari mesin.

⚠️ ATURAN INDUK (pelajaran 19Sep26, 6 putaran terbuang):
   SEBELUM menyalahkan MESIN, periksa DULU ALAT UKUR SENDIRI.
   Wulan mengejar mesin `app/diagnosis.py` 6 putaran padahal mesinnya BENAR
   sejak awal. Yang rusak: skrip ukur Wulan sendiri.

   3 CACAT SKRIP UKUR YANG PERNAH TERJADI (jangan ulang):
   ① `glejser_p(r, x)` TANPA `np.abs(r)` → Glejser WAJIB pakai |sisa|.
      Terukur: tanpa abs → p=1.000000 ; dengan abs → p=0.000000 (0/20 vs 20/20).
   ② SATU `rng` dipakai untuk banyak uji → data belakangan bukan data segar,
      menghasilkan p=1.000000 yang MUSTAHIL. → tiap uji benih SENDIRI.
   ③ SATU benih dianggap cukup → hasil bisa kebetulan. → pakai BANYAK benih,
      laporkan BERAPA dari N yang terdeteksi.

ATURAN: pembuat data ini TIDAK mengimpor app/ — supaya bisa jadi pembanding
INDEPENDEN. Kalau pembanding ikut memakai mesin, ia tidak membandingkan apa pun.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
from scipy import stats as st

# ══════════════════════════════════════════════════════════════════════════
# HITUNGAN DASAR (tulis-tangan, TIDAK pakai app/)
# ══════════════════════════════════════════════════════════════════════════
def regresi(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """OLS sederhana → (koefisien, sisa)."""
    A = np.column_stack([np.ones(len(x)), x])
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    return c, y - A @ c


def glejser_p(sisa: np.ndarray, x: np.ndarray) -> float:
    """Glejser: regresi |SISA| pada x, ambil p koefisien x.

    ⚠️ CACAT #1 — `np.abs()` WAJIB. Ini yang pernah hilang dan menghabiskan
    6 putaran. Kalau `sisa` dikirim mentah, p jadi ~1,0 (tidak terdeteksi).
    """
    ar = np.abs(sisa)                       # ← JANGAN DIHAPUS
    A = np.column_stack([np.ones(len(x)), x])
    c, *_ = np.linalg.lstsq(A, ar, rcond=None)
    rr = ar - A @ c
    k = A.shape[1]
    if len(x) <= k:
        return float('nan')
    s2 = float(rr @ rr) / (len(x) - k)
    se = np.sqrt(np.diag(s2 * np.linalg.pinv(A.T @ A)))
    t = c / np.where(se > 0, se, np.nan)
    # .sf() lebih aman daripada 1-cdf (1-cdf bisa underflow jadi 0)
    return float(2 * st.t.sf(np.abs(t), df=len(x) - k)[1])


def rasio_corong(x: np.ndarray, sisa: np.ndarray, q: float = 0.25) -> float:
    """Seberapa 'corong' datanya: SD sisa di X besar / SD sisa di X kecil.

    ≥ 1,5×  = corong terlihat mata
    ≥ 2,0×  = jelas
    ≥ 2,5×  = kuat, Glejser tidak mungkin melewatkan
    """
    lo, hi = float(np.quantile(x, q)), float(np.quantile(x, 1 - q))
    a, b = sisa[x <= lo], sisa[x >= hi]
    if len(a) < 3 or len(b) < 3:
        return float('nan')
    sa = float(np.std(a, ddof=1))
    return float(np.std(b, ddof=1) / sa) if sa > 0 else float('nan')


def breusch_pagan_p(sisa: np.ndarray, x: np.ndarray) -> float:
    """Breusch-Pagan: regresi sisa² pada x → LM = n·R² ~ chi²(1)."""
    from scipy.stats import chi2
    sq = sisa ** 2
    A = np.column_stack([np.ones(len(x)), x])
    c, *_ = np.linalg.lstsq(A, sq, rcond=None)
    rr = sq - A @ c
    ss_tot = float(np.sum((sq - sq.mean()) ** 2))
    if ss_tot <= 0:
        return float('nan')
    r2 = 1 - float(rr @ rr) / ss_tot
    return float(chi2.sf(len(x) * r2, 1))


# ══════════════════════════════════════════════════════════════════════════
# PEMBUAT DATA SAKIT — resep TERUKUR (bukan dikira)
# ══════════════════════════════════════════════════════════════════════════
def hetero_corong(rng: np.random.Generator, n: int,
                  x_min: float = 0.0, x_max: float = 6.0,
                  sd_dasar: float = 0.5, sd_miring: float = 1.0,
                  beta: float = 0.40) -> tuple[np.ndarray, np.ndarray]:
    """HETEROSKEDASTISITAS (corong) — X POSITIF, skala naik mengikuti X.

    ⚠️ TERUKUR 19Sep26 — kunci supaya corong BENAR-BENAR kelihatan:
      · X harus POSITIF & miring (0..6), BUKAN simetris (-3..3).
        X simetris → titik padat di tengah → corong TIDAK kelihatan.
      · skala naik MENGIKUTI x (bukan |x|) supaya hubungannya linier.
    Hasil terukur: rasio corong 4,15× → Glejser p = 0,000000 (20/20 terdeteksi).
    """
    x = rng.uniform(x_min, x_max, n)
    y = beta * x + rng.normal(0, 1, n) * (sd_dasar + sd_miring * x)
    return x, y


def homoskedastis(rng: np.random.Generator, n: int,
                  x_min: float = 0.0, x_max: float = 6.0,
                  sd: float = 1.0, beta: float = 0.40) -> tuple[np.ndarray, np.ndarray]:
    """Data BERsih — sebaran sisa rata (pembanding negatif)."""
    x = rng.uniform(x_min, x_max, n)
    return x, beta * x + rng.normal(0, sd, n)


def multikolinear(rng: np.random.Generator, n: int,
                  kemiripan: float = 0.995) -> tuple[np.ndarray, np.ndarray]:
    """MULTIKOLINEARITAS — X1 & X2 hampir kembar."""
    a = rng.normal(0, 1, n)
    b = a * kemiripan + rng.normal(0, 0.1, n)
    y = 0.4 * a + 0.3 * b + rng.normal(0, 1, n)
    return np.column_stack([a, b]), y


def beroutlier(rng: np.random.Generator, n: int,
               n_outlier: int = 2, jarak: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """OUTLIER — beberapa titik ekstrem di Y."""
    x = rng.normal(0, 1, n)
    y = 0.5 * x + rng.normal(0, 1, n)
    idx = rng.choice(n, n_outlier, replace=False)
    y[idx] = jarak * rng.choice([-1.0, 1.0], n_outlier)
    return x, y


# ══════════════════════════════════════════════════════════════════════════
# PEMERIKSA KESTABILAN — banyak benih, laporkan berapa yang terdeteksi
# ══════════════════════════════════════════════════════════════════════════
def ukur(nama: str, resep: Callable, n: int = 300, n_benih: int = 20,
         benih_dasar: int = 9000, harus_terdeteksi: bool = True) -> dict:
    """Uji satu resep pada BANYAK benih.

    ⚠️ CACAT #2 & #3 — tiap benih `default_rng(benih_dasar+i)` SENDIRI
    (bukan satu rng bersama), dan dipakai 20 benih (bukan 1).

    harus_terdeteksi=True  → minimal 90% benih harus bilang p < 0,05
    harus_terdeteksi=False → minimal 90% benih harus bilang p ≥ 0,05
    """
    det = 0
    rasio: list[float] = []
    p_gle: list[float] = []
    p_bp: list[float] = []
    for i in range(n_benih):
        rng = np.random.default_rng(benih_dasar + i)
        out = resep(rng, n)
        if isinstance(out[0], np.ndarray) and out[0].ndim == 2:
            X, y = out
            x = X[:, 0]                      # corong diukur pada X pertama
        else:
            x, y = out
        _, sisa = regresi(x, y)
        p = glejser_p(sisa, x)
        p_gle.append(p)
        p_bp.append(breusch_pagan_p(sisa, x))
        rasio.append(rasio_corong(x, sisa))
        if p < 0.05:
            det += 1
    persen = det / n_benih
    syarat = (persen >= 0.90) if harus_terdeteksi else (persen <= 0.10)
    return {
        'nama': nama, 'terdeteksi': det, 'n_benih': n_benih, 'persen': persen,
        'rasio_rata': float(np.nanmean(rasio)),
        'p_glejser_tengah': float(np.nanmedian(p_gle)),
        'p_bp_tengah': float(np.nanmedian(p_bp)),
        'lulus': syarat,
    }


def laporkan(h: dict) -> None:
    tanda = 'OK  ' if h['lulus'] else 'GAGAL'
    print(f"  [{tanda}] {h['nama']:<38} terdeteksi {h['terdeteksi']:>2}/{h['n_benih']}"
          f"   rasio {h['rasio_rata']:>5.2f}×   p tengah {h['p_glejser_tengah']:.2e}")
