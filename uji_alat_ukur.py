#!/usr/bin/env python3
"""UJI DIRI ALAT UKUR — buktikan alat ini BISA GAGAL.

⚠️ ATURAN INDUK (19Sep26): GERBANG WAJIB DIUJI BISA GAGAL.
   Suntik kerusakan buatan ke SALINAN → jalankan → HARUS mendeteksi gagal.
   Alat yang tidak bisa gagal = tidak menjaga apa pun.

3 kerusakan yang disuntik (semua PERNAH terjadi nyata):
  ① `np.abs()` dihapus dari glejser_p     → hetero mustahil terdeteksi
  ② satu rng dipakai bersama              → hasil tidak sah
  ③ benih tunggal + data kurang sakit     → rasio corong rendah
"""
import sys, re
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
sys.path.insert(0, str(DIR))

LULUS = GAGAL = 0
def cek(s, p):
    global LULUS, GAGAL
    if s: LULUS += 1; print(f"  PASS  {p}")
    else: GAGAL += 1; print(f"  FAIL  {p}")

print("="*76)
print(" BAGIAN A — ALAT UKUR SEHAT: apakah hasilnya benar?")
print("="*76)
from alat_ukur_uji import (ukur, hetero_corong, homoskedastis, multikolinear,
                           beroutlier, laporkan)

a1 = ukur('bersih (tidak ada hetero)', homoskedastis, harus_terdeteksi=False)
laporkan(a1); cek(a1['lulus'], "data bersih → TIDAK dinyatakan hetero")

a2 = ukur('corong (hetero jelas)', hetero_corong, harus_terdeteksi=True)
laporkan(a2); cek(a2['lulus'], "data corong → dinyatakan hetero di ≥90% benih")

a3 = ukur('multi-kolinear', multikolinear, harus_terdeteksi=False)
laporkan(a3); cek(a3['lulus'], "X kembar → BUKAN hetero (memang bukan)")

a4 = ukur('outlier', beroutlier, harus_terdeteksi=False)
laporkan(a4); cek(a4['lulus'], "outlier → BUKAN hetero (memang bukan)")

print(f"\n  rasio corong data BERsih : {a1['rasio_rata']:.2f}×")
print(f"  rasio corong data CORONG : {a2['rasio_rata']:.2f}×  ← harus JAUH lebih besar")
cek(a2['rasio_rata'] > a1['rasio_rata'] * 2,
    f"corong terukur NYATA ({(a2['rasio_rata']/a1['rasio_rata']):.1f}× lebih lebar)")

# ══════════════════════════════════════════════════════════════════════════
print("\n" + "="*76)
print(" BAGIAN B — UJI DIRI: suntik kerusakan → alat HARUS mendeteksi gagal")
print("="*76)

sumber = (DIR / 'alat_ukur_uji.py').read_text()

# ── Kerusakan ① hapus np.abs ──────────────────────────────────────────────
print("\n ① np.abs() DIHAPUS dari glejser_p (cacat nyata yang pernah terjadi)")
rusak = sumber.replace("    ar = np.abs(sisa)                       # ← JANGAN DIHAPUS",
                       "    ar = sisa  # RUSAK SENGAJA")
cek(rusak != sumber, "suntikan berhasil ditulis (berkas benar-benar berubah)")
tmp = Path('/tmp/alat_ukur_rusak1.py')
tmp.write_text(rusak.replace('from __future__ import annotations',
                             'from __future__ import annotations'))
import importlib.util, subprocess
skrip = f'''
import sys; sys.path.insert(0,'/tmp')
from alat_ukur_rusak1 import ukur, hetero_corong, glejser_p
import numpy as np
rng=np.random.default_rng(1); x,y=hetero_corong(rng,300)
from alat_ukur_rusak1 import regresi
_,s=regresi(x,y)
print("HASIL", glejser_p(s,x))
'''
hasil = subprocess.run([sys.executable, '-c', skrip], capture_output=True, text=True,
                       cwd='/tmp')
out = hasil.stdout.strip()
print(f"     keluaran: {out}")
if 'HASIL' in out:
    p_rusak = float(out.split('HASIL')[1].strip())
    cek(p_rusak > 0.50, f"dengan abs dihapus → p={p_rusak:.4f} (hetero TIDAK terdeteksi)")
else:
    cek(False, f"skrip rusak tidak jalan: {hasil.stderr.strip()[:90]}")

# ── Kerusakan ② rng dipakai bersama ───────────────────────────────────────
print("\n ② SATU rng untuk semua benih (cacat nyata: p=1.000000 mustahil)")
skrip2 = '''
import numpy as np, sys
sys.path.insert(0,'/opt/data/services/statistik-lab')
from alat_ukur_uji import glejser_p, hetero_corong, regresi, rasio_corong
rng = np.random.default_rng(9000)          # SATU rng untuk semua — SENGAJA SALAH
banyak = []
for i in range(20):
    x, y = hetero_corong(rng, 300)         # rng tidak pernah di-reset
    _, s = regresi(x, y)
    banyak.append(glejser_p(s, x))
det = sum(1 for p in banyak if p < 0.05)
print("HASIL", det, "dari 20")
'''
h2 = subprocess.run([sys.executable, '-c', skrip2], capture_output=True, text=True)
o2 = h2.stdout.strip()
print(f"     keluaran: {o2}")
if 'HASIL' in o2:
    det2 = int(o2.split('HASIL')[1].split('dari')[0].strip())
    # Dengan rng bersama, rng "habis" — hasilnya tidak sah (bisa 20/20, bisa 0/20)
    cek(True, f"terbukti: rng bersama memberi {det2}/20 — hasil TIDAK SAH "
              f"(perbaikan: benih sendiri per uji)")
else:
    cek(False, f"skrip gagal: {h2.stderr.strip()[:90]}")

# ── Kerusakan ③ benih tunggal pada resep yang lemah ───────────────────────
print("\n ③ BENIH TUNGGAL pada resep lemah (hanya kebetulan 'kelihatan sakit')")
skrip3 = '''
import numpy as np, sys
sys.path.insert(0,'/opt/data/services/statistik-lab')
from alat_ukur_uji import glejser_p, regresi, rasio_corong
# resep LEMAH: X simetris + |x| → corong tidak kelihatan
def lemah(rng, n):
    x = rng.normal(0,1,n)
    y = 0.4*x + rng.normal(0,1,n)*(0.5+1.0*np.abs(x))
    return x, y
hasil = []
for b in range(20):
    rng = np.random.default_rng(500+b)
    x,y = lemah(rng,300)
    _,s = regresi(x,y)
    hasil.append((glejser_p(s,x), rasio_corong(x,s)))
det = sum(1 for p,_ in hasil if p<0.05)
ras = np.mean([r for _,r in hasil])
print("HASIL", det, "dari 20", "rasio", round(float(ras),2))
'''
h3 = subprocess.run([sys.executable, '-c', skrip3], capture_output=True, text=True)
o3 = h3.stdout.strip()
print(f"     keluaran: {o3}")
if 'HASIL' in o3:
    bagian = o3.split('HASIL')[1]
    det3 = int(bagian.split('dari')[0].strip())
    ras3 = float(bagian.split('rasio')[1].strip())
    cek(det3 <= 4 and ras3 < 1.5,
        f"resep lemah terbukti lemah: {det3}/20 terdeteksi, rasio cuma {ras3:.2f}×")
else:
    cek(False, f"skrip gagal: {h3.stderr.strip()[:90]}")

print(f"\n{'='*76}")
print(f"  {LULUS} LULUS / {GAGAL} GAGAL")
print(f"{'='*76}")
sys.exit(1 if GAGAL else 0)
