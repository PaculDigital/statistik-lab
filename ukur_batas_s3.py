#!/usr/bin/env python3
"""UKUR BATAS OPTIMAL S3 BERGANDA-BERANTAI — dari jumlah X ke galat.

PERTANYAAN BOS (18Sep26): "Kenapa cuma sampai 3 variabel, berapa optimalnya?"

Yang diukur BUKAN tebakan: untuk tiap jumlah X (2..8) dan tiap tingkat
kekuatan rantai, jalankan mesin lalu CATAT galat maksimumnya.

Dibagi dua blok karena keduanya beda sifat:
  · RANTAI  (X1→X2→…): selalu sempurna (galat ~0,0003) di semua jumlah X
  · X→Y    (berganda) : inilah yang MENDESAK saat X banyak
"""
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from app.berkas_kerja import buat_data          # noqa: E402

N = 400
BARIS = []


def uji(x, beta_tiap, rantai):
    """beta_tiap = koefisien tiap X ke Y. rantai = kekuatan rantai."""
    beta = [beta_tiap] * x
    jml = sum(beta)
    try:
        d = buat_data(n=N, x=x, beta=beta, skala=5, alpha=0.85,
                      mode='presisi', cara='berantai', seed=7)
        # pisahkan galat dua bagian
        g_y = max(abs(j['terbaca'] - j['diminta']) for j in d['bersama'])
        g_r = (max(abs(j['terbaca'] - rantai) for j in d['rantai'])
               if d['rantai'] else 0.0)
        return dict(ok=True, x=x, jml=jml, g_y=g_y, g_r=g_r,
                    galat=d['galat_maks'])
    except ValueError as e:
        return dict(ok=False, x=x, jml=jml, pesan=str(e)[:60], g_y=None,
                    g_r=None, galat=None)


print("=" * 78)
print("PETA BATAS: galat X->Y menurut jumlah X dan tingkat kekuatan rantai")
print(f"(n={N}, mode presisi, alpha=0.85, tiap X diminta sama besar)")
print("=" * 78)
print(f"{'rantai':>7} | " + " | ".join(f"x={x}" for x in range(2, 9)))
print("-" * 78)

for rantai in (0.30, 0.45, 0.55, 0.65, 0.75):
    sel = []
    for x in range(2, 9):
        # cari beta ketiga yang MASIH bisa dipaksa persis untuk x ini
        hasil = None
        for b in (0.30, 0.25, 0.20, 0.15, 0.10):
            h = uji(x, b, rantai)
            if h['ok'] and h['g_y'] is not None and h['g_y'] <= 0.03:
                hasil = f"b={b:.2f}:OK"
                break
            if h['ok'] and h['g_y'] is not None:
                hasil = f"b={b:.2f}:{h['g_y']:.3f}"
        if hasil is None:
            hasil = "TOLAK"
        sel.append(f"{hasil:>9}")
        BARIS.append((rantai, x, hasil))
    print(f"{rantai:>7.2f} | " + " | ".join(sel))

print()
print("=" * 78)
print("PEMBANDING: cara BERGANDAlah yang menentukan (rantai selalu sempurna)")
print("=" * 78)
print(f"{'rantai':>7} | {'X':>3} | {'galat X->Y':>10} | {'galat rantai':>12}")
print("-" * 78)
for rantai in (0.00, 0.55):
    for x in (3, 4, 5, 8):
        h = uji(x, 0.20, rantai)
        if h['ok']:
            print(f"{rantai:>7.2f} | {x:>3} | {h['g_y']:>10.4f} | "
                  f"{h['g_r']:>12.4f}")
        else:
            print(f"{rantai:>7.2f} | {x:>3} | {'DITOLAK':>10} | "
                  f"{h['pesan']}")

print()
print("=" * 78)
print("CATATAN: rantai=0.00 artinya TANPA rantai (=regresi berganda murni).")
print("Bandingkan baris rantai=0.00 vs 0.55 untuk melihat pengaruh rantai.")
print("=" * 78)
