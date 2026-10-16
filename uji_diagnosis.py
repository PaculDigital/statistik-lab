#!/usr/bin/env python3
"""UJI mesin diagnosis — baca 3 format + hitung syarat pada data SAKIT.

⚠️ ATURAN (pelajaran 19Sep26): uji pada target BERSIH **dan** KOTOR.
Data bagus → semua lulus. Data SAKIT → HARUS ADA yang GAGAL.
Kalau data sakit juga "lulus semua" → alat ukurnya buta.
"""
import sys, io
sys.path.insert(0, '/opt/data/services/statistik-lab')
import numpy as np, pandas as pd
from app.diagnosis import baca_berkas, periksa_spss, periksa_pls, MAX_BYTE

LULUS = GAGAL = 0
def cek(syarat, pesan):
    global LULUS, GAGAL
    if syarat: LULUS += 1; print(f"  PASS  {pesan}")
    else:      GAGAL += 1; print(f"  FAIL  {pesan}")

rng = np.random.default_rng(7)

# ══ 1. BACA 3 FORMAT ══════════════════════════════════════════════════════
print("\n── 1. BACA 3 FORMAT ──")
df0 = pd.DataFrame({
    'KP1': rng.integers(1,6,120), 'KP2': rng.integers(1,6,120), 'KP3': rng.integers(1,6,120),
    'H1':  rng.integers(1,6,120), 'H2':  rng.integers(1,6,120),
    'Y1':  rng.integers(1,6,120), 'Y2':  rng.integers(1,6,120),
})
import tempfile, os, pyreadstat
td = tempfile.mkdtemp()
df0.to_csv(f'{td}/d.csv', index=False)
df0.to_excel(f'{td}/d.xlsx', index=False)
pyreadstat.write_sav(df0, f'{td}/d.sav')

for nm in ['d.csv','d.xlsx','d.sav']:
    d, ket = baca_berkas(nm, open(f'{td}/{nm}','rb').read())
    cek(d.shape == (120,7), f"{nm}: {d.shape} kolom {list(d.columns)[:3]}…")

# ══ 2. DATA BERSIH → harus LULUS ═════════════════════════════════════════
print("\n── 2. DATA BERSIH (harus aman) ──")
n = 200
X = rng.normal(0,1,(n,2))
y = 0.5*X[:,0] + 0.3*X[:,1] + rng.normal(0,1,n)
db = pd.DataFrame({'X1':X[:,0],'X2':X[:,1],'Y':y})
r = periksa_spss(db, ['X1','X2'], 'Y')
cek(r['normalitas']['lulus'] is True, f"normalitas lulus (KS p={r['normalitas']['ks_p']})")
cek(r['hetero']['lulus'] is True, f"hetero aman (Glejser p={r['hetero']['glejser_p']})")
cek(r['vif_maks'] < 2, f"VIF kecil ({r['vif_maks']}) — X tidak kembar")
cek(1.5 < r['dw'] < 2.5, f"Durbin-Watson wajar ({r['dw']})")
cek(abs(r['r2']-0.34) < 0.10, f"R² ≈ 0,34 (dapat {r['r2']})")

# ══ 3. DATA SAKIT — hetero (corong) → WAJIB ketahuan ═════════════════════
print("\n── 3. DATA SAKIT: HETEROSKEDASTISITAS (corong) ──")
# ⚠️ PELAJARAN 19Sep26 — UJI WULAN SENDIRI yang salah, BUKAN mesinnya:
#   Versi pertama pakai X SERAGAM + skala corong 0,55 → rasio corong cuma
#   0,87× (nyaris rata), Glejser p=0,38 → TIDAK terdeteksi. Wulan hampir
#   "menambal mesin" yang sudah benar. Terukur: X seragam + skala 0,55
#   memang BUKAN hetero. Data sakitnya harus benar-benar sakit.
#   ATURAN: uji gagal → periksa dulu APAKAH UJI/DATANYA yang salah.
x1 = rng.normal(0, 1, n)                       # X normal (bukan seragam)
noise = rng.normal(0, 0.4 + 1.5 * np.abs(x1), n)   # skala corong kuat
y_het = 0.4 * x1 + noise
dh = pd.DataFrame({'X1': x1, 'Y': y_het})
rh = periksa_spss(dh, ['X1'], 'Y')
cek(rh['hetero']['lulus'] is False,
    f"HETERO TERDETEKSI (Glejser p={rh['hetero']['glejser_p']})")

# ══ 4. DATA SAKIT — multikolinearitas → WAJIB ketahuan ═══════════════════
print("\n── 4. DATA SAKIT: MULTIKOLINEARITAS (X kembar) ──")
a = rng.normal(0,1,n)
b = a*0.995 + rng.normal(0,0.1,n)              # hampir identik
y2 = 0.4*a + 0.3*b + rng.normal(0,1,n)
dm = pd.DataFrame({'X1':a,'X2':b,'Y':y2})
rm = periksa_spss(dm, ['X1','X2'], 'Y')
cek(rm['vif_maks'] > 10, f"VIF BESAR TERDETEKSI (VIF={rm['vif_maks']})")

# ══ 5. DATA SAKIT — outlier → WAJIB ketahuan ═════════════════════════════
print("\n── 5. DATA SAKIT: OUTLIER ──")
xo = rng.normal(0,1,n)
yo = 0.5*xo + rng.normal(0,1,n)
yo[5] = 25; yo[50] = -22                        # 2 outlier ekstrem
do = pd.DataFrame({'X1':xo,'Y':yo})
ro = periksa_spss(do, ['X1'], 'Y')
cek(ro['outlier']['n_y'] >= 2, f"OUTLIER TERDETEKSI ({ro['outlier']['n_y']} titik di Y)")

# ══ 6. PLS ═══════════════════════════════════════════════════════════════
print("\n── 6. PERIKSA PLS ──")
k1 = rng.normal(0,1,150); k2 = rng.normal(0,1,150)
dp = pd.DataFrame({
    'KP1': k1 + rng.normal(0,.5,150), 'KP2': k1 + rng.normal(0,.5,150), 'KP3': k1 + rng.normal(0,.5,150),
    'H1':  k2 + rng.normal(0,.5,150), 'H2':  k2 + rng.normal(0,.5,150),
})
rp = periksa_pls(dp, {'Kualitas Produk':['KP1','KP2','KP3'], 'Harga':['H1','H2']}, 'Kualitas Produk')
cek(len(rp['konstruk']) == 2, f"2 konstruk diperiksa")
cek(all(h['lulus_cr'] for h in rp['konstruk']), f"CR lulus: {[h['cr'] for h in rp['konstruk']]}")
cek(all(h['lulus_ave'] for h in rp['konstruk']), f"AVE lulus: {[h['ave'] for h in rp['konstruk']]}")
cek(len(rp['vif_inner']) == 2, "VIF inner dihitung per konstruk")

# ══ 7. PAGAR — berkas rusak/kosong TIDAK boleh meledak ═══════════════════
print("\n── 7. PAGAR BERKAS RUSAK (pesan harus RAMAH, bukan traceback) ──")
from app.diagnosis import GagalBaca
def harus_gagal(fn, nama):
    try:
        fn(); cek(False, f"{nama}: TIDAK menolak (padahal harus)")
    except GagalBaca as e:
        cek(len(str(e)) > 10 and not str(e).startswith('Traceback'),
            f"{nama}: ditolak ramah → \"{str(e)[:58]}…\"")

harus_gagal(lambda: baca_berkas('x.pdf', b'%PDF-1.4 blah'), 'PDF')
harus_gagal(lambda: baca_berkas('x.csv', b''), 'kosong')
harus_gagal(lambda: baca_berkas('x.csv', b'a,b\n'), 'tanpa baris')
harus_gagal(lambda: baca_berkas('x.csv', b'x'*(MAX_BYTE+10)), 'kelebihan 10MB')
harus_gagal(lambda: periksa_spss(db, ['TIDAKADA'], 'Y'), 'kolom X tidak ada')
harus_gagal(lambda: periksa_spss(db.iloc[:5], ['X1','X2'], 'Y'), 'baris < 10')

# ══ 8. PERANTARA (M) — M ikut jadi prediktor ═════════════════════════════
print("\n── 8. PERANTARA (M) IKUT DIHITUNG ──")
x = rng.normal(0,1,n); m = 0.6*x + rng.normal(0,1,n); yy = 0.1*x + 0.5*m + rng.normal(0,1,n)
dmed = pd.DataFrame({'X':x,'M':m,'Y':yy})
rmed = periksa_spss(dmed, ['X'], 'Y', kolom_m=['M'])
cek(rmed['prediktor'] == ['X','M'], f"prediktor = {rmed['prediktor']} (M ikut)")
cek(rmed['r2'] > 0.3, f"R² naik karena M ikut ({rmed['r2']})")

print(f"\n{'='*62}\n  {LULUS} LULUS / {GAGAL} GAGAL\n{'='*62}")
sys.exit(1 if GAGAL else 0)
