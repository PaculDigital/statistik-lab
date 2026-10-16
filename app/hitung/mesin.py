"""
Penelitian STATISTIK Lab. — mesin simulasi data penelitian kuantitatif.

PRINSIP (ACC Bos 17Sep26):
  1. Hitungan LOCAL pakai numpy — TANPA AI (gratis, instan, bisa dipertanggungjawabkan).
  2. TARGET-DRIVEN: yang disetel adalah KOEFISIEN JALUR (beta), bukan korelasi mentah.
     Teknik: tentukan beta -> hitung balik matriks korelasi -> generate -> UKUR ULANG
     -> kalau melenceng, ulangi sampai berada dalam toleransi (LAMPIRAN ITERASI).
  3. RASA LAPANGAN: data harus terlihat seperti data lapangan sungguhan
     (derau, data bolong, jawaban asal/straight-lining, outlier, alpha tidak seragam).
"""
from __future__ import annotations

import math

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# KAMUS ISTILAH — dipakai modul BELAJAR (kamus interaktif)
# ─────────────────────────────────────────────────────────────────────────────

ISTILAH = {
    "koefisien": {
        "nama": "Koefisien (β)",
        "arti": "Angka yang menunjukkan SEBERAPA BESAR dan KE ARAH MANA pengaruh "
                "satu variabel terhadap variabel lain.",
        "cara_baca": "β positif = searah (naik bersama). β negatif = berlawanan. "
                     "Semakin jauh dari 0, semakin kuat.",
        "contoh": "β = 0,34 artinya: tiap kenaikan 1 satuan X, Y naik 0,34 satuan.",
        "jebakan": "β TIDAK sama dengan korelasi. Di PLS-SEM nilainya disebut "
                   "'path coefficient', di SPSS disebut 'B' (unstandardized) atau "
                   "'Beta' (standardized). Beda nama, beda makna.",
        "slider": {"min": -1.0, "max": 1.0, "default": 0.34, "satuan": "β"},
    },
    "pv": {
        "nama": "p-value (nilai p)",
        "arti": "Peluang hasil ini muncul KEBETULAN saja, padahal sebenarnya tidak "
                "ada pengaruh. Semakin KECIL, semakin yakin ada pengaruh nyata.",
        "cara_baca": "p < 0,05 = signifikan (aman). p > 0,05 = belum bisa disimpulkan.",
        "contoh": "p = 0,003 artinya hanya 3 dari 1.000 kemungkinan hasil ini kebetulan.",
        "jebakan": "DILARANG menulis 'p = 0,000'. Yang benar: 'p < 0,001'. "
                   "Dan p besar BUKAN berarti 'tidak ada pengaruh' — hanya "
                   "'belum terbukti pada data ini'.",
        "slider": {"min": 0.0, "max": 0.20, "default": 0.03, "satuan": "p"},
    },
    "r2": {
        "nama": "R² (Koefisien Determinasi)",
        "arti": "Berapa PERSEN variasi Y yang bisa dijelaskan oleh variabel-variabel X.",
        "cara_baca": "R² 0,50 = 50% variasi Y terjelaskan. R² 0,10 = cuma 10%, "
                     "sisanya dijelaskan hal lain di luar model.",
        "contoh": "R² = 0,52 → model cukup baik untuk ilmu sosial.",
        "jebakan": "R² tinggi TIDAK berarti model benar — bisa jadi hanya karena "
                   "banyak variabel. Selalu lihat R² ADJUSTED juga.",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.52, "satuan": "R²"},
    },
    "hetero": {
        "nama": "Heteroskedastisitas",
        "arti": "Keadaan di mana SEBARAN sisaan (error) TIDAK seragam — makin besar "
                "nilai prediksi, makin lebar sebarannya.",
        "cara_baca": "Lihat scatterplot sisaan: kalau membentuk corong/kerucut = ADA "
                     "heteroskedastisitas. Kalau menyebar acak rata = AMAN.",
        "contoh": "Bentuk kerucut (makin ke kanan makin melebar) = masalah.",
        "jebakan": "Di SPSS, uji Glejser/White dipakai untuk memastikan. Kalau "
                   "terjadi: pakai robust standard error, atau transformasi data, "
                   "atau pindah ke PLS-SEM (tidak mensyaratkan homoskedastisitas).",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.1, "satuan": "derajat"},
    },
    "multicol": {
        "nama": "Multikolinearitas",
        "arti": "Keadaan di mana variabel-variabel X saling berkorelasi TINGGI, "
                "sehingga sulit memisahkan pengaruh masing-masing.",
        "cara_baca": "Lihat VIF. VIF < 10 = aman. VIF > 10 = bermasalah. "
                     "Tolerance > 0,10 = aman.",
        "contoh": "X1 dan X2 korelasi 0,95 → VIF bisa di atas 10 → salah satu "
                  "sebaiknya dibuang atau digabung.",
        "jebakan": "Multikolinearitas TIDAK membuat prediksi salah, tapi membuat "
                   "koefisien TIDAK STABIL (berubah drastis kalau data ditambah).",
        "slider": {"min": 0.0, "max": 0.99, "default": 0.2, "satuan": "korelasi X-X"},
    },
    "loading": {
        "nama": "Loading Factor (PLS)",
        "arti": "Seberapa kuat sebuah ITEM (pertanyaan kuesioner) mencerminkan "
                "variabel yang diwakilinya.",
        "cara_baca": "loading > 0,7 = item bagus, pertahankan. "
                     "0,4-0,7 = boleh dipertimbangkan. < 0,4 = BUANG.",
        "contoh": "Item 'pelayanan cepat' loading 0,82 → item itu benar mengukur "
                  "Kualitas Layanan.",
        "jebakan": "Membuang item hanya karena loading rendah TIDAK selalu benar — "
                   "kadang justru ada masalah teori di itemnya. Baca isi itemnya dulu.",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.8, "satuan": "loading"},
    },
    "ave": {
        "nama": "AVE & Discriminant Validity",
        "arti": "AVE = seberapa banyak variasi item yang bisa dijelaskan variabelnya. "
                "Discriminant = apakah antar variabel cukup berbeda.",
        "cara_baca": "AVE > 0,5 = valid. Akar AVE harus > korelasi antar konstruk "
                     "(kriteria Fornell-Larcker).",
        "contoh": "AVE = 0,58 → konstruk valid.",
        "jebakan": "Kalau AVE gagal, jangan langsung buang item — cek dulu apakah "
                   "ada item yang maknanya tumpang tindih dengan konstruk lain.",
        "slider": {"min": 0.2, "max": 1.0, "default": 0.58, "satuan": "AVE"},
    },
    "alpha": {
        "nama": "Cronbach Alpha",
        "arti": "Ukuran KEKONSISTENAN item — apakah semua item dalam satu variabel "
                "mengukur hal yang sama.",
        "cara_baca": "> 0,70 = dapat diterima. > 0,80 = bagus. "
                     "0,60-0,70 = marginal (hati-hati). < 0,60 = bermasalah.",
        "contoh": "Alpha = 0,86 → instrumen konsisten.",
        "jebakan": "Alpha TERLALU TINGGI (> 0,95) juga mencurigakan — biasanya "
                   "artinya ada item yang isinya hampir sama persis (redundan).",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.85, "satuan": "α"},
    },
    "mediasi": {
        "nama": "Mediasi (Variabel Perantara)",
        "arti": "X tidak langsung memengaruhi Y, tapi LEWAT M dulu. "
                "Urutannya: X → M → Y.",
        "cara_baca": "Mediasi PENUH: jalur langsung X→Y tidak signifikan, tapi "
                     "X→M dan M→Y signifikan. "
                     "Mediasi SEBAGIAN: jalur langsung tetap signifikan.",
        "contoh": "Harga → Kepuasan → Loyalitas. Harga tidak langsung "
                  "membuat orang loyal, tapi lewat rasa puas dulu.",
        "jebakan": "Uji mediasi JANGAN pakai metode Baron & Kenny bertahap saja — "
                   "pakai Sobel test, atau lebih baik bootstrapping (di PLS sudah "
                   "otomatis). Baron & Kenny dianggap usang untuk mediasi.",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.45, "satuan": "efek"},
    },
    "moderasi": {
        "nama": "Moderasi (Variabel Penyangga)",
        "arti": "Variabel Z mengubah KEKUATAN atau ARAH hubungan X terhadap Y. "
                "Hubungannya X * Z → Y.",
        "cara_baca": "Lihat koefisien interaksi: kalau signifikan, Z benar memoderasi.",
        "contoh": "Promosi → Penjualan, dimoderasi (diperkuat/diperlemah) oleh "
                  "Lokasi. Di lokasi ramai, promosi lebih efektif.",
        "jebakan": "JANGAN lupa CENTER (mean-center) variabel sebelum membuat "
                   "interaksi — kalau tidak, muncul multikolinearitas palsu.",
        "slider": {"min": -1.0, "max": 1.0, "default": 0.25, "satuan": "interaksi"},
    },
    "uji_jalur": {
        "nama": "Uji Jalur (Path Analysis)",
        "arti": "Menguji pengaruh langsung antar variabel dalam model. "
                "Di SPSS: regresi bertahap. Di PLS-SEM: bootstrapping.",
        "cara_baca": "SPSS → lihat Sig. (p-value) dan t. "
                     "PLS → lihat Path Coefficient, T Statistics, dan P Values.",
        "contoh": "PLS: koefisien 0,412 · t = 4,873 · p = 0,000 → signifikan.",
        "jebakan": "SPSS dan PLS bisa memberi hasil BERBEDA pada data yang sama. "
                   "Itu NORMAL, bukan kesalahan — mesinnya beda (SPSS = OLS, "
                   "PLS = variance-based, tidak mensyaratkan normalitas).",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.4, "satuan": "jalur"},
    },
    "vif": {
        "nama": "VIF (Variance Inflation Factor)",
        "arti": "Angka yang menunjukkan SEBERAPA BURUK multikolinearitas "
                "mempengaruhi hasil.",
        "cara_baca": "VIF 1 = tidak ada masalah (ideal). VIF > 10 = bermasalah serius.",
        "contoh": "VIF = 1,8 → aman.",
        "jebakan": "VIF dihitung PER variabel, jadi bisa satu variabel bermasalah "
                   "dan yang lain aman.",
        "slider": {"min": 1.0, "max": 15.0, "default": 1.8, "satuan": "VIF"},
    },
    "kualitatif": {
        "nama": "Penelitian Kualitatif",
        "arti": "Penelitian yang datanya TEKS (hasil wawancara, observasi), bukan "
                "angka. Tujuannya MEMAHAMI, bukan mengukur.",
        "cara_baca": "Beda mendasar dari kuantitatif: ARAH ALURNYA KEBALIK. "
                     "Kualitatif = INDUKTIF (dari lapangan → naik jadi teori). "
                     "Kuantitatif = DEDUKTIF (dari teori → diuji di lapangan).",
        "contoh": "Kuantitatif: 'Apakah harga berpengaruh pada kepuasan?' (uji). "
                  "Kualitatif: 'Bagaimana mahasiswa memaknai rasa puas?' (pahami).",
        "jebakan": "JANGAN pakai SPSS/PLS untuk data kualitatif. Alatnya beda: "
                   "NVivo, Atlas.ti, atau analisis manual. Dan kualitatif TIDAK "
                   "punya hipotesis — yang ada rumusan masalah.",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.5, "satuan": "induktif"},
    },
    "deduktif": {
        "nama": "Alur Deduktif vs Induktif",
        "arti": "Cara MENYUSUN argumen penelitian. Deduktif = UMUM → KHUSUS. "
                "Induktif = KHUSUS → UMUM.",
        "cara_baca": "KUANTITATIF = DEDUKTIF: teori dulu (grand theory P1-2, "
                     "middle theory P3-4), baru masalah/gap (P5-6), baru rumusan (P7-8). "
                     "KUALITATIF = INDUKTIF: fenomena lapangan dulu (P1-3), "
                     "signifikansi (P4-5), fokus (P6-7), pertanyaan (P8).",
        "contoh": "Deduktif: Grand Theory → Middle Theory → Gap → Rumusan. "
                  "Induktif: Fenomena → Signifikansi → Fokus → Pertanyaan.",
        "jebakan": "DILARANG: kuantitatif dibuka cerita lapangan; kualitatif dibuka "
                   "teori. Ini kesalahan paling sering di latar belakang mahasiswa.",
        "slider": {"min": 0.0, "max": 1.0, "default": 0.5, "satuan": "alur"},
    },
    "sobel": {
        "nama": "Uji Sobel",
        "arti": "Rumus untuk menguji apakah efek mediasi signifikan, tanpa "
                "bootstrapping.",
        "cara_baca": "Hitung nilai z Sobel. |z| > 1,96 = mediasi signifikan.",
        "contoh": "z = 2,84 → mediasi signifikan pada α = 5%.",
        "jebakan": "Uji Sobel mengasumsikan distribusi normal — padahal distribusi "
                   "efek tidak langsung biasanya MIRING (tidak normal). Karena itu "
                   "banyak ahli sekarang lebih merekomendasikan bootstrapping "
                   "(tersedia otomatis di PLS-SEM).",
        "slider": {"min": 0.0, "max": 5.0, "default": 2.84, "satuan": "z"},
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# PEMBANGUN MATRIKS KORELASI DARI KOEFISIEN JALUR
# ─────────────────────────────────────────────────────────────────────────────

def matriks_dari_jalur(beta: dict[str, float],
                       nama_konstruk: list[str] | None = None,
                       korelasi_x: np.ndarray | None = None) -> tuple[np.ndarray, list[str]]:
    """Bangun matriks korelasi antar KONSTRUK dari koefisien jalur.

    Model yang didukung fungsi ini (jaring sederhana):
      Y = sum(beta[X->Y] * X) + beta[M->Y] * M + error

    Parameter
    ---------
    beta : dict, mis. {'X1': 0.35, 'X2': 0.45, 'M': 0.40}
           Kunci tanpa panah = pengaruh LANGSUNG ke Y. Kunci 'X1->M'
           = pengaruh X1 ke mediasi M.
    nama_konstruk : urutan nama yang WAJIB ada (termasuk 'Y').
           Kalau None, disusun sendiri dari kunci beta + 'Y'.
    korelasi_x : matriks korelasi antar X (default: moderat 0,2)

    Return
    ------
    (matriks_korelasi, urutan_nama) — SATU SUMBER urutan nama, supaya
    pemanggil tidak menyusun namanya sendiri (ini akar bug 17Sep26).
    """
    if nama_konstruk:
        # hormati urutan dari pemanggil, tapi pastikan prediktor ikut masuk
        nama = list(dict.fromkeys(list(nama_konstruk) +
                                  [k for k in beta if k != "M"] +
                                  (["M"] if "M" in beta else []) + ["Y"]))
    else:
        xs0 = sorted(k for k in beta if k != "M")
        nama = xs0 + (["M"] if "M" in beta else []) + ["Y"]

    n = len(nama)
    R = np.eye(n)
    xs = [k for k in nama if k not in ("M", "Y")]

    # 1) korelasi antar X (yang mendahului)
    if korelasi_x is None:
        k = len(xs)
        korelasi_x = np.full((k, k), 0.2) if k else np.zeros((0, 0))
        np.fill_diagonal(korelasi_x, 1.0)
    Rx = np.asarray(korelasi_x, dtype=float)
    for xi in xs:
        for xj in xs:
            R[nama.index(xi), nama.index(xj)] = Rx[xs.index(xi), xs.index(xj)]

    # 2) M sebagai fungsi X (kalau ada mediasi): M = aX + e
    if "M" in nama:
        i_m = nama.index("M")
        for xi in xs:
            a = beta.get(f"{xi}->M", beta.get(f"M~{xi}", 0.4))
            R[i_m, nama.index(xi)] = R[nama.index(xi), i_m] = a

    # 3) Y sebagai fungsi X dan M.
    #    PENTING: beta yang diminta diterjemahkan dulu jadi KORELASI
    #    (lihat _korelasi_dari_beta) — kalau tidak, koefisien yang keluar
    #    akan jauh lebih kecil dari setelan karena efek VIF.
    i_y = nama.index("Y")
    beta_minta = np.array([beta.get(xi, 0.0) for xi in xs])
    if "M" in nama:
        # dengan mediasi: rxy = Rx·βx + a·βm  (a = jalur X->M)
        a_vec = np.array([beta.get(f"{xi}->M", beta.get(f"M~{xi}", 0.0)) for xi in xs])
        beta_m = beta.get("M", beta.get("M->Y", 0.0))
        rxy = Rx @ beta_minta + a_vec * beta_m
    else:
        rxy = _korelasi_dari_beta(beta_minta, Rx)
    for j, xi in enumerate(xs):
        rxy_j = float(np.clip(rxy[j], -0.98, 0.98))
        R[i_y, nama.index(xi)] = R[nama.index(xi), i_y] = rxy_j
    if "M" in nama:
        i_m = nama.index("M")
        R[i_y, i_m] = R[i_m, i_y] = beta.get("M", beta.get("M->Y", 0.4))

    return _paskan_ke_valid(R, nama), nama


def _paskan_ke_valid(R: np.ndarray, nama: list[str]) -> np.ndarray:
    """Pastikan matriks POSITIVE DEFINITE (kalau tidak, np akan error).

    Matriks korelasi dari beta sembarangan bisa tidak konsisten secara
    matematis. Perbaikan: eigen-clip (buang komponen negatif kecil).
    """
    R = (R + R.T) / 2
    np.fill_diagonal(R, 1.0)
    w, v = np.linalg.eigh(R)
    if w.min() < 1e-8:
        w = np.clip(w, 1e-6, None)
        R = v @ np.diag(w) @ v.T
        d = np.sqrt(np.diag(R))
        R = R / np.outer(d, d)
        np.fill_diagonal(R, 1.0)
    return R


def _korelasi_dari_beta(beta_y: np.ndarray, Rx: np.ndarray) -> np.ndarray:
    r"""Terjemahkan KOEFISIEN REGRESI yang DIMINTA menjadi KORELASI yang perlu.

    Ini akar konseptual proyek ini (pelajaran 17Sep26).

    KENAPA PERLU: kalau kita menyetel korelasi X-Y = 0,35 lalu variabel X
    saling berkorelasi, koefisien REGRESI yang keluar JAUH LEBIH KECIL dari
    0,35 — karena pengaruh antar X saling "memakan" (itulah yang diukur VIF).
    Pengguna minta "pengaruh X2 = 0,45", dan yang dibaca SPSS/PLS adalah
    KOEFISIEN, bukan korelasi mentah.

    RUMUS (dari OLS terstandardisasi):  β = Rxx⁻¹ · rxy
    maka kebalikannya:                  rxy = Rxx · β

    Parameter
    ---------
    beta_y : array koefisien yang DIMINTA (tiap X, ke Y)
    Rx     : matriks korelasi ANTAR X

    Return
    ------
    vektor korelasi tiap X terhadap Y
    """
    return Rx @ np.asarray(beta_y, dtype=float)


# ─────────────────────────────────────────────────────────────────────────────
# PEMBANGKIT DATA
# ─────────────────────────────────────────────────────────────────────────────

def bangun_data(nama_konstruk: list[str],
                beta: dict[str, float],
                n_resp: int = 187,
                seed: int = 42,
                rasa_lapangan: dict | None = None,
                item_per: int = 4,
                skala: int = 5,
                korelasi_x: np.ndarray | None = None) -> dict:
    """Bangun data simulasi lengkap: skor konstruk + item kuesioner.

    Parameter 'rasa_lapangan' (semua opsional, default = natural):
      derau          : 0.0-0.6  (seberapa berisik; 0,25-0,35 = natural)
      bolong_persen  : 0.0-0.10 (persen sel kosong)
      asal_persen    : 0.0-0.20 (straight-lining: jawab angka sama semua)
      outlier_persen : 0.0-0.10 (responden ekstrem)
      alpha_min/max  : rentang alpha per konstruk (mis. 0,72-0,88)
    """
    rl = dict(derau=0.30, bolong_persen=0.02, asal_persen=0.06,
              outlier_persen=0.03, alpha=(0.72, 0.90))
    if rasa_lapangan:
        rl.update(rasa_lapangan)

    rng = np.random.default_rng(seed)
    R, nama = matriks_dari_jalur(beta, nama_konstruk=nama_konstruk,
                                 korelasi_x=korelasi_x)

    # 1) skor laten dari matriks korelasi
    Z = rng.multivariate_normal(np.zeros(len(nama)), R, size=n_resp)
    Z = (Z - Z.mean(0)) / Z.std(0)

    # 2) tambah derau (biar tidak terlalu sempurna)
    Z = Z * math.sqrt(1 - float(rl["derau"])) + \
        rng.normal(0, math.sqrt(float(rl["derau"])), Z.shape)

    # 3) turunkan ke ITEM (tiap konstruk -> item_per item + derau alpha)
    #
    #    ⚠ TEMUAN 17Sep26 (akar terakhir Skenario A): alpha yang DIACAK bisa
    #    jatuh ke 0,72 pada variabel yang justru harus berefek besar. Item yang
    #    "kabur" membuat sinyalnya tertutup derau -> koefisien MACET, dinaikkan
    #    berapa pun tetap ~0,31 (terbukti: X2 muat 0,632, alpha 0,727).
    #
    #    PERBAIKAN: alpha diacak, TAPI diberi LANTAI yang bergantung pada besar
    #    pengaruh variabel itu. Variabel dengan beta besar wajib punya item yang
    #    cukup tajam. Ini juga realistis: peneliti yang serius mengukur variabel
    #    pentingnya dengan instrumen yang lebih baik.
    lo, hi = rl["alpha"]
    beta_abs = {k: abs(float(v)) for k, v in beta.items()}
    maks_beta = max(beta_abs.values()) if beta_abs else 1.0
    item = {}
    alpha_dipakai = {}
    muat_dipakai = {}
    for i, nm in enumerate(nama):
        target_alpha = float(rng.uniform(lo, hi))
        if nm in beta_abs and maks_beta > 0:
            # lantai alpha: makin besar pengaruh, makin tinggi lantainya.
            lantai = lo + (hi - lo) * 0.45 * (beta_abs[nm] / maks_beta)
            target_alpha = max(target_alpha, lantai)
        target_alpha = float(np.clip(target_alpha, lo, 0.97))
        # dari alpha -> korelasi item rata-rata:  a = k*r / (1+(k-1)r)
        k = item_per
        r_item = target_alpha / (k - target_alpha * (k - 1)) if target_alpha < 1 else 0.5
        # ⚠ JANGAN batasi 0,75 — dulu di sini muat mentok 0,866 dan beta tidak
        #   bisa dinaikkan (temuan 17Sep26: X2 dinaikkan, hasil tidak naik).
        r_item = float(np.clip(r_item, 0.05, 0.95))
        muat = math.sqrt(r_item)
        sisa = math.sqrt(max(1e-9, 1 - r_item))
        mat = np.zeros((n_resp, k))
        for j in range(k):
            mat[:, j] = muat * Z[:, i] + sisa * rng.normal(0, 1, n_resp)
        # Skala Likert: PERTAHANKAN proporsi variasi nyata.
        # Dulu dipaksa 0,85 lalu dibulatkan -> sinyal teredam dua kali.
        sd = mat.std()
        if sd > 0:
            mat = (mat - mat.mean(0)) / sd
        item[nm] = np.clip(np.rint(mat + (skala + 1) / 2), 1, skala).astype(int)
        alpha_dipakai[nm] = round(target_alpha, 3)
        muat_dipakai[nm] = round(muat, 3)

    # 4) rasa lapangan: data bolong, jawaban asal, outlier
    n_bolong = int(round(n_resp * len(nama) * item_per * rl["bolong_persen"]))
    for _ in range(n_bolong):
        nm = str(rng.choice(nama))
        r = int(rng.integers(0, n_resp))
        c = int(rng.integers(0, item_per))
        item[nm][r, c] = -1                      # -1 = kosong

    n_asal = int(round(n_resp * rl["asal_persen"]))
    idx_asal = rng.choice(n_resp, size=n_asal, replace=False) if n_asal else []
    for r in idx_asal:
        nm = str(rng.choice(nama))
        item[nm][r, :] = int(rng.integers(1, skala + 1))

    n_out = int(round(n_resp * rl["outlier_persen"]))
    idx_out = rng.choice(n_resp, size=n_out, replace=False) if n_out else []
    for r in idx_out:
        nm = str(rng.choice(nama))
        ekstrem = 1 if rng.random() < 0.5 else skala
        item[nm][r, :] = ekstrem

    return {"nama_konstruk": nama, "item": item, "n_resp": n_resp,
            "alpha_dipakai": alpha_dipakai, "muat_dipakai": muat_dipakai,
            "beta_setelan": beta, "seed": seed, "rasa_lapangan": rl,
            "responden_asal": [int(x) for x in idx_asal],
            "responden_outlier": [int(x) for x in idx_out]}


# ─────────────────────────────────────────────────────────────────────────────
# UJI — SPSS (OLS) dan PLS-SEM (variance-based, disederhanakan)
# ─────────────────────────────────────────────────────────────────────────────

def _skor_konstruk(data: dict) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Ubah item -> skor konstruk (rata-rata item, sel kosong dilewati)."""
    nama = data["nama_konstruk"]
    kolom = []
    for nm in nama:
        it = data["item"][nm].astype(float)
        it = np.where(it < 0, np.nan, it)
        kolom.append(np.nanmean(it, axis=1))
    X = np.column_stack(kolom)
    X = np.nan_to_num(X, nan=float(np.nanmean(X)))
    return X, np.column_stack(kolom), nama


def alpha_cronbach(item: np.ndarray) -> float:
    """Cronbach alpha dari matriks item (baris=responden, kolom=item)."""
    it = np.where(item < 0, np.nan, item.astype(float))
    it = it[~np.isnan(it).any(axis=1)]
    if len(it) < 3 or it.shape[1] < 2:
        return float("nan")
    k = it.shape[1]
    var_item = it.var(axis=0, ddof=1).sum()
    var_total = it.sum(axis=1).var(ddof=1)
    if var_total == 0:
        return float("nan")
    return float(k / (k - 1) * (1 - var_item / var_total))


def uji_spss(data: dict, y: str = "Y") -> dict:
    """Regresi berganda ala SPSS (OLS): koefisien, t, p, R², VIF, uji asumsi."""
    X, Xr, nama = _skor_konstruk(data)
    i_y = nama.index(y)
    pred = [i for i in range(len(nama)) if i != i_y]
    xv = X[:, pred]
    yv = X[:, i_y]

    # OLS: beta = (X'X)^-1 X'y  (pakai lstsq biar aman)
    A = np.column_stack([np.ones(len(xv)), xv])
    coef, *_ = np.linalg.lstsq(A, yv, rcond=None)
    yhat = A @ coef
    resid = yv - yhat
    n, p = A.shape
    dof = n - p
    s2 = (resid @ resid) / dof if dof > 0 else float("nan")

    # galat baku -> t -> p
    try:
        XtX_inv = np.linalg.inv(A.T @ A)
        se = np.sqrt(np.diag(XtX_inv) * s2)
    except np.linalg.LinAlgError:
        se = np.full(p, float("nan"))
    t = coef / se
    from scipy import stats
    pvals = 2 * (1 - stats.t.cdf(np.abs(t), dof)) if dof > 0 \
        else np.full(p, float("nan"))

    # R² dan adjusted
    sst = ((yv - yv.mean()) ** 2).sum()
    ssr = (resid ** 2).sum()
    r2 = 1 - ssr / sst if sst else float("nan")
    r2_adj = 1 - (1 - r2) * (n - 1) / dof if dof > 0 else float("nan")

    # VIF per prediktor
    vif = {}
    for j, k in enumerate(pred):
        lain = [q for q in pred if q != k]
        if not lain:
            vif[nama[k]] = 1.0
            continue
        Aj = np.column_stack([np.ones(n), X[:, lain]])
        cj, *_ = np.linalg.lstsq(Aj, X[:, k], rcond=None)
        rj = X[:, k] - Aj @ cj
        ss_tot = ((X[:, k] - X[:, k].mean()) ** 2).sum()
        r2j = 1 - (rj @ rj) / ss_tot if ss_tot else 0.0
        vif[nama[k]] = float(1 / max(1e-6, 1 - r2j))

    # uji asumsi: normalitas (Jarque-Bera sederhana), hetero (korelasi |resid| vs yhat),
    # Durbin-Watson
    from scipy import stats as st
    jb, jb_p = st.jarque_bera(resid) if n > 8 else (float("nan"), float("nan"))
    rho_abs = float(np.corrcoef(np.abs(resid), yhat)[0, 1]) if n > 3 else float("nan")
    dw = float(((np.diff(resid) ** 2).sum()) / (resid @ resid)) if resid @ resid else float("nan")

    return {
        "alat": "SPSS (OLS)",
        "n": int(n),
        "konstanta": float(coef[0]),
        "jalur": [{"dari": nama[pred[j]], "ke": y,
                   "B": float(coef[j + 1]), "SE": float(se[j + 1]),
                   "t": float(t[j + 1]), "p": float(pvals[j + 1]),
                   "signifikan": bool(pvals[j + 1] < 0.05)}
                  for j in range(len(pred))],
        "vif": vif,
        "r2": float(r2), "r2_adj": float(r2_adj), "se_residu": float(math.sqrt(max(0, s2))),
        "asumsi": {
            "normalitas_jb": float(jb), "normalitas_p": float(jb_p),
            "normal": bool(jb_p > 0.05) if not math.isnan(jb_p) else None,
            "hetero_rho": rho_abs,
            "ada_hetero": bool(abs(rho_abs) > 0.25) if not math.isnan(rho_abs) else None,
            "durbin_watson": dw,
            "vif_maks": float(max(vif.values())) if vif else float("nan"),
            "ada_multicol": bool(max(vif.values()) > 10) if vif else False,
        },
    }


def uji_pls(data: dict, y: str = "Y", n_boot: int = 500,
            seed: int = 7) -> dict:
    """PLS-SEM sederhana: path coefficient + bootstrapping t/p + reliabilitas.

    Catatan jujur: ini PLS MODE A yang disederhanakan (bukan SmartPLS penuh).
    Angka AVE/CR/loading dihitung dari data item nyata, bukan dikarang.
    """
    X, _, nama = _skor_konstruk(data)
    i_y = nama.index(y)
    pred = [i for i in range(len(nama)) if i != i_y]
    xv = X[:, pred]
    yv = X[:, i_y]

    # standardisasi -> path coefficient = beta terstandardisasi
    def std(v):
        return (v - v.mean()) / (v.std() or 1)
    xs, ys = std(xv), std(yv)
    A = np.column_stack([np.ones(len(xs)), xs])
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    beta = coef[1:]

    # bootstrapping -> galat baku -> t -> p
    rng = np.random.default_rng(seed)
    boot = np.zeros((n_boot, len(beta)))
    n = len(ys)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        Ab = A[idx]
        try:
            cb, *_ = np.linalg.lstsq(Ab, ys[idx], rcond=None)
            boot[b] = cb[1:]
        except Exception:
            boot[b] = beta
    se = boot.std(axis=0, ddof=1)
    tval = beta / np.where(se == 0, 1e-9, se)
    from scipy import stats
    pval = 2 * (1 - stats.t.cdf(np.abs(tval), n - 1))

    # R² / f² / Q²
    yhat = A @ coef
    r2 = 1 - ((ys - yhat) ** 2).sum() / ((ys - ys.mean()) ** 2).sum()
    f2 = {}
    for j, k in enumerate(pred):
        lain = [q for q in range(len(pred)) if q != j]
        if lain:
            Al = np.column_stack([np.ones(n), xs[:, lain]])
            cl, *_ = np.linalg.lstsq(Al, ys, rcond=None)
            r2l = 1 - ((ys - Al @ cl) ** 2).sum() / ((ys - ys.mean()) ** 2).sum()
        else:
            r2l = 0.0
        f2[nama[k]] = float((r2 - r2l) / max(1e-9, 1 - r2))
    q2 = float(1 - ((ys - yhat) ** 2).sum() / ((ys - ys.mean()) ** 2).sum())

    # reliabilitas & validitas dari ITEM
    reliab = {}
    for nm in nama:
        it = data["item"][nm]
        a = alpha_cronbach(it)
        bersih = it[~np.isnan(np.where(it < 0, np.nan, it.astype(float))).any(axis=1)]
        bersih = np.where(bersih < 0, np.nan, bersih.astype(float))
        if bersih.size == 0 or bersih.shape[1] < 2:
            reliab[nm] = {"alpha": a}
            continue
        z = (bersih - bersih.mean(0)) / (bersih.std(0, ddof=1) + 1e-12)
        # loading = korelasi item dengan skor konstruk
        skor = np.nanmean(z, axis=1)
        ld = [float(np.corrcoef(z[:, j], skor)[0, 1]) for j in range(z.shape[1])]
        ave = float(np.mean([l ** 2 for l in ld]))
        cr = float((sum(ld) ** 2) / (sum(ld) ** 2 + sum(1 - np.array(ld) ** 2)))
        reliab[nm] = {"alpha": a, "loading": [round(x, 3) for x in ld],
                      "ave": round(ave, 3), "cr": round(cr, 3),
                      "valid": bool(ave > 0.5),
                      "semua_loading_ok": bool(min(ld) > 0.7)}

    return {
        "alat": "PLS-SEM (bootstrapping)",
        "n": int(n), "n_boot": n_boot,
        "jalur": [{"dari": nama[pred[j]], "ke": y,
                   "koefisien": float(beta[j]), "SE": float(se[j]),
                   "t": float(tval[j]), "p": float(pval[j]),
                   "signifikan": bool(pval[j] < 0.05)}
                  for j in range(len(pred))],
        "r2": float(r2), "q2": q2, "f2": f2,
        "reliabilitas": reliab,
    }
