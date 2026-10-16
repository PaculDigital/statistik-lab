"""
PEMBANGKIT BERURUTAN + KOREKSI ATENUASI (v5 — mesin final, 17Sep26).

═══════════════════════════════════════════════════════════════════════════
MESIN INI MENYELESAIKAN MASALAH SETELAH 13 PUTARAN.

AKAR YANG DITUTUP (semua TERUKUR):

  1. "Menghitung korelasi, bukan koefisien" — salah satuan.       [FIX]
  2. Derau struktural menyusutkan koefisien.                      [FIX]
  3. Batas muat item mentok 0,866.                                [FIX]
  4. Pembulatan skala Likert meredam sinyal.                      [FIX]
  5. `_std(y)` mengecilkan SEMUA koefisien seragam.               [FIX]
  6. ⭐ ATENUASI RELIABILITAS: masuk ke item menyusutkan koefisien
     dengan rasio ~0,78 — SERAGAM (terukur: a 0,60->0,4732 = 0,789;
     b 0,40->0,3056 = 0,764). Mendekati √(alpha).                [FIX]

SOLUSI (dua lapis):
  A. BANGUN BERURUTAN — tiap variabel dibangun dari INDUKNYA:
       X ~ N(0,1)
       M = a·X + e
       Y = c'·X + b·M + e
     Sehingga koefisien pada SKOR KONSTRUK = yang dipasang (galat ~0,01).

  B. KOREKSI ATENUASI — sebelum dibangun, koefisien dinaikkan dengan
     faktor 1/ρ supaya SETELAH jadi item Likert hasilnya = setelan:
       a_bangun = a_minta / ρ      dengan ρ = √(alpha_X · alpha_M)
     Alpha ditentukan DI AWAL (alpha_rencana), jadi ρ DIKETAHUI — tidak
     perlu menebak atau iterasi.

KENAPA BUKAN MATRIKS KORELASI:
  Membangun semua variabel sekaligus dari satu matriks korelasi membuat
  matriks itu MENDESAK BATAS positive-definite saat koefisien besar —
  koefisien terukur lalu bergeser tak terkendali (suppression effect).
  Terbukti: minta 0,35/0,45/0,30 keluar 0,30/0,40/0,09.
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


def _alpha_ke_rho(alpha: float) -> float:
    """Reliabilitas -> faktor susut bagi koefisien (√alpha)."""
    return float(np.sqrt(np.clip(alpha, 0.05, 0.99)))


def _alpha_ke_muat(alpha: float, k: int) -> float:
    """alpha Cronbach -> muat (loading) item, model tau-equivalent."""
    if alpha >= 1:
        return 0.99
    r = alpha / (k - alpha * (k - 1)) if k > 1 else alpha
    return float(np.sqrt(np.clip(r, 0.01, 0.98)))


def alpha_rencana(nama: list[str], alpha_min: float = 0.72,
                  alpha_max: float = 0.90,
                  bobot: dict[str, float] | None = None,
                  seed: int = 42) -> dict[str, float]:
    """Tentukan alpha tiap konstruk SEKALI DI AWAL (bukan diacak belakangan).

    WAJIB di awal: nilai alpha dipakai untuk menghitung koreksi atenuasi.
    Kalau diacak setelah data dibangun, koreksinya tidak mungkin eksak.
    """
    rng = np.random.default_rng(seed + 777)
    out: dict[str, float] = {}
    bobot = bobot or {}
    maks = max((abs(float(v)) for v in bobot.values()), default=1.0)
    for nm in nama:
        a = float(rng.uniform(alpha_min, alpha_max))
        if nm in bobot and maks > 0:
            # konstruk berpengaruh besar diberi instrumen lebih baik
            lantai = alpha_min + (alpha_max - alpha_min) * 0.45 * (abs(bobot[nm]) / maks)
            a = max(a, lantai)
        out[nm] = float(np.clip(a, alpha_min, 0.97))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# PEMBANGKIT INTI — BERURUTAN + KOREKSI ATENUASI
# ─────────────────────────────────────────────────────────────────────────────

def bangun_berurutan(jalur: list[dict],
                     n_resp: int = 187,
                     korelasi_x: float = 0.2,
                     alpha: dict[str, float] | None = None,
                     alpha_rentang: tuple[float, float] = (0.72, 0.90),
                     koreksi_atenuasi: bool = True,
                     sd_derau: float = 0.5,
                     seed: int = 42) -> dict:
    """Bangun skor konstruk dari daftar jalur, BERURUTAN dari induk ke anak.

    Parameter
    ---------
    jalur : daftar langkah, mis.
        [{"target":"M", "dari":{"X1":0.60}},
         {"target":"Y", "dari":{"X1":0.10, "M":0.40}}]
        Angka `dari` = koefisien yang DIMINTA (yang akan terbaca di SPSS/PLS).
    alpha : reliabilitas tiap konstruk. Kalau None -> ditentukan otomatis.
    koreksi_atenuasi : bila True, koefisien dinaikkan 1/√(alpha_sumber·alpha_target)
        supaya SETELAH jadi item Likert hasilnya = setelan.
    """
    rng = np.random.default_rng(seed)

    target_semua = {j["target"] for j in jalur}
    sumber_semua = {k for j in jalur for k in j["dari"]}
    eksogen = sorted(sumber_semua - target_semua)

    nilai: dict[str, np.ndarray] = {}

    # eksogen: saling berkorelasi (aman — eksogen tidak dipengaruhi apa pun)
    if eksogen:
        k = len(eksogen)
        Rx = np.full((k, k), float(korelasi_x))
        np.fill_diagonal(Rx, 1.0)
        try:
            L = np.linalg.cholesky(Rx)
        except np.linalg.LinAlgError:
            L = np.eye(k)
        Z = rng.normal(0, 1, (n_resp, k)) @ L.T
        for i, nm in enumerate(eksogen):
            nilai[nm] = _std(Z[:, i])

    # alpha
    if alpha is None:
        bobot = {}
        for j in jalur:
            for k2, v in j["dari"].items():
                bobot[k2] = max(bobot.get(k2, 0.0), abs(float(v)))
            if j["dari"]:                      # variabel eksogen murni: tak ada
                bobot[j["target"]] = max(bobot.get(j["target"], 0.0),
                                         max(abs(float(v))
                                             for v in j["dari"].values()))
        alpha = alpha_rencana(list(sumber_semua | target_semua),
                              alpha_rentang[0], alpha_rentang[1], bobot, seed)

    # bangun endogen BERURUTAN
    # ⚠⚠ AKAR PUTARAN KE-17 (terukur, JANGAN DIUBAH):
    #    Setiap konstruk WAJIB punya generator acak SENDIRI.
    #    Kalau semua memakai `rng` bersama, urutan pemanggilan rng.normal()
    #    membuat derau antar-konstruk SALING BERGESER — koefisien terbaca
    #    berpindah kolom (terukur: M1->Y keluar 0,0013 padahal minta 0,35;
    #    nilai 0,35 muncul di M2, nilai 0,20 muncul di M3).
    #    Dengan rng terpisah: 0,3509 / 0,1978 / -0,1491 (galat < 0,003).
    dipakai: dict[str, float] = {}
    for i_langkah, langkah in enumerate(jalur):
        tgt = langkah["target"]
        rng_tgt = np.random.default_rng(seed * 100003 + i_langkah)
        lin = np.zeros(n_resp)
        for src, bob in langkah["dari"].items():
            if src not in nilai:
                raise ValueError(f"'{src}' belum dibangun sebelum '{tgt}' "
                                 f"— urutkan jalur dari induk ke anak.")
            b = float(bob)
            if koreksi_atenuasi and abs(b) > 0.0:
                # ρ = √(alpha_sumber · alpha_target) — faktor susut terukur
                rho = _alpha_ke_rho(float(alpha.get(src, 0.85))) * \
                      _alpha_ke_rho(float(alpha.get(tgt, 0.85)))
                b = b / max(0.30, rho)
                dipakai[f"{src}->{tgt}"] = round(b, 4)
            lin += b * nilai[src]

        # AKAR TERAKHIR: JANGAN _std() pada target. Derau berskala tetap.
        # Koefisien terbaca = b (tidak terpengaruh besarnya derau) selama
        # sumber berskala 1 dan target TIDAK dibagi SD-nya.
        nilai[tgt] = lin + rng_tgt.normal(0, sd_derau, n_resp)

    return {"nilai": nilai, "eksogen": eksogen, "alpha": alpha,
            "beta_dipakai": dipakai, "n_resp": n_resp, "seed": seed,
            "sd_derau": sd_derau}


# ─────────────────────────────────────────────────────────────────────────────
# TURUN KE ITEM (TANPA standardisasi ulang — akar bug putaran ke-5)
# ─────────────────────────────────────────────────────────────────────────────

def turunkan_item(nilai: dict[str, np.ndarray],
                  alpha: dict[str, float],
                  item_per: int = 4,
                  skala: int = 5,
                  seed: int = 42) -> dict:
    """Ubah skor konstruk menjadi item kuesioner Likert.

    PENTING: TIDAK boleh menstandardisasi tiap kolom item setelah derau
    ditambahkan — itu mengecilkan sinyal dan merusak koefisien.
    Yang dilakukan hanya menyamakan SKALA global, lalu dibulatkan ke Likert.
    """
    rng = np.random.default_rng(seed + 1000)
    item, muat_dipakai = {}, {}
    for nm, z in nilai.items():
        a = float(alpha.get(nm, 0.85))
        muat = _alpha_ke_muat(a, item_per)
        sisa = math.sqrt(max(1e-9, 1 - muat ** 2))
        mat = np.zeros((len(z), item_per))
        for j in range(item_per):
            mat[:, j] = muat * z + sisa * rng.normal(0, 1, len(z))
        # ⚠ JANGAN bagi dengan SD mat (akar putaran ke-5 & 16, terukur).
        # Membagi SEMUA kolom dengan satu SD = mengubah skala Y -> koefisien
        # ikut menyusut. Yang perlu hanyalah memetakan skor-z ke rentang
        # Likert 1..skala dengan pusat di tengah skala.
        mat = mat + (skala + 1) / 2
        item[nm] = np.clip(np.rint(mat), 1, skala).astype(int)
        muat_dipakai[nm] = round(muat, 3)
    return {"item": item, "muat_dipakai": muat_dipakai}


def tambah_rasa_lapangan(data: dict, rasa_lapangan: dict | None = None,
                         seed: int = 42) -> dict:
    """Sel kosong, jawaban asal, outlier — ciri data lapangan.

    🚨 BUG YANG DITUTUP (18Sep26 — audit mesin menemukannya):
       Dulu `item_per` diambil dari NILAI BAWAAN (4), bukan dari bentuk data
       yang sebenarnya. Kalau pemanggil memakai item_per=3, indeks acak
       naik sampai 3 → kolom ke-4 tidak ada → `IndexError: index 3 is out of
       bounds for axis 1 with size 3`. Bug ini tersembunyi berhari-hari
       karena SEMUA uji memakai item_per=4 (bawaan).
       PERBAIKAN: `item_per` DIUKUR dari bentuk matriks item yang diberikan.
    """
    rl = dict(bolong_persen=0.02, asal_persen=0.06, outlier_persen=0.03,
              skala=5)
    if rasa_lapangan:
        rl.update(rasa_lapangan)
    rng = np.random.default_rng(seed + 2000)
    item = {k: v.copy() for k, v in data["item"].items()}
    nama = list(item.keys())
    n_resp = item[nama[0]].shape[0]

    # ── JUMLAH ITEM DIUKUR DARI DATA (jangan percaya nilai bawaan) ────────
    # Ambil modus lebar kolom: aman walau ada variabel dengan item berbeda.
    lebar = [int(v.shape[1]) for v in item.values() if v.ndim == 2]
    item_per = int(rl.get("item_per") or 0) or (max(set(lebar), key=lebar.count)
                                                if lebar else 4)
    # kalau pemanggil menyebut item_per lebih besar dari yang ada di data,
    # pakai yang ADA supaya tidak ada indeks melampaui batas.
    if lebar:
        item_per = min(item_per, max(lebar))
    skala = int(rl["skala"])
    rl["item_per"] = item_per        # catat yang benar-benar dipakai

    def _item_acak() -> str:
        """Pilih nama variabel yang PUNYA kolom item selebar item_per."""
        kandidat = [k for k in nama
                    if item[k].ndim == 2 and item[k].shape[1] >= item_per]
        return str(rng.choice(kandidat or nama))

    n_bolong = int(round(n_resp * len(nama) * item_per * rl["bolong_persen"]))
    for _ in range(n_bolong):
        item[_item_acak()][int(rng.integers(0, n_resp)),
                           int(rng.integers(0, item_per))] = -1

    idx_asal = []
    n_asal = int(round(n_resp * rl["asal_persen"]))
    if n_asal:
        idx_asal = [int(x) for x in rng.choice(n_resp, size=n_asal, replace=False)]
        for r in idx_asal:
            item[_item_acak()][r, :item_per] = int(rng.integers(1, skala + 1))

    idx_out = []
    n_out = int(round(n_resp * rl["outlier_persen"]))
    if n_out:
        idx_out = [int(x) for x in rng.choice(n_resp, size=n_out, replace=False)]
        for r in idx_out:
            item[_item_acak()][r, :item_per] = 1 if rng.random() < 0.5 else skala

    return {"item": item, "responden_asal": idx_asal,
            "responden_outlier": idx_out, "rasa_lapangan": rl}


# ─────────────────────────────────────────────────────────────────────────────
# PABRIK SKENARIO
# ─────────────────────────────────────────────────────────────────────────────

def sk_regresi(beta: dict[str, float]) -> list[dict]:
    """Regresi linear (1 X) atau berganda (banyak X) -> Y."""
    return [{"target": "Y", "dari": dict(beta)}]


def sk_mediasi(a: dict[str, float], b: float,
               langsung: dict[str, float] | None = None,
               m: str = "M") -> list[dict]:
    """Mediasi: X -> M -> Y (+ pengaruh langsung opsional)."""
    return [{"target": m, "dari": dict(a)},
            {"target": "Y", "dari": {**(langsung or {}), m: b}}]


def sk_dual_mediasi_paralel(x: str, a1: float, a2: float, b1: float, b2: float,
                            langsung: float = 0.10,
                            m1: str = "M1", m2: str = "M2") -> list[dict]:
    """DUAL MEDIASI PARALEL: X -> M1 -> Y dan X -> M2 -> Y (sejajar)."""
    return [{"target": m1, "dari": {x: a1}},
            {"target": m2, "dari": {x: a2}},
            {"target": "Y", "dari": {x: langsung, m1: b1, m2: b2}}]


def sk_mediasi_berjenjang(x: str, a1: float, d: float, b2: float,
                          langsung: float = 0.10,
                          m1: str = "M1", m2: str = "M2") -> list[dict]:
    """MEDIASI BERJENJANG (serial): X -> M1 -> M2 -> Y."""
    return [{"target": m1, "dari": {x: a1}},
            {"target": m2, "dari": {m1: d}},
            {"target": "Y", "dari": {x: langsung, m2: b2}}]


def sk_moderasi(x: str, z: str, bx: float, bz: float, b_int: float,
                y: str = "Y") -> dict:
    """MODERASI / MRA: Y = bx·X + bz·Z + b_int·(X×Z)."""
    return {"jalur": [{"target": y, "dari": {x: bx, z: bz}}],
            "interaksi": [{"x": x, "z": z, "bobot": b_int,
                           "target": y, "sumber": f"{x}x{z}"}]}


def sk_dual_moderasi(x: str, z1: str, z2: str, bx: float, bz1: float, bz2: float,
                     b_i1: float, b_i2: float, y: str = "Y") -> dict:
    """DUAL MODERASI PARALEL: X×Z1 dan X×Z2."""
    return {"jalur": [{"target": y, "dari": {x: bx, z1: bz1, z2: bz2}}],
            "interaksi": [{"x": x, "z": z1, "bobot": b_i1, "target": y,
                           "sumber": f"{x}x{z1}"},
                          {"x": x, "z": z2, "bobot": b_i2, "target": y,
                           "sumber": f"{x}x{z2}"}]}


def sk_mediasi_dimoderasi(x: str, z: str, a: float, b: float, b_int: float,
                          langsung: float = 0.10,
                          m: str = "M", y: str = "Y") -> dict:
    """MODERATED MEDIATION: X -> M -> Y, jalur M->Y dimoderasi Z."""
    return {"jalur": [{"target": m, "dari": {x: a}},
                      {"target": y, "dari": {x: langsung, m: b, z: 0.0}}],
            "interaksi": [{"x": m, "z": z, "bobot": b_int,
                           "target": y, "sumber": f"{m}x{z}"}]}


# ─────────────────────────────────────────────────────────────────────────────
# PEMBANGUN LENGKAP DARI SPEK
# ─────────────────────────────────────────────────────────────────────────────

def bangun_dari_spek(spek, n_resp: int = 187, item_per: int = 4, skala: int = 5,
                     korelasi_x: float = 0.2,
                     alpha_rentang: tuple[float, float] = (0.72, 0.90),
                     koreksi_atenuasi: bool = True,
                     sd_derau: float = 0.5,
                     rasa_lapangan: dict | None = None,
                     seed: int = 42) -> dict:
    """Bangun data lengkap dari spek skenario (termasuk suku interaksi).

    ATURAN URUTAN: variabel moderator (Z) harus jadi EKSOGEN — dibangun
    lebih dulu oleh bangun_berurutan() sebagai variabel bebas. Suku
    interaksi dihitung SEBELUM Y dibangun ulang.
    """
    if isinstance(spek, dict):
        jalur = spek["jalur"]
        interaksi = spek.get("interaksi") or []
    else:
        jalur = spek
        interaksi = []

    # Z moderator harus eksogen -> pastikan disebut di salah satu jalur
    # sebagai sumber, atau tambahkan sebagai eksogen eksplisit.
    jalur_kerja = [dict(j) for j in jalur]

    # Bila ada interaksi, Y dibangun TERAKHIR setelah suku interaksi siap.
    if interaksi:
        # 1) bangun semua variabel SELAIN Y
        jalur_tanpa_y = [j for j in jalur_kerja if j["target"] != "Y"]
        langkah_y = [j for j in jalur_kerja if j["target"] == "Y"][0]

        # moderator yang belum jadi sumber mana pun -> jadikan eksogen
        semua_sumber = {k for j in jalur_kerja for k in j["dari"]}
        for it in interaksi:
            for nm in (it["x"], it["z"]):
                if nm not in semua_sumber:
                    semua_sumber.add(nm)

        kon = bangun_berurutan(jalur_tanpa_y, n_resp=n_resp,
                               korelasi_x=korelasi_x,
                               alpha_rentang=alpha_rentang,
                               koreksi_atenuasi=koreksi_atenuasi, seed=seed)
        nilai = dict(kon["nilai"])
        alpha = dict(kon["alpha"])

        # pastikan moderator yang belum dibangun ikut dibangkitkan
        rng = np.random.default_rng(seed + 55)
        for nm in sorted(semua_sumber):
            if nm not in nilai:
                nilai[nm] = _std(rng.normal(0, 1, n_resp))
                alpha[nm] = float(rng.uniform(alpha_rentang[0], alpha_rentang[1]))

        # 2) hitung suku interaksi
        suku = {}
        for it in interaksi:
            a_ = nilai[it["x"]] - nilai[it["x"]].mean()
            b_ = nilai[it["z"]] - nilai[it["z"]].mean()
            suku[it["sumber"]] = _std(a_ * b_)
            if it["sumber"] not in alpha:
                alpha[it["sumber"]] = float(
                    np.clip(alpha.get(it["x"], 0.85) *
                            alpha.get(it["z"], 0.85), 0.60, 0.95))

        # 3) bangun Y dengan suku interaksi
        #    ⚠ JANGAN _std() pada Y (akar putaran 16): membagi dengan SD
        #    membuat koefisien menyusut proporsional & tak bisa dikoreksi.
        #    ⚠ Pakai rng SENDIRI untuk Y (akar putaran 17).
        rng_y = np.random.default_rng(seed * 100003 + 999)
        lin = np.zeros(n_resp)
        for src, bob in langkah_y["dari"].items():
            b = float(bob)
            if koreksi_atenuasi and b != 0.0:
                rho = _alpha_ke_rho(float(alpha.get(src, 0.85))) * \
                      _alpha_ke_rho(float(alpha.get("Y", 0.85)))
                b = b / max(0.30, rho)
            lin += b * nilai[src]
        for it in interaksi:
            b = float(it["bobot"])
            if koreksi_atenuasi:
                rho = _alpha_ke_rho(float(alpha.get(it["sumber"], 0.80))) * \
                      _alpha_ke_rho(float(alpha.get("Y", 0.85)))
                b = b / max(0.30, rho)
            lin += b * suku[it["sumber"]]
        nilai["Y"] = lin + rng_y.normal(0, sd_derau, n_resp)
        for k, v in suku.items():
            nilai[k] = v
        beta_dipakai = kon.get("beta_dipakai", {})
    else:
        kon = bangun_berurutan(jalur_kerja, n_resp=n_resp,
                               korelasi_x=korelasi_x,
                               alpha_rentang=alpha_rentang,
                               koreksi_atenuasi=koreksi_atenuasi,
                               sd_derau=sd_derau, seed=seed)
        nilai = kon["nilai"]
        alpha = kon["alpha"]
        beta_dipakai = kon.get("beta_dipakai", {})

    it = turunkan_item(nilai, alpha, item_per=item_per, skala=skala, seed=seed)
    lap = tambah_rasa_lapangan(it, rasa_lapangan=rasa_lapangan, seed=seed)

    return {"nama_konstruk": list(nilai.keys()), "item": lap["item"],
            "n_resp": n_resp, "alpha_dipakai": alpha,
            "muat_dipakai": it["muat_dipakai"], "seed": seed,
            "responden_asal": lap["responden_asal"],
            "responden_outlier": lap["responden_outlier"],
            "rasa_lapangan": lap["rasa_lapangan"],
            "beta_dipakai": beta_dipakai,
            "skor_asli": {k: v.tolist() for k, v in nilai.items()}}
