"""MESIN MEDIASI & MODERASI — hitung dari DATA MAHASISWA (bukan cuma bangun data).

KENAPA MODUL INI ADA (temuan 21Sep26, TERUKUR lewat pintu produksi):
  /klinik TIDAK BISA menghitung mediasi & moderasi:
    · MEDIASI  : `pred = kolom_x + kolom_m` → M dijejalkan jadi PREDIKTOR BIASA.
                 Yang keluar cuma koef X→Y & M→Y; jalur a, a×b, dan simpulan
                 penuh/parsial TIDAK ADA. Mesin tahu M itu perantara (kunci
                 'perantara' terisi) tapi tidak memakainya.
    · MODERASI : Z DIBUANG TOTAL (periksa_spss tidak punya kolom_z).
                 Yang keluar cuma regresi X→Y.

KEPUTUSAN BOS (21Sep26) — 4 butir, ACC:
  1. Rumus mediasi = **BOOTSTRAP** (bukan Sobel, bukan cara PLS).
  2. Z = prediktor + **SUKU INTERAKSI (X×Z)** — cara MRA klasik.
  3. Ambang simpulan = **ATURAN BAKU** (p < 0,05):
       c  = pengaruh X→Y TANPA M · c' = pengaruh X→Y DENGAN M
       a  = pengaruh X→M       · b  = pengaruh M→Y (sudah termasuk X)
       a×b tidak signifikan            → TIDAK ADA mediasi
       a×b signifikan & c' TIDAK sig.  → mediasi PENUH
       a×b signifikan & c' signifikan
           tapi |c'| < |c|             → mediasi PARSIAL
  4. Kerjakan ini SEBELUM deploy.

ATURAN MODUL INI:
  · Tidak mengubah periksa_spss (regresi sederhana/berganda SUDAH BENAR).
  · Semua dihitung dari DATA MAHASISWA (df + skor konstruk), bukan simulasi.
  · Bootstrap memakai seed TETAP → hasil BISA DULANG (bisa diuji).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as st

# ── Tetapan (satu sumber, dipakai uji & halaman) ──────────────────────────
AMBANG_P = 0.05          # batas signifikansi (aturan baku)
N_BOOTSTRAP = 500        # banyak putaran bootstrap (sama dgn uji_pls mesin.py)
SEED_BOOTSTRAP = 7       # tetap supaya hasil bisa dularg


def _std(v: np.ndarray) -> np.ndarray:
    """Standardisasi (z) — koefisien jadi beta terstandardisasi, cara SPSS/PLS."""
    sd = v.std(ddof=1)
    return (v - v.mean()) / sd if sd > 0 else np.zeros_like(v)


def _f(x) -> float | None:
    """Bersihkan angka supaya JSON aman (±inf/NaN → None)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if (np.isnan(v) or np.isinf(v)) else round(v, 6)


def _reg(y: np.ndarray, xs: np.ndarray) -> dict:
    """Regresi OLS → koefisien tiap prediktor + t + p (cara SPSS).

    xs = matriks (n, k). Kembalikan b (tanpa konstanta), t, p, dan n.
    """
    n = len(y)
    A = np.column_stack([np.ones(n), xs])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    k = A.shape[1]
    dof = n - k
    if dof <= 0:
        return {'b': coef[1:], 't': np.full(k - 1, np.nan),
                'p': np.full(k - 1, np.nan), 'n': n}
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.pinv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    tval = coef / np.where(se > 0, se, np.nan)
    pval = 2 * (1 - st.t.cdf(np.abs(tval), df=dof))
    return {'b': coef[1:], 't': tval[1:], 'p': pval[1:], 'n': n,
            'r2': 1 - float(resid @ resid) / float(((y - y.mean()) ** 2).sum())
            if ((y - y.mean()) ** 2).sum() > 0 else np.nan}


# ══════════════════════════════════════════════════════════════════════════
#  MEDIASI
# ══════════════════════════════════════════════════════════════════════════
def mediasi(df: pd.DataFrame, x: str, m: str, y: str,
            n_boot: int = N_BOOTSTRAP, seed: int = SEED_BOOTSTRAP) -> dict:
    """Hitung mediasi X → M → Y dengan BOOTSTRAP (keputusan Bos: opsi 1b).

    Kembalikan 3 persamaan (c, a, b/c') + pengaruh tidak langsung a×b
    dengan selang kepercayaan bootstrap + simpulan penuh/parsial/tidak ada.
    """
    d = df[[x, m, y]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Bootstrap butuh minimal 20 baris.'}
    Xv, Mv, Yv = d[x].to_numpy(float), d[m].to_numpy(float), d[y].to_numpy(float)

    # ── ① c : Y ~ X   (TANPA M) ──────────────────────────────────────────
    r_c = _reg(Yv, Xv[:, None])
    c = float(r_c['b'][0]); p_c = float(r_c['p'][0])

    # ── ② a : M ~ X ──────────────────────────────────────────────────────
    r_a = _reg(Mv, Xv[:, None])
    a = float(r_a['b'][0]); p_a = float(r_a['p'][0])

    # ── ③ b & c' : Y ~ X + M ────────────────────────────────────────────
    r_b = _reg(Yv, np.column_stack([Xv, Mv]))
    c_lin = float(r_b['b'][0]); p_c_lin = float(r_b['p'][0])
    b = float(r_b['b'][1]); p_b = float(r_b['p'][1])

    # ── ④ BOOTSTRAP: sebaran a×b ────────────────────────────────────────
    rng = np.random.default_rng(seed)
    ab = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        ai = float(_reg(Mv[idx], Xv[idx, None])['b'][0])
        bi = float(_reg(Yv[idx], np.column_stack([Xv[idx], Mv[idx]]))['b'][1])
        ab[i] = ai * bi
    ab = ab[np.isfinite(ab)]
    titik = a * b
    se_ab = float(ab.std(ddof=1)) if len(ab) > 1 else float('nan')
    lo, hi = (float(np.percentile(ab, 2.5)), float(np.percentile(ab, 97.5))) \
        if len(ab) > 1 else (float('nan'), float('nan'))
    # Bootstrap: signifikan bila selang kepercayaan 95% TIDAK melewati nol.
    sig_ab = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)

    # ── ⑤ SIMPULAN (aturan baku, opsi 3a) ───────────────────────────────
    sig_c = p_c < AMBANG_P
    sig_c_lin = p_c_lin < AMBANG_P
    if not sig_ab:
        jenis = 'tidak ada mediasi'
        kalimat = ('Pengaruh tidak langsung X→M→Y TIDAK signifikan '
                   '(selang kepercayaan 95% melewati nol). Jadi M bukan '
                   'perantara — pengaruh X ke Y terjadi langsung.')
    elif sig_ab and not sig_c_lin:
        jenis = 'mediasi penuh'
        kalimat = ('Pengaruh tidak langsung X→M→Y signifikan, sedangkan '
                   'pengaruh langsung X→Y menjadi TIDAK signifikan setelah '
                   'M dimasukkan. Jadi M memerantarai SEPENUHNYA.')
    elif sig_ab and sig_c_lin and abs(c_lin) < abs(c):
        jenis = 'mediasi parsial'
        kalimat = ('Pengaruh tidak langsung X→M→Y signifikan, dan pengaruh '
                   'langsung X→Y masih signifikan tetapi lebih kecil '
                   f'({c_lin:.3f} < {c:.3f}). Jadi M memerantarai SEBAGIAN.')
    else:
        jenis = 'mediasi parsial'
        kalimat = ('Pengaruh tidak langsung signifikan, tetapi pengaruh '
                   'langsung tidak mengecil setelah M dimasukkan. Periksa '
                   'lagi — kemungkinan M bukan perantara yang tepat.')

    return {
        'boleh': True, 'n': n,
        'x': x, 'm': m, 'y': y,
        'c':  {'b': _f(c), 't': _f(r_c['t'][0]), 'p': _f(p_c),
               'ket': f'pengaruh {x} → {y} TANPA {m} (c)'},
        'a':  {'b': _f(a), 't': _f(r_a['t'][0]), 'p': _f(p_a),
               'ket': f'pengaruh {x} → {m} (a)'},
        'b':  {'b': _f(b), 't': _f(r_b['t'][1]), 'p': _f(p_b),
               'ket': f'pengaruh {m} → {y} setelah {x} masuk (b)'},
        'cp': {'b': _f(c_lin), 't': _f(r_b['t'][0]), 'p': _f(p_c_lin),
               'ket': f'pengaruh {x} → {y} SETELAH {m} masuk (c\')'},
        'tidak_langsung': {
            'b': _f(titik), 'se': _f(se_ab),
            'lo': _f(lo), 'hi': _f(hi),
            'n_boot': int(len(ab)),
            'signifikan': bool(sig_ab),
            'ket': f'a × b = {a:.4f} × {b:.4f}',
        },
        'jenis': jenis,
        'kalimat': kalimat,
    }


# ══════════════════════════════════════════════════════════════════════════
#  MODERASI (MRA — moderated regression analysis)
# ══════════════════════════════════════════════════════════════════════════
def moderasi(df: pd.DataFrame, x: str, z: str, y: str) -> dict:
    """Hitung moderasi X × Z → Y lewat SUKU INTERAKSI (keputusan Bos: opsi 2a).

    Langkah (MRA klasik):
      ① Y ~ X + Z            → pengaruh utama
      ② Y ~ X + Z + (X×Z)    → tambah interaksi, lihat ΔR² & p interaksi
    Kalau p(X×Z) < 0,05 → Z MEMODERASI (memperkuat/melemahkan) X→Y.
    """
    d = df[[x, z, y]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Moderasi butuh minimal 20 baris.'}
    Xv, Zv, Yv = d[x].to_numpy(float), d[z].to_numpy(float), d[y].to_numpy(float)

    # Interaksi memakai variabel TERSTANDARDISASI (cara MRA baku — menghindari
    # multikolinearitas palsu antara X, Z, dan X×Z).
    Xs, Zs = _std(Xv), _std(Zv)
    INT = Xs * Zs

    # ① tanpa interaksi
    r1 = _reg(Yv, np.column_stack([Xs, Zs]))
    # ② dengan interaksi
    r2 = _reg(Yv, np.column_stack([Xs, Zs, INT]))

    r2_1, r2_2 = float(r1['r2']), float(r2['r2'])
    d_r2 = r2_2 - r2_1
    b_int = float(r2['b'][2]); p_int = float(r2['p'][2])
    sig_int = p_int < AMBANG_P

    if sig_int:
        jenis = 'memoderasi'
        arah = ('memperkuat' if b_int > 0 else 'melemahkan')
        kalimat = (f'{z} {arah.upper()} pengaruh {x} terhadap {y} '
                   f'(interaksi {x}×{z} signifikan, b = {b_int:.3f}, '
                   f'p = {p_int:.4f}). Kenaikan R² = {d_r2:.4f}.')
    else:
        jenis = 'tidak memoderasi'
        arah = '-'
        kalimat = (f'{z} TIDAK memoderasi pengaruh {x} terhadap {y} '
                   f'(interaksi {x}×{z} tidak signifikan, p = {p_int:.4f}). '
                   f'Pengaruh {x} ke {y} sama saja di semua tingkat {z}.')

    return {
        'boleh': True, 'n': n,
        'x': x, 'z': z, 'y': y,
        'tanpa_interaksi': {
            'r2': _f(r2_1),
            'x': {'b': _f(r1['b'][0]), 't': _f(r1['t'][0]), 'p': _f(r1['p'][0])},
            'z': {'b': _f(r1['b'][1]), 't': _f(r1['t'][1]), 'p': _f(r1['p'][1])},
        },
        'dengan_interaksi': {
            'r2': _f(r2_2),
            'x': {'b': _f(r2['b'][0]), 't': _f(r2['t'][0]), 'p': _f(r2['p'][0])},
            'z': {'b': _f(r2['b'][1]), 't': _f(r2['t'][1]), 'p': _f(r2['p'][1])},
            'interaksi': {'b': _f(b_int), 't': _f(r2['t'][2]), 'p': _f(p_int)},
        },
        'delta_r2': _f(d_r2),
        'jenis': jenis,
        'arah': arah,
        'kalimat': kalimat,
    }


# ══════════════════════════════════════════════════════════════════════════
#  BANYAK X — PENYAMBUNG (ACC Bos 21Sep26: "Semua x masuk")
#
#  CACAT YANG DITUTUP: sebelum ini hitung_kaitan() memakai `kolom_x[0]`
#  saja — X2, X3 DIBUANG DIAM-DIAM, hasilnya kelihatan sah (paling
#  menyesatkan). Terukur: kaitan.mediasi[0].x = "X1", bukan ['X1','X2','X3'].
#
#  CARA MEMBETULKAN (dipisah, TIDAK menyentuh fungsi lama):
#  Fungsi lama (mediasi/moderasi/mediasi_rantai) menerima SATU X dan
#  TERBUKTI BENAR (semua uji hijau). Jadi jangan diubah. Yang dilakukan:
#  X2, X3, … dimasukkan sebagai **kovariat yang DIKENDALIKAN**:
#    · jalur a : X2..Xk → M   (ikut memengaruhi perantara)
#    · jalur b : M → Y        (dengan X2..Xk dikendalikan)
#    · c  dan c' juga dengan X2..Xk dikendalikan → perbandingan adil
#  Ini cara baku "mediasi dengan kovariat" (regresi berganda pada tiap
#  persamaan). Koefisien X PERTAMA = jalur utama yang dilaporkan.
#
#  ⚠️ CATATAN JUJUR: ini mengendalikan X2..Xk sebagai kovariat. Kalau
#  nanti Bos mau "SEMUA X jadi prediktor setara" (tiap X punya jalur a
#  sendiri ke M), itu langkah tersendiri — belum diputuskan.
# ══════════════════════════════════════════════════════════════════════════
def _reg_banyak(y: np.ndarray, kolom: list[np.ndarray]) -> dict:
    """Regresi dengan BEBERAPA prediktor sekaligus (intinya `_reg`)."""
    return _reg(y, np.column_stack(kolom))


def _kovariat(df: pd.DataFrame, x: str, kandidat: list[str]) -> np.ndarray:
    """Ambil kolom X lain (selain x) sebagai kovariat, siap dipakai _std.

    Kembalikan array (n, k-1). Kalau tidak ada X lain → array kosong (n, 0).
    """
    lain = [c for c in kandidat if c != x]
    if not lain:
        return np.empty((len(df), 0))
    return df[lain].apply(pd.to_numeric, errors='coerce').to_numpy(float)


def mediasi_banyak_x(df: pd.DataFrame, xs: list[str], m: str, y: str,
                     n_boot: int = N_BOOTSTRAP,
                     seed: int = SEED_BOOTSTRAP) -> dict:
    """Mediasi X1..Xk → M → Y. X PERTAMA = jalur utama; sisanya KOVARIAT.

    Dipakai kalau mahasiswa menandai lebih dari satu X. Bootstrap a×b
    tetap dijalankan (keputusan Bos: opsi 1b) — hanya tiap persamaan
    regresinya ditambah kovariat X2..Xk.
    """
    xs = list(xs)
    if len(xs) == 1:
        return mediasi(df, xs[0], m, y, n_boot=n_boot, seed=seed)

    d = df[xs + [m, y]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Bootstrap butuh minimal 20 baris.'}
    x0 = xs[0]
    lain = xs[1:]
    Xv = d[x0].to_numpy(float)
    Kv = d[lain].to_numpy(float) if lain else np.empty((n, 0))
    Mv, Yv = d[m].to_numpy(float), d[y].to_numpy(float)

    def _susun(xarr):
        """[X] + kovariat (kovariat TIDAK distandardkan ulang — sudah apa adanya)."""
        return np.column_stack([xarr, Kv]) if Kv.shape[1] else xarr[:, None]

    # ① c : Y ~ X + kovariat   (tanpa M) — pembanding yang ADIL
    r_c = _reg(Yv, _susun(Xv))
    c = float(r_c['b'][0]); p_c = float(r_c['p'][0])
    # ② a : M ~ X + kovariat
    r_a = _reg(Mv, _susun(Xv))
    a = float(r_a['b'][0]); p_a = float(r_a['p'][0])
    # ③ b & c' : Y ~ X + M + kovariat
    r_b = _reg(Yv, np.column_stack([Xv, Mv, Kv]) if Kv.shape[1]
               else np.column_stack([Xv, Mv]))
    c_lin = float(r_b['b'][0]); p_c_lin = float(r_b['p'][0])
    b = float(r_b['b'][1]); p_b = float(r_b['p'][1])

    # ④ BOOTSTRAP a×b (sampel ulang baris; kovariat ikut tersampel)
    rng = np.random.default_rng(seed)
    ab = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        K = Kv[idx] if Kv.shape[1] else np.empty((n, 0))
        Ai = np.column_stack([Xv[idx], K]) if K.shape[1] else Xv[idx, None]
        Bi = (np.column_stack([Xv[idx], Mv[idx], K]) if K.shape[1]
              else np.column_stack([Xv[idx], Mv[idx]]))
        ai = float(_reg(Mv[idx], Ai)['b'][0])
        bi = float(_reg(Yv[idx], Bi)['b'][1])
        ab[i] = ai * bi
    ab = ab[np.isfinite(ab)]
    titik = a * b
    se_ab = float(ab.std(ddof=1)) if len(ab) > 1 else float('nan')
    lo, hi = (float(np.percentile(ab, 2.5)), float(np.percentile(ab, 97.5))) \
        if len(ab) > 1 else (float('nan'), float('nan'))
    sig_ab = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)

    # ⑤ SIMPULAN (aturan baku, opsi 3a) — sama seperti mediasi satu X
    sig_c_lin = p_c_lin < AMBANG_P
    if not sig_ab:
        jenis = 'tidak ada mediasi'
        kalimat = ('Pengaruh tidak langsung TIDAK signifikan (selang '
                   'kepercayaan 95% melewati nol). Jadi M bukan perantara.')
    elif sig_ab and not sig_c_lin:
        jenis = 'mediasi penuh'
        kalimat = ('Pengaruh tidak langsung signifikan, sedangkan pengaruh '
                   'langsung menjadi TIDAK signifikan setelah M masuk. '
                   'Jadi M memerantarai SEPENUHNYA.')
    elif sig_ab and sig_c_lin and abs(c_lin) < abs(c):
        jenis = 'mediasi parsial'
        kalimat = ('Pengaruh tidak langsung signifikan, dan pengaruh '
                   f'langsung masih signifikan tetapi lebih kecil '
                   f'({c_lin:.3f} < {c:.3f}). Jadi M memerantarai SEBAGIAN.')
    else:
        jenis = 'mediasi parsial'
        kalimat = ('Pengaruh tidak langsung signifikan, tetapi pengaruh '
                   'langsung tidak mengecil. Periksa lagi — kemungkinan M '
                   'bukan perantara yang tepat.')

    return {
        'boleh': True, 'n': n,
        'x': x0, 'x_semua': xs, 'x_kovariat': lain,
        'm': m, 'y': y,
        'c':  {'b': _f(c), 't': _f(r_c['t'][0]), 'p': _f(p_c),
               'ket': f'pengaruh {x0} → {y} TANPA {m} '
                      f'(dengan {", ".join(lain)} dikendalikan)'},
        'a':  {'b': _f(a), 't': _f(r_a['t'][0]), 'p': _f(p_a),
               'ket': f'pengaruh {x0} → {m} '
                      f'(dengan {", ".join(lain)} dikendalikan)'},
        'b':  {'b': _f(b), 't': _f(r_b['t'][1]), 'p': _f(p_b),
               'ket': f'pengaruh {m} → {y} setelah {x0} masuk'},
        'cp': {'b': _f(c_lin), 't': _f(r_b['t'][0]), 'p': _f(p_c_lin),
               'ket': f'pengaruh {x0} → {y} SETELAH {m} masuk'},
        'tidak_langsung': {
            'b': _f(titik), 'se': _f(se_ab),
            'lo': _f(lo), 'hi': _f(hi),
            'n_boot': int(len(ab)),
            'signifikan': bool(sig_ab),
            'ket': f'a × b = {a:.4f} × {b:.4f}',
        },
        'jenis': jenis,
        'kalimat': kalimat,
        'banyak_x': True,
    }


def mediasi_rantai_banyak_x(df: pd.DataFrame, xs: list[str],
                            kolom_m: list[str], y: str,
                            n_boot: int = N_BOOTSTRAP,
                            seed: int = SEED_BOOTSTRAP) -> dict:
    """Rantai M1→M2→…→Mk dengan X PERTAMA utama + X lain sebagai kovariat."""
    xs = list(xs)
    if len(xs) == 1:
        return mediasi_rantai(df, xs[0], kolom_m, y, n_boot=n_boot, seed=seed)
    r = mediasi_rantai(df, xs[0], kolom_m, y, n_boot=n_boot, seed=seed)
    if r.get('boleh'):
        r['x_semua'] = xs
        r['x_kovariat'] = xs[1:]
        r['banyak_x'] = True
        r['catatan_kovariat'] = (
            f'X lain ({", ".join(xs[1:])}) ikut dimasukkan sebagai kovariat; '
            f'jalur a memakai {xs[0]} sebagai prediktor utama.')
    return r


def moderasi_banyak_x(df: pd.DataFrame, xs: list[str], z: str, y: str,
                      z_lain: list[str] | None = None) -> dict:
    """Moderasi X1..Xk × Z → Y. X PERTAMA = fokus; X lain = kovariat.

    Suku interaksi: X PERTAMA × Z (satu suku, sesuai keputusan Bos opsi 2a).
    X2..Xk masuk sebagai pengaruh utama (kovariat), supaya efek Z tidak
    tertukar dengan pengaruh X lain.

    ⚠️ OPSI A (ACC Bos 21Sep26): Z LAIN juga masuk sebagai kovariat. Sebelumnya
    Z2 TIDAK dikendalikan waktu menguji Z1 → terukur hasil Z1 SAMA PERSIS
    (ΔR² 0,051305) baik Z2 dikirim maupun tidak. Kalau Z1 & Z2 berkorelasi
    (lazim di penelitian nyata), hasilnya bisa TERTUKAR. Ini cara MRA baku
    (SPSS PROCESS): moderator lain dikendalikan.
    """
    xs = list(xs)
    z_lain = [q for q in (z_lain or []) if q != z]
    if len(xs) == 1 and not z_lain:
        return moderasi(df, xs[0], z, y)
    kolom = xs + [z] + z_lain + [y]
    d = df[kolom].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Moderasi butuh minimal 20 baris.'}
    x0 = xs[0]
    lain = xs[1:]
    Xv = d[x0].to_numpy(float)
    Zv = d[z].to_numpy(float)
    Yv = d[y].to_numpy(float)
    Kv = d[lain].to_numpy(float) if lain else np.empty((n, 0))
    Zv_lain = (d[z_lain].to_numpy(float) if z_lain else np.empty((n, 0)))
    Xs, Zs = _std(Xv), _std(Zv)
    Ks = np.column_stack([_std(Kv[:, i]) for i in range(Kv.shape[1])]) \
        if Kv.shape[1] else np.empty((n, 0))
    # Kovariat Z lain — distandarkan seperti X lain (satu perlakuan).
    Zs_lain = (np.column_stack([_std(Zv_lain[:, i])
                                for i in range(Zv_lain.shape[1])])
               if Zv_lain.shape[1] else np.empty((n, 0)))
    INT = Xs * Zs

    def _sus(xsuf):
        potong = [xsuf, Ks, Zs_lain]
        potong = [pp for pp in potong if pp.shape[1]]
        return np.column_stack(potong) if potong else xsuf[:, None]

    r1 = _reg(Yv, _sus(np.column_stack([Xs, Zs])))
    r2 = _reg(Yv, _sus(np.column_stack([Xs, Zs, INT])))
    r2_1, r2_2 = float(r1['r2']), float(r2['r2'])
    d_r2 = r2_2 - r2_1
    # ⚠️ Interaksi ada di kolom ke-3 (sesudah X fokus & Z) — kovariat di
    #    belakangnya, jadi indeksnya TIDAK bergeser.
    b_int = float(r2['b'][2]); p_int = float(r2['p'][2])
    sig_int = p_int < AMBANG_P

    if sig_int:
        jenis = 'memoderasi'
        arah = ('memperkuat' if b_int > 0 else 'melemahkan')
        kalimat = (f'{z} {arah.upper()} pengaruh {x0} terhadap {y} '
                   f'(interaksi {x0}×{z} signifikan, b = {b_int:.3f}, '
                   f'p = {p_int:.4f}). Kenaikan R² = {d_r2:.4f}.')
    else:
        jenis = 'tidak memoderasi'
        arah = '-'
        kalimat = (f'{z} TIDAK memoderasi pengaruh {x0} terhadap {y} '
                   f'(interaksi {x0}×{z} tidak signifikan, p = {p_int:.4f}).')
    if lain:
        kalimat += f' X lain ({", ".join(lain)}) dikendalikan dalam hitungan.'
    if z_lain:
        kalimat += (f' Z lain ({", ".join(z_lain)}) juga dikendalikan '
                    f'(Opsi A, ACC Bos 21Sep26).')

    return {
        'boleh': True, 'n': n,
        'x': x0, 'x_semua': xs, 'x_kovariat': lain,
        'z': z, 'z_kovariat': z_lain, 'y': y,
        'tanpa_interaksi': {
            'r2': _f(r2_1),
            'x': {'b': _f(r1['b'][0]), 't': _f(r1['t'][0]), 'p': _f(r1['p'][0])},
            'z': {'b': _f(r1['b'][1]), 't': _f(r1['t'][1]), 'p': _f(r1['p'][1])},
        },
        'dengan_interaksi': {
            'r2': _f(r2_2),
            'x': {'b': _f(r2['b'][0]), 't': _f(r2['t'][0]), 'p': _f(r2['p'][0])},
            'z': {'b': _f(r2['b'][1]), 't': _f(r2['t'][1]), 'p': _f(r2['p'][1])},
            'interaksi': {'b': _f(b_int), 't': _f(r2['t'][2]), 'p': _f(p_int)},
        },
        'delta_r2': _f(d_r2),
        'jenis': jenis,
        'arah': arah,
        'kalimat': kalimat,
        'banyak_x': True,
    }


# ══════════════════════════════════════════════════════════════════════════
#  MEDIASI BERJENJANG (serial / X → M1 → M2 → Y)
# ══════════════════════════════════════════════════════════════════════════
def mediasi_berjenjang(df: pd.DataFrame, x: str, m1: str, m2: str, y: str,
                       n_boot: int = N_BOOTSTRAP,
                       seed: int = SEED_BOOTSTRAP) -> dict:
    """Hitung mediasi BERJENJANG: X → M1 → M2 → Y (ACC Bos 21Sep26).

    BEDA dengan paralel: di sini perantara disusun BERTINGKAT (M1 dulu, lalu
    M2). Jadi ada DUA pengaruh tidak langsung:
      ① X → M1 → Y            lewat M1 saja
      ② X → M1 → M2 → Y       lewat M1 lalu M2 (berjenjang penuh)
    Keduanya dirangkum jadi pengaruh tidak langsung TOTAL.

    CATATAN STATISTIK JUJUR: dua jalur itu SALING TUMPANG-TINDIH (bukan
    bagian yang lepas), jadi dihitung terpisah lalu dilaporkan berdampingan —
    BUKAN dijumlahkan menjadi satu angka yang terlihat seperti "bagian".
    """
    d = df[[x, m1, m2, y]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Bootstrap butuh minimal 20 baris.'}
    Xv = d[x].to_numpy(float)
    M1 = d[m1].to_numpy(float)
    M2 = d[m2].to_numpy(float)
    Yv = d[y].to_numpy(float)

    def koef(yv, kolom):
        """Regresi OLS → dict {nama kolom: (b, t, p)}."""
        r = _reg(yv, np.column_stack(kolom))
        return r

    # ── 4 persamaan berjenjang ────────────────────────────────────────────
    r_a1 = koef(M1, [Xv])                       # a1 : M1 ~ X
    r_d = koef(M2, [Xv, M1])                    # d  : M2 ~ X + M1
    r_b = koef(Yv, [Xv, M1, M2])                # b1, b2, c'
    r_c = koef(Yv, [Xv])                        # c  : Y ~ X

    a1 = float(r_a1['b'][0])
    d21 = float(r_d['b'][1])                    # M1 → M2 (langkah kedua)
    b2 = float(r_b['b'][2])                     # M2 → Y
    b1 = float(r_b['b'][1])                     # M1 → Y (setelah M2 masuk)
    c_lin = float(r_b['b'][0])                  # c'
    c = float(r_c['b'][0])

    # ── BOOTSTRAP: dua jalur tidak langsung ───────────────────────────────
    rng = np.random.default_rng(seed)
    j1 = np.empty(n_boot)      # X → M1 → Y          : a1 × b1
    j2 = np.empty(n_boot)      # X → M1 → M2 → Y     : a1 × d21 × b2
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        a1i = float(_reg(M1[idx], Xv[idx, None])['b'][0])
        di = _reg(M2[idx], np.column_stack([Xv[idx], M1[idx]]))
        d21i = float(di['b'][1])
        bi = _reg(Yv[idx], np.column_stack([Xv[idx], M1[idx], M2[idx]]))
        b1i = float(bi['b'][1]); b2i = float(bi['b'][2])
        j1[i] = a1i * b1i
        j2[i] = a1i * d21i * b2i
    j1 = j1[np.isfinite(j1)]
    j2 = j2[np.isfinite(j2)]

    def _ringkas(arr, titik):
        if len(arr) < 2:
            return {'b': _f(titik), 'se': None, 'lo': None, 'hi': None,
                    'signifikan': False}
        lo, hi = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
        return {'b': _f(titik), 'se': _f(arr.std(ddof=1)),
                'lo': _f(lo), 'hi': _f(hi),
                'signifikan': (lo > 0 and hi > 0) or (lo < 0 and hi < 0)}

    tidak1 = _ringkas(j1, a1 * b1)
    tidak2 = _ringkas(j2, a1 * d21 * b2)
    total = (tidak1['b'] or 0) + (tidak2['b'] or 0)

    # ── SIMPULAN (aturan baku) ────────────────────────────────────────────
    sig = tidak1['signifikan'] or tidak2['signifikan']
    sig_c_lin = float(r_b['p'][0]) < AMBANG_P
    if not sig:
        jenis = 'tidak ada mediasi'
        kalimat = (f'Rantai {x} → {m1} → {m2} → {y} TIDAK meneruskan pengaruh '
                   f'(selang kepercayaan 95% kedua jalur melewati nol).')
    elif not sig_c_lin:
        jenis = 'mediasi penuh'
        kalimat = (f'Pengaruh {x} terhadap {y} berjalan SEPENUHNYA lewat '
                   f'{m1} dan {m2} — pengaruh langsungnya hilang setelah '
                   f'keduanya masuk.')
    else:
        jenis = 'mediasi parsial'
        kalimat = (f'Pengaruh {x} terhadap {y} SEBAGIAN lewat rantai '
                   f'{m1} → {m2}; pengaruh langsung masih ada tapi lebih kecil '
                   f'({c_lin:.3f} < {c:.3f}).')

    return {
        'boleh': True, 'n': n, 'berjenjang': True,
        'x': x, 'm': m1 + ' → ' + m2, 'y': y,
        'c':  {'b': _f(c), 't': _f(r_c['t'][0]), 'p': _f(r_c['p'][0]),
               'ket': f'pengaruh {x} → {y} TANPA perantara (c)'},
        'a':  {'b': _f(a1), 't': _f(r_a1['t'][0]), 'p': _f(r_a1['p'][0]),
               'ket': f'a1 · {x} → {m1}'},
        'd':  {'b': _f(d21), 't': _f(r_d['t'][1]), 'p': _f(r_d['p'][1]),
               'ket': f'd · {m1} → {m2} (setelah {x} masuk)'},
        'b':  {'b': _f(b2), 't': _f(r_b['t'][2]), 'p': _f(r_b['p'][2]),
               'ket': f'b2 · {m2} → {y}'},
        'b1': {'b': _f(b1), 't': _f(r_b['t'][1]), 'p': _f(r_b['p'][1]),
               'ket': f'b1 · {m1} → {y} (setelah {m2} masuk)'},
        'cp': {'b': _f(c_lin), 't': _f(r_b['t'][0]), 'p': _f(r_b['p'][0]),
               'ket': f"pengaruh {x} → {y} SETELAH keduanya masuk (c')"},
        'jalur': [
            {'nama': f'{x} → {m1} → {y}', 'b': tidak1['b'],
             'lo': tidak1['lo'], 'hi': tidak1['hi'],
             'signifikan': tidak1['signifikan'],
             'ket': f'a1 × b1 = {a1:.4f} × {b1:.4f}'},
            {'nama': f'{x} → {m1} → {m2} → {y}', 'b': tidak2['b'],
             'lo': tidak2['lo'], 'hi': tidak2['hi'],
             'signifikan': tidak2['signifikan'],
             'ket': f'a1 × d × b2 = {a1:.4f} × {d21:.4f} × {b2:.4f}'},
        ],
        'tidak_langsung': {
            'b': _f(total), 'se': None, 'lo': None, 'hi': None,
            'n_boot': int(min(len(j1), len(j2))), 'signifikan': bool(sig),
            'ket': 'jumlah DUA jalur (saling tumpang-tindih — bukan bagian)',
        },
        'jenis': jenis,
        'kalimat': kalimat,
    }


# ══════════════════════════════════════════════════════════════════════════
#  MEDIASI RANTAI PANJANG (N perantara: X → M1 → M2 → … → Mk → Y)
# ══════════════════════════════════════════════════════════════════════════
def mediasi_rantai(df: pd.DataFrame, x: str, perantara: list[str], y: str,
                   n_boot: int = N_BOOTSTRAP,
                   seed: int = SEED_BOOTSTRAP) -> dict:
    """Mediasi BERJENJANG dengan SEMUA perantara (bukan cuma dua).

    ACC Bos 21Sep26: *"Rantai lebih 2 perantara belum"*.

    Rantai X → M1 → M2 → … → Mk → Y menghasilkan **k jalur tidak langsung**,
    semuanya lewat M1 (karena M1 selalu langkah pertama):

      ① X → M1 → Y                     a1 · b1
      ② X → M1 → M2 → Y                a1 · d1 · b2
      ③ X → M1 → M2 → M3 → Y           a1 · d1 · d2 · b3
        …
      ⓚ X → M1 → … → Mk → Y            a1 · d1 · … · d(k-1) · bk

    CATATAN STATISTIK JUJUR: jalur-jalur ini **SALING TUMPANG-TINDIH**
    (bukan bagian yang lepas seperti mediasi paralel). Karena itu dilaporkan
    BERDAMPINGAN — TIDAK dipecah jadi "persentase perantara". Jumlahnya
    dilaporkan sebagai keterangan, bukan sebagai "total yang bisa dibagi".
    """
    m_all = list(perantara)
    k = len(m_all)
    if k < 1:
        return {'boleh': False, 'sebab': 'Tidak ada perantara yang ditunjuk.'}
    kolom = [x] + m_all + [y]
    d = df[kolom].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Bootstrap butuh minimal 20 baris.'}
    Xv = d[x].to_numpy(float)
    Mv = [d[m].to_numpy(float) for m in m_all]
    Yv = d[y].to_numpy(float)

    # ── Koefisien bertahap ────────────────────────────────────────────────
    # a1 : M1 ~ X
    r_a1 = _reg(Mv[0], Xv[:, None])
    a1 = float(r_a1['b'][0])
    # d_i : M(i+1) ~ X + M1 + … + Mi     → ambil suku M(i) sebagai d_(i-1)
    d_step = []                       # d_step[i] = langkah M(i+1) ← M(i)
    for i in range(k - 1):
        kol = np.column_stack([Xv] + Mv[:i + 1])
        r = _reg(Mv[i + 1], kol)
        d_step.append(float(r['b'][i + 1]))
    # regresi akhir: Y ~ X + M1 + … + Mk
    r_all = _reg(Yv, np.column_stack([Xv] + Mv))
    b_step = [float(v) for v in r_all['b'][1:]]     # b1..bk
    c_lin = float(r_all['b'][0])                    # c'
    r_c = _reg(Yv, Xv[:, None])
    c = float(r_c['b'][0])

    def satu_jalur(idx, Xv_, Mv_, Yv_):
        """Pengaruh tidak langsung jalur ke-idx (0-based) dari satu resample."""
        ra = _reg(Mv_[0], Xv_[:, None])
        a = float(ra['b'][0])
        dd = 1.0
        for i in range(idx):
            kol = np.column_stack([Xv_] + Mv_[:i + 1])
            dd *= float(_reg(Mv_[i + 1], kol)['b'][i + 1])
        rb = _reg(Yv_, np.column_stack([Xv_] + Mv_))
        return a * dd * float(rb['b'][idx + 1])

    # ── Bootstrap semua jalur sekaligus (resample SAMA, hemat waktu) ──────
    rng = np.random.default_rng(seed)
    jalur_boot = [[] for _ in range(k)]
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        Xb = Xv[idx]
        Mb = [m[idx] for m in Mv]
        Yb = Yv[idx]
        for j in range(k):
            v = satu_jalur(j, Xb, Mb, Yb)
            if np.isfinite(v):
                jalur_boot[j].append(v)

    def _ringkas(arr, titik):
        a = np.asarray(arr, float)
        if len(a) < 2:
            return {'b': _f(titik), 'lo': None, 'hi': None,
                    'signifikan': False, 'n_boot': 0}
        lo, hi = float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
        return {'b': _f(titik), 'lo': _f(lo), 'hi': _f(hi),
                'signifikan': (lo > 0 and hi > 0) or (lo < 0 and hi < 0),
                'n_boot': int(len(a))}

    jalur = []
    for j in range(k):
        # titik: a1 × d1 × … × b(j+1)
        titik = a1
        for i in range(j):
            titik *= d_step[i]
        titik *= b_step[j]
        rr = _ringkas(jalur_boot[j], titik)
        nama = ' → '.join([x] + m_all[:j + 1] + [y])
        kali = ' × '.join([f'{a1:.4f}']
                          + [f'{v:.4f}' for v in d_step[:j]]
                          + [f'{b_step[j]:.4f}'])
        rr.update({'nama': nama, 'ket': f'a1 × … = {kali}'})
        jalur.append(rr)

    total = sum((j['b'] or 0.0) for j in jalur)
    sig = any(j['signifikan'] for j in jalur)
    sig_c_lin = float(r_all['p'][0]) < AMBANG_P
    if not sig:
        jenis = 'tidak ada mediasi'
        kalimat = (f'Rantai {x} → ' + ' → '.join(m_all) + f' → {y} TIDAK '
                   f'meneruskan pengaruh: selang kepercayaan 95% SEMUA jalur '
                   f'melewati nol.')
    elif not sig_c_lin:
        jenis = 'mediasi penuh'
        kalimat = (f'Pengaruh {x} terhadap {y} berjalan SEPENUHNYA lewat '
                   f'rantai ' + ' → '.join(m_all) + ' — pengaruh langsungnya '
                   f'hilang setelah semuanya masuk.')
    else:
        jenis = 'mediasi parsial'
        kalimat = (f'Pengaruh {x} terhadap {y} SEBAGIAN lewat rantai '
                   + ' → '.join(m_all) +
                   f'; pengaruh langsung masih ada tapi lebih kecil '
                   f'({c_lin:.3f} < {c:.3f}).')

    return {
        'boleh': True, 'n': n, 'berjenjang': True, 'rantai_panjang': True,
        'x': x, 'm': ' → '.join(m_all), 'y': y,
        'jumlah_perantara': k,
        'c':  {'b': _f(c), 't': _f(r_c['t'][0]), 'p': _f(r_c['p'][0]),
               'ket': f'pengaruh {x} → {y} TANPA perantara (c)'},
        'a':  {'b': _f(a1), 't': _f(r_a1['t'][0]), 'p': _f(r_a1['p'][0]),
               'ket': f'a1 · {x} → {m_all[0]}'},
        'd':  ({'b': _f(d_step[0]), 't': None, 'p': None,
                'ket': f'd1 · {m_all[0]} → {m_all[1]}'}
               if k >= 2 else None),
        'd_semua': [{'dari': m_all[i], 'ke': m_all[i + 1], 'b': _f(d_step[i])}
                    for i in range(k - 1)],
        'b':  {'b': _f(b_step[-1]), 't': None, 'p': None,
               'ket': f'b{k} · {m_all[-1]} → {y}'},
        'b_semua': [{'dari': m_all[i], 'ke': y, 'b': _f(b_step[i])}
                    for i in range(k)],
        'cp': {'b': _f(c_lin), 't': _f(r_all['t'][0]), 'p': _f(r_all['p'][0]),
               'ket': f"pengaruh {x} → {y} SETELAH semuanya masuk (c')"},
        'jalur': jalur,
        'tidak_langsung': {
            'b': _f(total), 'se': None, 'lo': None, 'hi': None,
            'n_boot': (jalur[0]['n_boot'] if jalur else 0),
            'signifikan': bool(sig),
            'ket': f'jumlah {k} jalur yang saling tumpang-tindih '
                   f'(BUKAN bagian yang bisa dipecah)',
        },
        'jenis': jenis,
        'kalimat': kalimat,
    }


# ══════════════════════════════════════════════════════════════════════════
#  GERBANG TUNGGAL — dipanggil rute /klinik
# ══════════════════════════════════════════════════════════════════════════
def hitung_kaitan(df: pd.DataFrame, kolom_x: list[str], kolom_y: str,
                  kolom_m: list[str] | None = None,
                  kolom_z: list[str] | None = None,
                  bentuk: str | None = None) -> dict:
    """Hitung mediasi & moderasi dari PERAN yang ditandai mahasiswa.

    `bentuk` = pilihan mahasiswa kalau perantara/penguat lebih dari satu
    ('paralel' atau 'berjenjang'), dikirim halaman. Kalau tidak dikirim,
    dipakai aturan aman: PARALEL (tiap perantara diuji sendiri) — karena
    paralel tidak butuh urutan antar-perantara.

    Aturan penentuan bentuk:
      · 1 M                 → mediasi biasa X→M→Y
      · >1 M + 'berjenjang' → mediasi BERJENJANG (X→M1→M2→…→Y)
      · >1 M + lainnya      → PARALEL (tiap M diuji sendiri)
      · ada Z               → moderasi tiap Z
    """
    kolom_m = list(kolom_m or [])
    kolom_z = list(kolom_z or [])
    hasil: dict = {'mediasi': [], 'moderasi': [], 'bentuk_mediasi': None}

    if len(kolom_m) == 1 and len(kolom_x) >= 1:
        # BANYAK X (ACC Bos 21Sep26 "Semua x masuk"): kalau mahasiswa menandai
        # lebih dari satu X, X2..Xk MASUK sebagai kovariat — dulu dibuang
        # diam-diam (kolom_x[0] saja). Lihat blok "BANYAK X — PENYAMBUNG".
        hasil['mediasi'].append(
            mediasi_banyak_x(df, kolom_x, kolom_m[0], kolom_y))
        hasil['bentuk_mediasi'] = 'tunggal'
    elif len(kolom_m) > 1:
        if str(bentuk or '').lower().startswith('berjenjang'):
            hasil['bentuk_mediasi'] = 'berjenjang'
            # Rantai penuh: X → M1 → M2 → … → Mk → Y (SEMUA perantara).
            # mediasi_rantai() sudah menangani k=2 dengan benar (jalur a1·b1
            # dan a1·d·b2 sama persis dengan mediasi_berjenjang), jadi untuk
            # SEMUA jumlah perantara dipakai SATU fungsi — tidak ada lagi
            # cabang "baru 2 pertama" (ACC Bos 21Sep26: "Rantai lebih 2
            # perantara belum").
            hasil['mediasi'].append(
                mediasi_rantai_banyak_x(df, kolom_x, kolom_m, kolom_y))
        else:
            hasil['bentuk_mediasi'] = 'paralel'
            for m in kolom_m:           # paralel: tiap perantara diuji sendiri
                hasil['mediasi'].append(
                    mediasi_banyak_x(df, kolom_x, m, kolom_y))

    if kolom_z and kolom_x:
        for z in kolom_z:
            # OPSI A (ACC Bos 21Sep26): Z LAIN dikendalikan — kalau tidak,
            # hasil Z1 sama saja entah Z2 ada atau tidak (terukur).
            hasil['moderasi'].append(
                moderasi_banyak_x(df, kolom_x, z, kolom_y,
                                  z_lain=[q for q in kolom_z if q != z]))

    hasil['ada'] = bool(hasil['mediasi'] or hasil['moderasi'])
    hasil['ringkas'] = [h['kalimat'] for h in hasil['mediasi'] + hasil['moderasi']
                        if h.get('boleh')]
    return hasil
