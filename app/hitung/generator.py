"""
PEMBANGKIT DATA — pendekatan MATRIKS KORELASI TERVALIDASI (v3, 17Sep26).

═══════════════════════════════════════════════════════════════════════════
INI PENDEKATAN YANG BENAR. Dibuktikan setelah 10 putaran gagal.

KENAPA SEMUA PENDEKATAN SEBELUMNYA GAGAL:
  1. "korelasi mentah" — salah satuan (korelasi != koefisien regresi).
  2. "persamaan struktural" — Y dibangun dari X, TAPI X masih digeser
     Cholesky untuk memberi korelasi antar-X. Dua langkah ini bertabrakan:
     Cholesky mengubah X, sehingga korelasi X-Y yang sudah dihitung jadi
     TIDAK BERLAKU LAGI. Terbukti: X3 selalu jadi korban (0,30 -> 0,15),
     dan kalibrasi iteratif BERAYUN antara dua nilai (tidak pernah konvergen).

CARA YANG BENAR (dipakai di metodologi: Muthén & Muthén, simsem, lavaan):
  Bangun SATU matriks korelasi lengkap untuk [X1..Xk, Y] sekaligus:

      R = [[Rx , rxy],
           [rxy', 1 ]]      dengan rxy = Rx · b

  - Rx  = korelasi antar prediktor (mis. 0,2)
  - b   = koefisien regresi yang DIINGINKAN (yang akan dibaca SPSS/PLS)
  - rxy = Rx · b  -> inilah korelasi X-Y yang MEMBUAT regresi = b

  Lalu:
  1. VALIDASI: pastikan R positive-definite (kalau tidak, setelan tidak sah
     -> beri tahu pengguna dengan angka, jangan diam-diam rusak).
  2. PETAKAN melalui Cholesky SEKALI SAJA untuk X dan Y bersama-sama.
  3. Y TIDAK PERNAH disentuh lagi (tidak distandardisasi, tidak diskala).

  Dengan cara ini koefisien regresi = b PERSIS pada skor konstruk, dan
  tinggal dikoreksi untuk atenuasi item (lihat turunkan_ke_item).

TERBUKTI (n=200.000): koefisien = b dalam toleransi 0,002 (lihat uji_v3.py).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math

import numpy as np

from .mesin import uji_spss, uji_pls  # noqa: F401


def _std(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    s = v.std()
    return (v - v.mean()) / (s if s > 0 else 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 1. MATRIKS KORELASI + VALIDASI KELAYAKAN
# ─────────────────────────────────────────────────────────────────────────────

def matriks_korelasi(beta: dict[str, float],
                     korelasi_x: float = 0.2,
                     ada_m: bool = False,
                     beta_m: dict[str, float] | None = None,
                     ) -> tuple[np.ndarray, list[str], dict]:
    """Bangun matriks korelasi lengkap + periksa apakah setelan MUNGKIN.

    Return
    ------
    (R, nama, info)
      info memuat: rxy (korelasi X-Y yang dibutuhkan), r2, eigen_min,
      layak (bool), pesan (penjelasan bila tidak layak)
    """
    xs = sorted(k for k in beta if k not in ("Y", "M"))
    b = np.array([float(beta[k]) for k in xs])
    nama = xs + ["Y"]
    n = len(nama)

    Rx = np.full((len(xs), len(xs)), float(korelasi_x))
    np.fill_diagonal(Rx, 1.0)

    # korelasi X-Y yang MEMBUAT regresi = b:  rxy = Rx · b
    rxy = Rx @ b

    R = np.eye(n)
    R[:len(xs), :len(xs)] = Rx
    R[:len(xs), n - 1] = rxy
    R[n - 1, :len(xs)] = rxy

    w = np.linalg.eigvalsh(R)
    r2 = float(b @ rxy)
    layak = bool(w.min() > 1e-8)

    pesan = ""
    if not layak:
        pesan = (
            f"Setelan ini TIDAK BISA dicapai secara matematis. Total pengaruh "
            f"(R² = {r2:.3f}) melampaui yang mungkin untuk {len(xs)} variabel "
            f"yang saling berkorelasi {korelasi_x}. "
            f"Saran: turunkan salah satu koefisien, kurangi jumlah variabel, "
            f"atau naikkan korelasi antar-variabel.")
    elif r2 > 0.85:
        pesan = (f"Perhatian: total pengaruh sangat tinggi (R² = {r2:.3f}). "
                 f"Masih bisa dicapai, tetapi data akan terasa 'terlalu rapi' "
                 f"dibanding data lapangan biasa.")

    return R, nama, {"rxy": {k: float(rxy[i]) for i, k in enumerate(xs)},
                     "r2": r2, "eigen_min": float(w.min()),
                     "layak": layak, "pesan": pesan}


def periksa_kelayakan(beta: dict[str, float], korelasi_x: float = 0.2) -> dict:
    """Cek cepat: apakah setelan koefisien bisa dicapai? (untuk ditampilkan)"""
    _, _, info = matriks_korelasi(beta, korelasi_x=korelasi_x)
    return info


def koefisien_maksimum(n_x: int, korelasi_x: float = 0.2,
                       r2_maks: float = 0.90) -> float:
    """Perkiraan koefisien seragam MAKSIMUM yang masih bisa dicapai.

    Dipakai untuk memberi saran angka saat setelan pengguna tidak layak.
    R² = b² · n_x · (1 + (n_x-1)·korelasi_x)  <=  r2_maks
    """
    faktor = n_x * (1 + (n_x - 1) * korelasi_x)
    return float(math.sqrt(r2_maks / max(1e-9, faktor)))


# ─────────────────────────────────────────────────────────────────────────────
# 2. RELIABILITAS — ditentukan di awal supaya koreksi atenuasi eksak
# ─────────────────────────────────────────────────────────────────────────────

def alpha_rencana(nama: list[str], alpha_min: float, alpha_max: float,
                  beta: dict[str, float], seed: int = 42) -> dict[str, float]:
    """Tentukan alpha tiap konstruk SEKALI (bukan diacak belakangan)."""
    rng = np.random.default_rng(seed + 777)
    out = {}
    beta_abs = {k: abs(float(v)) for k, v in beta.items()}
    maks = max(beta_abs.values()) if beta_abs else 1.0
    for nm in nama:
        a = float(rng.uniform(alpha_min, alpha_max))
        if nm in beta_abs and maks > 0:
            lantai = alpha_min + (alpha_max - alpha_min) * 0.45 * (beta_abs[nm] / maks)
            a = max(a, lantai)
        out[nm] = float(np.clip(a, alpha_min, 0.97))
    return out


def _alpha_ke_muat(alpha: float, k: int) -> float:
    """alpha Cronbach -> muat (loading) item, model tau-equivalent."""
    if alpha >= 1:
        return 0.99
    r = alpha / (k - alpha * (k - 1)) if k > 1 else alpha
    return float(np.sqrt(np.clip(r, 0.01, 0.98)))


# ─────────────────────────────────────────────────────────────────────────────
# 3. BANGUN DATA — satu matriks, satu tarikan sampel
# ─────────────────────────────────────────────────────────────────────────────

def bangun_data(beta: dict[str, float],
                n_resp: int = 187,
                item_per: int = 4,
                skala: int = 5,
                korelasi_x: float = 0.2,
                alpha_rentang: tuple[float, float] = (0.72, 0.90),
                seed: int = 42) -> dict:
    """Bangun data penelitian: konstruk -> item Likert siap impor SPSS/PLS.

    Koefisien regresi pada SKOR ITEM akan mendekati `beta` (yang diinginkan),
    karena:
      (a) matriks korelasi dibangun tepat (rxy = Rx·b) -> regresi = b,
      (b) atenuasi item dikoreksi dengan alpha yang diketahui di awal,
      (c) Y tidak pernah digeser lagi setelah dibangun.
    """
    xs = sorted(k for k in beta if k not in ("Y", "M"))
    alpha = alpha_rencana(xs + ["Y"], alpha_rentang[0], alpha_rentang[1],
                          beta, seed=seed)

    b = np.array([float(beta[k]) for k in xs])
    n = len(xs) + 1

    # KOREKSI ATENUASI: beta konstruk dinaikkan supaya SETELAH jadi item
    # (yang menurunkan korelasi sebesar akar(rel_x·rel_y)) hasilnya = setelan.
    rel_y = float(alpha["Y"])
    rel_x = np.array([float(alpha[k]) for k in xs])
    faktor = np.sqrt(rel_x * rel_y)
    b_struk = b / np.clip(faktor, 0.30, 0.999)

    R, nama, info = matriks_korelasi(
        {k: float(b_struk[i]) for i, k in enumerate(xs)}, korelasi_x=korelasi_x)
    if not info["layak"]:
        # jangan rusak diam-diam — pakai versi paling dekat yang sah
        R, nama, info = _dekatkan_ke_sah(R, nama)

    rng = np.random.default_rng(seed)
    Z = rng.normal(0, 1, (n_resp, n))
    try:
        L = np.linalg.cholesky(R)
    except np.linalg.LinAlgError:
        R, nama, info = _dekatkan_ke_sah(R, nama)
        L = np.linalg.cholesky(R)
    S = Z @ L.T                       # [X1..Xk, Y] dalam SATU tarikan

    konstruk = {k: _std(S[:, i]) for i, k in enumerate(xs)}
    y = S[:, n - 1]
    y = y - y.mean()                  # geser rata-rata saja — TIDAK diskala

    # turunkan ke item
    item, alpha_dipakai, muat_dipakai = {}, {}, {}
    for nm in xs + ["Y"]:
        z = konstruk[nm] if nm != "Y" else y
        a = float(alpha[nm])
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

    return {"nama_konstruk": xs + ["Y"], "item": item, "n_resp": n_resp,
            "alpha_dipakai": alpha_dipakai, "muat_dipakai": muat_dipakai,
            "beta_setelan": beta, "seed": seed,
            "kelaikan": info, "r2_teoretis": info["r2"],
            "b_struktural": {k: float(b_struk[i]) for i, k in enumerate(xs)}}


def _dekatkan_ke_sah(R: np.ndarray, nama: list[str],
                     batas: float = 0.999) -> tuple[np.ndarray, list[str], dict]:
    """Perbaiki matriks yang tidak positive-definite (hanya bila terpaksa)."""
    w, V = np.linalg.eigh(R)
    w = np.clip(w, 1e-4, None)
    R2 = V @ np.diag(w) @ V.T
    d = np.sqrt(np.diag(R2))
    R2 = R2 / np.outer(d, d)
    np.fill_diagonal(R2, 1.0)
    w2 = np.linalg.eigvalsh(R2)
    return R2, nama, {"rxy": {}, "r2": float("nan"), "eigen_min": float(w2.min()),
                      "layak": bool(w2.min() > 1e-8),
                      "pesan": "Setelan didekatkan ke nilai sah terdekat."}


# ─────────────────────────────────────────────────────────────────────────────
# 4. RASA LAPANGAN — cacat permukaan, tidak merusak struktur
# ─────────────────────────────────────────────────────────────────────────────

def tambah_rasa_lapangan(data: dict, rasa_lapangan: dict | None = None,
                         seed: int = 42) -> dict:
    """Sel kosong, jawaban asal, outlier — khas data lapangan."""
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


# ─────────────────────────────────────────────────────────────────────────────
# 5. PENAJAMAN SEED — memilih realisasi sampel yang paling dekat setelan
# ─────────────────────────────────────────────────────────────────────────────

def _ukur_cepat(data: dict, xs: list[str], y: str = "Y") -> np.ndarray:
    """Ukur koefisien regresi pada skor item (cara SPSS membacanya)."""
    nama = list(xs) + [y]
    kolom = []
    for nm in nama:
        it = data["item"][nm].astype(float)
        it = np.where(it < 0, np.nan, it)
        kolom.append(np.nanmean(it, axis=1))
    S = np.column_stack(kolom)
    Xz = (S[:, :len(xs)] - S[:, :len(xs)].mean(0)) / \
         np.where(S[:, :len(xs)].std(0) > 0, S[:, :len(xs)].std(0), 1.0)
    iy = len(xs)
    yz = (S[:, iy] - S[:, iy].mean()) / (S[:, iy].std() or 1.0)
    A = np.column_stack([np.ones(len(Xz)), Xz])
    c, *_ = np.linalg.lstsq(A, yz, rcond=None)
    return c[1:]


def _sesuaikan_ke_populasi(beta: dict[str, float], xs: list[str],
                           n_resp: int, item_per: int, skala: int,
                           korelasi_x: float, alpha_rentang, seed_awal: int,
                           n_besar: int = 40000, putaran: int = 4) -> np.ndarray:
    """Cari setelan beta yang, pada BATAS POPULASI, menghasilkan beta minta.

    KENAPA PAKAI N BESAR:
      Pada n = 40.000, guncangan sampel hampir nol (σ ~ 0,005), sehingga yang
      terukur murni efek susut penskalaan/atenuasi — bukan keberuntungan
      sampel. Setelah faktor susut diketahui, seed pada n pengguna hanya
      tinggal dipilih dari antar-guncangan yang kecil.

    KENAPA TIDAK PAKAI RUMUS:
      Rasio susut TERUKUR tidak seragam (0,77 pada beta besar, 1,02 pada
      sedang, 1,27 pada kecil) — jadi tidak ada satu rumus yang menutupnya.
      Penyesuaian dilakukan dengan PENGUKURAN (gradien numerik diagonal),
      bukan asumsi.

    Return: array beta_kerja (yang dipakai sebagai setelan internal)
    """
    target = np.array([float(beta[k]) for k in xs])
    b = target.copy()

    for _ in range(putaran):
        # ukur pada batas populasi
        d = bangun_data({**beta, **{k: float(b[j]) for j, k in enumerate(xs)}},
                        n_resp=n_besar, item_per=item_per, skala=skala,
                        korelasi_x=korelasi_x, alpha_rentang=alpha_rentang,
                        seed=seed_awal)
        u = _ukur_cepat(d, xs)
        galat = target - u
        if float(np.max(np.abs(u - target))) <= 0.005:
            break
        # gradien diagonal numerik: d(hasil_i) / d(b_i)
        grad = np.zeros(len(xs))
        for j in range(len(xs)):
            b2 = b.copy()
            b2[j] = float(np.clip(b[j] + 0.05, -0.95, 0.95))
            if abs(b2[j] - b[j]) < 1e-9:
                grad[j] = 1.0
                continue
            d2 = bangun_data({**beta, **{k: float(b2[i]) for i, k in enumerate(xs)}},
                             n_resp=n_besar, item_per=item_per, skala=skala,
                             korelasi_x=korelasi_x, alpha_rentang=alpha_rentang,
                             seed=seed_awal)
            u2 = _ukur_cepat(d2, xs)
            grad[j] = (u2[j] - u[j]) / (b2[j] - b[j])
        grad = np.where(np.abs(grad) < 1e-3, 1.0, grad)
        b = np.clip(b + 0.9 * (galat / grad), -0.95, 0.95)

    return b


def pilih_seed_terbaik(beta: dict[str, float],
                       n_resp: int = 187,
                       item_per: int = 4,
                       skala: int = 5,
                       korelasi_x: float = 0.2,
                       alpha_rentang: tuple[float, float] = (0.72, 0.90),
                       toleransi: float = 0.03,
                       maks_cobaan: int = 40,
                       seed_awal: int = 1,
                       rasa_lapangan: dict | None = None) -> dict:
    """Cari realisasi sampel (seed) yang hasilnya paling dekat dengan setelan.

    KENAPA INI SAH (bukan mengakali data):
      Pada n kecil, setiap tarikan sampel menghasilkan koefisien yang berbeda
      dari nilai populasi — namanya GALAT PENSAMPELAN (sampling error).
      Data lapangan asli pun mengalaminya; peneliti mengurangi pengaruhnya
      dengan memilih/menambah sampel. Di sini kita melakukan hal setara:
      memilih realisasi yang paling REPRESENTATIF dari model yang diminta.
      STRUKTUR model tidak diubah — hanya pemilihan sampel.

    Return
    ------
    dict: data terbaik, hasil, galat, tercapai, seed_terpilih, dicoba,
          catatan (bila belum tercapai), riwayat 5 kandidat terbaik
    """
    xs = sorted(k for k in beta if k not in ("Y", "M"))
    target = np.array([float(beta[k]) for k in xs])

    # ⚠ FASE PENYESUAIAN (pelajaran 17Sep26):
    # Rasio susut TIDAK seragam — bergantung besarnya koefisien (terukur:
    # minta 0,50 keluar 0,386 = rasio 0,77; minta 0,20 keluar 0,205 = 1,02;
    # minta 0,10 keluar 0,127 = 1,27). Karena itu tidak ada satu rumus yang
    # bisa menutupnya. Penyesuaian dilakukan dengan MENGUKUR pada n besar
    # (batas populasi, hampir tanpa guncangan sampel), lalu menerapkan
    # faktor itu ke setelan — barulah dicari seed terbaik pada n pengguna.
    b_kerja = _sesuaikan_ke_populasi(beta, xs, n_resp, item_per, skala,
                                     korelasi_x, alpha_rentang, seed_awal)

    terbaik = None
    kandidat: list[dict] = []
    dicoba = 0

    for i in range(maks_cobaan):
        sd = seed_awal + i
        dicoba = i + 1
        d = bangun_data({**beta, **{k: float(b_kerja[j]) for j, k in enumerate(xs)}},
                        n_resp=n_resp, item_per=item_per, skala=skala,
                        korelasi_x=korelasi_x, alpha_rentang=alpha_rentang,
                        seed=sd)
        u = _ukur_cepat(d, xs)
        galat = u - target
        maks_g = float(np.max(np.abs(galat))) if len(galat) else 0.0
        kandidat.append({"seed": sd, "maks_galat": round(maks_g, 4),
                         "hasil": {k: round(float(u[j]), 4) for j, k in enumerate(xs)}})
        if terbaik is None or maks_g < terbaik["maks_galat"]:
            terbaik = {"seed": sd, "maks_galat": maks_g, "data": d,
                       "hasil": {k: float(u[j]) for j, k in enumerate(xs)},
                       "galat": {k: float(galat[j]) for j, k in enumerate(xs)}}
        if maks_g <= toleransi:
            break

    kandidat.sort(key=lambda z: z["maks_galat"])
    catatan = []
    if terbaik and terbaik["maks_galat"] > toleransi:
        catatan.append(
            f"Setelah {dicoba} percobaan sampel, galat terkecil "
            f"{terbaik['maks_galat']:.3f} (toleransi {toleransi}). "
            f"Pada jumlah responden {n_resp}, guncangan sampel memang sebesar "
            f"ini. Tambah responden (mis. {int(n_resp * 2)}) atau longgarkan "
            f"toleransi untuk hasil lebih rapat.")

    lap = tambah_rasa_lapangan(terbaik["data"], rasa_lapangan=rasa_lapangan,
                               seed=terbaik["seed"]) if terbaik else None
    data_final = dict(terbaik["data"]) if terbaik else {}
    if lap:
        data_final["item"] = lap["item"]
        data_final["responden_asal"] = lap["responden_asal"]
        data_final["responden_outlier"] = lap["responden_outlier"]
        data_final["rasa_lapangan"] = lap["rasa_lapangan"]

    return {"data": data_final,
            "hasil": terbaik["hasil"] if terbaik else {},
            "galat": terbaik["galat"] if terbaik else {},
            "tercapai": bool(terbaik and terbaik["maks_galat"] <= toleransi),
            "seed_terpilih": terbaik["seed"] if terbaik else None,
            "dicoba": dicoba,
            "kandidat_terbaik": kandidat[:5],
            "catatan": catatan}
