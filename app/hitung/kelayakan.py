"""
PEMERIKSA KELAYAKAN SETELAN — gerbang jujur sebelum data dibuat.

═══════════════════════════════════════════════════════════════════════════
KENAPA INI ADA (temuan 17Sep26):
  Wulan uji 8 prediktor dengan setelan β = 0,42/0,39/0,36/0,33/0,30/0,27/
  0,24/0,21. Kalibrasi GAGAL (galat 0,26) walau 60 putaran, dan derau
  berapa pun (0,5-2,0) TIDAK mengubah apa pun (galat tetap ~0,26).

  Akarnya: total β = 2,52 -> R² yang diminta ~0,83, padahal:
    R² = Σ(β_i · r_XYi)  dan  R² <= 1  SELALU.
  Setelan itu menuntut R² > 0,83 dengan 8 prediktor yang saling
  berkorelasi 0,2 — secara matematis TIDAK MUNGKIN dipenuhi serentak.

  Ini BUKAN bug mesin. Ini hukum matematika: ruang varians hasil itu
  TERBATAS (maksimal 1,0), jadi jumlah pengaruh semua prediktor tidak
  bisa melebihi ruang yang tersedia.

PRINSIP: tolak jujur + beri jalan keluar (angka wajar), JANGAN diam-diam
menghasilkan data yang meleset. Ini juga bahan ajar: mahasiswa belajar
kenapa "semua hipotesis signifikan" itu tidak realistis.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math

import numpy as np


# Ambang keputusan (dipakai untuk pesan, bukan untuk menolak mentah)
R2_SANGAT_TINGGI = 0.85     # hampir mustahil di penelitian sosial
R2_TINGGI = 0.75            # mungkin tapi jarang; minta justifikasi
R2_WAJAR_ATAS = 0.65        # batas atas yang realistis
R2_WAJAR_BAWAH = 0.15       # terlalu kecil -> semua jalur tidak signifikan
VIF_BATAS = 10.0            # ambang multikolinearitas klasik
VIF_PERHATIAN = 5.0


def _matriks_korelasi(korelasi_x, k: int, r_dalam_grup=None) -> np.ndarray:
    """Bangun matriks korelasi antar-prediktor (k x k) dari bermacam bentuk.

    Menerima:
      - float  -> korelasi seragam (perkiraan kasar)
      - matriks -> dipakai langsung
      - daftar grup -> tiap grup = variabel yang mengukur hal sama
        (r tinggi di dalam grup, rendah antar grup) — ini yang REALISTIS
    """
    if isinstance(korelasi_x, np.ndarray) and korelasi_x.ndim == 2:
        R = np.array(korelasi_x, dtype=float)
        if R.shape != (k, k):
            raise ValueError(f'matriks korelasi {R.shape} tidak cocok dengan {k} prediktor')
        return R

    if isinstance(korelasi_x, (list, tuple)) and korelasi_x and \
            isinstance(korelasi_x[0], (list, tuple, set)):
        r_dalam = 0.82 if r_dalam_grup is None else float(r_dalam_grup)
        r_antar = 0.22
        R = np.full((k, k), r_antar)
        np.fill_diagonal(R, 1.0)
        for grup in korelasi_x:
            idx = [int(i) for i in grup]
            for a in idx:
                for b in idx:
                    if a != b:
                        R[a, b] = r_dalam
        return R

    r = float(korelasi_x)
    R = np.full((k, k), r)
    np.fill_diagonal(R, 1.0)
    return R


def _r2_perkiraan(beta: dict[str, float], korelasi_x=0.2,
                  r_dalam_grup=None) -> float:
    """Perkiraan R² dari setelan β dan korelasi antar-prediktor.

    R² = β' R_xx β        (bentuk matriks, terstandardisasi)
    """
    nama = list(beta)
    k = len(nama)
    if k == 0:
        return 0.0
    R = _matriks_korelasi(korelasi_x, k, r_dalam_grup)
    b = np.array([float(beta[n]) for n in nama])
    r2 = float(b @ R @ b)
    return r2


def _vif(korelasi_x, k: int, r_dalam_grup=None) -> np.ndarray:
    """VIF per prediktor — BENAR untuk model realistis.

    ⚠️ KOREKSI 17Sep26 (temuan terukur): rumus LAMA memakai asumsi
    "korelasi SERAGAM" (semua X saling berkorelasi sama persis). Asumsi itu
    TERLALU HALUS: dihitung sampai k=10 & r=0,9 pun VIF cuma 9,0 — padahal
    di dunia nyata VIF>10 itu biasa.

    SEBABNYA: korelasi antar-X di dunia nyata TIDAK seragam. Ada kelompok
    item yang mengukur hal mirip (r 0,80-0,85 antar mereka) dan lemah ke
    yang lain (r 0,20). JUSTRU ketidak-seragaman itu yang meledakkan VIF.

    Rumus yang dipakai sekarang (bentuk matriks, benar secara umum):
        VIF_j = 1 / (1 - R_j²)
    dengan R_j² = R[j, lain] @ inv(R[lain,lain]) @ R[lain, j].

    `korelasi_x` boleh:
      - angka (float) -> korelasi seragam (dipakai kalau tidak ada info)
      - matriks (k x k) -> korelasi nyata antar-X (paling akurat)
      - daftar grup -> tiap grup = item yang mengukur hal sama (r tinggi
        di dalam grup, rendah antar grup)
    """
    # ── bentuk matriks: pakai langsung ────────────────────────────────────
    if isinstance(korelasi_x, np.ndarray) and korelasi_x.ndim == 2:
        R = np.array(korelasi_x, dtype=float)
        return _vif_dari_matriks(R)

    # ── daftar grup: bangun matriks realistis ─────────────────────────────
    if isinstance(korelasi_x, (list, tuple)) and korelasi_x and \
            isinstance(korelasi_x[0], (list, tuple, set)):
        return _vif_dari_matriks(_matriks_korelasi(korelasi_x, k, r_dalam_grup))

    # ── angka: korelasi seragam (perkiraan kasar) ─────────────────────────
    r = float(korelasi_x)
    R = np.full((k, k), r)
    np.fill_diagonal(R, 1.0)
    return _vif_dari_matriks(R)


def _vif_dari_matriks(R: np.ndarray) -> np.ndarray:
    """VIF tiap prediktor dari matriks korelasi apa pun (bentuk umum)."""
    k = R.shape[0]
    if k <= 1:
        return np.array([1.0])
    try:
        inv = np.linalg.pinv(R)
    except np.linalg.LinAlgError:
        return np.full(k, np.inf)
    diag = np.clip(np.diag(inv), 1.0, None)
    return diag.astype(float)


def _vif_maks(R: np.ndarray) -> float:
    return float(np.max(_vif_dari_matriks(R)))


def periksa_setelan(beta: dict[str, float],
                    korelasi_x=0.2,
                    n_resp: int = 187,
                    per_jalur: bool = True,
                    r_dalam_grup=None) -> dict:
    """Periksa apakah setelan β mungkin dicapai. JANGAN ubah data — cuma nilai.

    Parameter
    ---------
    beta : dict nama_prediktor -> koefisien yang diminta (target yang sama)
    korelasi_x : korelasi antar-prediktor (default 0,2)
    n_resp : jumlah responden
    per_jalur : True bila ini satu target (regresi berganda)

    Return
    ------
    dict: layak (bool), r2 (float), pesan (list[str]), saran (dict),
          tingkat ('aman'|'perhatian'|'tidak_layak'), vif
    """
    nama = [k for k, v in beta.items() if abs(float(v)) > 1e-9]
    k = len(nama)
    pesan: list[str] = []
    saran: dict[str, float] = {}

    if k == 0:
        return {"layak": False, "r2": 0.0, "tingkat": "tidak_layak",
                "pesan": ["Setelan kosong — tidak ada jalur yang diminta."],
                "saran": {}, "vif": 1.0, "vif_tiap": [], "n_resp": n_resp}

    r2 = _r2_perkiraan({n: beta[n] for n in nama}, korelasi_x, r_dalam_grup)
    vif_arr = _vif(korelasi_x, k, r_dalam_grup)
    vif = float(np.max(vif_arr))

    # ── 1. Total pengaruh & R² ────────────────────────────────────────────
    total_b = sum(abs(float(beta[n])) for n in nama)

    if r2 > 1.0:
        tingkat = "tidak_layak"
        pesan.append(
            f"❌ Setelan ini tidak mungkin dicapai: total pengaruhnya menuntut "
            f"R² = {r2:.2f}, padahal R² tidak pernah bisa melebihi 1,00. "
            f"Artinya {k} variabel diminta menjelaskan lebih banyak daripada "
            f"seluruh ruang yang tersedia.")
    elif r2 > R2_SANGAT_TINGGI:
        tingkat = "tidak_layak"
        pesan.append(
            f"❌ R² yang diminta {r2:.2f} — hampir mustahil di penelitian "
            f"manusia (batas wajar {R2_WAJAR_ATAS:.2f}). Biasanya ini tanda "
            f"terlalu banyak jalur besar sekaligus.")
    elif r2 > R2_TINGGI:
        tingkat = "perhatian"
        pesan.append(
            f"⚠️ R² yang diminta {r2:.2f} — mungkin, tapi jarang. Biasanya "
            f"butuh justifikasi teori yang kuat.")
    elif r2 < R2_WAJAR_BAWAH:
        tingkat = "perhatian"
        pesan.append(
            f"⚠️ R² yang diminta hanya {r2:.2f} — sangat kecil. Pada n={n_resp} "
            f"kemungkinan besar semua jalur jadi TIDAK SIGNIFIKAN.")
    else:
        tingkat = "aman"
        pesan.append(f"✅ R² yang diminta {r2:.2f} — wajar untuk penelitian "
                     f"ilmu sosial ({R2_WAJAR_BAWAH:.2f}–{R2_WAJAR_ATAS:.2f}).")

    # ── 2. Multikolinearitas ──────────────────────────────────────────────
    r_tampil = (korelasi_x if isinstance(korelasi_x, (int, float))
                else 'berkelompok')
    if vif > VIF_BATAS:
        tingkat = "tidak_layak" if r2 > R2_TINGGI else "perhatian"
        pesan.append(
            f"❌ Multikolinearitas berat: VIF = {vif:.1f} (ambang {VIF_BATAS:.0f}). "
            f"Dengan {k} prediktor yang sebagian mengukur hal serupa "
            f"(korelasi {r_tampil}), koefisien tidak bisa dipisahkan — "
            f"hasilnya akan liar.")
    elif vif > VIF_PERHATIAN:
        pesan.append(f"⚠️ Multikolinearitas mulai terasa: VIF = {vif:.1f}. "
                     f"Perhatikan hasilnya.")
    else:
        pesan.append(f"✅ Multikolinearitas aman: VIF = {vif:.1f}.")

    # ── 3. Saran angka wajar ──────────────────────────────────────────────
    # Target R² wajar: 0,45 (tengah rentang ilmu sosial).
    if r2 > R2_WAJAR_ATAS:
        sasaran = 0.45
        skala = math.sqrt(sasaran / max(r2, 1e-9))
        for n in nama:
            saran[n] = round(float(beta[n]) * skala, 3)
        pesan.append(
            f"💡 Saran: k perkalian semua jalur dengan ~{skala:.2f}, sehingga "
            f"total pengaruhnya wajar dan R² menjadi ~{sasaran:.2f}. "
            f"Contoh hasil saran ada di bagian 'saran'.")

    # ── 4. Sampel kecil ───────────────────────────────────────────────────
    sigma = 1.0 / math.sqrt(max(n_resp, 1))
    if n_resp < 100:
        pesan.append(
            f"⚠️ n = {n_resp} kecil. SIGNIFIKANSI akan tetap benar, tapi "
            f"angka koefisien bisa bergeser ±{sigma*2:.2f} — itu hukum "
            f"statistik (galat pensampelan), bukan kesalahan aplikasi. "
            f"Jelaskan ini ke mahasiswa: data lapangan asli pun begitu.")
    else:
        pesan.append(f"✅ n = {n_resp} cukup untuk koefisien yang stabil.")

    layak = tingkat != "tidak_layak"
    return {"layak": layak, "r2": round(r2, 4), "vif": round(vif, 2),
            "vif_tiap": [round(float(v), 2) for v in vif_arr],
            "tingkat": tingkat, "pesan": pesan, "saran": saran,
            "total_beta": round(total_b, 4), "n_prediktor": k,
            "korelasi_x": korelasi_x if isinstance(korelasi_x, (int, float))
            else "matriks/grup", "n_resp": n_resp}


def periksa_model(jalur: list[dict], korelasi_x: float = 0.2,
                  n_resp: int = 187) -> dict:
    """Periksa SELURUH model: tiap target diperiksa sendiri-sendiri.

    Return dict: layak (bool), per_target (dict), pesan_gabungan (list[str])
    """
    per_target: dict[str, dict] = {}
    pesan: list[str] = []

    # kelompokkan per target
    target: dict[str, dict[str, float]] = {}
    for j in jalur:
        target.setdefault(j["target"], {}).update(j["dari"])

    for t, beta in target.items():
        hasil = periksa_setelan(beta, korelasi_x, n_resp)
        per_target[t] = hasil
        for p in hasil["pesan"]:
            pesan.append(f"[{t}] {p}")

    # rangkaian (rantai) — periksa akumulasi koefisien tak langsung
    layak = all(h["layak"] for h in per_target.values())

    # deteksi rantai terlalu panjang (gema pengaruh makin kecil)
    kedalaman = _kedalaman_rantai(jalur, target)
    if kedalaman >= 4:
        pesan.append(
            f"ℹ️ Rantai pengaruh sepanjang {kedalaman} tingkat. Pengaruh tak "
            f"langsung akan sangat kecil (mis. 0,45×0,35×0,30 = 0,047) — "
            f"wajar, dan justru bagus untuk mengajar apa itu 'efek tidak "
            f"langsung yang menyusut'.")
        per_target["_rantai"] = {"kedalaman": kedalaman}

    return {"layak": layak, "per_target": per_target,
            "pesan_gabungan": pesan, "kedalaman_rantai": kedalaman}


def _kedalaman_rantai(jalur: list[dict], target: dict[str, dict]) -> int:
    """Hitung kedalaman rantai terpanjang (induk -> anak -> cucu...)."""
    peta = {j["target"]: list(j["dari"]) for j in jalur}
    terpanjang = 1

    def dalam(nama: str, dilihat: set[str]) -> int:
        if nama in dilihat:
            return 1
        induk = peta.get(nama)
        if not induk:
            return 1
        return 1 + max((dalam(x, dilihat | {nama}) for x in induk), default=0)

    for t in peta:
        terpanjang = max(terpanjang, dalam(t, set()))
    return terpanjang


def format_laporan(hasil: dict) -> str:
    """Ringkasan siap tampil ke pengguna (bahasa akademik, tanpa kata keras)."""
    baris = []
    lambang = {"aman": "✅", "perhatian": "⚠️", "tidak_layak": "❌"}
    baris.append(f'PERIKSA KELAYAKAN SETELAN')
    baris.append('=' * 60)
    baris.append(f'  Prediktor    : {hasil["n_prediktor"]}')
    baris.append(f'  Total pengaruh: {hasil["total_beta"]:.2f}')
    baris.append(f'  Perkiraan R² : {hasil["r2"]:.2f}')
    baris.append(f'  VIF          : {hasil["vif"]:.1f}')
    baris.append(f'  Tingkat      : {lambang.get(hasil["tingkat"], "")} '
                 f'{hasil["tingkat"].upper()}')
    baris.append('')
    for p in hasil["pesan"]:
        baris.append('  ' + p)
    if hasil["saran"]:
        baris.append('')
        baris.append('  Setelan yang disarankan:')
        for n, v in hasil["saran"].items():
            baris.append(f'    {n} = {v}')
    baris.append('')
    baris.append(f'  KEPUTUSAN: {"LAYAK — data bisa dibuat" if hasil["layak"] else "TIDAK LAYAK — perbaiki setelan dulu"}')
    return '\n'.join(baris)
