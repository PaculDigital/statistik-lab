"""
Jembatan web → mesin hitung.

Aturan:
  - Hitungan LOKAL (numpy/scipy) — tanpa AI, gratis, instan.
  - Ukur ulang hasilnya sendiri, laporkan selisihnya JUJUR.
  - Nilai LULUS/GAGAL dari EXIT CODE / angka, bukan dari tebakan.
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent))
sys.path.insert(0, str(BASE))

from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur  # noqa: E402
from app.hitung.berurutan import bangun_dari_spek  # noqa: E402

# ── ambang signifikansi (dua sisi) ──────────────────────────────────────
AMBANG = [(0.001, 'pita-hijau', 'Sangat signifikan'),
          (0.05,  'pita-hijau', 'Signifikan'),
          (0.10,  'pita-amber', 'Marginal')]

# ── BATAS TOTAL β untuk S3 BERGANDA-BERANTAI (ACC Bos 18Sep26, Opsi C) ──
# 🚨 SATU SUMBER. Batas yang sama dipakai di tiga tempat dan WAJIB sinkron:
#    (1) pagar di buat_data()  — menolak setelan di luar batas,
#    (2) keterangan di halaman /buat-data — memberi tahu user SEBELUM kena,
#    (3) gerbang_s3.py — menguji batas ini.
# ⚠️ PELAJARAN EduAi 15Sep26 (batas MAXMB ditulis di JS & server): kalau
#    angka bisnis ditulis di dua tempat, tempat pertama memblokir → tempat
#    kedua TAK PERNAH tersentuh → gerbang mustahil kejadian. Karena itu
#    halaman mengambil angka ini DARI SERVER (main.py), bukan hardcode di JS.
#
# DASAR ANGKA (terukur 18Sep26, rantai 0,55, n=400, toleransi 0,03):
#   total β ≤ 1,20 → LULUS di semua jumlah X 2..8
#   total β ≥ 1,30 → PECAH (galat 0,03 → 0,10)
# Diambil 1,20 karena itu batas TERKETAT (kasus 3 X & 4 X); 8 X masih
# selamat sampai 1,50 tapi sengaja tidak dipakai supaya aman semua bentuk.
BATAS_BETA_RANTAI = 1.20


def kelas_p(p: float) -> tuple[str, str]:
    for batas, kelas, label in AMBANG:
        if p < batas:
            return kelas, label
    return 'pita-merah', 'Tidak signifikan'


def _skor_item(data: dict, nama: str) -> np.ndarray:
    """Skor konstruk = rata-rata item VALID (-1 = sel kosong, diabaikan).

    (Wulan, 19Okt26 — bug uji Boss) VERSI LAMA menjumlah MENTAH termasuk
    -1: satu sel kosong menurunkan skor seenaknya (FATAL untuk produk
    X×Z). Versi ini SAMA dengan skor_item() di kalibrasi_jalur.py —
    satu cara mengukur di hulu (kalibrasi) dan hilir (tampilan).
    Catatan: rata-rata vs jumlah tidak mengubah apa pun setelah
    standardisasi (cara SPSS/PLS membaca beta)."""
    it = np.asarray(data['item'][nama], dtype=float)
    it = np.where(it < 0, np.nan, it)
    with np.errstate(invalid='ignore'):
        return np.nanmean(it, axis=1)


def _regresi_terstandar(X, y):
    """Regresi terstandardisasi cara SPSS: baku dulu, lalu OLS."""
    Xz = (X - X.mean(0)) / X.std(0, ddof=1)
    yz = (y - y.mean()) / y.std(ddof=1)
    A = np.column_stack([Xz, np.ones(len(yz))])
    b = np.linalg.lstsq(A, yz, rcond=None)[0]
    resid = yz - A @ b
    dof = len(yz) - A.shape[1]
    s2 = float(np.sum(resid ** 2) / max(1, dof))
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    t = b / np.where(se > 0, se, np.nan)
    p = 2 * (1 - stats.t.cdf(np.abs(t), dof))
    r2 = 1 - float(np.sum(resid ** 2) / np.sum((yz - yz.mean()) ** 2))
    return b[:X.shape[1]], t[:X.shape[1]], p[:X.shape[1]], r2


def uji_f(X, y) -> dict:
    """UJI F + TABEL ANOVA — pengaruh SEMUA X secara BERSAMA-SAMA (simultan).

    ── KENAPA FUNGSI INI ADA (ACC Bos 21Sep26, Langkah 2) ──────────────────
    Statistik baku: SATU regresi berganda menghasilkan DUA uji.
      · uji t  → PARSIAL  (tiap X sendiri-sendiri)   ← SUDAH ADA
      · uji F  → SIMULTAN (semua X bersama-sama)     ← INI YANG DITAMBAH
    Sebelum ini mesin hanya punya R² — bisa bilang "45% keragaman dijelaskan"
    tapi TIDAK BISA bilang "semua X secara simultan berpengaruh" (p-value).
    Mahasiswa melihat tabel ANOVA di SPSS tapi tidak ada padanannya di sini.

    ── ANGKA YANG DIKEMBALIKAN (sama seperti tabel ANOVA SPSS) ─────────────
      sumber · ss (Sum of Squares) · df · ms (Mean Square) · F · p · r2
    Baris: 'Regresi' (SSR) · 'Residu' (SSE) · 'Total' (SST).

    ── BUKTI RUMUS (terukur 21Sep26, /tmp/ukur_uji_f.py) ───────────────────
    F = (R²/k) ÷ ((1−R²)/(n−k−1))  COCOK PERSIS dengan F dari SSR/MS_residu
    (beda 0,0000000000 pada 3 kasus: berganda 3X, sederhana 1X, berantai 3X).
    ⇒ Dua jalan menghitung (dari R² vs dari tabel ANOVA) menghasilkan angka
      yang SAMA — jadi tidak ada rumus yang dikarang.

    X = matriks skor prediktor (2D), y = skor Y (1D).
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    n, k = X.shape

    # dof habis → uji F tidak bisa dihitung (jujur, bukan angka palsu)
    if n <= k + 1:
        return {'bisa': False, 'sebab': f'n={n} terlalu kecil untuk k={k}',
                'n': int(n), 'k': int(k), 'tabel': []}

    Xz = (X - X.mean(0)) / X.std(0, ddof=1)
    yz = (y - y.mean()) / y.std(ddof=1)
    A = np.column_stack([Xz, np.ones(n)])
    b = np.linalg.lstsq(A, yz, rcond=None)[0]
    resid = yz - A @ b

    sst = float(np.sum((yz - yz.mean()) ** 2))
    sse = float(np.sum(resid ** 2))
    ssr = sst - sse
    df_reg, df_res, df_tot = k, n - k - 1, n - 1

    ms_reg = ssr / df_reg if df_reg else float('nan')
    ms_res = sse / df_res if df_res else float('nan')
    F = ms_reg / ms_res if ms_res and ms_res > 0 else float('nan')
    p = float(1 - stats.f.cdf(F, df_reg, df_res)) if np.isfinite(F) else float('nan')
    r2 = ssr / sst if sst > 0 else 0.0

    kelas, label = kelas_p(p)

    tabel = [
        {'sumber': 'Regresi', 'ss': ssr, 'df': df_reg, 'ms': ms_reg,
         'F': F, 'p': p},
        {'sumber': 'Residu', 'ss': sse, 'df': df_res, 'ms': ms_res,
         'F': None, 'p': None},
        {'sumber': 'Total', 'ss': sst, 'df': df_tot, 'ms': None,
         'F': None, 'p': None},
    ]

    return {'bisa': True, 'n': int(n), 'k': int(k),
            'ss_regresi': ssr, 'ss_residu': sse, 'ss_total': sst,
            'df_regresi': df_reg, 'df_residu': df_res, 'df_total': df_tot,
            'ms_regresi': ms_reg, 'ms_residu': ms_res,
            'F': float(F), 'p': p, 'r2': float(r2),
            'kelas': kelas, 'label': label,
            # kalimat siap-pakai untuk mahasiswa — HANGAT, tidak menakutkan
            'kalimat': (
                f'Secara bersama-sama, {k} variabel ini {"berpengaruh" if p < 0.05 else "tidak berpengaruh"} '
                f'terhadap Y (F={F:.3f}; p={p:.4f}; R²={r2:.3f}).'),
            'tabel': tabel}


def buat_data(n: int, x: int, beta: list[float], skala: int = 5,
              alpha: float = 0.85, mode: str = 'presisi',
              seed: int | None = None,
              nama_x: list[str] | None = None,
              cara: str = 'sederhana') -> dict:
    """Bangun data + ukur ulang HASILNYA SENDIRI (jujur).

    nama_x = nama variabel dari user (mis. ['Tingkat Edukasi', 'Motivasi']).
             Dipakai untuk label hasil & nama kolom berkas unduhan.
             Kalau kosong → kembali ke X1, X2, ...

    cara = CARA MENGUJI Y — ini TERPISAH dari jumlah X (ACC Bos 18Sep26):
      'sederhana' → tiap X diuji SENDIRI-SENDIRI ke Y. 3 X = 3 uji terpisah.
                    Contoh: X1→Y, lalu X2→Y, lalu X3→Y.
      'berganda'  → semua X diuji BERSAMA-SAMA ke Y. 3 X = 1 uji.
                    Contoh: X1+X2+X3→Y (satu tabel, tiga baris).
      'keduanya'  → hitung dua-duanya supaya murid bisa MEMBANDINGKAN.

    ⚠️ JEBAKAN YANG DITUTUP (18Sep26): dulu LABEL halaman mengunci
       "1 X = sederhana, banyak X = berganda". Itu SALAH — jumlah X tidak
       menentukan cara menguji. Datanya SAMA, yang beda cara menghitungnya.
    """
    n = max(30, min(2000, int(n)))
    x = max(1, min(8, int(x)))
    cara = cara if cara in ('sederhana', 'berganda', 'keduanya',
                            'berantai') else 'sederhana'
    if x == 1:
        # 1 prediktor: sederhana & berganda menghasilkan angka yang SAMA
        # (rumusnya identik), jadi jangan bingungkan user dengan dua pilihan.
        # 'berantai' pun tak mungkin: tidak ada X lain untuk dirantai.
        cara = 'sederhana'
    beta = [float(b) for b in beta[:x]]
    while len(beta) < x:
        beta.append(0.15)

    # ── PAGAR KELAYAKAN (18Sep26) ────────────────────────────────────────
    # 🚨 AKAR CACAT YANG DITUTUP: pagar ini SUDAH ADA (app/hitung/kelayakan.py,
    # ditulis 17Sep26) tapi TIDAK PERNAH DIPANGGIL dari sini. Akibatnya
    # setelan mustahil tetap diproses → kalibrasi BERAYUN, berhenti di
    # putaran terakhir → koefisien MELESET JAUH tanpa penjelasan.
    #
    # ⚠️ PAGAR INI TIDAK DIPAKAI untuk cara='berantai'. Sebab TERUKUR
    #   18Sep26: pagar menghitung R² dengan asumsi X saling BEBAS. Pada
    #   model berantai, X TERHUBUNG (X1→X2→X3) sehingga rumusnya tidak
    #   berlaku. Terukur: 8 X β=0,20 → pagar bilang R²=1,55 (menolak),
    #   padahal mesin NYATA berhasil (galat 0,0080). Pagar yang menolak
    #   hal yang nyatanya bisa = pagar SALAH, bukan mesin yang salah.
    #
    # ── BATAS RANTAI (ACC Bos 18Sep26, Opsi C) ──────────────────────────
    # Untuk cara='berantai', batasnya BUKAN jumlah X, melainkan TOTAL β.
    # PETA TERUKUR (rantai 0,55, n=400, toleransi 0,03):
    #   total β  0,6  0,8  1,0  1,2 | 1,3  1,4  1,5  1,6
    #   3 X      ok   ok   ok   X  | X
    #   4 X      ok   ok   ok   ok | X    X    X    X
    #   5 X      ok   ok   ok   ok | X    X    X    X
    #   6 X      ok   ok   ok   ok | X    X    X    X
    #   7 X      ok   ok   ok   ok | ok   ok   X    X
    #   8 X      ok   ok   ok   ok | ok   ok   ok   X
    # Batas AMAN: total β ≤ 1,20 (semua jumlah X 2..8 LULUS).
    # Di ≥1,30 pecah; di 8 X masih selamat sampai 1,5 — jadi batas 1,2
    # SENGAJA diambil dari kasus TERKETAT (3 X & 4 X) supaya aman semua.
    _BATAS_TOTAL_BETA = BATAS_BETA_RANTAI
    if cara == 'berantai' and sum(abs(b) for b in beta) > _BATAS_TOTAL_BETA:
        raise ValueError(
            f'Total pengaruh yang diminta {sum(abs(b) for b in beta):.2f} '
            f'melebihi batas aman {_BATAS_TOTAL_BETA:.2f} untuk model '
            f'berganda-berantai. Mohon kecilkan koefisien tiap X '
            f'(mis. {_BATAS_TOTAL_BETA / x:.2f} per variabel).')

    try:
        from app.hitung.kelayakan import periksa_setelan
        _beta_map = {f'X{i+1}': beta[i] for i in range(x)}
        _layak = periksa_setelan(_beta_map, korelasi_x=0.2, n_resp=n)
    except Exception:                              # noqa: BLE001
        _layak = {'layak': True, 'pesan': [], 'tingkat': 'aman'}
    if not _layak.get('layak', True) and cara != 'berantai':
        raise ValueError(
            'Setelan koefisien ini tidak bisa dicapai — ' +
            ' '.join(_layak.get('pesan', [])[:2]))

    # kolom internal HARUS tetap X1..X8 (mesin mengenali nama itu);
    # nama ramah-user disimpan terpisah untuk TAMPILAN dan BERKAS.
    kode_x = [f'X{i+1}' for i in range(x)]
    label_x = []
    for i in range(x):
        nm = (nama_x[i].strip() if nama_x and i < len(nama_x) and nama_x[i] else '')
        label_x.append(nm or kode_x[i])

    # ═══════════════════════════════════════════════════════════════════════
    # CATATAN: 'jalur' dibangun di dalam _bangun() karena bisa dibangun DUA
    # KALI (sekali normal + sekali dengan target terkoreksi).
    #
    # MASALAH TERUKUR (18Sep26): kalau cara='sederhana', mesin tetap
    # mengkalibrasi agar koefisien BERSAMA persis setelan. Akibatnya koefisien
    # TERPISAH meleset 0,083 (diminta 0,35 → terbaca 0,414), padahal itu yang
    # dilihat user pada cara sederhana.
    #
    # SEBAB: kalibrasi menyetel bobot pada jalur X→Y BERSAMA. Karena antar-X
    # saling berkorelasi, koefisien sederhana SELALU lebih besar dari koefisien
    # berganda (b_sederhana = b_berganda + bagian yang tumpang tindih).
    #
    # SOLUSI PALING SEDERHANA (tanpa mesin baru): KOREKSI TARGET.
    #   1. Bangun sekali dengan target β (cara lama).
    #   2. UKUR koefisien sederhana & berganda yang benar-benar keluar.
    #   3. Hitung RATIO sederhana/berganda yang terjadi.
    #   4. Bangun ULANG dengan target β÷ratio → hasil sederhana jadi pas.
    # Satu putaran ulang saja; tidak mengubah mesin kalibrasi yang terbukti.
    # ═══════════════════════════════════════════════════════════════════════

    # toleransi mengikuti mode
    if mode == 'natural':
        tol, putaran = 0.40, 1
    elif mode == 'presisi_variasi':
        tol, putaran = 0.02, 40
    else:
        tol, putaran = 0.02, 40

    seed_pakai = seed if seed is not None else 7

    # ── KEKUATAN RANTAI antar-X (S3, ACC Bos 18Sep26) ───────────────────
    # 0,55 dipilih karena: (a) cukup kuat supaya hubungan antar-X TERLIHAT
    # di data (korelasi nyata, bukan kebetulan), (b) tidak terlalu kuat
    # sehingga masih di bawah ambang multikolinearitas yang bikin VIF
    # bermasalah (VIF bawaan ~1,4 → jauh di bawah batas 10).
    # Angka ini BUKAN tarif bisnis, hanya derajat hubungan antar-X.
    ranta = [0.55] * max(0, x - 1)

    def _bangun(target_beta, seed_ini):
        """Bangun data sekali, kembalikan (keluaran, S, terpisah, bersama).

        ── S3 BERGANDA-BERANTAI (ACC Bos 18Sep26) ──────────────────────
        Kalau cara='berantai', jalur yang dikirim ke mesin BUKAN sekadar
        semua-X→Y. Ada DUA proses:
          (1) BERANTAI : X1→X2, X2→X3, … (X saling berhubungan)
          (2) BERGANDA : semua X bersama-sama → Y
        Terukur 18Sep26 (uji_mesin_s3_kalibrasi.py): galat maks 0,024 —
        di bawah toleransi 0,03, selesai 2–3 putaran. JADI MESIN SUDAH
        SANGGUP; tidak perlu mesin baru.
        """
        jap = [{'target': 'Y',
                'dari': {nm: b for nm, b in zip(kode_x, target_beta)}}]
        if cara == 'berantai':
            # rantai disisipkan DI DEPAN supaya X dibangun berurutan
            # (X2 lahir dari X1, X3 dari X2, …) baru Y dari semuanya.
            jap = [{'target': kode_x[i + 1], 'dari': {kode_x[i]: ranta[i]}}
                   for i in range(x - 1)] + jap
        kel = kalibrasi_per_jalur(
            jap, n_resp=n, toleransi=tol, maks_putaran=putaran,
            item_per=3, skala=int(skala), alpha_rentang=(alpha, alpha),
            seed=seed_ini)
        dat = kel['data']
        Sk = np.column_stack([_skor_item(dat, nm) for nm in kode_x] +
                             [_skor_item(dat, 'Y')])
        return kel, Sk

    def _ukur(Sk):
        """Hitung koefisien KEDUA cara dari satu matriks skor."""
        yy = Sk[:, -1]
        tp = np.array([_regresi_terstandar(Sk[:, [i]], yy)[0][0]
                       for i in range(x)])
        bb, tt, pp, rr = _regresi_terstandar(Sk[:, :x], yy)
        return tp, bb, tt, pp, rr

    keluaran, S = _bangun(beta, seed_pakai)
    tp, bb, tt, pp, rr = _ukur(S)

    # ── Koreksi supaya CARA yang dipilih user yang PERSIS (18Sep26) ─────
    # Kalau user memilih 'sederhana', yang harus pas adalah koefisien
    # TERPISAH — bukan bersama. Terukur: tanpa koreksi, diminta 0,35 keluar
    # 0,414 (meleset 0,083). Dengan koreksi target ÷ ratio → pas.
    #
    # ⚠️ PAGAR PENTING (temuan gerbang uji 18Sep26): koreksi target bisa
    # MELEWATI batas matematika saat prediktornya banyak (5–8 X). Terukur:
    # tanpa pagar, 5–8 X galat MALAH membesar jadi 0,083–0,120. Karena itu
    # koreksi hanya dipakai kalau:
    #   (a) jumlah X sedikit (<= 4), dan
    #   (b) hasilnya BENAR-BENAR lebih baik (galat_baru < galat_lama).
    if cara == 'sederhana' and 1 < x <= 4 and mode != 'natural':
        ratio = np.where(np.abs(bb) > 1e-6, tp / bb, 1.0)
        ratio = np.clip(ratio, 0.7, 1.4)      # pagar: jangan liar
        if np.any(np.abs(ratio - 1.0) > 0.02):   # hanya kalau memang meleset
            target2 = [float(np.clip(beta[i] / ratio[i], 0.01, 0.80))
                       for i in range(x)]
            kel2, S2 = _bangun(target2, seed_pakai + 1000)
            tp2, bb2, tt2, pp2, rr2 = _ukur(S2)
            galat_lama = max(abs(tp[i] - beta[i]) for i in range(x))
            galat_baru = max(abs(tp2[i] - beta[i]) for i in range(x))
            if galat_baru < galat_lama:      # pakai HANYA kalau lebih baik
                keluaran, S = kel2, S2
                tp, bb, tt, pp, rr = tp2, bb2, tt2, pp2, rr2

    data = keluaran['data']
    y = S[:, -1]

    # ── Cara 1: TIAP X DIUJI SENDIRI-SENDIRI (regresi sederhana) ────────
    # 3 X → 3 uji terpisah. Tiap uji: satu X saja sebagai prediktor.
    terpisah = []
    for i in range(x):
        bi, ti, pi, r2i = _regresi_terstandar(S[:, [i]], y)
        kelas, label = kelas_p(float(pi[0]))
        terpisah.append({'nama': label_x[i], 'kode': kode_x[i],
                         'diminta': beta[i],
                         'terbaca': float(bi[0]), 't': float(ti[0]),
                         'p': float(pi[0]), 'r2': float(r2i),
                         'kelas': kelas, 'label': label})

    # ── Cara 2: SEMUA X DIUJI BERSAMA-SAMA (regresi berganda) ───────────
    # 3 X → 1 uji dengan 3 prediktor sekaligus. Koefisien tiap X = pengaruh
    # SETELAH memperhitungkan X lain (inilah bedanya dengan cara 1).
    b, t, p, r2 = _regresi_terstandar(S[:, :x], y)
    bersama = []
    for i in range(x):
        kelas, label = kelas_p(float(p[i]))
        bersama.append({'nama': label_x[i], 'kode': kode_x[i],
                        'diminta': beta[i],
                        'terbaca': float(b[i]), 't': float(t[i]),
                        'p': float(p[i]), 'r2': float(r2),
                        'kelas': kelas, 'label': label})

    # ── Cara 3: RANTAI antar-X (S3 BERGANDA-BERANTAI, ACC Bos 18Sep26) ──
    # Setiap X diuji ke X berikutnya: X1→X2, X2→X3, … Ini BAGIAN KEDUA
    # dari S3. Diukur terstandardisasi (cara SPSS), sama seperti cara lain.
    rantai = []
    if cara == 'berantai':
        for i in range(x - 1):
            # S[:, [i+1]] bentuknya 2D -> _regresi_terstandar balikin array;
            # ambil skalar supaya float() tidak error (catatan 18Sep26).
            bi, ti, pi, r2i = _regresi_terstandar(S[:, [i]], S[:, [i + 1]])
            kelas, label = kelas_p(float(np.ravel(pi)[0]))
            rantai.append({'dari': label_x[i], 'ke': label_x[i + 1],
                           'kode_dari': kode_x[i], 'kode_ke': kode_x[i + 1],
                           'terbaca': float(np.ravel(bi)[0]),
                           't': float(np.ravel(ti)[0]),
                           'p': float(np.ravel(pi)[0]),
                           'r2': float(np.ravel(r2i)[0]),
                           'kelas': kelas, 'label': label})

    # ── Cara 4: UJI F + TABEL ANOVA (ACC Bos 21Sep26, Langkah 2) ────────
    # SIMULTAN — semua X bersama-sama. Bahan uji F sudah ada di mesin (R², n,
    # jumlah X); fungsi `uji_f()` merapikannya jadi tabel ANOVA seperti SPSS.
    # ⚠️ Murni MENAMBAH: tidak mengubah satu pun angka di terpisah/bersama.
    # 'F' = simultan (semua X) · 'F_terpisah' = per-X (padanan SPSS baris ANOVA
    # tiap regresi sederhana) supaya kartu ① (parsial) juga punya p-value F.
    f_semua = uji_f(S[:, :x], y)
    f_per_x = [uji_f(S[:, [i]], y) for i in range(x)]

    # mode presisi_variasi: koefisien tetap, p digeser sedikit oleh derau
    if mode == 'presisi_variasi' and seed is None:
        rng2 = np.random.default_rng(99)
        for blok in (terpisah, bersama):
            for baris_ in blok:
                baris_['p'] = float(np.clip(baris_['p'] * rng2.uniform(0.55, 1.0),
                                            1e-6, 1.0))
                baris_['kelas'], baris_['label'] = kelas_p(baris_['p'])

    # 'daftar' = hasil yang dipakai untuk pagar & pemeriksaan galat.
    # Pakai hasil cara yang DIPILIH user (keduanya → pakai bersama, yang
    # paling ketat karena antar-X saling memperhitungkan).
    daftar = terpisah if cara == 'sederhana' else bersama

    galat = max(abs(j['terbaca'] - j['diminta']) for j in daftar)

    # label cara menguji (bahasa awam — ACC Bos 21Sep26, keputusan N1)
    if cara == 'berganda':
        cara_label = (f'Regresi BERGANDA (parsial + simultan) — {x} X diuji '
                      f'bersama-sama ke Y. Ada uji t (parsial) DAN uji F '
                      f'(simultan) dari satu regresi yang sama.')
    elif cara == 'berantai':
        cara_label = (f'Regresi berganda-berantai (DIARSIPKAN 21Sep26) — '
                      f'{x} X diuji BERSAMA-SAMA ke Y, sekaligus saling '
                      f'berhubungan berantai (X1→X2→…→X{x}→Y)')
    elif cara == 'keduanya':
        cara_label = (f'Dua-duanya ditampilkan — {x} uji sendiri-sendiri '
                      f'(parsial) DAN {x} X bersama-sama (simultan)')
    else:
        cara_label = (f'Regresi PARSIAL (sederhana) — tiap X diuji '
                      f'SENDIRI-SENDIRI ke Y ({x} uji terpisah, '
                      f'X lain tidak ikut dihitung)' if x > 1
                      else 'Regresi sederhana — 1 prediktor (parsial)')

    # label mode
    mode_label = {'presisi': '🎯 Mode Presisi — koefisien persis setelan',
                  'natural': '🌿 Mode Natural — bervariasi seperti data lapangan',
                  'presisi_variasi': '⚖️ Presisi, p bervariasi'}[mode]

    kolom = []
    for nm in data['item']:
        for i in range(data['item'][nm].shape[1]):
            kolom.append(f'{nm}{i+1}')
    pratinjau = [[int(data['item'][nm][i, j])
                  for nm in data['item']
                  for j in range(data['item'][nm].shape[1])]
                 for i in range(min(6, n))]

    # Kode kolom versi SmartPLS (KP1, H1, Y1) — dikirim supaya halaman hasil
    # bisa MENAMPILKAN bedanya dengan versi SPSS sebelum user mengunduh.
    # Bos: "Unduh untuk SPSS (nama panjang) / Unduh untuk PLS (kode pendek)".
    from app.berkas_kerja import _header_pls
    kolom_pls = _header_pls({'kolom': kolom, 'nama_x': label_x, 'kode_x': kode_x})

    return {'n': n, 'jumlah_item': len(kolom), 'kolom': kolom,
            'kolom_pls': kolom_pls,
            'pratinjau': pratinjau, 'jalur': daftar, 'r2': r2,
            'galat_maks': galat, 'mode': mode, 'mode_label': mode_label,
            'nama_x': label_x, 'kode_x': kode_x,
            # hasil DUA CARA (ACC Bos 18Sep26) — halaman hasil menampilkan
            # keduanya supaya murid bisa MEMBANDINGKAN (opsi 1+3 digabung).
            'cara': cara, 'cara_label': cara_label,
            'terpisah': terpisah, 'bersama': bersama,
            # rantai antar-X (S3 berganda-berantai) — kosong kalau bukan S3
            'rantai': rantai,
            # ── UJI F + TABEL ANOVA (ACC Bos 21Sep26, Langkah 2) ──────────
            # 'f'       = SIMULTAN (semua X bersama-sama)  → kartu ②
            # 'f_terpisah' = per-X (parsial, padanan SPSS) → kartu ①
            # ⚠️ Murni MENAMBAH: angka terpisah/bersama TIDAK berubah.
            'f': f_semua,
            'f_terpisah': f_per_x,
            'ranta_setel': (ranta[0] if ranta else None),
            'r2_terpisah': (max((j['r2'] for j in terpisah), default=0.0)
                            if terpisah else 0.0),
            'data': data}


# ═══════════════════════════════════════════════════════════════════════
# MODEL JALUR — MEDIASI & MODERASI (Wulan, 19Okt26 — temuan audit 16Okt26)
#
# MASALAH: halaman /buat-data?model=mediasi|moderasi dulu hanya menampilkan
# UI REGRESI biasa — tidak ada variabel mediator (M), tidak ada jalur a/b,
# tidak ada efek tak langsung, tidak ada suku interaksi X×Z. Fitur mediasi/
# moderasi di sisi PEMBANGUNAN DATA tidak berfungsi sama sekali.
#
# PERBAIKAN (memakai yang SUDAH TERUJI, bukan mesin baru):
#   bangun : kalibrasi_per_jalur() + spek sk_mediasi()/sk_moderasi()
#            (kalibrasi iteratif — koefisien terukur = yang diminta,
#             toleransi mengikuti mode, sama seperti buat_data())
#   ukur   : app/hitung/kaitan.py — analis yang SAMA dengan /klinik
#            (mediasi bootstrap + simpulan; moderasi MRA + ΔR²).
#            SATU SUMBER kebenaran: angka di sini = angka di klinik.
# ═══════════════════════════════════════════════════════════════════════
"""Spesifikasi 9 varian jalur lanjutan untuk buat_data_jalur() (Wulan, 19Okt26).

Boss 19Okt26: "sambungkan semua". Sebelumnya ke-9 varian ini kartunya ADA
tapi mesinnya TIDAK DISAMBUNG (hanya preset regresi yang menyesatkan +
penanda jujur "segera disiapkan"). Sekarang semuanya membangun & mengukur
struktur jalurnya sungguhan via kalibrasi_per_jalur + analis.

Mesin yang dipakai (SEMUA sudah teruji):
  - DGP + kalibrasi : kalibrasi_per_jalur() — generik untuk sembarang
    jalur + interaksi (termasuk _ukur_interaksi_mra, 19Okt26).
  - Analis          : kaitan.mediasi_berjenjang (ada, teruji) untuk
    berjenjang; app/hitung/jalur_umum.py (analisis_jalur_umum) untuk
    8 varian lainnya.
"""

# ── kesimpulan per varian (Bahasa Indonesia, gaya mengajar) ──────────────
def _simpul_paralel(p, h, nm):
    t = h['tak_langsung']
    s1, s2 = t[0]['signifikan'], t[1]['signifikan']
    cp_sig = _p_sig(_cari_p(h, 'Y', 'X'))
    if s1 and s2:
        jenis = 'mediasi paralel penuh' if not cp_sig else 'mediasi paralel parsial'
    elif s1:
        jenis = f'mediasi hanya via {nm["m1"]}'
    elif s2:
        jenis = f'mediasi hanya via {nm["m2"]}'
    else:
        jenis = 'tidak ada mediasi'
    kalimat = (f'Pengaruh tak langsung via {nm["m1"]}: {t[0]["b"]:.3f} '
               f'{"(signifikan)" if s1 else "(tidak signifikan)"}; '
               f'via {nm["m2"]}: {t[1]["b"]:.3f} '
               f'{"(signifikan)" if s2 else "(tidak signifikan)"}. '
               f'Total tak langsung: {t[0]["b"]+t[1]["b"]:.3f}.')
    return jenis, kalimat


def _simpul_campuran(p, h, nm):
    t = h['tak_langsung']
    sig = [x['signifikan'] for x in t]
    n_sig = sum(sig)
    jenis = ('tidak ada mediasi' if n_sig == 0
             else f'mediasi campuran ({n_sig} dari 3 jalur signifikan)')
    kalimat = '; '.join(
        f"{x['nama']}: {x['b']:.3f} "
        f"({'signifikan' if x['signifikan'] else 'tidak signifikan'})"
        for x in t)
    return jenis, kalimat + '.'


def _simpul_dual(p, h, nm):
    ks = [k for e in h['persamaan'] if e['target'] == 'Y'
          for k in e['koef'] if k['interaksi']]
    s = [k['p'] < 0.05 for k in ks]
    z1 = s[0] if len(s) > 0 else False
    z2 = s[1] if len(s) > 1 else False
    if z1 and z2:
        jenis = 'kedua penguat memoderasi'
    elif z1:
        jenis = f'hanya {nm["z1"]} yang memoderasi'
    elif z2:
        jenis = f'hanya {nm["z2"]} yang memoderasi'
    else:
        jenis = 'tidak ada yang memoderasi'
    d = next(e['delta_r2'] for e in h['persamaan'] if e['target'] == 'Y')
    kalimat = (f'Interaksi X×{nm["z1"]}: b={ks[0]["b"]:.3f} (p={ks[0]["p"]:.4f}); '
               f'X×{nm["z2"]}: b={ks[1]["b"]:.3f} (p={ks[1]["p"]:.4f}). '
               f'Kenaikan R² setelah kedua interaksi masuk: {d:.4f}.')
    return jenis, kalimat


def _simpul_jalur_a(p, h, nm):
    k = next(k for e in h['persamaan'] if e['target'] == 'M'
             for k in e['koef'] if k['interaksi'])
    sig = k['p'] < 0.05
    arah = 'memperkuat' if k['b'] > 0 else 'melemahkan'
    jenis = (f'{nm["z"]} memoderasi jalur X→M ({arah})'
             if sig else f'{nm["z"]} tidak memoderasi jalur X→M')
    d = next(e['delta_r2'] for e in h['persamaan'] if e['target'] == 'M')
    kon = '; '.join(f"{c['nama']}: {c['b']:.3f}" for c in h['kondisional'])
    kalimat = (f'Interaksi X×{nm["z"]} → {nm["m"]}: b={k["b"]:.3f} '
               f'(p={k["p"]:.4f}, ΔR²={d:.4f}). '
               f'Pengaruh tak langsung X→{nm["m"]}→{nm["y"]} '
               f'pada tiga tingkat {nm["z"]} — {kon}.')
    return jenis, kalimat


def _simpul_jalur_b(p, h, nm):
    k = next(k for e in h['persamaan'] if e['target'] == 'Y'
             for k in e['koef'] if k['interaksi'])
    sig = k['p'] < 0.05
    arah = 'memperkuat' if k['b'] > 0 else 'melemahkan'
    jenis = (f'{nm["z"]} memoderasi jalur M→Y ({arah})'
             if sig else f'{nm["z"]} tidak memoderasi jalur M→Y')
    d = next(e['delta_r2'] for e in h['persamaan'] if e['target'] == 'Y')
    kon = '; '.join(f"{c['nama']}: {c['b']:.3f}" for c in h['kondisional'])
    kalimat = (f'Interaksi {nm["m"]}×{nm["z"]} → {nm["y"]}: b={k["b"]:.3f} '
               f'(p={k["p"]:.4f}, ΔR²={d:.4f}). '
               f'Pengaruh tak langsung pada tiga tingkat {nm["z"]} — {kon}.')
    return jenis, kalimat


def _simpul_keduanya(p, h, nm):
    ka = next(k for e in h['persamaan'] if e['target'] == 'M'
              for k in e['koef'] if k['interaksi'])
    kb = next(k for e in h['persamaan'] if e['target'] == 'Y'
              for k in e['koef'] if k['interaksi'])
    sa, sb = ka['p'] < 0.05, kb['p'] < 0.05
    if sa and sb:
        jenis = f'{nm["z"]} memoderasi kedua jalur'
    elif sa:
        jenis = f'{nm["z"]} hanya memoderasi jalur X→M'
    elif sb:
        jenis = f'{nm["z"]} hanya memoderasi jalur M→Y'
    else:
        jenis = f'{nm["z"]} tidak memoderasi jalur mana pun'
    kalimat = (f'Jalur X→{nm["m"]}: interaksi b={ka["b"]:.3f} (p={ka["p"]:.4f}); '
               f'jalur {nm["m"]}→{nm["y"]}: interaksi b={kb["b"]:.3f} '
               f'(p={kb["p"]:.4f}).')
    return jenis, kalimat


def _simpul_3jalur(p, h, nm):
    ka = next(k for e in h['persamaan'] if e['target'] == 'M'
              for k in e['koef'] if k['interaksi'])
    kb = next(k for e in h['persamaan'] if e['target'] == 'Y'
              for k in e['koef'] if k['interaksi'])
    sa, sb = ka['p'] < 0.05, kb['p'] < 0.05
    if sa and sb:
        jenis = f'{nm["z1"]} dan {nm["z2"]} masing-masing memoderasi'
    elif sa:
        jenis = f'hanya {nm["z1"]} yang memoderasi (jalur X→M)'
    elif sb:
        jenis = f'hanya {nm["z2"]} yang memoderasi (jalur M→Y)'
    else:
        jenis = 'tidak ada yang memoderasi'
    kalimat = (f'X×{nm["z1"]} → {nm["m"]}: b={ka["b"]:.3f} (p={ka["p"]:.4f}); '
               f'{nm["m"]}×{nm["z2"]} → {nm["y"]}: b={kb["b"]:.3f} '
               f'(p={kb["p"]:.4f}).')
    return jenis, kalimat


def _simpul_gabungan(p, h, nm):
    t = h['tak_langsung'][0]
    kb = next(k for e in h['persamaan'] if e['target'] == 'Y'
              for k in e['koef'] if k['interaksi'])
    sb = kb['p'] < 0.05
    arah = 'memperkuat' if kb['b'] > 0 else 'melemahkan'
    if t['signifikan'] and sb:
        jenis = f'rentetan berjenjang signifikan + {nm["z"]} memoderasi ({arah})'
    elif t['signifikan']:
        jenis = 'rentetan berjenjang signifikan, tanpa moderasi'
    elif sb:
        jenis = f'tidak ada rentetan, tapi {nm["z"]} memoderasi ({arah})'
    else:
        jenis = 'tidak ada rentetan maupun moderasi'
    kalimat = (f'Pengaruh tak langsung X→{nm["m1"]}→{nm["m2"]}→{nm["y"]}: '
               f'{t["b"]:.3f} [{t["lo"]:.3f}, {t["hi"]:.3f}] '
               f'{"(signifikan)" if t["signifikan"] else "(tidak signifikan)"}; '
               f'interaksi {nm["m2"]}×{nm["z"]}: b={kb["b"]:.3f} '
               f'(p={kb["p"]:.4f}).')
    return jenis, kalimat


def _p_sig(p):
    return p is not None and p < 0.05


def _cari_p(h, target, nama):
    for e in h['persamaan']:
        if e['target'] == target:
            for k in e['koef']:
                if k['nama'] == nama and not k['interaksi']:
                    return k['p']
    return None


# ── tabel spesifikasi 9 varian (dibaca buat_data_jalur) ────────────────────
# roles   : [(kunci_nama, konstruk), ...] — konstruk 'Y' selalu terakhir
# params  : [(kunci, default, label_untuk_slider), ...]
# nama_def: label ramah default per peran
# spek(p) : -> (jalur, interaksi) untuk kalibrasi_per_jalur
# persamaan/rantai/kondisional: untuk analisis_jalur_umum
# diminta : {(target, nama_koef): kunci_param} — kolom "β diminta"
VARIAN_JALUR = {
'mediasi-paralel': {
    'roles': [('x', 'X'), ('m1', 'M1'), ('m2', 'M2'), ('y', 'Y')],
    'params': [('a1', 0.50, 'Jalur a1 · X → M1'), ('a2', 0.45, 'Jalur a2 · X → M2'),
               ('b1', 0.35, 'Jalur b1 · M1 → Y'), ('b2', 0.30, 'Jalur b2 · M2 → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm1': 'Kepuasan', 'm2': 'Kepercayaan',
                 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'M1', 'dari': {'X': p['a1']}},
                        {'target': 'M2', 'dari': {'X': p['a2']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M1': p['b1'], 'M2': p['b2']}}],
                       []),
    'persamaan': [{'target': 'M1', 'pred': ['X']},
                  {'target': 'M2', 'pred': ['X']},
                  {'target': 'Y', 'pred': ['X', 'M1', 'M2']}],
    'rantai': [{'nama': 'X→M1→Y', 'jalur': ['X', 'M1', 'Y']},
               {'nama': 'X→M2→Y', 'jalur': ['X', 'M2', 'Y']}],
    'kondisional': [],
    'diminta': {('M1', 'X'): 'a1', ('M2', 'X'): 'a2', ('Y', 'X'): 'langsung',
                ('Y', 'M1'): 'b1', ('Y', 'M2'): 'b2'},
    'simpulan': _simpul_paralel,
},
'mediasi-berjenjang': {
    'roles': [('x', 'X'), ('m1', 'M1'), ('m2', 'M2'), ('y', 'Y')],
    'params': [('a1', 0.55, 'Jalur a1 · X → M1'), ('d', 0.45, 'Jalur d · M1 → M2'),
               ('b2', 0.40, 'Jalur b2 · M2 → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm1': 'Kepuasan', 'm2': 'Loyalitas',
                 'y': 'Beli Lagi'},
    'analisis': 'berjenjang',  # kaitan.mediasi_berjenjang (teruji)
},
'mediasi-campuran': {
    'roles': [('x', 'X'), ('m1', 'M1'), ('m2', 'M2'), ('y', 'Y')],
    'params': [('a1', 0.50, 'Jalur a1 · X → M1'), ('a2', 0.40, 'Jalur a2 · X → M2'),
               ('d', 0.35, 'Jalur d · M1 → M2'),
               ('b1', 0.30, 'Jalur b1 · M1 → Y'), ('b2', 0.30, 'Jalur b2 · M2 → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm1': 'Kepuasan', 'm2': 'Kepercayaan',
                 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'M1', 'dari': {'X': p['a1']}},
                        {'target': 'M2', 'dari': {'X': p['a2'], 'M1': p['d']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M1': p['b1'], 'M2': p['b2']}}],
                       []),
    'persamaan': [{'target': 'M1', 'pred': ['X']},
                  {'target': 'M2', 'pred': ['X', 'M1']},
                  {'target': 'Y', 'pred': ['X', 'M1', 'M2']}],
    'rantai': [{'nama': 'X→M1→Y', 'jalur': ['X', 'M1', 'Y']},
               {'nama': 'X→M2→Y', 'jalur': ['X', 'M2', 'Y']},
               {'nama': 'X→M1→M2→Y', 'jalur': ['X', 'M1', 'M2', 'Y']}],
    'kondisional': [],
    'diminta': {('M1', 'X'): 'a1', ('M2', 'X'): 'a2', ('M2', 'M1'): 'd',
                ('Y', 'X'): 'langsung', ('Y', 'M1'): 'b1', ('Y', 'M2'): 'b2'},
    'simpulan': _simpul_campuran,
},
'moderasi-dual': {
    'roles': [('x', 'X'), ('z1', 'Z1'), ('z2', 'Z2'), ('y', 'Y')],
    'params': [('bx', 0.35, 'Pengaruh X → Y'), ('bz1', 0.20, 'Pengaruh Z1 → Y'),
               ('bz2', 0.20, 'Pengaruh Z2 → Y'),
               ('i1', 0.22, 'Interaksi X×Z1 → Y'),
               ('i2', 0.20, 'Interaksi X×Z2 → Y')],
    'nama_def': {'x': 'Harga', 'z1': 'Kualitas', 'z2': 'Promosi',
                 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'Y', 'dari': {'X': p['bx'], 'Z1': p['bz1'],
                                                 'Z2': p['bz2']} }],
                       [{'target': 'Y', 'x': 'X', 'z': 'Z1', 'bobot': p['i1']},
                        {'target': 'Y', 'x': 'X', 'z': 'Z2', 'bobot': p['i2']}]),
    'persamaan': [{'target': 'Y', 'pred': ['X', 'Z1', 'Z2'],
                   'interaksi': [{'x': 'X', 'z': 'Z1'}, {'x': 'X', 'z': 'Z2'}]}],
    'rantai': [],
    'kondisional': [],
    'diminta': {('Y', 'X'): 'bx', ('Y', 'Z1'): 'bz1', ('Y', 'Z2'): 'bz2',
                ('Y', 'X×Z1'): 'i1', ('Y', 'X×Z2'): 'i2'},
    'simpulan': _simpul_dual,
},
'moderasi-jalur-a': {
    'roles': [('x', 'X'), ('m', 'M'), ('z', 'Z'), ('y', 'Y')],
    'params': [('a', 0.50, 'Jalur a · X → M'), ('az', 0.15, 'Z → M'),
               ('ia', 0.30, 'Interaksi X×Z → M (penguat jalur a)'),
               ('b', 0.40, 'Jalur b · M → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm': 'Kepuasan', 'z': 'Kualitas',
                 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'M', 'dari': {'X': p['a'], 'Z': p['az']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M': p['b']}}],
                       [{'target': 'M', 'x': 'X', 'z': 'Z',
                         'bobot': p['ia']}]),
    'persamaan': [{'target': 'M', 'pred': ['X', 'Z'],
                   'interaksi': [{'x': 'X', 'z': 'Z'}]},
                  {'target': 'Y', 'pred': ['X', 'M']}],
    'rantai': [{'nama': 'X→M→Y', 'jalur': ['X', 'M', 'Y']}],
    'kondisional': [
        {'nama': 'Z rendah (−1 SD)', 'jalur': ['X', 'M', 'Y'],
         'mod': {('X', 'M'): ('X', 'Z', -1.0)}},
        {'nama': 'Z sedang', 'jalur': ['X', 'M', 'Y'],
         'mod': {('X', 'M'): ('X', 'Z', 0.0)}},
        {'nama': 'Z tinggi (+1 SD)', 'jalur': ['X', 'M', 'Y'],
         'mod': {('X', 'M'): ('X', 'Z', 1.0)}}],
    'diminta': {('M', 'X'): 'a', ('M', 'Z'): 'az', ('M', 'X×Z'): 'ia',
                ('Y', 'X'): 'langsung', ('Y', 'M'): 'b'},
    'simpulan': _simpul_jalur_a,
},
'moderasi-jalur-b': {
    'roles': [('x', 'X'), ('m', 'M'), ('z', 'Z'), ('y', 'Y')],
    'params': [('a', 0.50, 'Jalur a · X → M'), ('b', 0.40, 'Jalur b · M → Y'),
               ('bz', 0.15, 'Z → Y'), ('ib', 0.25, 'Interaksi M×Z → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm': 'Kepuasan', 'z': 'Kualitas',
                 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'M', 'dari': {'X': p['a']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M': p['b'], 'Z': p['bz']}}],
                       [{'target': 'Y', 'x': 'M', 'z': 'Z',
                         'bobot': p['ib']}]),
    'persamaan': [{'target': 'M', 'pred': ['X']},
                  {'target': 'Y', 'pred': ['X', 'M', 'Z'],
                   'interaksi': [{'x': 'M', 'z': 'Z'}]}],
    'rantai': [{'nama': 'X→M→Y', 'jalur': ['X', 'M', 'Y']}],
    'kondisional': [
        {'nama': 'Z rendah (−1 SD)', 'jalur': ['X', 'M', 'Y'],
         'mod': {('M', 'Y'): ('M', 'Z', -1.0)}},
        {'nama': 'Z sedang', 'jalur': ['X', 'M', 'Y'],
         'mod': {('M', 'Y'): ('M', 'Z', 0.0)}},
        {'nama': 'Z tinggi (+1 SD)', 'jalur': ['X', 'M', 'Y'],
         'mod': {('M', 'Y'): ('M', 'Z', 1.0)}}],
    'diminta': {('M', 'X'): 'a', ('Y', 'X'): 'langsung', ('Y', 'M'): 'b',
                ('Y', 'Z'): 'bz', ('Y', 'M×Z'): 'ib'},
    'simpulan': _simpul_jalur_b,
},
'moderasi-keduanya': {
    'roles': [('x', 'X'), ('m', 'M'), ('z', 'Z'), ('y', 'Y')],
    'params': [('a', 0.50, 'Jalur a · X → M'), ('az', 0.15, 'Z → M'),
               ('ia', 0.22, 'Interaksi X×Z → M'),
               ('b', 0.40, 'Jalur b · M → Y'), ('bz', 0.15, 'Z → Y'),
               ('ib', 0.22, 'Interaksi M×Z → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm': 'Kepuasan', 'z': 'Kualitas',
                 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'M', 'dari': {'X': p['a'], 'Z': p['az']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M': p['b'], 'Z': p['bz']}}],
                       [{'target': 'M', 'x': 'X', 'z': 'Z', 'bobot': p['ia']},
                        {'target': 'Y', 'x': 'M', 'z': 'Z',
                         'bobot': p['ib']}]),
    'persamaan': [{'target': 'M', 'pred': ['X', 'Z'],
                   'interaksi': [{'x': 'X', 'z': 'Z'}]},
                  {'target': 'Y', 'pred': ['X', 'M', 'Z'],
                   'interaksi': [{'x': 'M', 'z': 'Z'}]}],
    'rantai': [{'nama': 'X→M→Y', 'jalur': ['X', 'M', 'Y']}],
    'kondisional': [],
    'diminta': {('M', 'X'): 'a', ('M', 'Z'): 'az', ('M', 'X×Z'): 'ia',
                ('Y', 'X'): 'langsung', ('Y', 'M'): 'b', ('Y', 'Z'): 'bz',
                ('Y', 'M×Z'): 'ib'},
    'simpulan': _simpul_keduanya,
},
'moderasi-3jalur': {
    'roles': [('x', 'X'), ('m', 'M'), ('z1', 'Z1'), ('z2', 'Z2'), ('y', 'Y')],
    'params': [('a', 0.50, 'Jalur a · X → M'), ('az1', 0.15, 'Z1 → M'),
               ('ia', 0.25, 'Interaksi X×Z1 → M'),
               ('b', 0.40, 'Jalur b · M → Y'), ('bz2', 0.15, 'Z2 → Y'),
               ('ib', 0.25, 'Interaksi M×Z2 → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm': 'Kepuasan', 'z1': 'Kualitas',
                 'z2': 'Promosi', 'y': 'Keputusan'},
    'spek': lambda p: ([{'target': 'M', 'dari': {'X': p['a'], 'Z1': p['az1']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M': p['b'], 'Z2': p['bz2']}}],
                       [{'target': 'M', 'x': 'X', 'z': 'Z1', 'bobot': p['ia']},
                        {'target': 'Y', 'x': 'M', 'z': 'Z2',
                         'bobot': p['ib']}]),
    'persamaan': [{'target': 'M', 'pred': ['X', 'Z1'],
                   'interaksi': [{'x': 'X', 'z': 'Z1'}]},
                  {'target': 'Y', 'pred': ['X', 'M', 'Z2'],
                   'interaksi': [{'x': 'M', 'z': 'Z2'}]}],
    'rantai': [{'nama': 'X→M→Y', 'jalur': ['X', 'M', 'Y']}],
    'kondisional': [],
    'diminta': {('M', 'X'): 'a', ('M', 'Z1'): 'az1', ('M', 'X×Z1'): 'ia',
                ('Y', 'X'): 'langsung', ('Y', 'M'): 'b', ('Y', 'Z2'): 'bz2',
                ('Y', 'M×Z2'): 'ib'},
    'simpulan': _simpul_3jalur,
},
'gabungan': {
    'roles': [('x', 'X'), ('m1', 'M1'), ('m2', 'M2'), ('z', 'Z'), ('y', 'Y')],
    'params': [('a1', 0.55, 'Jalur a1 · X → M1'), ('d', 0.45, 'Jalur d · M1 → M2'),
               ('b2', 0.40, 'Jalur b2 · M2 → Y'), ('bz', 0.15, 'Z → Y'),
               ('ib', 0.22, 'Interaksi M2×Z → Y'),
               ('langsung', 0.10, 'Jalur langsung (c′) · X → Y')],
    'nama_def': {'x': 'Harga', 'm1': 'Kepuasan', 'm2': 'Loyalitas',
                 'z': 'Kualitas', 'y': 'Beli Lagi'},
    'spek': lambda p: ([{'target': 'M1', 'dari': {'X': p['a1']}},
                        {'target': 'M2', 'dari': {'M1': p['d']}},
                        {'target': 'Y', 'dari': {'X': p['langsung'],
                                                 'M2': p['b2'], 'Z': p['bz']}}],
                       [{'target': 'Y', 'x': 'M2', 'z': 'Z',
                         'bobot': p['ib']}]),
    'persamaan': [{'target': 'M1', 'pred': ['X']},
                  {'target': 'M2', 'pred': ['M1']},
                  {'target': 'Y', 'pred': ['X', 'M2', 'Z'],
                   'interaksi': [{'x': 'M2', 'z': 'Z'}]}],
    'rantai': [{'nama': 'X→M1→M2→Y', 'jalur': ['X', 'M1', 'M2', 'Y']}],
    'kondisional': [],
    'diminta': {('M1', 'X'): 'a1', ('M2', 'M1'): 'd', ('Y', 'X'): 'langsung',
                ('Y', 'M2'): 'b2', ('Y', 'Z'): 'bz', ('Y', 'M2×Z'): 'ib'},
    'simpulan': _simpul_gabungan,
},
}


def _hasil_umum(model: str, df, spec: dict, p: dict, nama_lb: dict) -> dict:
    """Analisis untuk 8 varian via analisis_jalur_umum + simpulan."""
    from app.hitung.jalur_umum import analisis_jalur_umum
    h = analisis_jalur_umum(
        df, persamaan=spec['persamaan'],
        rantai=spec.get('rantai') or [],
        kondisional=spec.get('kondisional') or [])
    if not h.get('boleh'):
        raise ValueError(h.get('sebab', 'Analisis jalur gagal.'))
    # tempel nama ramah + β diminta ke tiap koefisien
    kode_nama = {k: nama_lb.get(kk, k) for kk, k in spec['roles']}
    peta_diminta = spec.get('diminta') or {}
    for eq in h['persamaan']:
        eq['nama_target'] = kode_nama.get(eq['target'], eq['target'])
        for kf in eq['koef']:
            kf['diminta'] = p.get(peta_diminta.get((eq['target'], kf['nama'])))
            if kf['interaksi']:
                x_, z_ = kf['nama'].split('×')
                kf['nama_panjang'] = (
                    f"{kode_nama.get(x_, x_)}×{kode_nama.get(z_, z_)}")
            else:
                kf['nama_panjang'] = kode_nama.get(kf['nama'], kf['nama'])
    for r in h['tak_langsung']:
        for kk, k in spec['roles']:
            r['nama'] = r['nama'].replace(k, nama_lb.get(kk, k))
    jenis, kalimat = spec['simpulan'](p, h, nama_lb)
    h['jenis'] = jenis
    h['kalimat'] = kalimat
    return h


def _hasil_berjenjang(df, p: dict, nama_lb: dict) -> dict:
    """Bungkus kaitan.mediasi_berjenjang + β diminta untuk tabel."""
    from app.hitung import kaitan as _kaitan
    from app.hitung.berurutan import sk_mediasi_berjenjang
    h = _kaitan.mediasi_berjenjang(df, 'X', 'M1', 'M2', 'Y')
    if not h.get('boleh'):
        raise ValueError(h.get('sebab', 'Analisis jalur gagal.'))
    h['diminta'] = dict(p)
    return h


def buat_data_jalur(model: str, n: int, params: dict, nama: dict,
                    skala: int = 5, alpha: float = 0.85,
                    mode: str = 'presisi', seed: int | None = None) -> dict:
    """Bangun data model jalur + ukur ulang HASILNYA SENDIRI (jujur).

    model  : 'mediasi' | 'moderasi'
    params : mediasi  -> {'a': X→M, 'b': M→Y, 'langsung': X→Y (c')}
             moderasi -> {'bx': X→Y, 'bz': Z→Y, 'interaksi': X×Z→Y}
    nama   : label ramah user, mis. {'x': 'Harga', 'm': 'Kepuasan',
             'y': 'Keputusan'}
    """
    import pandas as pd
    from app.hitung import kaitan as _kaitan
    from app.hitung.berurutan import sk_mediasi, sk_moderasi, sk_mediasi_berjenjang

    model = str(model or '').strip()
    _MODEL_JALUR = ('mediasi', 'moderasi') + tuple(VARIAN_JALUR.keys())
    if model not in _MODEL_JALUR:
        raise ValueError(f"Model jalur '{model}' belum didukung.")

    n = max(30, min(2000, int(n or 150)))
    skala = int(skala or 5)
    alpha = min(0.95, max(0.60, float(alpha or 0.85)))
    seed_pakai = seed if seed is not None else 7
    params = dict(params or {})
    nama = dict(nama or {})

    def _batas(v, baku=0.0):
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = baku
        if v != v:  # NaN
            v = baku
        return max(-0.90, min(0.90, v))

    def _label(kunci, baku):
        t = str(nama.get(kunci, '') or '').strip()
        return t[:40] if t else baku

    if model == 'mediasi':
        a = _batas(params.get('a'), 0.50)
        b = _batas(params.get('b'), 0.40)
        c2 = _batas(params.get('langsung'), 0.10)
        jalur = sk_mediasi({'X': a}, b, langsung={'X': c2}, m='M')
        interaksi = None
        konstruk = ['X', 'M', 'Y']
        kode_x = ['X', 'M']
        label_x = [_label('x', 'X'), _label('m', 'M')]
        diminta = {'a': a, 'b': b, 'langsung': c2}
        analisis_kind = 'mediasi'
        nama_lb = {'x': _label('x', 'X'), 'm': _label('m', 'M'),
                   'y': _label('y', 'Y')}
    elif model == 'moderasi':
        bx = _batas(params.get('bx'), 0.35)
        bz = _batas(params.get('bz'), 0.20)
        bi = _batas(params.get('interaksi'), 0.25)
        spek = sk_moderasi('X', 'Z', bx, bz, bi)
        jalur, interaksi = spek['jalur'], spek['interaksi']
        konstruk = ['X', 'Z', 'Y']
        kode_x = ['X', 'Z']
        label_x = [_label('x', 'X'), _label('z', 'Z')]
        diminta = {'bx': bx, 'bz': bz, 'interaksi': bi}
        analisis_kind = 'moderasi'
        nama_lb = {'x': _label('x', 'X'), 'z': _label('z', 'Z'),
                   'y': _label('y', 'Y')}
    elif model == 'mediasi-berjenjang':
        spec = VARIAN_JALUR[model]
        p = {k: _batas(params.get(k), dflt) for k, dflt, _ in spec['params']}
        jalur = sk_mediasi_berjenjang('X', p['a1'], p['d'], p['b2'],
                                      langsung=p['langsung'], m1='M1', m2='M2')
        interaksi = None
        konstruk = ['X', 'M1', 'M2', 'Y']
        kode_x = ['X', 'M1', 'M2']
        label_x = [_label(kk, k) for kk, k in spec['roles'] if k != 'Y']
        diminta = p
        analisis_kind = 'berjenjang'
        nama_lb = {kk: _label(kk, dv)
                   for kk, dv in spec['nama_def'].items()}
    else:  # 8 varian generik
        spec = VARIAN_JALUR[model]
        p = {k: _batas(params.get(k), dflt) for k, dflt, _ in spec['params']}
        jalur, interaksi = spec['spek'](p)
        # nama konstruk suku interaksi — CARA SAMA seperti spek_pembangun.py
        # (kalibrasi MENYALIN dict ini, jadi setdefault harus di sini supaya
        #  kolom interaksi bisa dibuang dari unduhan di bawah).
        for _it in (interaksi or []):
            _it.setdefault('sumber', f"{_it['x']}x{_it['z']}")
        konstruk = [k for _kk, k in spec['roles']]
        kode_x = [k for _kk, k in spec['roles'] if k != 'Y']
        label_x = [_label(kk, k) for kk, k in spec['roles'] if k != 'Y']
        diminta = p
        analisis_kind = 'umum'
        nama_lb = {kk: _label(kk, dv)
                   for kk, dv in spec['nama_def'].items()}

    # toleransi mengikuti mode (sama seperti buat_data())
    if mode == 'natural':
        tol, putaran = 0.40, 1
    else:  # 'presisi' & 'presisi_variasi' -> kalibrasi penuh
        tol, putaran = 0.02, 40

    kel = kalibrasi_per_jalur(
        jalur, n_resp=n, item_per=3, skala=skala,
        alpha_rentang=(alpha, alpha), toleransi=tol,
        maks_putaran=putaran, seed=seed_pakai,
        interaksi=interaksi)
    data = kel['data']

    # skor konstruk via _skor_item() = rata-rata item VALID (-1 = sel
    # kosong diabaikan), SAMA dengan skor_item() yang dipakai kalibrasi.
    # Prinsip: yang diukur saat kalibrasi = yang ditampilkan ke user.
    # Baris yang semua itemnya kosong menjadi NaN lalu dibuang kaitan.
    df = pd.DataFrame({k: _skor_item(data, k) for k in konstruk})

    # ── UKUR TERSTANDARDISASI (cara SPSS: koefisien beta) ──────────
    # Alasan (Wulan, 19Okt26): kaitan._reg menghitung OLS MENTAH (b dalam
    # satuan skor), sedangkan user menyetel koefisien TERSTANDARDISASI.
    # Tanpa pembakuan, "β diminta vs β terbaca" meleset jauh — terukur:
    # interaksi moderasi diminta 0,30 → terbaca 0,77 (Y tidak dibakukan
    # di kaitan.moderasi). Setelah dibakukan: b = β, sejajar dengan halaman
    # regresi (yang juga menampilkan β terstandardisasi). T/p/R²/CI/
    # simpulan TIDAK berubah (invariant terhadap standardisasi).
    # Catatan: /klinik menampilkan B mentah untuk data unggahan — sama
    # seperti kartu regresi klinik yang menampilkan kolom 'B', bukan 'β'.
    def _z(s):
        sd = float(s.std(ddof=1))
        return (s - s.mean()) / sd if sd > 0 else s * 0.0
    df = df.apply(_z)

    if analisis_kind == 'mediasi':
        hasil = _kaitan.mediasi(df, 'X', 'M', 'Y')
    elif analisis_kind == 'moderasi':
        hasil = _kaitan.moderasi(df, 'X', 'Z', 'Y')
    elif analisis_kind == 'berjenjang':
        hasil = _hasil_berjenjang(df, diminta, nama_lb)
    else:
        hasil = _hasil_umum(model, df, VARIAN_JALUR[model], diminta, nama_lb)
    if not hasil.get('boleh'):
        raise ValueError(hasil.get('sebab', 'Analisis jalur gagal.'))

    # ── siapkan struktur unduhan (format SAMA seperti buat_data()) ──
    # Kolom SUKU INTERAKSI (mis. 'XxZ') TIDAK ikut diunduh — mahasiswa
    # menghitungnya sendiri di SPSS/SmartPLS (alur belajar yang benar;
    # kalau sudah jadi kolom, mahasiswa bingung "ini variabel apa").
    for _it in (interaksi or []):
        _nm_suku = _it.get('sumber')
        if _nm_suku and _nm_suku in data['item']:
            del data['item'][_nm_suku]
    kolom = []
    for nm in data['item']:
        for i in range(data['item'][nm].shape[1]):
            kolom.append(f'{nm}{i+1}')
    pratinjau = [[int(data['item'][nm][i, j])
                  for nm in data['item']
                  for j in range(data['item'][nm].shape[1])]
                 for i in range(min(6, n))]
    kolom_pls = _header_pls({'kolom': kolom, 'nama_x': label_x,
                             'kode_x': kode_x})

    galat_maks = float(kel.get('galat_maks', 0.0) or 0.0)
    return {'model': model, 'n': n, 'diminta': diminta,
            'hasil': hasil,
            'nama': {k: _label(k, k.upper()) for k in nama_lb},
            'galat_maks': galat_maks,
            'tercapai': bool(kel.get('tercapai', False)),
            'mode': mode,
            'kolom': kolom, 'kolom_pls': kolom_pls,
            'jumlah_item': len(kolom), 'pratinjau': pratinjau,
            'nama_x': label_x, 'kode_x': kode_x,
            'data': data}


# ── simpan hasil terakhir untuk unduhan ─────────────────────────────────
# ⚠️ Disimpan ke BERKAS, bukan hanya memori: kalau server restart atau ada
# beberapa pekerja (uvicorn worker), memori proses bisa berbeda → unduhan 404.
_TERAKHIR_JALUR = None


def _berkas_terakhir():
    from pathlib import Path
    d = Path('/app/data')
    if not d.exists():
        d = Path(__file__).resolve().parent.parent / 'data'
    d.mkdir(parents=True, exist_ok=True)
    return d / 'terakhir.pkl'


def simpan_terakhir(d: dict) -> None:
    import pickle
    with open(_berkas_terakhir(), 'wb') as f:
        pickle.dump(d, f, protocol=5)


def ambil_terakhir() -> dict:
    global _TERAKHIR_JALUR
    if _TERAKHIR_JALUR is not None:
        return _TERAKHIR_JALUR
    import pickle
    p = _berkas_terakhir()
    if not p.exists():
        return {}
    try:
        with open(p, 'rb') as f:
            _TERAKHIR_JALUR = pickle.load(f)
        return _TERAKHIR_JALUR
    except Exception:                          # noqa: BLE001
        return {}


def _baris(d: dict):
    """Hasilkan baris data sebagai list nilai (item demi item)."""
    data = d['data']
    for i in range(d['n']):
        yield [int(data['item'][nm][i, j])
               for nm in data['item']
               for j in range(data['item'][nm].shape[1])]


def _header_ramah(d: dict) -> list[str]:
    """Nama kolom berkas unduhan — memakai nama variabel dari user.

    Contoh: X11, X12, X13 → 'X1_Tingkat_Edukasi_1', ...
    Tanda spasi diganti garis bawah supaya AMAN dibaca SPSS/SmartPLS
    (SPSS menolak nama kolom berspasi).
    """
    nama_x = d.get('nama_x') or []
    kode_x = d.get('kode_x') or []
    peta = {}
    for k, n in zip(kode_x, nama_x):
        bersih = ''.join(c if (c.isalnum() or c in '-_') else '_' for c in n)
        bersih = bersih.strip('_') or k
        peta[k] = bersih[:40]

    hasil = []
    for kol in d['kolom']:
        cocok = None
        for k in kode_x:
            if kol.startswith(k) and kol[len(k):].isdigit():
                cocok = k
                break
        if cocok:
            nomor = kol[len(cocok):]
            hasil.append(f"{peta.get(cocok, cocok)}_{nomor}")
        else:
            hasil.append(kol)
    return hasil


def _kode_pendek(kol: str) -> str:
    """Ubah nama kolom panjang → KODE PENDEK konvensi SmartPLS.

    KENAPA ADA (permintaan Bos, Tahap 1 · 19Sep26):
    SmartPLS memakai KODE PENDEK (KP1, H1, Y1) sebagai nama indikator,
    sedangkan SPSS memakai NAMA PANJANG yang mudah dibaca.
    Bos: "Format unduhan = PILIHAN: Unduh untuk SPSS (nama panjang) /
    Unduh untuk PLS (kode pendek)."

    Cara kerja: ambil HURUF AWAL tiap kata + nomor item.
        'Harga_1'                       → 'H1'
        'Kualitas_Produk_2'             → 'KP2'
        'X1_Tingkat_Edukasi_1'          → 'XTE1'
        'Y1'                            → 'Y1'      (sudah pendek, biarkan)
        'skor_M'                        → 'M'       (kata 'skor' dibuang)

    ⚠️ ATURAN: kalau hasilnya kosong/bentrok, JANGAN mengarang —
    biarkan nama aslinya dipakai. Kode pendek yang salah lebih berbahaya
    daripada nama panjang yang benar.
    """
    bersih = kol.strip()
    if not bersih:
        return kol

    # Pisahkan jadi kata + nomor di ujung.
    # 'Kualitas_Produk_2' → kata ['Kualitas','Produk'], nomor '2'
    cocok = re.match(r'^(.+?)[_\s-]*(\d+)?$', bersih)
    if not cocok:
        return kol
    inti, nomor = cocok.group(1), cocok.group(2) or ''

    kata = [w for w in re.split(r'[_\s-]+', inti) if w]
    # Buang kata umum yang bukan nama konstruk.
    BUANG = {'skor', 'total', 'mean', 'rerata', 'item', 'score'}
    kata = [w for w in kata if w.lower() not in BUANG] or kata
    if not kata:
        return kol

    # ⚠️ CACAT YANG DIPERBAIKI 19Sep26 (terukur dari uji fungsi langsung):
    # aturan pertama "satu kata → pakai apa adanya" SALAH untuk nama konstruk.
    #   'Harga_1'   → keluar 'Harga1'  padahal SmartPLS pakai 'H1'
    #   'Promosi_3' → keluar 'Pro3'    padahal harus 'P3'
    # AKAR: nama konstruk SATU KATA tetap perlu disingkat jadi HURUF AWAL,
    # sama seperti konstruk banyak kata. Yang TIDAK boleh disingkat hanya
    # kode yang MEMANG sudah pendek (Y1, M, XTE1).
    if len(kata) == 1:
        dasar = kata[0]
        # Kalau sudah pendek (≤3 huruf) ATAU sudah memuat angka (kode buatan
        # user seperti X1/Y1), biarkan apa adanya — jangan diubah.
        if len(dasar) <= 3 or any(c.isdigit() for c in dasar):
            pass  # pakai apa adanya
        else:
            # Huruf awal saja (konvensi SmartPLS): Harga → H, Promosi → P
            dasar = dasar[0].upper()
    else:
        # Banyak kata: ambil HURUF AWAL tiap kata → 'Kualitas Produk' = 'KP'
        dasar = ''.join(w[0] for w in kata if w).upper()

    return f"{dasar}{nomor}"


def _header_pls(d: dict) -> list[str]:
    """Header untuk SmartPLS — KODE PENDEK, dan WAJIB unik.

    ⚠️ KENAPA dicek unik: dua kolom berbeda bisa menghasilkan kode sama
    (mis. 'Kualitas_Produk_1' dan 'Kualitas_Pelayanan_1' → 'KP1').
    SmartPLS MENOLAK berkas dengan nama kolom kembar. Kalau bentrok,
    Wulan beri akhiran angka (KP1, KP1b, KP1c) supaya berkas tetap sah
    — dan itu lebih baik daripada gagal impor.
    """
    hasil = []
    terpakai = {}
    for kol in _header_ramah(d):
        kode = _kode_pendek(kol)
        if kode in terpakai:
            terpakai[kode] += 1
            # KP1 → KP1b, KP1c, ... (hindari '_2' yang bisa disangka item)
            akhiran = chr(ord('a') + terpakai[kode] - 1)
            kode = f"{kode}{akhiran}"
        else:
            terpakai[kode] = 1
        hasil.append(kode)
    return hasil


def ke_csv(d: dict, untuk: str = 'spss', pemisah: str = ',') -> bytes:
    """CSV siap impor.

    untuk   : 'spss' → nama PANJANG ('Kualitas_Produk_1')
              'pls'  → kode PENDEK  ('KP1') — konvensi SmartPLS
    pemisah : ',' atau ';' — Windows berbahasa Indonesia sering butuh ';'
              (Excel Indonesia memakai koma sebagai pemisah DESIMAL,
               jadi kalau kolom dipisah koma juga, berkas terbaca 1 kolom).
    """
    judul = _header_pls(d) if untuk == 'pls' else _header_ramah(d)
    buf = io.StringIO()
    buf.write(pemisah.join(judul) + '\n')
    for baris in _baris(d):
        buf.write(pemisah.join(str(v) for v in baris) + '\n')
    return buf.getvalue().encode('utf-8')


def ke_xlsx(d: dict, untuk: str = 'spss') -> bytes:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Data Penelitian'
    ws.append(_header_pls(d) if untuk == 'pls' else _header_ramah(d))
    for baris in _baris(d):
        ws.append(baris)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
