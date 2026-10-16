"""DIAGNOSIS DATA SPSS & PLS — membaca berkas user lalu memeriksa syarat.

ACC Bos 19Sep26: "1. B (xlsx, csv, sav) 2. A 3. A"
  1B → terima .xlsx + .csv + .sav
  2A → user TUNJUK KOLOM MANUAL (mesin tidak menebak)
  3A → 7 kartu bacaan /syarat PINDAH ke BELAJAR

ATURAN INDUK (jangan dilanggar):
  · Hitungan LOKAL (numpy/scipy/pandas) — TANPA AI. Gratis, instan, bisa diaudit.
  · BENAR katakan benar, SALAH katakan salah, + cara membetulkannya.
  · Kalau belum bisa diperiksa → KATAKAN BELUM BISA (jangan diam-diam dilewat).

⚠️ PELAJARAN 19Sep26 (jangan ulang): SEBELUM memakai NAMA apa pun (kelas CSS,
variabel, ikon, fungsi) — GREP dulu buktikan ADA. Contoh nyata: `--tinta-1` dan
ikon `arrow-left-right` TIDAK ADA, hampir dipakai.
"""
from __future__ import annotations

import io
import math
import time
from typing import Any

import numpy as np
import pandas as pd

# ── Batas berkas (satu sumber, jangan hardcode di JS) ────────────────────────
# ⚠️ PELAJARAN 15Sep26 (EduAi): batas yang ditulis di DUA tempat = yang pertama
# memblokir, yang kedua tak pernah tersentuh → gerbang mustahil kejadian.
# Karena itu MAX_BYTE dikirim server ke template, JANGAN ditulis ulang di JS.
MAX_BYTE = 10 * 1024 * 1024          # 10 MB
BARIS_MAKS = 50_000                  # cukup untuk semua skripsi/tesis


class GagalBaca(Exception):
    """Berkas tidak bisa dibaca — pesannya SUDAH ramah untuk user."""


# ═══════════════════════════════════════════════════════════════════════════
# 1. BACA BERKAS (xlsx · csv · sav)
# ═══════════════════════════════════════════════════════════════════════════
def baca_berkas(nama: str, isi: bytes) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Baca berkas unggahan → (DataFrame, keterangan).

    TERUKUR 19Sep26 (uji /tmp/uji_sav.py): ketiga format terbaca.
      csv  → pandas 3.0.5
      xlsx → openpyxl 3.1.5
      sav  → pyreadstat 1.3.6 (+ label kolom & label NILAI ikut terbaca)
    """
    if len(isi) > MAX_BYTE:
        mb = len(isi) / 1024 / 1024
        raise GagalBaca(
            f"Berkasnya {mb:.1f} MB — melebihi batas {MAX_BYTE // 1024 // 1024} MB. "
            f"Coba simpan sebagian kolom saja, atau pecah berkasnya.")
    if not isi:
        raise GagalBaca('Berkasnya kosong — tidak ada isi yang bisa dibaca.')

    ext = (nama or '').lower().rsplit('.', 1)
    ext = ext[-1] if len(ext) == 2 else ''
    if ext not in ('xlsx', 'xls', 'csv', 'sav', 'txt'):
        raise GagalBaca(
            f"Format .{ext} belum didukung. Yang bisa dibaca: "
            f".xlsx · .csv · .sav (SPSS).")

    ket: dict[str, Any] = {'label_nilai': {}, 'sumber': ext}
    try:
        if ext in ('xlsx', 'xls'):
            df = pd.read_excel(io.BytesIO(isi), engine='openpyxl')
        elif ext == 'sav':
            import pyreadstat
            df, meta = pyreadstat.read_sav(io.BytesIO(isi))
            # label nilai (mis. 1 = Sangat Tidak Setuju) — dipakai untuk
            # menjelaskan hasil dengan bahasa user, bukan angka mesin.
            ket['label_nilai'] = dict(meta.variable_value_labels or {})
            ket['label_kolom'] = dict(meta.column_names_to_labels or {})
        else:
            # ⚠️ Pemisah bisa koma ATAU titik-koma (Excel bahasa Indonesia).
            # Jangan tebak satu saja — coba dua-duanya, ambil yang jumlah
            # kolomnya lebih banyak. Ini yang sering bikin "kolom jadi 1".
            teks = isi.decode('utf-8-sig', errors='replace')
            df = pd.read_csv(io.StringIO(teks), sep=',')
            if df.shape[1] == 1 and ';' in teks.split('\n')[0]:
                df = pd.read_csv(io.StringIO(teks), sep=';')
    except GagalBaca:
        raise
    except Exception as e:                                   # noqa: BLE001
        # Pesan asli mesin TIDAK ditampilkan mentah ke user — tapi dicatat.
        raise GagalBaca(
            f"Berkasnya belum bisa dibaca sebagai .{ext}. "
            f"Pastikan ini berkas data (bukan hasil cetak/PDF), "
            f"lalu coba simpan ulang dari SPSS/Excel.") from e

    if df.empty:
        raise GagalBaca('Berkasnya terbaca, tapi tidak ada baris data di dalamnya.')
    if len(df) > BARIS_MAKS:
        raise GagalBaca(
            f"Barisnya {len(df):,} — melebihi batas {BARIS_MAKS:,}. "
            f"Ini biasanya bukan data kuesioner, melainkan data lain.")

    # Buang kolom yang seluruhnya kosong (sering muncul dari Excel).
    df = df.dropna(axis=1, how='all')
    # Buang kolom yang jelas bukan angka → bisa jadi kolom nama/NIM.
    ket['kolom_teks'] = [c for c in df.columns if not _numerik(df[c])]
    ket['n_baris'] = int(len(df))
    ket['n_kolom'] = int(df.shape[1])
    ket['sel_kosong'] = int(df.isna().sum().sum())
    return df, ket


def _numerik(s: pd.Series) -> bool:
    """Apakah kolom ini angka? (data .sav datang sebagai float64 — normal)"""
    s2 = s.dropna()
    if s2.empty:
        return False
    return pd.api.types.is_numeric_dtype(s2)


# ═══════════════════════════════════════════════════════════════════════════
# 1b. PENYIMPANAN SEMENTARA — supaya user tidak perlu unggah dua kali
# ═══════════════════════════════════════════════════════════════════════════
# MENGAPA tidak ditulis ke disk: aplikasi ini TIDAK punya login dan TIDAK
# punya basis data (terukur 19Sep26: nol cookie/session di app/main.py).
# Menyimpan data responden orang ke disk berarti menyimpan tanpa pemiliknya
# bisa menghapus — itu tidak pantas. ⇒ disimpan di MEMORI, kadaluarsa
# sendiri, jumlahnya dibatasi.
_SEMENTARA: dict[str, tuple[float, pd.DataFrame]] = {}
_MAX_SEMENTARA = 12              # cukup untuk beberapa orang bersamaan
_UMUR_SEMENTARA = 60 * 45        # 45 menit — lebih dari cukup sekali kerja


def simpan_sementara(df: pd.DataFrame) -> str:
    """Simpan data di memori → kembalikan kunci pendek. TIDAK menyentuh disk."""
    import secrets
    bersihkan_sementara()
    kunci = secrets.token_urlsafe(12)
    _SEMENTARA[kunci] = (time.time(), df)
    if len(_SEMENTARA) > _MAX_SEMENTARA:
        tua = sorted(_SEMENTARA.items(), key=lambda kv: kv[1][0])
        for k, _ in tua[:len(_SEMENTARA) - _MAX_SEMENTARA]:
            _SEMENTARA.pop(k, None)
    return kunci


def ambil_sementara(kunci: str) -> pd.DataFrame | None:
    """Ambil data. Kadaluarsa → None (user diminta unggah ulang, pesannya ramah)."""
    if not kunci:
        return None
    isi = _SEMENTARA.get(kunci)
    if isi is None:
        return None
    waktu, df = isi
    if time.time() - waktu > _UMUR_SEMENTARA:
        _SEMENTARA.pop(kunci, None)
        return None
    return df


def bersihkan_sementara() -> int:
    """Buang data kadaluarsa. Kembalikan berapa yang dibuang."""
    sekarang = time.time()
    tua = [k for k, (t, _) in _SEMENTARA.items()
           if sekarang - t > _UMUR_SEMENTARA]
    for k in tua:
        _SEMENTARA.pop(k, None)
    return len(tua)


# ═══════════════════════════════════════════════════════════════════════════
# 2. PERIKSA SYARAT (SPSS)
# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ Ambang ini SENGAJA ditulis di satu tempat saja, sama seperti aturan
# kelayakan.py. Kalau diubah, ubah di sini — jangan di JS.
AMBANG = {
    'ks_p': 0.05,          # normalitas: p > 0,05 = sisa menyebar normal
    'glejser_p': 0.05,     # hetero: p > 0,05 = sisa rata (aman)
    'vif_perhatian': 5.0,
    'vif_batas': 10.0,
    'dw_bawah': 1.5,       # Durbin-Watson: 1,5–2,5 dianggap aman
    'dw_atas': 2.5,
    'outlier_z': 3.0,      # batas Z untuk outlier
}


def periksa_spss(df: pd.DataFrame, kolom_x: list[str], kolom_y: str,
                 kolom_m: list[str] | None = None,
                 kolom_z: list[str] | None = None,
                 bentuk_mediasi: str | None = None,
                 buang_kosong: str = 'baris') -> dict[str, Any]:
    """Diagnosa ala SPSS: normalitas, hetero, VIF, linearitas, outlier, DW.

    kolom_m (perantara) DIPAKAI kalau user menunjuknya: regresi jadi
    X + M → Y (itu yang sebenarnya terjadi kalau ada mediasi).
    Kalau tidak ditunjuk, prediktor = X saja — dan itu dikatakan apa adanya.

    kolom_z (penguat/provider) — DITAMBAHKAN 21Sep26. Sebelumnya parameter ini
    TIDAK ADA → PERAN Z yang ditandai mahasiswa DIBUANG TOTAL (terukur: halaman
    mengirim Z1 tapi hasil hanya X1). Cacat itu ditemukan lewat uji pintu
    produksi (unggah → Hasil), lihat TEMUAN_MEDIASI_MODERASI_21SEP2026.md.
    ⚠️ Z TIDAK dimasukkan ke `pred` di sini — bentuk moderasi (X×Z)
    dihitung di app/hitung/kaitan.py, supaya regresi biasa tetap bersih.
    """
    kolom_m = list(kolom_m or [])
    kolom_z = list(kolom_z or [])
    if not kolom_x:
        raise GagalBaca('Belum ada kolom X (variabel bebas) yang ditunjuk.')
    if kolom_y not in df.columns:
        raise GagalBaca(f'Kolom Y "{kolom_y}" tidak ada di berkas.')
    hilang = [c for c in list(kolom_x) + kolom_m + kolom_z if c not in df.columns]
    if hilang:
        raise GagalBaca(f'Kolom ini tidak ada di berkas: {", ".join(hilang)}')

    pred = list(kolom_x) + kolom_m
    pakai = pred + [kolom_y]
    d = df[pakai].apply(pd.to_numeric, errors='coerce')
    d = d.dropna() if buang_kosong == 'baris' else d.fillna(d.mean(numeric_only=True))
    n = len(d)
    if n < 10:
        raise GagalBaca(
            f'Setelah dibersihkan, tinggal {n} baris. Minimal 10 baris — '
            f'kalau terlalu sedikit, hasilnya tidak bisa dipercaya.')

    X = d[pred].to_numpy(dtype=float)
    y = d[kolom_y].to_numpy(dtype=float)

    # ── Regresi OLS (sama seperti SPSS: X'X)^-1 X'y lewat lstsq biar aman ──
    A = np.column_stack([np.ones(n), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ coef
    resid = y - yhat
    k = A.shape[1]

    # R²
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

    # Galat baku + t + p  (uji dua sisi, df = n - k)
    from scipy import stats as st
    try:
        sigma2 = ss_res / (n - k)
        cov = sigma2 * np.linalg.pinv(A.T @ A)
        se = np.sqrt(np.diag(cov))
        tval = coef / np.where(se > 0, se, np.nan)
        pval = 2 * (1 - st.t.cdf(np.abs(tval), df=n - k))
    except Exception:                                        # noqa: BLE001
        se = tval = pval = np.full(k, float('nan'))

    # ── ① NORMALITAS — 3 uji sekaligus (seperti SPSS menawarkan pilihan) ──
    # ⚠️ AKAR 19Sep26: `st.kstest(r,'norm',args=(m,s))` GAGAL di scipy 1.18 —
    #    `TypeError ndtr() takes from 1 to 2 positional arguments but 3 were given`.
    #    Bentuk `args=` DILARANG. Yang jalan: kirim FUNGSI CDF-nya langsung.
    #    Terukur: kstest(...cdf) → D=0,0468 p=0,754 (jalan).
    m_r, s_r = float(np.mean(resid)), float(np.std(resid, ddof=1))
    ks_s = ks_p = float('nan')
    if s_r > 0:
        try:
            kr = st.kstest(resid, st.norm(loc=m_r, scale=s_r).cdf)
            ks_s, ks_p = float(kr.statistic), float(kr.pvalue)
        except Exception:                                    # noqa: BLE001
            pass
    # Uji tambahan: Saphiro-Wilk (paling kuat untuk n < 50) & D'Agostino.
    # Dipakai sebagai pembanding — kalau ketiganya sepakat, kesimpulan kokoh.
    sh_p = da_p = float('nan')
    if 3 <= n <= 5000:
        try:
            sh_p = float(st.shapiro(resid).pvalue)
        except Exception:                                    # noqa: BLE001
            pass
    if n >= 20:
        try:
            da_p = float(st.normaltest(resid).pvalue)
        except Exception:                                    # noqa: BLE001
            pass
    skew = float(st.skew(resid)) if n > 2 else float('nan')
    kurt = float(st.kurtosis(resid)) if n > 3 else float('nan')
    # Kesimpulan: SEPAKAT mayoritas (tidak butuh semua lolos — beda uji beda
    # kepekaan; yang penting tidak ada yang jelas menolak).
    votes = [v for v in (ks_p, sh_p, da_p) if _ada(v)]
    normal = (sum(1 for v in votes if v > AMBANG['ks_p']) >= max(1, len(votes) - 1)
              if votes else None)

    # ── ② HETEROSKEDASTISITAS — uji Glejser ──
    # Glejser: regresikan |sisa| pada X. Kalau ADA X yang signifikan → ada hetero.
    # ⚠️ AKAR 19Sep26 — CACAT LOGIKA WULAN: mula-mula Wulan ambil `nanmin` dari
    #    SEMUA p, TERMASUK KONSTANTA. Konstanta SELALU p ≈ 0 (garis potong selalu
    #    "signifikan") → hetero SELALU dinyatakan ada, walau data bersih.
    #    Terukur: p_tiap=[0.0, 0.2184, 0.5173] → nanmin=0.0 → lulus=None/False.
    #    BENAR: BUANG p konstanta, lihat HANYA p milik X.
    glej = _regresi_sederhana(X, np.abs(resid))
    p_x = [float(v) for v in np.atleast_1d(glej['p'])[1:] if _ada(float(v))]
    glej_p_min = min(p_x) if p_x else float('nan')
    # ⚠️ AKAR 19Sep26 — CACAT NAMA (ketemu dari UJI, bukan dari membaca kode):
    #   Baris ini mula-mula menulis `hetero = glej_p_min < 0.05` lalu hasilnya
    #   dipakai sebagai `lulus`. Artinya TERBALIK: `glej_p_min < 0,05` = ADA
    #   hetero, tapi namanya `lulus`. Terukur: data BERSIH (p=0,2184) → lulus=False,
    #   data SAKIT (p=0,0143) → lulus=False juga. DUA-DUANYA False → mustahil.
    #   ATURAN: nama variabel WAJIB menggambarkan artinya. `ada_hetero` ≠ `lulus`.
    ada_hetero = (glej_p_min < AMBANG['glejser_p']) if _ada(glej_p_min) else None
    hetero = None if ada_hetero is None else (not ada_hetero)

    # ── ③ MULTIKOLINEARITAS — VIF per prediktor ──
    vif = _vif(X)
    vif_maks = float(np.nanmax(vif)) if len(vif) else float('nan')

    # ── ④ LINEARITAS — lengkung: tambah X² untuk tiap X ──
    lin = _uji_linearitas(d, pred, kolom_y, r2, n, k)

    # ── ⑤ OUTLIER — Z pada sisa (standar) ──
    sd_res = float(np.std(resid, ddof=1)) if n > 1 else 0.0
    z_res = resid / sd_res if sd_res > 0 else np.zeros(n)
    luar = np.where(np.abs(z_res) > AMBANG['outlier_z'])[0]
    # Outlier di Y (bukan cuma sisa) — ini yang biasanya dimaksud mahasiswa.
    sd_y = float(np.std(y, ddof=1)) if n > 1 else 0.0
    z_y = (y - y.mean()) / sd_y if sd_y > 0 else np.zeros(n)
    luar_y = np.where(np.abs(z_y) > AMBANG['outlier_z'])[0]

    # ── ⑥ DURBIN-WATSON ──
    dw = _durbin_watson(resid)

    # ── ⑦ MEDIASI & MODERASI (ACC Bos 21Sep26) ──────────────────────────
    # Sebelum ini, peran Z DIBUANG dan M diperlakukan seperti X biasa →
    # mahasiswa yang memilih kartu Mediasi/Moderasi TIDAK dapat hasilnya.
    # Sekarang dihitung dari DATA MAHASISWA (bukan simulasi) di modul
    # app/hitung/kaitan.py. Bentuk: mediasi = bootstrap (1b), moderasi =
    # suku interaksi X×Z (2a), simpulan = aturan baku p<0,05 (3a).
    kaitan = None
    if kolom_m or kolom_z:
        try:
            from app.hitung.kaitan import hitung_kaitan
            # `d` = tabel angka yang SUDAH dibersihkan (pred + Y). Tapi `pred`
            # tidak memuat Z, jadi Z ditempel di sini supaya moderasi bisa
            # dihitung — tanpa mengubah `pred` (regresi biasa tetap bersih).
            d_kaitan = d.copy()
            for c in kolom_m + kolom_z:
                if c not in d_kaitan.columns:
                    d_kaitan[c] = pd.to_numeric(df[c], errors='coerce')
            d_kaitan = d_kaitan.dropna()
            kaitan = hitung_kaitan(d_kaitan, kolom_x, kolom_y,
                                   kolom_m=kolom_m, kolom_z=kolom_z,
                                   bentuk=bentuk_mediasi)
        except Exception as e:                                   # noqa: BLE001
            kaitan = {'ada': False,
                      'sebab': f'Tidak bisa menghitung mediasi/moderasi: {e}'}

    return {
        'n': int(n), 'n_dibuang': int(len(df) - n),
        'prediktor': pred, 'y': kolom_y, 'perantara': kolom_m, 'penguat': kolom_z,
        'kaitan': kaitan,
        'r2': _f(r2), 'r2_adj': _f(1 - (1 - r2) * (n - 1) / (n - k)) if n > k else None,
        'koef': [{'nama': nm, 'b': _f(c), 'se': _f(s), 't': _f(t), 'p': _f(p)}
                 for nm, c, s, t, p in zip(['(Konstanta)'] + pred, coef, se, tval, pval)],
        'normalitas': {'ks_s': _f(ks_s), 'ks_p': _f(ks_p),
                       'shapiro_p': _f(sh_p), 'dagostino_p': _f(da_p),
                       'skew': _f(skew), 'kurtosis': _f(kurt), 'lulus': normal},
        'hetero': {'glejser_p': _f(glej_p_min), 'p_tiap': [_f(v) for v in glej['p']],
                   'lulus': hetero},
        'vif': [{'nama': nm, 'vif': _f(v)} for nm, v in zip(pred, vif)],
        'vif_maks': _f(vif_maks),
        'linearitas': lin,
        'outlier': {'sisa': [int(i) + 1 for i in luar], 'y': [int(i) + 1 for i in luar_y],
                    'n_sisa': int(len(luar)), 'n_y': int(len(luar_y))},
        'dw': _f(dw),
        # ── BAHAN GAMBAR (Tahap 2, ACC Bos 20Sep26) ────────────────────────
        # Sisa mentah DIPAKAI untuk menggambar scatter ZPRED × ZRESID
        # di browser — jadi grafiknya dari DATA USER, bukan contoh.
        # ⚠️ SEMUA di bawah ini memakai angka yang SUDAH dihitung di atas.
        #    Tidak ada rumus statistik baru — cuma meneruskan ke halaman.
        'titik': {
            'zpred': [_f(v) for v in _std(zhat_x(A, coef))],
            'zresid': [_f(v) for v in _std(resid)],
            # P-P plot normalitas: pasangan (peluang teoritis, peluang teramati)
            # dari z sisa yang SUDAH dihitung (`z_res` di atas). Rumusnya cuma
            # mengurutkan z lalu memakai Φ⁻¹(i/(n+1)) — bukan uji baru.
            'pp': _titik_pp(z_res),
            # histogram sisa: batas bin + tinggi tiap bin (dihitung di sini
            # supaya JS tidak perlu tahu aturan pengelompokan).
            'hist': _histogram(resid),
            # scatter X pertama × Y — untuk membaca linearitas.
            # Pakai X PERTAMA saja: itu yang dimaksud mahasiswa saat bilang
            # "hubungan X dan Y lurus tidak?" (kalau X banyak, modelnya
            # ditangani uji Linearitas yang sudah ada).
            'xy': _titik_xy(d, pred[0], kolom_y) if pred else {'x': [], 'y': []},
        },
    }


def _titik_pp(z: np.ndarray) -> dict[str, list[float]]:
    """Bahan Normal P-P Plot — dari z sisa yang SUDAH dihitung.

    Cara bacanya (sama seperti SPSS): urutkan sisa dari kecil ke besar, lalu
    bandingkan dengan nilai harapan distribusi normal pada urutan yang sama.

      sumbu X = peluang teoritis  Φ⁻¹(i/(n+1))
      sumbu Y = peluang teramati  Φ((z_urut[i] − rata2) / simpangan)

    Titik yang MENEMPEL pada garis 45° = sisa menyebar normal.
    Tidak ada uji baru di sini — cuma menata angka untuk digambar.
    """
    from scipy import stats as st
    n = len(z)
    if n < 3:
        return {'teori': [], 'amati': []}
    urut = np.sort(np.asarray(z, dtype=float))
    m, s = float(np.mean(urut)), float(np.std(urut, ddof=1))
    if s <= 0:
        return {'teori': [], 'amati': []}
    i = np.arange(1, n + 1)
    teori = st.norm.ppf(i / (n + 1))
    amati = st.norm.cdf((urut - m) / s)
    return {'teori': [_f(v) for v in teori], 'amati': [_f(v) for v in amati]}


def _histogram(resid: np.ndarray) -> dict[str, Any]:
    """Bahan histogram sisa — bin + tinggi.

    Aturan Sturges (dipakai SPSS juga): jumlah bin ≈ √n, dibatasi 5…14 supaya
    di layar HP tidak jadi garis-garis tipis yang tak terbaca.
    """
    r = np.asarray(resid, dtype=float)
    n = len(r)
    if n < 5:
        return {'batas': [], 'tinggi': [], 'n_bin': 0}
    n_bin = int(min(14, max(5, round(math.sqrt(n)))))
    tinggi, batas = np.histogram(r, bins=n_bin)
    return {'batas': [_f(v) for v in batas],
            'tinggi': [int(v) for v in tinggi],
            'n_bin': int(n_bin)}


def _titik_xy(d: pd.DataFrame, kolom_x: str, kolom_y: str) -> dict[str, list[float]]:
    """Bahan scatter X × Y untuk membaca linearitas (bukan uji formal)."""
    x = pd.to_numeric(d[kolom_x], errors='coerce').to_numpy(dtype=float)
    y = pd.to_numeric(d[kolom_y], errors='coerce').to_numpy(dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    return {'x': [_f(v) for v in x[ok]], 'y': [_f(v) for v in y[ok]]}


def periksa_pls(df: pd.DataFrame, konstruk: dict[str, list[str]],
                kolom_y_konstruk: str) -> dict[str, Any]:
    """Diagnosa khas SmartPLS: outer loading, AVE, CR, VIF inner.

    konstruk = {'Kualitas Produk': ['KP1','KP2','KP3'], 'Harga': [...]}
    """
    if not konstruk:
        raise GagalBaca('Belum ada konstruk yang disusun dari kolom.')
    hasil = []
    for nama, kolom in konstruk.items():
        ada = [c for c in kolom if c in df.columns]
        if len(ada) < 2:
            raise GagalBaca(
                f'Konstruk "{nama}" cuma punya {len(ada)} kolom yang ada di berkas. '
                f'Minimal 2 butir agar outer loading bisa dihitung.')
        item = df[ada].apply(pd.to_numeric, errors='coerce').dropna()
        if len(item) < 10:
            raise GagalBaca(f'Konstruk "{nama}" tinggal {len(item)} baris setelah dibersihkan — terlalu sedikit.')
        skor = item.sum(axis=1).to_numpy(dtype=float)      # cara SPSS: skor total
        muat = []
        for c in ada:
            v = item[c].to_numpy(dtype=float)
            r = _r(v, skor)
            muat.append({'butir': c, 'muat': _f(r)})
        # AVE = rata-rata muat² (karena muat = korelasi butir↔skor, ini
        # pendekatan yang sama dipakai untuk konstruk unidimensi)
        ave = float(np.nanmean([m['muat'] ** 2 for m in muat if _ada(m['muat'])])) if muat else float('nan')
        # CR dari alpha (bentuk standar: CR ≈ alpha untuk skor total)
        al = _alpha(item.to_numpy(dtype=float))
        hasil.append({
            'nama': nama, 'kolom': ada, 'muat': muat,
            'ave': _f(ave), 'cr': _f(al),
            'lulus_muat': all((m['muat'] or 0) >= 0.70 for m in muat),
            'lulus_ave': _ada(ave) and ave >= 0.50,
            'lulus_cr': _ada(al) and al >= 0.70,
        })

    # VIF inner: seberapa kembar skor antar konstruk
    skor_all = {}
    for h in hasil:
        skor_all[h['nama']] = df[h['kolom']].apply(pd.to_numeric, errors='coerce').sum(axis=1)
    K = pd.DataFrame(skor_all).dropna()
    vif_inner = []
    if K.shape[1] >= 2:
        M = K.to_numpy(dtype=float)
        for i, nama in enumerate(K.columns):
            lain = [j for j in range(M.shape[1]) if j != i]
            v = _vif_satu(M[:, i], M[:, lain])
            vif_inner.append({'nama': nama, 'vif': _f(v)})

    # ── Fornell-Larcker + HTMT (20Sep26) ────────────────────────────────
    # Bahan SUDAH ADA: `hasil` (kolom + ave per konstruk) & `K` (skor tiap
    # konstruk). Tidak ada rumus statistik baru — cuma membandingkan angka
    # yang sudah dihitung. Jujur: hasilnya [] kalau konstruk < 2.
    #
    # ⚠️ CACAT YANG DITUTUP (20Sep26, ketemu saat menulis): HTMT butuh
    # korelasi ANTAR-BUTIR (kolom asli), bukan skor konstruk. `K` hanya
    # memuat SKOR (satu kolom per konstruk). Karena itu `df` WAJIB dikirim.
    fornell_pasangan, htmt_pasangan = _fornell_htmt(hasil, K, df)

    return {'konstruk': hasil, 'vif_inner': vif_inner,
            'fornell': fornell_pasangan, 'htmt': htmt_pasangan,
            'y_konstruk': kolom_y_konstruk,
            'n': int(len(df))}


def _korelasi_konstruk(hasil: list[dict], K: pd.DataFrame
                       ) -> dict[tuple[str, str], float]:
    """Korelasi ANTAR konstruk (skor total) — dasar Fornell & HTMT.

    Kunci = pasangan nama konstruk DALAM URUTAN ABJAD (supaya tidak dobel).
    """
    keluar: dict[tuple[str, str], float] = {}
    nama2 = [h['nama'] for h in hasil if h['nama'] in K.columns]
    for i in range(len(nama2)):
        for j in range(i + 1, len(nama2)):
            a, b = nama2[i], nama2[j]
            r = _r(K[a].to_numpy(dtype=float), K[b].to_numpy(dtype=float))
            if _ada(r):
                keluar[(a, b)] = float(r)
    return keluar


def _fornell_htmt(hasil: list[dict], K: pd.DataFrame, df: pd.DataFrame
                  ) -> tuple[list[dict], list[dict]]:
    """Hitung Fornell-Larcker & HTMT dari konstruk yang SUDAH dihitung.

    ── FORNELL-LARCKER (1981) ──
      Syarat: akar AVE tiap konstruk HARUS LEBIH BESAR daripada korelasi
      konstruk itu dengan konstruk LAIN. Artinya: variabel lebih erat
      dengan butirnya sendiri daripada dengan variabel lain.

    ── HTMT (Heterotrait-Monotrait Ratio, Henseler 2015) ──
      Rata-rata korelasi butir ANTAR-dua-konstruk dibagi akar dari
      (rata-rata korelasi butir DI DALAM masing-masing konstruk).
      Ambang: < 0,85 (ketat) · < 0,90 (longgar). Di atas itu = konstruk
      terlalu kembar → mahasiswa disarankan menggabung/membuang butir.

    ⚠️ `K` = SKOR konstruk (untuk Fornell) · `df` = data asli (untuk HTMT,
    yang butuh korelasi ANTAR-BUTIR).
    """
    pasangan = _korelasi_konstruk(hasil, K)
    akar_ave = {h['nama']: (math.sqrt(h['ave']) if _ada(h['ave'])
                            and h['ave'] > 0 else None)
                for h in hasil}
    kolom_konstruk = {h['nama']: [c for c in h['kolom'] if c in df.columns]
                      for h in hasil}

    def _r_kolom(x: str, y: str) -> float:
        a = pd.to_numeric(df[x], errors='coerce').to_numpy(dtype=float)
        b = pd.to_numeric(df[y], errors='coerce').to_numpy(dtype=float)
        return _r(a, b)

    fornell: list[dict] = []
    htmt: list[dict] = []
    for (a, b), r in sorted(pasangan.items()):
        ra, rb = akar_ave.get(a), akar_ave.get(b)
        # Fornell: batas = akar AVE TERKECIL dari pasangan itu.
        if ra is not None and rb is not None:
            batas = min(ra, rb)
            fornell.append({
                'pasangan': f'{a} ↔ {b}',
                'korelasi': _f(r, 3),
                'batas': _f(batas, 3),
                'lulus': abs(r) < batas,
            })

        # HTMT: butir antar ÷ akar(butir dalam).
        ka, kb = kolom_konstruk.get(a, []), kolom_konstruk.get(b, [])
        if ka and kb:
            antar = [abs(_r_kolom(x, y)) for x in ka for y in kb]
            dalam_a = [abs(_r_kolom(x, y))
                       for i, x in enumerate(ka) for y in ka[i + 1:]]
            dalam_b = [abs(_r_kolom(x, y))
                       for i, x in enumerate(kb) for y in kb[i + 1:]]

            def _rerata(v: list[float]) -> float | None:
                bagus = [x for x in v if _ada(x)]
                return sum(bagus) / len(bagus) if bagus else None

            ma, mb = _rerata(antar), _rerata(dalam_a + dalam_b)
            if ma is not None and mb is not None and mb > 0:
                nilai = ma / math.sqrt(mb)
                htmt.append({
                    'pasangan': f'{a} ↔ {b}',
                    'nilai': _f(nilai, 3),
                    'lulus_ketat': nilai < 0.85,
                    'lulus_longgar': nilai < 0.90,
                })

    return fornell, htmt


# ═══════════════════════════════════════════════════════════════════════════
# 3. ALAT HITUNG KECIL
# ═══════════════════════════════════════════════════════════════════════════
def _ada(v: Any) -> bool:
    """True hanya kalau angka dan bukan NaN."""
    return isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v))


def _f(v: Any, n: int = 4) -> float | None:
    """Bulatkan untuk JSON — None kalau NaN (JSON tidak kenal NaN)."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else round(f, n)


def _std(a: np.ndarray) -> np.ndarray:
    s = float(np.std(a, ddof=1)) if len(a) > 1 else 0.0
    return (a - a.mean()) / s if s > 0 else np.zeros_like(a)


def zhat_x(A: np.ndarray, coef: np.ndarray) -> np.ndarray:
    return A @ coef


def _r(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float('nan')
    return float(np.corrcoef(a, b)[0, 1])


def _regresi_sederhana(X: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    from scipy import stats as st
    n = len(y)
    k = X.shape[1] + 1
    A = np.column_stack([np.ones(n), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    try:
        s2 = float(np.sum(resid ** 2)) / (n - k)
        se = np.sqrt(np.diag(s2 * np.linalg.pinv(A.T @ A)))
        t = coef / np.where(se > 0, se, np.nan)
        p = 2 * (1 - st.t.cdf(np.abs(t), df=n - k))
    except Exception:                                        # noqa: BLE001
        t = p = np.full(k, np.nan)
    return {'coef': coef, 't': t, 'p': p}


def _vif(X: np.ndarray) -> list[float]:
    """VIF tiap prediktor: 1/(1-R²_j) dengan X_j dijelaskan X lain."""
    out = []
    for j in range(X.shape[1]):
        lain = [i for i in range(X.shape[1]) if i != j]
        if not lain:
            out.append(1.0)          # prediktor tunggal → VIF = 1 (memang begitu)
            continue
        out.append(_vif_satu(X[:, j], X[:, lain]))
    return out


def _vif_satu(yj: np.ndarray, Xlain: np.ndarray) -> float:
    n = len(yj)
    A = np.column_stack([np.ones(n), Xlain])
    coef, *_ = np.linalg.lstsq(A, yj, rcond=None)
    resid = yj - A @ coef
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((yj - yj.mean()) ** 2))
    if ss_tot <= 0:
        return float('nan')
    r2 = 1 - ss_res / ss_tot
    r2 = min(max(r2, 0.0), 0.999999)
    return 1.0 / (1.0 - r2)


def _uji_linearitas(d: pd.DataFrame, pred: list[str], y: str,
                    r2_lin: float, n: int, k: int) -> dict[str, Any]:
    """Uji lengkung: tambah X_j² lalu lihat apakah R² naik berarti.

    Kalau lengkungan nyata (p < 0,05) → hubungannya TIDAK lurus →
    regresi garis lurus kurang tepat. Ini yang dicari di uji linearitas.
    """
    from scipy import stats as st
    try:
        A1 = np.column_stack([np.ones(n)] + [d[c].to_numpy(dtype=float) for c in pred])
        yv = d[y].to_numpy(dtype=float)
        c1, *_ = np.linalg.lstsq(A1, yv, rcond=None)
        r1 = float(np.sum((yv - A1 @ c1) ** 2))
        A2 = np.column_stack([A1] + [d[c].to_numpy(dtype=float) ** 2 for c in pred])
        c2, *_ = np.linalg.lstsq(A2, yv, rcond=None)
        r2s = float(np.sum((yv - A2 @ c2) ** 2))
        df1 = A2.shape[1] - A1.shape[1]
        df2 = n - A2.shape[1]
        if df1 <= 0 or df2 <= 0 or r2s <= 0:
            return {'lulus': None, 'p': None, 'pesan': 'tidak bisa diuji (data terlalu sedikit)'}
        F = ((r1 - r2s) / df1) / (r2s / df2)
        p = float(1 - st.f.cdf(F, df1, df2))
        return {'lulus': p > 0.05, 'p': _f(p), 'F': _f(F),
                'r2_naik': _f(1 - r2s / r1) if r1 > 0 else None,
                'pesan': None}
    except Exception:                                        # noqa: BLE001
        return {'lulus': None, 'p': None, 'pesan': 'tidak bisa diuji'}


def _durbin_watson(resid: np.ndarray) -> float:
    e = resid - resid.mean()
    den = float(np.sum(e ** 2))
    if den <= 0:
        return float('nan')
    return float(np.sum(np.diff(e) ** 2) / den)


def _alpha(X: np.ndarray) -> float:
    """Cronbach alpha — rumus sama seperti mesin.py (jangan bikin rumus baru)."""
    k = X.shape[1]
    if k < 2:
        return float('nan')
    var_item = float(np.sum(np.var(X, axis=0, ddof=1)))
    var_total = float(np.var(np.sum(X, axis=1), ddof=1))
    if var_total <= 0:
        return float('nan')
    return float((k / (k - 1)) * (1 - var_item / var_total))


# ══════════════════════════════════════════════════════════════════════════
# PERAN KOLOM — "mesin & mahasiswa satu bahasa" (ACC Bos 21Sep26)
# ══════════════════════════════════════════════════════════════════════════
# ARAH BOS (verbatim):
#   "Yang paling baik, mahasiswa identifikasi kolom ini X1 kolom ini X2 dst.
#    Kolom ini M1, kolom ini M2 dst.. begitu juga Z dan Y, Y1, Y2 dst."
#   "Sebelum proses tampilkan kondisi yang telah di parsing benar atau tidak?
#    Kalau tidak minta beberapa hal untuk mhs verifikasi."
#   "Lebih bagus lagi kalo kesalahan itu terdeteksi script dan suruh ulang yg benar"
#
# Bentuk masukan (dari halaman konfirmasi):
#   peran = {'Kualitas_Produk_1': 'X1', 'Kualitas_Produk_2': 'X1', ...}
# Nilai yang sah: X1..Xn · M1..Mn · Z1..Zn · Y1..Yn  (huruf besar + angka)
#
# ⚠️ Fungsi ini MURNI MEMERIKSA — tidak menghitung apa pun, tidak menyentuh
#    periksa_spss(). Tujuannya: mesin PROTES DULU sebelum data diproses.

import re as _re

_POLA_PERAN = _re.compile(r'^([XMZY])([1-9][0-9]*)$')
_NAMA_PERAN = {'X': 'penyebab (X)', 'M': 'perantara (M)',
               'Z': 'penguat (Z)', 'Y': 'hasil (Y)'}


def rapikan_peran(peran: dict) -> dict[str, str]:
    """Buang entri kosong & samakan bentuk ('x1' → 'X1'). Tidak memeriksa."""
    bersih: dict[str, str] = {}
    for kolom, nilai in (peran or {}).items():
        if nilai in (None, '', '-'):
            continue
        bersih[str(kolom)] = str(nilai).strip().upper()
    return bersih


def skor_konstruk(df: pd.DataFrame, peran: dict) -> tuple[pd.DataFrame, dict]:
    """Gabung kolom berperan sama jadi SATU skor per konstruk (SPSS: skor total).

    ACC Bos 21Sep26 (Opsi A): mahasiswa menandai PERAN tiap kolom; beberapa
    kolom bisa satu peran (mis. X1 = 3 pertanyaan). Sebelum dihitung, kolom
    itu HARUS digabung jadi satu angka per responden — kalau tidak, mesin
    menghitung 3 kolom terpisah (salah: X1 jadi 3 variabel, bukan 1).

    ── ATURAN JAWABAN KOSONG (ACC Bos 21Sep26, **Opsi B**) ──────────────
    Kalau responden mengosongkan SEBAGIAN item, skornya = RATA-RATA item
    yang dijawab × JUMLAH ITEM seluruhnya.

        X1 = 3 item · dijawab 2 (skor 4 dan 5) → (4+5)/2 × 3 = 13,5

    Alasan (keputusan statistik, bukan teknis):
      · Opsi A (skor kosong) membuang responden yang cuma kosong 1 item —
        sayang, dan pada kuesioner lapangan itu biasa.
      · Opsi C (SPSS `SUM` melompati kosong) MENGHASILKAN SKOR TERLALU
        KECIL yang kelihatan sah — responden jawab 1 dari 2 dapat skor 2,0
        seolah lengkap. Itu jebakan klasik yang bikin hasil analisis salah.
      · Opsi B menaruh skor di SKALA YANG SAMA dengan responden lengkap,
        jadi perbandingan antar-responden tetap adil.
    Kalau SEMUA item kosong → skor kosong (NaN), bukan 0. Nol itu nilai,
    bukan ketiadaan.

    Kembalikan (tabel_skor, peta) di mana:
      · tabel_skor — DataFrame satu kolom per PERAN, nama kolom = nama peran
      · peta       — {nama_peran: [kolom asal, …]}  (untuk ditampilkan)
    Kolom yang tidak ditandai DILEWATI.
    """
    peran = rapikan_peran(peran)
    peta: dict[str, list[str]] = {}
    for kolom in df.columns:                 # urut berkas, bukan urut dict
        p = peran.get(kolom)
        if p:
            peta.setdefault(p, []).append(kolom)

    skor: dict[str, pd.Series] = {}
    for nama, kolom in peta.items():
        ada = [k for k in kolom if k in df.columns]
        if not ada:
            continue
        angka = df[ada].apply(pd.to_numeric, errors='coerce')
        # Opsi B: rata-rata item yang DIJAWAB × jumlah item SELURUHNYA.
        # `sum(min_count=1)` menghitung hanya yang terisi, dan menghasilkan
        # NaN kalau SEMUA kosong (bukan 0).
        dijawab = angka.sum(axis=1, min_count=1)
        jml_dijawab = angka.notna().sum(axis=1)
        skor[nama] = (dijawab / jml_dijawab) * len(ada)

    if not skor:
        return pd.DataFrame(index=df.index), {}
    return pd.DataFrame(skor), peta


def periksa_peran(kolom_berkas: list[str], peran: dict) -> dict[str, Any]:
    """Periksa penandaan peran kolom oleh mahasiswa.

    Kembalikan {'boleh_lanjut': bool, 'masalah': [...], 'tanya': [...],
                'kelompok': {...}, 'ringkas': str}

    · masalah  → HARUS diperbaiki (boleh_lanjut=False). Mis. tidak ada Y.
    · tanya    → boleh lanjut, tapi mesin minta dikonfirmasi. Mis. >1 M.
    """
    peran = rapikan_peran(peran)
    masalah: list[dict[str, Any]] = []
    tanya: list[dict[str, Any]] = []

    # ── 1. Ada kolom yang belum ditandai? ────────────────────────────────
    belum = [k for k in kolom_berkas if k not in peran]
    if belum:
        contoh = ', '.join(belum[:5]) + ('…' if len(belum) > 5 else '')
        masalah.append({
            'jenis': 'belum_ditandai', 'gawat': True, 'kolom': belum,
            'pesan': (f'Masih ada {len(belum)} kolom yang belum kamu tandai: '
                      f'{contoh}. Tandai dulu semua, atau tekan "Bukan data".')})

    # ── 2. Peran tak dikenal / kolom asing? ──────────────────────────────
    asing = [k for k in peran if k not in kolom_berkas]
    if asing:
        masalah.append({
            'jenis': 'kolom_asing', 'gawat': True, 'kolom': asing,
            'pesan': (f'Kolom ini tidak ada di berkas: {", ".join(asing[:5])}. '
                      f'Coba unggah ulang berkasnya.')})

    salah_bentuk = sorted({v for v in peran.values()
                           if not _POLA_PERAN.match(v or '')})
    if salah_bentuk:
        masalah.append({
            'jenis': 'peran_tak_dikenal', 'gawat': True, 'nilai': salah_bentuk,
            'pesan': (f'Peran ini tidak saya kenal: {", ".join(salah_bentuk)}. '
                      f'Yang bisa dipakai: X1…, M1…, Z1…, Y1…')})

    if masalah:
        return {'boleh_lanjut': False, 'masalah': masalah, 'tanya': tanya,
                'kelompok': {}, 'ringkas': masalah[0]['pesan']}

    # ── 3. Kelompokkan kolom per peran ───────────────────────────────────
    kelompok: dict[str, list[str]] = {}
    for kolom in kolom_berkas:                    # urut berkas, bukan urut dict
        kelompok.setdefault(peran[kolom], []).append(kolom)

    # ── 4. Dobel peran: 1 kolom dipakai 2 peran? (tak mungkin di dict,
    #      tapi nilai kembar bisa terjadi kalau halaman mengirim daftar) ──
    #      → sudah ditangani oleh bentuk dict; lewati.

    # ── 5. WAJIB ada Y ───────────────────────────────────────────────────
    ada_y = sorted({p for p in kelompok if p.startswith('Y')})
    if not ada_y:
        masalah.append({
            'jenis': 'tanpa_y', 'gawat': True,
            'pesan': ('Belum ada kolom hasil (Y). Tanpa Y, tidak ada yang '
                      'bisa dijelaskan — tandai dulu kolom hasilnya.')})

    # ── 6. WAJIB ada X ───────────────────────────────────────────────────
    ada_x = sorted({p for p in kelompok if p.startswith('X')})
    if not ada_x:
        masalah.append({
            'jenis': 'tanpa_x', 'gawat': True,
            'pesan': ('Belum ada kolom penyebab (X). Tanpa X, tidak ada yang '
                      'memengaruhi — tandai dulu kolom penyebabnya.')})

    # ── 7. Nomor melompat: X1, X3 tanpa X2 ───────────────────────────────
    for huruf in ('X', 'M', 'Z', 'Y'):
        nomor = sorted(int(p[1:]) for p in kelompok if p.startswith(huruf))
        if nomor and nomor != list(range(1, len(nomor) + 1)):
            tanya.append({
                'jenis': 'nomor_melompat', 'gawat': False, 'huruf': huruf,
                'pesan': (f'Nomor {huruf} kamu {nomor} — ada yang melompat. '
                          f'Coba cek, mungkin ada yang salah tandai.')})

    # ── 8. Konstruk cuma 1 kolom — biasanya minimal 2-3 ──────────────────
    tipis = [p for p, k in kelompok.items() if len(k) == 1]
    if tipis:
        tanya.append({
            'jenis': 'satu_kolom', 'gawat': False, 'peran': sorted(tipis),
            'pesan': (f'{", ".join(sorted(tipis))} cuma punya 1 kolom. '
                      f'Biasanya satu variabel minimal 2-3 pertanyaan — '
                      f'kalau memang cuma 1, tidak apa-apa.')})

    # ── 9. >1 M atau >1 Z → tanya SEKALI (paralel / berjenjang) ──────────
    banyak_m = sorted(p for p in kelompok if p.startswith('M'))
    banyak_z = sorted(p for p in kelompok if p.startswith('Z'))
    if len(banyak_m) > 1:
        tanya.append({
            'jenis': 'bentuk_mediasi', 'gawat': False, 'peran': banyak_m,
            'pilihan': ['paralel', 'berjenjang'],
            'pesan': (f'Ada {len(banyak_m)} perantara ({", ".join(banyak_m)}). '
                      f'Keduanya keluar dari X (paralel), atau M1 dulu lalu '
                      f'M2 (berjenjang)?')})
    if len(banyak_z) > 1:
        tanya.append({
            'jenis': 'bentuk_moderasi', 'gawat': False, 'peran': banyak_z,
            'pilihan': ['bersama', 'bertahap'],
            'pesan': (f'Ada {len(banyak_z)} penguat ({", ".join(banyak_z)}). '
                      f'Bekerja bersama-sama, atau Z1 dulu lalu Z2?')})

    boleh = not any(m.get('gawat') for m in masalah)

    # ── Ringkasan bahasa manusia ─────────────────────────────────────────
    bagian = []
    for huruf in ('X', 'M', 'Z', 'Y'):
        nama = [p for p in sorted(kelompok) if p.startswith(huruf)]
        if nama:
            isi = ' · '.join(f'{p} ({len(kelompok[p])} kolom)' for p in nama)
            bagian.append(f'{_NAMA_PERAN[huruf]}: {isi}')
    ringkas = ' | '.join(bagian) if bagian else 'Belum ada yang ditandai.'

    return {'boleh_lanjut': boleh, 'masalah': masalah, 'tanya': tanya,
            'kelompok': kelompok, 'ringkas': ringkas}
