#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/mesin.py
   Sebab                  : Mengukur dari fungsi internal. Mesin produksi dijaga uji_mesin_s3.py + uji_kalibrasi_jalur.py (masuk gerbang).
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""Uji mesin statistik: apakah data yang dibangun SESUAI setelan koefisien?

Prinsip: JANGAN percaya kode sendiri — UKUR hasilnya.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

from app.hitung.mesin import bangun_data, uji_spss, uji_pls, alpha_cronbach

LULUS = GAGAL = 0
def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1; print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1; print(f'  GAGAL  {nama}  {bukti}')

print('=' * 74)
print(' UJI 1 — APAKAH BETA YANG DIHASILKAN SESUAI SETELAN?')
print('=' * 74)
beta_minta = {'X1': 0.35, 'X2': 0.45, 'X3': 0.10}
d = bangun_data(['X1', 'X2', 'X3', 'Y'], beta_minta, n_resp=200, seed=11)
s = uji_spss(d)

print(f'  responden: {s["n"]} | R² = {s["r2"]:.3f} | VIF maks = {s["asumsi"]["vif_maks"]:.2f}')
print()
print(f'  {"JALUR":10} {"DIMINTA":>9} {"DIHASILKAN":>11} {"SELISIH":>9}  {"p":>8} SIG')
for j in s['jalur']:
    minta = beta_minta[j['dari']]
    hasil = j['B']
    sel = abs(hasil - minta)
    print(f'  {j["dari"]+" -> Y":10} {minta:9.3f} {hasil:11.3f} {sel:9.3f}  {j["p"]:8.4f} {"YA" if j["signifikan"] else "tidak"}')
    cek(f'beta {j["dari"]} mendekati setelan (<0,06)', sel < 0.06, f'selisih {sel:.3f}')

print()
print('=' * 74)
print(' UJI 2 — TARGET SIGNIFIKANSI DIHORMATI?')
print('=' * 74)
# X3 sengaja lemah -> harus TIDAK signifikan; X2 kuat -> harus signifikan
for j in s['jalur']:
    if j['dari'] == 'X3':
        cek('X3 (lemah 0,10) TIDAK signifikan', not j['signifikan'], f'p={j["p"]:.4f}')
    if j['dari'] == 'X2':
        cek('X2 (kuat 0,45) SIGNIFIKAN', j['signifikan'], f'p={j["p"]:.4f}')

print()
print('=' * 74)
print(' UJI 3 — RASA LAPANGAN: DATA TIDAK TERLALU BERSIH?')
print('=' * 74)
item = d['item']['X1']
kosong = int((item < 0).sum())
print(f'  sel kosong: {kosong} | responden asal: {len(d["responden_asal"])} | outlier: {len(d["responden_outlier"])}')
cek('ada data bolong (natural)', kosong > 0, f'{kosong} sel')
cek('ada responden jawab asal', len(d['responden_asal']) > 0)
cek('ada outlier', len(d['responden_outlier']) > 0)
cek('responden BUKAN angka bulat pas', d['n_resp'] == 200)
for nm in d['nama_konstruk']:
    a = d['alpha_dipakai'][nm]
    cek(f'alpha {nm} TIDAK seragam (natural)', 0.68 < a < 0.93, f'α={a}')

print()
print('=' * 74)
print(' UJI 4 — SPSS vs PLS: BEDA MESIN, HASIL MIRIP TAPI TIDAK SAMA')
print('=' * 74)
p = uji_pls(d, n_boot=300)
print(f'  {"JALUR":10} {"SPSS B":>9} {"PLS koef":>10}  {"p_SPSS":>9} {"p_PLS":>9}')
for a, b in zip(s['jalur'], p['jalur']):
    print(f'  {a["dari"]+" -> Y":10} {a["B"]:9.3f} {b["koefisien"]:10.3f}  {a["p"]:9.4f} {b["p"]:9.4f}')
cek('PLS menghasilkan koefisien', len(p['jalur']) == len(s['jalur']))
cek('PLS punya R²', 0 < p['r2'] < 1, f'R²={p["r2"]:.3f}')
cek('PLS punya Q²', -1 < p['q2'] <= 1, f'Q²={p["q2"]:.3f}')
cek('ada f² per prediktor', len(p['f2']) == 3)

print()
print('=' * 74)
print(' UJI 5 — RELIABILITAS & VALIDITAS (PLS)')
print('=' * 74)
for nm, r in p['reliabilitas'].items():
    print(f'  {nm}: α={r.get("alpha", float("nan")):.3f}  AVE={r.get("ave", "?")}  CR={r.get("cr","?")}  loading={r.get("loading")}')
    cek(f'{nm} punya loading', bool(r.get('loading')), f'{len(r.get("loading") or [])} item')

print()
print('=' * 74)
print(' UJI 6 — DATA BOLONG TIDAK MEMBUAT PERHITUNGAN RUSAK')
print('=' * 74)
d2 = bangun_data(['X1', 'X2', 'Y'], {'X1': 0.4, 'X2': 0.3}, n_resp=60, seed=5,
                 rasa_lapangan={'bolong_persen': 0.08, 'asal_persen': 0.12})
s2 = uji_spss(d2)
import math
cek('uji tetap jalan dgn 8% sel kosong', not math.isnan(s2['r2']), f'R²={s2["r2"]:.3f}')
cek('n tetap utuh (baris tidak dibuang)', s2['n'] == 60, f'n={s2["n"]}')

print()
print('=' * 74)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 74)
sys.exit(0 if GAGAL == 0 else 1)
