"""UJI F + TABEL ANOVA - dibandingkan dengan KEBENARAN LUAR (scipy).

AKAR YANG DITUTUP 21Sep26: versi pertama uji ini HANYA memeriksa keajegan
internal (SS_regresi + SS_residu = SS_total, MS = SS/df, F = MS/MS). Uji
seperti itu **BUTA** - kalau rumusnya dibalik (MS_residu/MS_regresi) atau
df-nya salah, semua hubungan internal TETAP konsisten. Terbukti: 4 suntikan
kerusakan LOLOS semua (lihat _sketsa/bukti_uji_f_gagal.py).

PERBAIKAN DI AKAR: hitung F & p dari SUMBER INDEPENDEN memakai statistik
library (scipy), lalu bandingkan dengan keluaran mesin. Sumber luar tidak
ikut rusak waktu mesin disuntik -> kerusakan PASTI tertangkap.

Dipakai sebagai bukti Langkah 2 keputusan 21Sep26 (ACC Bos).
"""
import sys
from pathlib import Path

# ⚠️ JEBAKAN TERBUKTI (21Sep26) — JANGAN pakai jalur ABSOLUT di sini.
# Versi pertama uji ini menulis sys.path.insert(0, '/opt/data/services/...')
# -> saat dijalankan dari SALINAN tersuntik, uji tetap membaca berkas ASLI
# -> 4 suntikan kerusakan LOLOS (uji tampak buta padahal uji benar).
# Benar: ambil jalur dari LOKASI BERKAS INI (ikut pindah ke salinan).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy import stats
from app.berkas_kerja import buat_data, uji_f

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  OK   {nama}')
    else:
        GAGAL += 1
        print(f'  GAGAL {nama}  {bukti}')


def benar_luar(X, y):
    """F & p & R2 dari SUMBER INDEPENDEN (numpy lstsq + scipy.f).

    Sengaja TIDAK memakai fungsi apa pun dari app/ - supaya kalau app/
    disuntik kerusakan, angka pembanding ini TETAP benar.
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float).ravel()
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    n, k = X.shape
    Xz = (X - X.mean(0)) / X.std(0, ddof=1)
    yz = (y - y.mean()) / y.std(ddof=1)
    A = np.column_stack([Xz, np.ones(n)])
    b = np.linalg.lstsq(A, yz, rcond=None)[0]
    resid = yz - A @ b
    sst = float(np.sum((yz - yz.mean()) ** 2))
    sse = float(np.sum(resid ** 2))
    ssr = sst - sse
    df1, df2 = k, n - k - 1
    ms1, ms2 = ssr / df1, sse / df2
    F = ms1 / ms2
    p = float(1 - stats.f.cdf(F, df1, df2))
    return dict(F=F, p=p, r2=ssr / sst, ssr=ssr, sse=sse, sst=sst,
                df1=df1, df2=df2, ms1=ms1, ms2=ms2)


def skor(r):
    """Ambil matriks skor dari keluaran buat_data."""
    d = r['data']
    return np.column_stack([d['item'][nm].sum(axis=1).astype(float)
                            for nm in d['item']])


print('=' * 74)
print(' UJI F + TABEL ANOVA - dibandingkan KEBENARAN LUAR (scipy)')
print('=' * 74)

for x, cara, nm in [(1, 'sederhana', 'Sederhana 1X'),
                    (3, 'sederhana', 'Parsial 3X'),
                    (3, 'berganda', 'Berganda 3X'),
                    (3, 'berantai', 'Berantai 3X'),
                    (5, 'berganda', 'Berganda 5X'),
                    (8, 'berganda', 'Berganda 8X')]:
    beta_x = [0.30] * x if x <= 5 else [0.12] * x
    r = buat_data(n=200, x=x, beta=beta_x, mode='presisi', seed=777,
                  cara=cara)
    f = r['f']
    Sk = skor(r)
    luar = benar_luar(Sk[:, :x], Sk[:, -1])

    print(f'\n-- {nm} --')
    cek(f'{nm}: uji F BISA dihitung', f.get('bisa') is True, str(f.get('sebab')))
    if not f.get('bisa'):
        continue

    print(f'     mesin: F={f["F"]:.4f} p={f["p"]:.6e} R2={f["r2"]:.6f} '
          f'df=({f["df_regresi"]},{f["df_residu"]})')
    print(f'     LUAR : F={luar["F"]:.4f} p={luar["p"]:.6e} R2={luar["r2"]:.6f} '
          f'df=({luar["df1"]},{luar["df2"]})')

    # ── BANDINGKAN DENGAN SUMBER LUAR (inti gigi uji) ──
    cek(f'{nm}: F mesin == F luar',
        abs(f['F'] - luar['F']) < 1e-6, f"{f['F']} vs {luar['F']}")
    cek(f'{nm}: p mesin == p luar',
        abs(f['p'] - luar['p']) < 1e-9, f"{f['p']} vs {luar['p']}")
    cek(f'{nm}: R2 mesin == R2 luar',
        abs(f['r2'] - luar['r2']) < 1e-9, f"{f['r2']} vs {luar['r2']}")
    cek(f'{nm}: SS regresi mesin == luar',
        abs(f['ss_regresi'] - luar['ssr']) < 1e-6)
    cek(f'{nm}: SS residu mesin == luar',
        abs(f['ss_residu'] - luar['sse']) < 1e-6)
    cek(f'{nm}: df mesin == luar',
        f['df_regresi'] == luar['df1'] and f['df_residu'] == luar['df2'],
        f"({f['df_regresi']},{f['df_residu']}) vs ({luar['df1']},{luar['df2']})")
    cek(f'{nm}: MS regresi mesin == luar',
        abs(f['ms_regresi'] - luar['ms1']) < 1e-6)
    cek(f'{nm}: MS residu mesin == luar',
        abs(f['ms_residu'] - luar['ms2']) < 1e-6)

    # ── keajegan internal (tetap diperiksa, TAPI bukan satu-satunya) ──
    cek(f'{nm}: SS regresi + SS residu = SS total',
        abs(f['ss_regresi'] + f['ss_residu'] - f['ss_total']) < 1e-9)
    cek(f'{nm}: tabel ANOVA 3 baris', len(f['tabel']) == 3)
    cek(f'{nm}: R2 uji F == R2 mesin', abs(f['r2'] - r['r2']) < 1e-9)
    cek(f'{nm}: f_terpisah ada {x} buah', len(r['f_terpisah']) == x)

    # ── uji F per-X (parsial) juga dibandingkan luar ──
    for i in range(x):
        fp = r['f_terpisah'][i]
        lp = benar_luar(Sk[:, [i]], Sk[:, -1])
        cek(f'{nm}: F parsial X{i+1} == luar',
            abs(fp['F'] - lp['F']) < 1e-6, f"{fp['F']} vs {lp['F']}")

# ── 1 X: uji F harus SAMA dengan t^2 (hukum statistik) ──
r = buat_data(n=200, x=1, beta=[0.40], mode='presisi', seed=11, cara='sederhana')
t1 = r['terpisah'][0]['t']
F1 = r['f']['F']
cek('1 X: F == t^2 (hukum statistik)', abs(F1 - t1 ** 2) < 1e-6,
    f'F={F1} t^2={t1**2}')

print('\n' + '=' * 74)
print(f'  {"LULUS SEMUA" if GAGAL == 0 else "ADA GAGAL"}: '
      f'{LULUS} lulus / {GAGAL} gagal')
print('=' * 74)
sys.exit(0 if GAGAL == 0 else 1)
