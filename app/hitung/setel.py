"""
Penyetel iteratif — inti janji "data sesuai setelan".

RIWAYAT PENYELESAIAN (17Sep26) — semua TERUKUR, bukan dugaan:

  Masalah awal: minta 0,35/0,45/0,30 -> keluar 0,070/0,165/0,078. GAGAL besar.

  Akar 1 — SALAH SATUAN. Yang disetel mula-mula adalah KORELASI X-Y,
    padahal SPSS/PLS membaca KOEFISIEN REGRESI. Dua angka yang berbeda.
    Perbaikan: rxy = Rxx · β  (rumus OLS terstandardisasi).

  Akar 2 — SUSUT DERAU bersifat BERATURAN (bukan acak):
    derau 0,00 -> 100% dari nilai asli
    derau 0,10 ->  93%
    derau 0,20 ->  86%
    derau 0,30 ->  78%
    Pola: faktor = 1 - 0,75·derau. Perbaikan: koreksi_derau().

  Akar 3 — BATAS MUAT item mentok. r_item dibatasi 0,75 -> muat maksimum
    hanya sqrt(0,75) = 0,866. Akibatnya menaikkan beta TIDAK menaikkan hasil
    (sudah dibuktikan: X2 0,45->0,95, hasil tetap ~0,27). Perbaikan: batas
    dinaikkan ke 0,95 -> muat maksimum 0,974.

  Akar 4 — PEMBULATAN skala Likert menyusutkan sinyal ~13%:
    murni 0,348/0,450/0,300 -> setelah item 0,305/0,390/0,266.
    Ini susut NYATA dan memang harus terjadi (data nyata juga begitu).

  KESIMPULAN: tiga akar pertama bisa dihitung, akar keempat tidak bisa
  dihilangkan — HARUS ditutup dengan ITERASI pada hasil UKUR AKHIR.
  Karena itu penyetel ini mengukur uji_spss() (data nyata yang sudah jadi
  item + derau), bukan menghitung dari teori. Satu mekanisme menutup
  seluruh sumber susut, tanpa perlu tahu asalnya satu per satu.

BATAS KEJUJURAN: matriks korelasi wajib positive definite. Kalau setelan
tidak memenuhi (mis. semua variabel 0,9 dengan n kecil), penyetel BERHENTI
dan melaporkan galat terkecil — tidak menyembunyikan, tidak memalsukan.
"""
from __future__ import annotations

import numpy as np

from .mesin import bangun_data, uji_spss, _korelasi_dari_beta  # noqa: F401


def koreksi_derau(beta_minta: dict[str, float], derau: float) -> dict[str, float]:
    """Kompensasi SUSUT akibat derau — dihitung dari pola terukur.

    derau 0,30 -> faktor 0,775 (terukur 78%). Batas: beta tidak boleh
    melewati 0,95·faktor supaya korelasi tetap < 1.
    """
    f = 1.0 - 0.75 * max(0.0, min(0.9, float(derau)))
    batas = 0.95 * f
    return {k: float(np.clip(v / f, -batas, batas)) for k, v in beta_minta.items()}


def _ukur(nama_konstruk, beta, n_resp, item_per, skala, rl, kx, seed,
          ada_med, beta_med):
    """Bangun data + ukur koefisien nyata. Satu tempat, dipakai berulang."""
    d = bangun_data(nama_konstruk, beta, n_resp=n_resp, seed=seed,
                    rasa_lapangan=rl, item_per=item_per, skala=skala,
                    korelasi_x=kx)
    s = uji_spss(d)
    return d, s, {j["dari"]: j["B"] for j in s["jalur"]}


def setel_beta(nama_konstruk: list[str],
               beta_minta: dict[str, float],
               n_resp: int = 187,
               item_per: int = 4,
               skala: int = 5,
               rasa_lapangan: dict | None = None,
               toleransi: float = 0.02,
               maks_putaran: int = 40,
               korelasi_x: np.ndarray | None = None,
               seed: int = 42,
               ada_med: bool = False,
               beta_med: dict[str, float] | None = None) -> dict:
    """Cari beta INTERNAL yang membuat hasil ukur SESUAI beta yang DIMINTA.

    TIGA LAPIS:
      1. Terjemah matematis (rxy = Rxx · β)      — tepat pada derau 0
      2. Kompensasi derau (1 - 0,75·derau)        — menutup susut derau
      3. ITERASI pada hasil ukur akhir            — menutup SEMUA sisa susut
         (item, pembulatan, sel kosong, derau acak)

    Lapis 3 memakai REDAMAN bertahap (faktor mengecil bila makin dekat)
    supaya konvergen dan tidak berayun.

    Return: data, setelan, hasil, galat, putaran, tercapai, catatan, uji_spss
    """
    xs = [k for k in nama_konstruk if k not in ("Y", "M")]
    kx = korelasi_x
    if kx is None:
        m = len(xs)
        kx = np.full((m, m), 0.2) if m else np.zeros((0, 0))
        np.fill_diagonal(kx, 1.0)

    derau = float((rasa_lapangan or {}).get("derau", 0.30))
    beta_kerja = koreksi_derau(beta_minta, derau)

    hasil: dict[str, float] = {}
    galat: dict[str, float] = {}
    catatan: list[str] = []
    data = None
    s_akhir = None
    putaran = 0
    tercapai = False

    for putaran in range(1, maks_putaran + 1):
        data, s_akhir, hasil = _ukur(nama_konstruk, beta_kerja, n_resp,
                                     item_per, skala, rasa_lapangan, kx, seed,
                                     ada_med, beta_med)

        galat = {k: hasil.get(k, 0.0) - float(beta_minta[k]) for k in beta_minta}
        maks_galat = max(abs(v) for v in galat.values()) if galat else 0.0

        if maks_galat <= toleransi:
            tercapai = True
            break

        # REDAMAN BERTAHAP: faktor mengecil saat galat mengecil -> konvergen.
        # f = 0,85 bila galat jauh; turun sampai 0,45 bila galat kecil.
        if maks_galat > 6 * toleransi:
            f_redam = 0.85
        elif maks_galat > 3 * toleransi:
            f_redam = 0.70
        else:
            f_redam = 0.55

        for k in beta_minta:
            beta_kerja[k] = float(np.clip(
                beta_kerja[k] - f_redam * galat[k], -0.97, 0.97))

    if not tercapai:
        sisa = max(abs(v) for v in galat.values()) if galat else 0.0
        catatan.append(
            f"Setelan ini tidak bisa dicapai penuh: setelah {putaran} putaran, "
            f"galat terkecil {sisa:.3f} (toleransi {toleransi}). Penyebab umum: "
            f"total pengaruh yang diminta melebihi kapasitas model "
            f"(n={n_resp}, {item_per} item, derau {derau}). "
            f"Saran: turunkan salah satu koefisien, tambah responden, "
            f"atau kecilkan derau.")

    if s_akhir is None:
        data, s_akhir, hasil = _ukur(nama_konstruk, beta_kerja, n_resp,
                                     item_per, skala, rasa_lapangan, kx, seed,
                                     ada_med, beta_med)

    return {
        "data": data,
        "setelan": {k: float(v) for k, v in beta_minta.items()},
        "hasil": hasil,
        "galat": galat,
        "putaran": putaran,
        "tercapai": tercapai,
        "catatan": catatan,
        "uji_spss": s_akhir,
    }
