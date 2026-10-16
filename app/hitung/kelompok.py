"""PEMBANGUN DATA BERKELOMPOK untuk MANOVA — pola "MASUK".

═══════════════════════════════════════════════════════════════════════════
KENAPA TERPISAH (R4 dipatuhi)
  Format data lama `{'item':…, 'skor_konstruk':…}` dipakai 17 grup gerbang.
  Menambah kolom "kelompok" ke bentuk itu = MENYENTUH SEMUA UJI LAMA, dan
  itu DILARANG (perintah Bos: "agar tidak bertumpuk dan menimpa").
  ⇒ Kelompok dibangun di berkas SENDIRI, tidak mengubah bentuk lama.

POLA YANG SUDAH JALAN (catatan RUANG_MANOVA §6):
  MASUK  → mesin MEMBANGUN data (termasuk kelompok)
  KELUAR → mesin MENGUJI & memberi kunci jawaban

CARA MEMBANGUN (mengikuti pelajaran mesin lama, 17Sep26):
  Bangun BERURUTAN, jangan dari satu matriks korelasi (itu mendesak batas
  positive-definite → koefisien liar). Di sini urutannya:
    (1) tiap kelompok punya RERATA sendiri pada tiap Y  ← INI sumber bedanya
    (2) responden digeser ke rerata kelompoknya
    (3) diberi skor item (Likert) 2–3 butir per Y, dengan susut yang sama
  Koefisien/rerata yang DIPASANG = yang TERBACA (diukur, bukan diklaim).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

ALPHA_ITEM = 0.85          # keandalan butir (mengikuti mesin lama)
MIN_ITEM = 2
MAKS_ITEM = 3

# ═══════════════════════════════════════════════════════════════════════════
#  FAKTOR KALIBRASI — TERUKUR, BUKAN DIKARANG (ACC Bos 21Sep26, Opsi A)
# ═══════════════════════════════════════════════════════════════════════════
#  Kenapa perlu: beda kelompok yang DIPASANG tersusut saat jadi item Likert.
#  Diukur 90 kombinasi (6 butir × 5 beda × 3 undian) lewat
#  `ukur_kalibrasi_kelompok.py`. Hasil peta rasio (terbaca ÷ dipasang):
#
#     butir |  0,20   0,50   0,90   1,50   2,50
#     ------+------------------------------------
#       2   | 0,725  0,757  0,757  0,708  0,659
#       6   | 0,736  0,759  0,760  0,714  0,660
#       8   | 0,736  0,759  0,760  0,714  0,660
#
#  2 TEMUAN TERUKUR:
#    (1) Jumlah butir BUKAN akarnya — butir 2 vs 8 sama saja (0,757 vs 0,760).
#        Karena itu TIDAK perlu memaksa butir banyak.
#    (2) Rasio SERAGAM di rentang beda kecil–sedang (0,20–0,90 → 0,73–0,76);
#        baru menurun saat beda besar (1,50 → 0,71 · 2,50 → 0,66).
#
#  ⇒ Dipakai SATU faktor pada rentang lazim skripsi/tesis (0,20–0,90),
#    sesuai keputusan Bos: sederhana, sama gaya dengan koreksi `1/√alpha`
#    yang sudah terbukti di mesin lama.
#  Sebar antar-undian ±0,05 — itu galat pensampelan (hukum), bukan cacat.
FAKTOR_KALIBRASI = 1.0 / 0.755       # ≈ 1,3245
BEDA_LAZIM = 0.90                    # di atas ini pakai faktor kedua
FAKTOR_KALIBRASI_BESAR = 1.0 / 0.660  # ≈ 1,515 (khusus beda > 0,90)

#  ═══════════════════════════════════════════════════════════════════════
#  BATAS RENTANG RESMI — TERUKUR (ACC Bos 21Sep26, Opsi A)
#  ═══════════════════════════════════════════════════════════════════════
#  Kalibrasi HANYA akurat di rentang tertentu. Diukur 4 undian per titik:
#
#    dipasang | akurasi | keadaan
#    ---------+---------+------------------------
#      0,20   |  77%    | kurang akurat (beda terlalu kecil)
#      0,35   |  80%    | cukup
#      0,50   |  85%    | baik
#      0,70   |  88%    | baik
#      0,90   |  88%    | baik
#      1,20   |  96%    | ⭐ PALING akurat
#      1,50   |  ~90%   | baik  ← batas atas yang dipakai
#      1,80   |  90%    | mulai meleset tidak rata
#      2,50   |  76%    | ❌ di luar kemampuan — DITOLAK
#
#  ⇒ Rentang resmi = 0,30 .. 1,50. Di luar itu DITOLAK dengan saran
#    (pola pagar yang sudah ada di proyek: BATAS_BETA_RANTAI = 1,20).
#    Bukan dikarang: angkanya dari peta ukur di atas.
BEDA_MIN = 0.30
BEDA_MAKS = 1.50


def periksa_beda(beda) -> dict:
    """Pagar JUJUR untuk beda kelompok — tolak + beri jalan keluar.

    Kenapa dipagar (bukan dibiarkan): di luar 0,30–1,50 kalibrasi mesin
    TIDAK lagi akurat (terukur: beda 2,50 hanya 76% akurat). Menghasilkan
    data yang kelihatan sah padahal meleset = menyesatkan mahasiswa.
    ⇒ Prinsip proyek: tolak jujur + beri angka wajar, JANGAN diam-diam.
    """
    import numpy as _np
    b = _np.asarray(beda, dtype=float)
    salah = []
    # ⚠️ PELAJARAN UJI (21Sep26): beda 0,00 itu SAH — artinya "kelompok memang
    #    sama" (dipakai sebagai kelompok PEMBANDING / uji kontrol). Yang perlu
    #    dipagar hanya beda yang TERLALU KECIL tapi TIDAK nol (>0 s/d <0,30),
    #    karena di situ kalibrasi tidak akurat tapi hasilnya kelihatan sah.
    salah_kecil = (b > 1e-9) & (b < BEDA_MIN)
    if salah_kecil.any():
        kecil = _np.sort(b[salah_kecil])
        salah.append(f'ada beda terlalu kecil '
                     f'({", ".join(f"{v:.2f}" for v in kecil[:3])}) — '
                     f'mesin belum akurat di bawah {BEDA_MIN:.2f}')
    if (b > BEDA_MAKS).any():
        salah.append(f'ada beda di atas {BEDA_MAKS:.2f} '
                     f'(terbesar {float(b.max()):.2f})')
    if not salah:
        return {'boleh': True, 'bedamin': BEDA_MIN, 'bedamaks': BEDA_MAKS}
    # saran: tarik ke rentang yang akurat, TAPI beda nol dibiarkan nol
    b_saran = _np.where(_np.abs(b) <= 1e-9, 0.0,
                        _np.clip(b, BEDA_MIN, BEDA_MAKS))
    return {
        'boleh': False,
        'sebab': 'Beda kelompok: ' + ' · '.join(salah) +
                 f'. Mesin akurat pada {BEDA_MIN:.2f}–{BEDA_MAKS:.2f} '
                 f'(atau 0,00 = tidak ada beda).',
        'saran': b_saran.tolist(),
        'pesan': (f'Beda kelompok yang bisa dibuat dengan akurat: '
                  f'{BEDA_MIN:.2f} sampai {BEDA_MAKS:.2f} — '
                  f'atau 0,00 kalau kelompoknya memang sengaja dibuat sama. '
                  f'Di luar itu hasilnya akan meleset, jadi ditolak dulu '
                  f'supaya tidak menyesatkan. Nilai yang disarankan: '
                  f'{", ".join(f"{v:.2f}" for v in b_saran.tolist())}.'),
        'bedamin': BEDA_MIN, 'bedamaks': BEDA_MAKS,
    }


def buat_data_kelompok(
    n_per_kelompok: int | Sequence[int] = 60,
    nama_kelompok: Sequence[str] | None = None,
    nama_y: Sequence[str] | None = None,
    beda: Sequence[float] | Sequence[Sequence[float]] | None = None,
    skala: int = 5,
    mode: str = 'presisi',
    seed: int | None = None,
    butir: int = 2,
) -> dict:
    """Bangun data berkelompok + kolom kelompok (untuk MANOVA).

    n_per_kelompok : jumlah responden TIAP kelompok. Boleh satu angka
                     (sama rata) atau daftar (beda-beda).
    nama_kelompok  : mis. ['Kelas A', 'Kelas B'] — kalau kosong → 'Kelompok 1'…
    nama_y         : nama variabel hasil, mis. ['Minat', 'Nilai'].
    beda           : SEBERAPA BEDA tiap kelompok pada tiap Y.
                     · None        → diisi MESIN, PROPORSIONAL (keputusan Bos
                                     19Sep26: "range β ditentukan mesin",
                                     ikut pola model, bukan rata).
                     · [0.8, 0.0]  → satu angka per Y (beda makin besar antar
                                     kelompok, seragam untuk semua Y).
                     · [[0.8, 0.2], [0.0, 0.0]] → per kelompok × per Y.
    butir          : jumlah butir Likert per Y (2 atau 3).
    mode           : 'presisi' (susut butir dikoreksi) ·
                     'natural' (apa adanya, seperti data lapangan) ·
                     'presisi_variasi' (koefisien tetap, p digeser derau).
    """
    rng = np.random.default_rng(seed)

    # ── Nama kelompok ────────────────────────────────────────────────
    if nama_kelompok is None:
        if isinstance(n_per_kelompok, (list, tuple)):
            nama_kelompok = [f'Kelompok {i + 1}'
                             for i in range(len(n_per_kelompok))]
        else:
            nama_kelompok = ['Kelompok 1', 'Kelompok 2']
    nama_kelompok = [str(q) for q in nama_kelompok]
    k = len(nama_kelompok)

    # ── Jumlah responden tiap kelompok ───────────────────────────────
    if isinstance(n_per_kelompok, (list, tuple)):
        n_list = [max(3, int(q)) for q in n_per_kelompok]
        if len(n_list) != k:
            raise ValueError('n_per_kelompok dan nama_kelompok jumlahnya beda')
    else:
        n_list = [max(3, int(n_per_kelompok))] * k
    n = int(sum(n_list))

    # ── Nama Y ───────────────────────────────────────────────────────
    if nama_y is None:
        nama_y = ['Hasil 1', 'Hasil 2']
    nama_y = [str(q) for q in nama_y]
    p = len(nama_y)

    # ── Beda antar kelompok: kalau kosong, MESIN yang menentukan ─────
    #  PROPORSIONAL (keputusan Bos): beda pertama besar, berikutnya
    #  makin kecil mengikuti pola — bukan rata. Terukur, bukan karangan.
    if beda is None:
        # 0,90 lalu 0,55 lalu 0,35 …  (pola mengecil, seperti data nyata)
        pola = [0.90 * (0.60 ** i) for i in range(p)]
        beda = pola
    beda = np.asarray(beda, dtype=float)
    if beda.ndim == 1:
        # satu angka per Y → kelompok ke-i dapat i × beda (kelompok 1 = dasar)
        beda = np.outer(np.arange(k), beda)
    if beda.shape != (k, p):
        raise ValueError(
            f'bentuk "beda" harus {k} kelompok × {p} Y, dapat {beda.shape}')

    # ── PAGAR JUJUR (ACC Bos 21Sep26, Opsi A) ────────────────────────
    #  Cek SELISIH ANTAR KELOMPOK (beda relatif), bukan nilai mentahnya —
    #  karena yang dibaca mesin memang selisihnya.
    if mode != 'natural':
        rel = beda - beda[0]
        pagar = periksa_beda(np.abs(rel[1:]).ravel() if rel.shape[0] > 1
                             else np.array([0.0]))
        if not pagar['boleh']:
            raise ValueError(pagar['pesan'])

    # ── Bangun skor konstruk (tanpa butir dulu) ──────────────────────
    #  responden dasar: rerata 0, sebaran 1, TANPA beda kelompok
    dasar = rng.normal(size=(n, p))
    milik = np.concatenate([[i] * n_list[i] for i in range(k)])
    nama_kelompok_penuh = np.array([nama_kelompok[i] for i in milik])

    # ── Tingkat koreksi menurut MODE output (ACC Bos 17Sep26: 2 mode) ─
    #  presisi          : dikoreksi PENUH supaya terbaca = dipasang
    #  presisi_variasi  : dikoreksi 92% → hasilnya sedikit bergeser
    #                     (yang Bos sebut "campuran")
    #  natural          : mesin PASANG bedanya apa adanya, tanpa koreksi
    #                     sepenuhnya (yang terbaca ≈ 76% dari setelan —
    #                     itulah "seperti data lapangan")
    #
    # 🔴 CACAT YANG DITUTUP SENDIRI 21Sep26 (ditemukan saat menyiapkan MANOVA):
    #    dulu mode 'natural' memakai faktor_susut = 0.0 → rumus
    #    `x = x + bd_rel * faktor_k * faktor_susut` jadi × 0 = **BEDA HILANG
    #    SEPENUHNYA**. Akibatnya MANOVA mode Natural TIDAK PERNAH menemukan
    #    perbedaan, padahal kelompoknya memang dibuat berbeda → hasilnya
    #    kelihatan sah tapi menyesatkan.
    #    Kenapa 0,80: diukur dari peta kalibrasi — TANPA koreksi, yang terbaca
    #    ≈ 0,755–0,76 dari setelan (lihat ukur_kalibrasi_kelompok.py).
    #    Ikuti pola mesin lama: 'natural' di regresi BERBEDA dari 'presisi'
    #    karena derau/p-nya, BUKAN karena koefisiennya dimatikan.
    faktor_susut = {'presisi': 1.0,
                    'presisi_variasi': 0.92,
                    'natural': 0.80}.get(mode, 1.0)

    # ── Skala sebaran & PEMETAAN KE LIKERT ───────────────────────────
    # 🔴 AKAR YANG DITUTUP 21Sep26 (2 putaran gagal, TERUKUR):
    #    Wulan 2× menstandardisasi ULANG (`_std`) setelah beda dipasang →
    #    beda yang sudah dipasang HILANG, lalu hasilnya bergantung undian
    #    (terukur: dipasang 0,90 terbaca 0,663 · lalu 1,30).
    #    Pelajaran yang SAMA sudah tercatat di `berurutan.py` (akar putaran
    #    ke-5 & ke-17): (a) JANGAN `_std()` pada target; (b) generator acak
    #    WAJIB terpisah tiap variabel.
    #    ⇒ Perbaikan di AKAR: skala dulu, TEGASKAN beda, JANGAN distandardisasi
    #      ulang, dan tiap Y punya generator acaknya SENDIRI.
    skala_min, skala_maks = 1.0, float(skala)
    keluar_skala = (skala_maks - skala_min) / 6.0   # ±3 simpangan di skala

    # ── Butir Likert 2–3 per Y (generator TERPISAH tiap Y) ───────────
    jml_butir = max(MIN_ITEM, min(MAKS_ITEM, int(butir)))
    kolom: dict[str, np.ndarray] = {}
    Y_murni = np.zeros((n, p))
    for j, nm in enumerate(nama_y):
        rng_j = np.random.default_rng((seed or 0) * 100003 + j)
        # skala dasar (sebaran 1) — TANPA standardisasi ulang setelah ini
        x = dasar[:, j] - dasar[:, j].mean()
        x = x / max(x.std(), 1e-9)
        # ⭐ TEGASKAN beda kelompok DI SINI, setelah skala, sebelum item.
        #    ⚠️ KALIBRASI (ACC Bos 21Sep26 Opsi A): beda DINAIKKAN dengan
        #    faktor terukur supaya SETELAH jadi item Likert hasilnya =
        #    yang diminta. Faktor diambil dari peta 90 kombinasi
        #    (`ukur_kalibrasi_kelompok.py`), BUKAN dikarang.
        #    Dihitung per-NILAI (bukan per-kelompok): tiap sel beda milik
        #    satu kelompok lawan kelompok dasar, jadi faktornya menyesuaikan
        #    besarnya beda itu sendiri.
        bd = beda[milik, j].copy()
        # nilai absolut → faktor mana yang dipakai
        faktor_k = np.where(np.abs(bd) > BEDA_LAZIM,
                            FAKTOR_KALIBRASI_BESAR, FAKTOR_KALIBRASI)
        # beda relatif terhadap kelompok pertama sudah berbentuk bd - bd[0]
        bd_rel = bd - bd[0]
        x = x + bd_rel * faktor_k * faktor_susut
        Y_murni[:, j] = x
        for b in range(1, jml_butir + 1):
            # turun ke item: geser ke tengah skala, JANGAN standardisasi
            v = x * keluar_skala + (skala_maks + skala_min) / 2
            v = v + rng_j.normal(scale=0.30 * keluar_skala, size=n)
            kolom[f'{nm}_{b}'] = np.clip(np.rint(v), skala_min, skala_maks) \
                .astype(int)

    # ── Skor konstruk = rata-rata butir (KEMBALI dari butir) ─────────
    skor = {nm: np.mean([kolom[f'{nm}_{b}'] for b in range(1, jml_butir + 1)],
                        axis=0) for nm in nama_y}
    Y = np.column_stack([skor[nm] for nm in nama_y])

    return {
        'n': n,
        'nama_kelompok': nama_kelompok,
        'n_per_kelompok': {nama_kelompok[i]: n_list[i] for i in range(k)},
        'nama_y': nama_y,
        'butir_per_y': jml_butir,
        'kolom': kolom,                       # bentuk per-butir (unduhan)
        'kelompok': nama_kelompok_penuh,      # ← kolom kelompok (TERPISAH)
        'Y': Y,                               # matriks Y (n × p)
        'skor': skor,
        'beda_dipasang': beda,                # what we SET
        'beda_terbaca': (np.array([[Y[milik == i, j].mean()
                                    for j in range(p)] for i in range(k)]).tolist()),
        'mode': mode,
        'skala': skala,
    }


def ukur_ulang(hasil: dict) -> dict:
    """Mesin MENGAKUI hasilnya sendiri: seberapa tepat beda yang dipasang?

    Ini padanan "β terbaca" di mesin regresi — prinsip yang sudah jalan
    sejak awal (mesin membangun + memberi kunci jawaban).
    """
    pasang = np.asarray(hasil['beda_dipasang'], dtype=float)
    baca = np.asarray(hasil['beda_terbaca'], dtype=float)
    # beda antar kelompok relatif terhadap kelompok pertama
    pasang_rel = pasang - pasang[0]
    baca_rel = baca - baca[0]
    galat = np.abs(pasang_rel - baca_rel)
    return {
        'galat_maks': float(galat.max()) if galat.size else 0.0,
        'galat_rinci': galat.tolist(),
        'tepat': bool(galat.max() < 0.05) if galat.size else True,
        'beda_dipasang': pasang_rel.tolist(),
        'beda_terbaca': baca_rel.tolist(),
    }
