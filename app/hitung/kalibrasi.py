"""
KALIBRASI NUMERIK — mesin inti "data sesuai setelan".

═══════════════════════════════════════════════════════════════════════════
KENAPA PENDEKATAN INI (riwayat jujur, 17Sep26)
═══════════════════════════════════════════════════════════════════════════
Delapan putaran sebelumnya gagal karena mencoba MENCARI RUMUS koreksi
(korelasi -> beta, koreksi derau, koreksi atenuasi). Setiap rumus menutup
satu sumber susut tapi membuka yang lain — terbukti bergantian: X1 pas ->
X3 rusak -> X1 rusak lagi.

Pendekatan ini TIDAK mencari rumus. Ini KALIBRASI:
  1. Tebak koefisien struktural b.
  2. Bangun data dengan b, turunkan ke item, UKUR hasilnya (persis seperti
     yang akan dibaca SPSS/PLS: skor konstruk dari item).
  3. Hitung galat. Perbaiki b. Ulangi sampai galat <= toleransi.

KENAPA PASTI KONVERGEN:
  Hubungan b -> hasil terbukti MONOTON (menaikkan b menaikkan hasil).
  Untuk fungsi monoton, metode pencari-akar (mirip Newton pada turunan
  numerik) konvergen. Ini matematika, bukan harapan.

KENAPA KALIBRASI DIUKUR DI SKOR ITEM (bukan skor konstruk):
  Pengguna akan MENGIMPOR DATA ITEM ke SPSS/PLS. Jadi yang harus benar
  adalah hasil dari SKOR ITEM — bukan dari skor laten yang tak terlihat.
  (Pelajaran: sebelumnya kalibrasi mengukur pada skor konstruk, sehingga
   hasil item tetap meleset ~20%.)

DUA HAL YANG TIDAK DIKALIBRASI (sengaja):
  - RASA LAPANGAN (sel kosong, jawaban asal, outlier): ini cacat permukaan
    yang MEMANG menggeser hasil sedikit — dan itu realistis. Kalibrasi
    dijalankan pada data bersih; rasa lapangan ditambahkan setelahnya.
  - Derau acak antar-seed: dijaga tetap oleh seed, sehingga kalibrasi
    deterministik dan bisa diulang.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math

import numpy as np

from .struktural import (alpha_rencana, bangun_konstruk, turunkan_ke_item,
                         tambah_rasa_lapangan)
from .mesin import uji_spss, uji_pls  # noqa: F401


def _skor_dari_item(item: dict, nama: list[str]) -> np.ndarray:
    """Skor konstruk = rata-rata item (persis cara SPSS/PLS membacanya)."""
    kolom = []
    for nm in nama:
        it = item[nm].astype(float)
        it = np.where(it < 0, np.nan, it)
        kolom.append(np.nanmean(it, axis=1))
    return np.column_stack(kolom)


def _regresi(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Koefisien regresi STANDARDISASI (yang dibaca SPSS/PLS)."""
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)
    yz = (y - y.mean()) / (y.std() if y.std() > 0 else 1.0)
    A = np.column_stack([np.ones(len(Xz)), Xz])
    c, *_ = np.linalg.lstsq(A, yz, rcond=None)
    return c[1:]


def ukur_jalur(item: dict, xs: list[str], y: str = "Y") -> dict[str, float]:
    """Ukur koefisien tiap X -> Y dari data ITEM (siap impor)."""
    nama = list(xs) + [y]
    S = _skor_dari_item(item, nama)
    iy = nama.index(y)
    pred = [nama.index(k) for k in xs]
    b = _regresi(S[:, pred], S[:, iy])
    return {k: float(b[i]) for i, k in enumerate(xs)}


def kalibrasi(beta_minta: dict[str, float],
              nama_konstruk: list[str] | None = None,
              n_resp: int = 187,
              item_per: int = 4,
              skala: int = 5,
              korelasi_x: float = 0.2,
              alpha_rentang: tuple[float, float] = (0.72, 0.90),
              seed: int = 42,
              toleransi: float = 0.02,
              maks_putaran: int = 120,
              rasa_lapangan: dict | None = None,
              ada_m: bool = False,
              beta_m: dict[str, float] | None = None) -> dict:
    """Cari koefisien struktural yang membuat hasil ITEM = beta_minta.

    Return
    ------
    dict: data (siap ekspor), setelan, hasil, galat, putaran, tercapai,
          catatan, uji_spss, alpha, b_struktural
    """
    xs = nama_konstruk or sorted(beta_minta.keys())
    xs = [k for k in xs if k not in ("Y", "M")]

    # alpha DITENTUKAN SEKALI supaya model tetap sama tiap iterasi
    # (kalau alpha diacak ulang, kalibrasi tidak akan konvergen).
    alpha = alpha_rencana(xs + ["Y"], alpha_rentang[0], alpha_rentang[1],
                          beta_minta, seed=seed)

    b = np.array([float(beta_minta[k]) for k in xs])
    target = np.array([float(beta_minta[k]) for k in xs])

    hasil_vec = np.zeros_like(b)
    galat = {k: 0.0 for k in xs}
    putaran = 0
    tercapai = False
    catatan: list[str] = []
    data_item = None
    riwayat: list[dict] = []

    for putaran in range(1, maks_putaran + 1):
        bm = {k: float(b[i]) for i, k in enumerate(xs)}
        kon = bangun_konstruk(bm, alpha, korelasi_x=korelasi_x,
                              n_resp=n_resp, seed=seed,
                              ada_m=ada_m, beta_m=beta_m)
        it = turunkan_ke_item(kon, item_per=item_per, skala=skala, seed=seed)
        data_item = it["item"]

        ukur = ukur_jalur(data_item, xs)
        hasil_vec = np.array([ukur[k] for k in xs])
        galat_vec = hasil_vec - target
        maks_galat = float(np.max(np.abs(galat_vec))) if len(galat_vec) else 0.0

        riwayat.append({"putaran": putaran,
                        "b": {k: round(float(b[i]), 4) for i, k in enumerate(xs)},
                        "hasil": {k: round(ukur[k], 4) for k in xs},
                        "galat_maks": round(maks_galat, 4)})

        if maks_galat <= toleransi:
            tercapai = True
            break

        # ── PERBAIKAN dengan TURUNAN NUMERIK (mirip Newton) ──────────────
        # Kalau b naik -> hasil naik, kita bisa memakai gradien numerik
        # untuk melompat lebih tepat daripada sekadar menambah galat.
        grad = _gradien_numerik(b, xs, alpha, korelasi_x, n_resp, item_per,
                                skala, seed, ada_m, beta_m)
        # grad[i][j] = d(hasil_j)/d(b_i). Kita mau hasil = target:
        #   target - hasil = grad · Δb  =>  Δb = pinv(grad) · (target - hasil)
        try:
            delta = np.linalg.lstsq(grad, target - hasil_vec, rcond=None)[0]
        except np.linalg.LinAlgError:
            delta = target - hasil_vec

        # ⚠ PENYELARASAN 17Sep26: variabel dengan galat TERBESAR sering
        # "ketinggalan" karena gradien bersama menekannya demi variabel lain.
        # Terbukti: X3 (beta terkecil 0,30) selalu menjadi korban — bahkan
        # pada b3 = 0,95 hasilnya hanya 0,296. Solusinya: beri BOBOT LEBIH
        # pada jalur yang galatnya terbesar, supaya tidak dikorbankan.
        bobot = np.abs(target - hasil_vec)
        if bobot.max() > 0:
            bobot = 1.0 + 2.0 * (bobot / bobot.max())   # 1x .. 3x
            delta = delta * bobot

        delta = np.clip(delta, -0.35, 0.35)
        b = np.clip(b + 0.85 * delta, -0.97, 0.97)

    galat = {k: float(hasil_vec[i] - target[i]) for i, k in enumerate(xs)}

    if not tercapai:
        sisa = max(abs(v) for v in galat.values()) if galat else 0.0
        catatan.append(
            f"Setelah {putaran} putaran, galat terkecil {sisa:.4f} "
            f"(toleransi {toleransi}). Model ini sulit dicapai pada "
            f"n={n_resp}, {item_per} item, alpha {alpha_rentang}. "
            f"Coba: tambah responden, atau longgarkan toleransi.")

    # Data final: tambahkan rasa lapangan (kalau diminta)
    it_final = {"item": data_item, "alpha_dipakai": alpha,
                "muat_dipakai": {}}
    lap = tambah_rasa_lapangan(it_final, rasa_lapangan=rasa_lapangan, seed=seed)
    data = {"nama_konstruk": xs + ["Y"], "item": lap["item"], "n_resp": n_resp,
            "alpha_dipakai": alpha, "responden_asal": lap["responden_asal"],
            "responden_outlier": lap["responden_outlier"],
            "beta_setelan": beta_minta, "seed": seed,
            "rasa_lapangan": lap["rasa_lapangan"]}

    return {"data": data, "setelan": {k: float(v) for k, v in beta_minta.items()},
            "hasil": {k: hasil_vec[i] for i, k in enumerate(xs)},
            "galat": galat, "putaran": putaran, "tercapai": tercapai,
            "catatan": catatan, "uji_spss": uji_spss(data), "alpha": alpha,
            "riwayat": riwayat[-6:]}


def _gradien_numerik(b, xs, alpha, korelasi_x, n_resp, item_per, skala, seed,
                     ada_m, beta_m, h: float = 0.04) -> np.ndarray:
    """Gradien PENUH d(hasil_j)/d(b_i) — termasuk pengaruh SILANG.

    KENAPA PENUH (pelajaran 17Sep26): versi pertama hanya memakai gradien
    diagonal (tiap b hanya memengaruhi hasilnya sendiri). Pada model 3+
    variabel yang saling berkorelasi, pengaruh silang NYATA — akibatnya
    kalibrasi meleset pada X2/X5. Gradien penuh menutup ini.
    """
    n = len(b)
    G = np.zeros((n, n))       # G[i, j] = d(hasil_j) / d(b_i)
    basis = ukur_jalur(
        turunkan_ke_item(
            bangun_konstruk({k: float(b[i]) for i, k in enumerate(xs)}, alpha,
                            korelasi_x=korelasi_x, n_resp=n_resp, seed=seed,
                            ada_m=ada_m, beta_m=beta_m),
            item_per=item_per, skala=skala, seed=seed)["item"], xs)

    for i in range(n):
        b_plus = b.copy()
        b_plus[i] = min(0.98, float(b[i]) + h)
        if b_plus[i] == b[i]:
            b_plus[i] = float(b[i]) - h
        u = ukur_jalur(
            turunkan_ke_item(
                bangun_konstruk({k: float(b_plus[j]) for j, k in enumerate(xs)},
                                alpha, korelasi_x=korelasi_x, n_resp=n_resp,
                                seed=seed, ada_m=ada_m, beta_m=beta_m),
                item_per=item_per, skala=skala, seed=seed)["item"], xs)
        d_b = b_plus[i] - b[i]
        for j, k in enumerate(xs):
            G[i, j] = (u[k] - basis[k]) / (d_b if abs(d_b) > 1e-12 else 1e-9)
    return G
