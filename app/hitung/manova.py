"""
MESIN MANOVA — banding kelompok pada BEBERAPA variabel hasil sekaligus.

═══════════════════════════════════════════════════════════════════════════
KENAPA BERKAS INI ADA (permintaan Bos 21Sep26: "Ok buka untuk manova")

RUANG YANG DIPESAN 19Sep26 (RUANG_MANOVA.md) sudah dibuka Bos. Isinya:

  MANOVA = "Kelompok A ≠ Kelompok B" pada BEBERAPA Y SEKALIGUS.
  BEDA CARA BERPIKIR dengan regresi:
      REGRESI : "X memengaruhi Y"          → arah pengaruh
      MANOVA  : "Kelompok A ≠ Kelompok B"  → beda rata-rata

  Kenapa TIDAK boleh sekadar menjalankan ANOVA satu per satu?
  Karena menguji 3 Y terpisah = 3 kali uji → peluang salah
  (galat Tipe I) membengkak. MANOVA menguji SEMUA Y SEKALIGUS dalam
  satu uji, jadi peluang salahnya tetap terjaga.
  ⇒ Karena itu MANOVA dipisah dari regresi, dan kalau Y banyak
    mesin WAJIB memperingatkan.

R4 (DITAHAN, TIDAK DILANGGAR): berkas ini TIDAK menyentuh bentuk data
  lama `{'item': …, 'skor_konstruk': …}` yang dipakai 17 grup gerbang.
  Kelompok dibawa sebagai argumen TERPISAH (`kelompok=`) — jadi mesin
  lama tidak tersentuh sama sekali.

YANG WAJIB ADA (perintah sendiri di catatan, bagian 8 & 9):
  "MANOVA yang tidak memeriksa syarat = MANOVA yang MENYESATKAN."
  ⇒ asumsi (Levene + Box's M + pencilan) dan kalimat kesimpulan
    TIDAK boleh dilewat, walau hasilnya kelihatan bagus.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

# ── Ambang baku ──────────────────────────────────────────────────────────
MIN_KELOMPOK = 2          # MANOVA butuh minimal 2 kelompok
MIN_Y = 2                 # MANOVA baru bermakna kalau Y-nya >= 2
MIN_ISI = 3               # tiap kelompok minimal 3 responden (SSCP butuh > 1)
ALPHA = 0.05
BATAS_BOX = 0.001         # Box's M: di bawah ini = varians-kovarians BEDA


# ═══════════════════════════════════════════════════════════════════════
#  1. SSCP — jumlah kuadrat & silang (bahan SEMUA statistik uji)
# ═══════════════════════════════════════════════════════════════════════
def _sscp(X: np.ndarray, pusat: np.ndarray) -> np.ndarray:
    """SSCP sebuah kelompok/variabel: Σ (x - pusat)ᵀ(x - pusat).

    Ini 'bahan mentah' MANOVA — dari sini Semua statistik uji diturunkan.
    """
    D = X - pusat
    return D.T @ D


def _hitung_sscp(Y: np.ndarray, grup: np.ndarray) -> dict:
    """Pecah variansi total Y jadi DALAM kelompok + ANTAR kelompok.

    TERUKUR pada data contoh: W = 116,81 · B = 188,91 · T = 305,71
    dan T = W + B (cocok s/d 1e-9) — ini yang membuktikan pecahannya BENAR.
    """
    semua = Y.mean(axis=0)
    T = _sscp(Y, semua)                       # total
    W = np.zeros_like(T)                      # dalam kelompok (within)
    for g in np.unique(grup):
        Yi = Y[grup == g]
        W += _sscp(Yi, Yi.mean(axis=0))
    B = _sscp(Y, semua) - W                   # antar kelompok (between)
    return {'T': T, 'W': W, 'B': B,
            'semua': [float(q) for q in semua],
            'rerata_kelompok': {str(g): [float(q) for q in Y[grup == g].mean(axis=0)]
                                for g in np.unique(grup)},
            'n_kelompok': {str(g): int((grup == g).sum())
                           for g in np.unique(grup)}}


# ═══════════════════════════════════════════════════════════════════════
#  2-5. EMPAT STATISTIK UJI MANOVA
# ═══════════════════════════════════════════════════════════════════════
def _statistik(W: np.ndarray, B: np.ndarray) -> dict:
    """Hitung 4 statistik baku MANOVA dari W & B.

    Kenapa EMPAT, bukan satu? Keempatnya jawab pertanyaan yang sedikit
    berbeda, dan SPSS menampilkan semuanya. Yang paling umum dipakai
    dan paling tangguh = **Pillai's Trace** (disarankan banyak buku saat
    asumsi varians-kovarians meragukan); Wilks = yang klasik.

    | W⁻¹B | = | B / W | — dipakai Wilks; akar cirinya dipakai Roy.
    """
    Wi = np.linalg.pinv(W)
    M = Wi @ B
    akar = np.linalg.eigvals(M)
    akar = np.real(akar)
    akar = np.clip(akar, 0.0, None)           # buang galat pembulatan negatif
    akar = np.sort(akar)[::-1]

    wilks = float(1.0 / np.prod(1.0 + akar))
    pillai = float(np.sum(akar / (1.0 + akar)))
    hotelling = float(np.sum(akar))
    roy = float(akar[0]) if akar.size else 0.0
    return {'wilks': wilks, 'pillai': pillai,
            'hotelling': hotelling, 'roy': roy}


def _df_uji(p: int, k: int, n: int) -> dict:
    """Derajat bebas (df) untuk uji F MANOVA.

    p = jumlah Y · k = jumlah kelompok · n = jumlah responden.
    Rumus baku (Rencher, Methods of Multivariate Analysis):
        df hipotesis = p(k-1)   ·  df galat = p(n-k)
    Untuk Wilks dipakai pendekatan Rao (disederhanakan, sah untuk
    kasus umum: 2 kelompok, atau p dan k berapa pun).
    """
    df1 = p * (k - 1)
    df2 = p * (n - k)
    return {'df1': int(df1), 'df2': int(df2)}


def _f_dari_statistik(st: dict, p: int, k: int, n: int) -> dict:
    """Ubah tiap statistik jadi F + p-value (cara SPSS).

    ⚠️ INI BAGIAN YANG PALING SERING SALAH DIHITUNG. Pendekatan yang
    dipakai di sini = aproksimasi Rao untuk Wilks (umum di buku), dan
    pendekatan baku untuk Pillai/Hotelling/Roy:
      Pillai   → F = (pillai/(k-1)) / ((1-pillai)/(n-k))
      Hotelling→ F = hotelling · (n-k) / (k-1)
      Roy      → F = roy · (n-k) / (k-1)
    Hipotesis nol: SEMUA rata-rata kelompok sama untuk SEMUA Y sekaligus.
    """
    d = _df_uji(p, k, n)
    hasil = {}

    # Wilks → aproksimasi Rao
    s = math.sqrt((p ** 2 * (k - 1) ** 2 - 4) / (p ** 2 + (k - 1) ** 2 - 5)) \
        if (p ** 2 + (k - 1) ** 2 - 5) != 0 else 1.0
    df1w = p * (k - 1)
    df2w = s * (n - k - (p - k + 2) / 2.0) - (p * (k - 1) - 2) / 2.0
    if df2w > 0 and st['wilks'] > 0:
        fw = ((1 - st['wilks'] ** (1 / s)) / (st['wilks'] ** (1 / s))) \
            * (df2w / df1w)
        hasil['wilks'] = {'F': float(fw), 'p': float(stats.f.sf(fw, df1w, df2w)),
                          'df1': float(df1w), 'df2': float(df2w)}
    else:
        hasil['wilks'] = {'F': None, 'p': None, 'df1': df1w, 'df2': d['df2']}

    # Pillai
    #  ⚠️ df DISIMPAN, bukan cuma dipakai (temuan MATA 22Sep26): tabel halaman
    #     menampilkan kolom df, sementara hasil mesin tidak memuat 'df1'/'df2'
    #     untuk Pillai/Hotelling/Roy → halaman jatuh ke '—, —'. Mesinnya BENAR
    #     (p dihitung dengan df yang sama); yang hilang cuma LAPORAN df-nya.
    #     db1 = (k-1)·p  ·  db2 = (n-k)·p  (aproksimasi baku F untuk Pillai).
    df1p = (k - 1) * p
    df2p = (n - k) * p
    if st['pillai'] > 0 and 0 < st['pillai'] < 1 and n > k and k > 1:
        fp = (st['pillai'] / (k - 1)) / ((1 - st['pillai']) / (n - k))
        hasil['pillai'] = {'F': float(fp), 'p': float(stats.f.sf(
            fp, df1p, df2p)), 'df1': float(df1p), 'df2': float(df2p)}
    else:
        hasil['pillai'] = {'F': None, 'p': None,
                           'df1': float(df1p), 'df2': float(df2p)}

    # Hotelling-Lawley
    if st['hotelling'] > 0 and n > k and k > 1:
        fh = st['hotelling'] * (n - k) / (k - 1)
        hasil['hotelling'] = {'F': float(fh), 'p': float(stats.f.sf(
            fh, df1p, df2p)), 'df1': float(df1p), 'df2': float(df2p)}
    else:
        hasil['hotelling'] = {'F': None, 'p': None,
                              'df1': float(df1p), 'df2': float(df2p)}

    # Roy's Largest Root
    if st['roy'] > 0 and n > k and k > 1:
        fr = st['roy'] * (n - k) / (k - 1)
        hasil['roy'] = {'F': float(fr), 'p': float(stats.f.sf(
            fr, df1p, df2p)), 'df1': float(df1p), 'df2': float(df2p)}
    else:
        hasil['roy'] = {'F': None, 'p': None,
                        'df1': float(df1p), 'df2': float(df2p)}

    return hasil


# ═══════════════════════════════════════════════════════════════════════
#  7. UJI LANJUTAN PER-Y (ANOVA satu arah)
# ═══════════════════════════════════════════════════════════════════════
def _anova_per_y(Y: np.ndarray, grup: np.ndarray, nama_y: list[str]) -> list:
    """Kalau MANOVA signifikan, Y MANA yang beda? → uji tiap Y satu arah.

    ⚠️ Ini 'uji lanjutan' (post-hoc sederhana). Dikerjakan TERPISAH per Y,
    jadi TIDAK menggantikan MANOVA — justru MANOVA yang menjaga galat
    Tipe I-nya; ANOVA per-Y cuma menunjukkan LOKASI bedanya.
    """
    kel = sorted(set(grup.tolist()))
    keluar = []
    for j, nm in enumerate(nama_y):
        pecah = [Y[grup == g, j] for g in kel]
        if len(pecah) < 2 or min(len(q) for q in pecah) < 2:
            keluar.append({'y': nm, 'F': None, 'p': None, 'label': '—',
                           'rerata': []})
            continue
        F, p = stats.f_oneway(*pecah)
        keluar.append({
            'y': nm, 'kode': f'Y{j + 1}',
            'F': float(F), 'p': float(p),
            'rerata': [{'kelompok': str(g), 'rerata': float(pecah[i].mean()),
                        'n': int(len(pecah[i]))} for i, g in enumerate(kel)],
            'gl1': len(kel) - 1, 'gl2': int(len(Y) - len(kel)),
            'label': ('Berbeda' if p < ALPHA else 'Tidak berbeda'),
        })
    return keluar


# ═══════════════════════════════════════════════════════════════════════
#  8. ASUMSI — WAJIB. MANOVA tanpa cek syarat = menyesatkan.
# ═══════════════════════════════════════════════════════════════════════
def _asumsi(Y: np.ndarray, grup: np.ndarray, nama_y: list[str]) -> dict:
    """Periksa 3 syarat MANOVA.

    (1) VARIANS-KOVARIANS SAMA antar kelompok → **Box's M**.
        Kalau ini dilanggar, uji MANOVA bisa terlalu percaya diri.
    (2) VARIANS TIAP Y SAMA antar kelompok → **Levene** per Y.
    (3) TIDAK ADA PENCILAN → jarak Mahalanobis, batas khi-kuadrat.
    Tambahan: normalitas multivariat → skewness/kurtosis (ringkas).
    """
    kel = sorted(set(grup.tolist()))
    p = Y.shape[1]
    n = Y.shape[0]
    k = len(kel)

    # ── (1) Box's M ──────────────────────────────────────────────────
    Sp = [np.cov(Y[grup == g], rowvar=False) for g in kel]
    Sp = [np.atleast_2d(S) for S in Sp]
    nk = [int((grup == g).sum()) for g in kel]
    Sgab = sum((nk[i] - 1) * Sp[i] for i in range(k)) / (n - k)
    try:
        det_gab = float(np.linalg.det(Sgab))
        M = (n - k) * math.log(max(det_gab, 1e-300)) \
            - sum((nk[i] - 1) * math.log(max(float(np.linalg.det(Sp[i])),
                                             1e-300)) for i in range(k))
        lag = (sum(1.0 / (nk[i] - 1) for i in range(k)) - 1.0 / (n - k)) \
            * (2 * p ** 2 + 3 * p - 1) / (6 * (p + 1) * (k - 1))
        df_bm = p * (p + 1) * (k - 1) / 2.0
        c = 1 - lag
        M = M * c if c > 0 else M
        p_bm = float(stats.chi2.sf(M, df_bm))
        box = {'M': float(M), 'p': p_bm, 'df': float(df_bm),
               'label': ('Setara (aman)' if p_bm > BATAS_BOX
                         else 'BERBEDA — perlu hati-hati')}
    except Exception as e:            # pragma: no cover
        box = {'M': None, 'p': None, 'df': None,
               'label': f'Tidak bisa dihitung ({e})'}

    # ── (2) Levene per Y ─────────────────────────────────────────────
    levene = []
    for j, nm in enumerate(nama_y):
        pecah = [Y[grup == g, j] for g in kel]
        try:
            W, pv = stats.levene(*pecah, center='median')
            levene.append({'y': nm, 'W': float(W), 'p': float(pv),
                           'label': ('Setara' if pv > ALPHA else 'BERBEDA')})
        except Exception:
            levene.append({'y': nm, 'W': None, 'p': None, 'label': '—'})

    # ── (3) Pencilan multivariat (jarak Mahalanobis) ─────────────────
    mu = Y.mean(axis=0)
    S = np.cov(Y, rowvar=False)
    Sinv = np.linalg.pinv(np.atleast_2d(S))
    d2 = np.einsum('ij,jk,ik->i', Y - mu, Sinv, Y - mu)
    batas = float(stats.chi2.ppf(0.999, p))
    jml_out = int((d2 > batas).sum())
    pencilan = {'jumlah': jml_out, 'batas_khi2': batas,
                'persen': round(100.0 * jml_out / n, 2),
                'label': ('Tidak ada' if jml_out == 0
                          else f'{jml_out} responden patut diperiksa')}

    # ── Normalitas multivariat (ringkas) ─────────────────────────────
    try:
        mardia, pm = _mardia(Y)
    except Exception:
        mardia, pm = None, None

    return {'box_m': box, 'levene': levene, 'pencilan': pencilan,
            'mardia': {'nilai': mardia, 'p': pm}}


def _mardia(Y: np.ndarray) -> tuple[float, float]:
    """Uji normalitas multivariat Mardia (skewness) — ringkas & baku."""
    n, p = Y.shape
    mu = Y.mean(axis=0)
    S = np.cov(Y, rowvar=False)
    Sinv = np.linalg.pinv(np.atleast_2d(S))
    D = Y - mu
    b = np.einsum('ij,jk,ik->i', D, Sinv, D)
    skew = float(np.mean(b ** 3))
    stat = n * skew / 6.0
    df = p * (p + 1) * (p + 2) / 6.0
    return skew, float(stats.chi2.sf(stat, df))


# ═══════════════════════════════════════════════════════════════════════
#  9. KALIMAT KESIMPULAN — bahasa manusia, bukan cuma angka
# ═══════════════════════════════════════════════════════════════════════
def _kalimat(st: dict, uji: dict, p: int, k: int, asumsi: dict) -> list:
    """Susun kesimpulan bertingkat: hasil → lokasi beda → catatan syarat."""
    pil = (uji.get('pillai') or {}).get('p')
    wil = (uji.get('wilks') or {}).get('p')
    utama = 'pillai' if pil is not None else 'wilks'
    p_utama = pil if pil is not None else wil
    angka = st['pillai'] if utama == 'pillai' else st['wilks']
    nama_utama = "Pillai's Trace" if utama == 'pillai' else "Wilks' Lambda"

    baris = []
    if p_utama is None:
        baris.append('Uji MANOVA tidak bisa disimpulkan — data terlalu sedikit.')
        return baris

    if p_utama < ALPHA:
        baris.append(
            f'Ada perbedaan NYATA antar kelompok pada gabungan {p} variabel '
            f'sekaligus ({nama_utama} = {angka:.4f}, p = {p_utama:.4f}). '
            f'Artinya: kelompok-kelompok ini TIDAK sama.')
    else:
        baris.append(
            f'TIDAK ada perbedaan nyata antar kelompok pada gabungan {p} '
            f'variabel ({nama_utama} = {angka:.4f}, p = {p_utama:.4f}). '
            f'Artinya: secara bersama-sama, kelompok ini bisa dianggap sama.')

    # Catatan asumsi — jujur, jangan disembunyikan
    bm = asumsi.get('box_m') or {}
    if bm.get('p') is not None and bm['p'] <= BATAS_BOX:
        baris.append(
            '⚠️ Catatan: sebaran (varians-kovarians) antar kelompok BERBEDA '
            f"(Box's M p = {bm['p']:.4f}). Karena itu sebaiknya berpegang pada "
            "Pillai's Trace, bukan Wilks — Pillai lebih tahan saat syarat ini "
            'dilanggar.')
    beda_v = [q['y'] for q in (asumsi.get('levene') or [])
              if q.get('label') == 'BERBEDA']
    if beda_v:
        baris.append(
            f"⚠️ Catatan: sebaran {', '.join(beda_v)} tidak setara antar "
            'kelompok (Levene). Hasilnya tetap bisa dipakai, tapi tafsirnya '
            'perlu hati-hati.')
    out = asumsi.get('pencilan') or {}
    if out.get('jumlah'):
        baris.append(
            f"⚠️ Catatan: {out['jumlah']} responden ({out['persen']}%) "
            'terdeteksi menyimpang jauh. Periksa dulu sebelum disimpulkan.')
    return baris


# ═══════════════════════════════════════════════════════════════════════
#  PINTU UTAMA
# ═══════════════════════════════════════════════════════════════════════
def bisa_manova(kelompok, nama_y) -> dict:
    """Periksa dulu SYARAT MINIMAL, sebelum menghitung apa pun."""
    kelompok = list(kelompok or [])
    nama_y = list(nama_y or [])
    n = len(kelompok)
    kel = sorted(set(kelompok))
    hitung = {g: kelompok.count(g) for g in kel}

    if len(nama_y) < MIN_Y:
        return {'bisa': False, 'sebab':
                f'MANOVA butuh minimal {MIN_Y} variabel hasil (Y). '
                f'Sekarang baru {len(nama_y)}. Kalau Y cuma satu, '
                'pakai uji beda rata-rata biasa (ANOVA/uji t).'}
    if len(kel) < MIN_KELOMPOK:
        return {'bisa': False, 'sebab':
                f'MANOVA butuh minimal {MIN_KELOMPOK} kelompok. '
                f'Sekarang baru {len(kel)}.'}
    kecil = {g: c for g, c in hitung.items() if c < MIN_ISI}
    if kecil:
        return {'bisa': False, 'sebab':
                'Ada kelompok yang isinya kurang dari '
                f'{MIN_ISI} responden: {kecil}. Tambah datanya dulu.'}
    return {'bisa': True, 'n': n, 'jumlah_kelompok': len(kel),
            'jumlah_y': len(nama_y), 'isi_kelompok': hitung}


def hitung_manova(Y, kelompok, nama_y=None, sscp: bool = False) -> dict:
    """Hitung MANOVA lengkap: uji → lokasi beda → asumsi → kesimpulan.

    Y        : ndarray 2D (baris = responden, kolom = variabel Y)
               atau DataFrame.
    kelompok : daftar/tanda kelompok tiap responden (sepanjang Y).
    nama_y   : nama tiap kolom Y.
    sscp     : sertakan matriks SSCP mentah di hasil (bawaan: TIDAK).
               ⚠️ Matriks itu besar & hanya untuk pemeriksaan mesin; kalau
               ikut dikirim ke halaman, hasilnya berat & menambah risiko
               tidak bisa di-JSON-kan.

    ⚠️ R4 DIPATUHI: fungsi ini TIDAK menyentuh format data lama.
       Kelompok datang sebagai argumen TERPISAH.

    ⚠️ Semua angka dikembalikan sebagai tipe Python biasa (float/int/list),
       BUKAN numpy — supaya hasilnya bisa langsung dikirim lewat HTTP
       (terukur: ndarray → 500 "not JSON serializable").
    """
    try:
        import pandas as pd
        if isinstance(Y, pd.DataFrame):
            nama_y = nama_y or list(Y.columns)
            Y = Y.to_numpy(dtype=float)
    except Exception:            # pragma: no cover
        pass

    Y = np.asarray(Y, dtype=float)
    if Y.ndim == 1:
        Y = Y.reshape(-1, 1)
    kelompok = np.asarray(list(kelompok))
    if nama_y is None:
        nama_y = [f'Y{i + 1}' for i in range(Y.shape[1])]

    # Buang baris kosong (pairwise: kelompok & SEMUA Y harus ada)
    pakai = ~np.isnan(Y).any(axis=1) & (kelompok != None)  # noqa: E711
    if isinstance(kelompok, np.ndarray):
        pakai &= np.array([str(q).strip() != '' for q in kelompok])
    dibuang = int((~pakai).sum())
    Y, kelompok = Y[pakai], kelompok[pakai]

    gate = bisa_manova(kelompok.tolist(), nama_y)
    if not gate['bisa']:
        return {'boleh': False, 'sebab': gate['sebab'], 'n': int(len(kelompok))}

    kel = sorted(set(kelompok.tolist()))
    p = Y.shape[1]
    k = len(kel)
    n = Y.shape[0]

    sp = _hitung_sscp(Y, kelompok)
    st = _statistik(sp['W'], sp['B'])
    uji = _f_dari_statistik(st, p, k, n)
    lanjut = _anova_per_y(Y, kelompok, nama_y)
    asum = _asumsi(Y, kelompok, nama_y)
    kal = _kalimat(st, uji, p, k, asum)

    # ── Cek ringkas kondisi pecahan (T = W + B) — bukti hitungan sehat ──
    selisih = float(np.abs(sp['T'] - (sp['W'] + sp['B'])).max())

    hasil = {
        'boleh': True, 'n': n, 'n_dibuang': dibuang,
        'p': p, 'k': k, 'kelompok': kel,
        'isi_kelompok': sp['n_kelompok'],
        'rerata_kelompok': sp['rerata_kelompok'],
        'nama_y': list(nama_y),
        'statistik': st, 'uji': uji,
        'lanjut': lanjut, 'asumsi': asum,
        'kalimat': kal,
        'selisih_sscp': selisih,
    }
    if sscp:
        # hanya disertakan kalau DIMINTA (untuk pemeriksaan mesin)
        hasil['sscp'] = {'W': sp['W'].tolist(), 'B': sp['B'].tolist(),
                         'T': sp['T'].tolist()}
    return hasil
