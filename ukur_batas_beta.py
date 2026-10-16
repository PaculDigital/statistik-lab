#!/usr/bin/env python3
"""PETA BATAS beta TOTAL untuk S3 BERGANDA-BERANTAI (Opsi C, ACC Bos 18Sep26).

TUJUAN: cari angka batas yang BERDASAR DATA, bukan tebakan.
Pertanyaan: pada tiap jumlah X, berapa TOTAL beta paling besar yang MASIH
bisa dipaksa persis (galat <= 0,03)?

CARA: sengaja TIDAK memakai buat_data() karena di situ sudah ada pagar;
kita panggil mesin kalibrasi langsung supaya bisa mengukur di luar batas.

⚠️ PELAJARAN 18Sep26: jangan simpulkan dari 1 angka. Ukur MATRIKS
(jumlah X × kekuatan rantai), lalu lihat polanya.
"""
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur   # noqa: E402

N = 400
TOL = 0.03
RANTAI = 0.55


def coba(x, beta_ketiga, rantai=RANTAI, n=N):
    """Jalankan kalibrasi untuk S3 dengan x X, beta sama besar."""
    Xs = [f'X{i+1}' for i in range(x)]
    jalur = [{'target': Xs[i + 1], 'dari': {Xs[i]: rantai}}
             for i in range(x - 1)]
    jalur.append({'target': 'Y', 'dari': {nm: beta_ketiga for nm in Xs}})
    try:
        h = kalibrasi_per_jalur(jalur, n_resp=n, item_per=3, skala=5,
                                toleransi=TOL, maks_putaran=30,
                                lapor=False, seed=7)
        g = h.get('galat') or {}
        g_y = max((abs(v) for k, v in g.items() if k.endswith('->Y')),
                  default=9.9)
        return g_y, h.get('tercapai'), h.get('putaran')
    except Exception as e:                      # noqa: BLE001
        return None, False, str(e)[:50]


print("=" * 76)
print("PETA: beta TERBESAR yang masih bisa dipaksa persis (galat <= 0,03)")
print(f"     rantai={RANTAI}, n={N}, mode kalibrasi")
print("=" * 76)
print(f"{'X':>3} | {'beta maks':>9} | {'TOTAL beta':>10} | {'galat':>8} | "
      f"{'putaran':>7}")
print("-" * 76)

HASIL = {}
for x in range(2, 9):
    terbaik = None
    for b in (0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.12, 0.10):
        g_y, tercapai, put = coba(x, b)
        if g_y is None:
            continue
        if g_y <= TOL:
            terbaik = (b, b * x, g_y, put)
            break
        else:
            terbaik = (b, b * x, g_y, put)   # catat yang gagal juga
    if terbaik:
        b, tot, g, put = terbaik
        tanda = 'OK' if g <= TOL else 'X'
        print(f"{x:>3} | {b:>9.2f} | {tot:>10.2f} | {g:>8.4f} | {str(put):>7} {tanda}")
        HASIL[x] = terbaik

print()
print("=" * 76)
print("KESIMPULAN DARI DATA:")
tots = [v[1] for v in HASIL.values() if v[2] <= TOL]
if tots:
    print(f"  total beta yang BERHASIL: {min(tots):.2f} .. {max(tots):.2f}")
    print(f"  -> batas aman yang diusulkan: {min(tots):.2f}")
print("=" * 76)
