#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/generator.py
   Sebab                  : generator.py SUDAH TIDAK DIPAKAI produksi (0 pemakai).
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI v3 — matriks korelasi tervalidasi. Apakah Skenario A kini presisi?

Prinsip: jangan klaim; UKUR pada n besar DAN n realistis.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.generator import (bangun_data, periksa_kelayakan,
                                  tambah_rasa_lapangan, koefisien_maksimum)
from app.hitung.mesin import uji_spss, uji_pls

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


def lapor(judul, beta, data, tol=0.03):
    s = uji_spss(data)
    print(f'  {judul}')
    print(f'    {"JALUR":10} {"DIMINTA":>9} {"TERUKUR":>9} {"GALAT":>8}  {"p":>9}  STATUS')
    maks = 0.0
    for j in s['jalur']:
        mi = beta[j['dari']]
        g = j['B'] - mi
        maks = max(maks, abs(g))
        st = 'SIGNIFIKAN' if j['p'] < 0.05 else ('MARGINAL' if j['p'] < 0.10 else 'TIDAK')
        print(f'    {j["dari"]+" -> Y":10} {mi:9.3f} {j["B"]:9.3f} {g:+8.3f}  {j["p"]:9.4f}  {st}')
    print(f'    R² = {s["r2"]:.3f} | VIF maks = {s["asumsi"]["vif_maks"]:.2f} | n = {s["n"]}')
    return s, maks


print('=' * 78)
print(' 1. KONSTRUK MURNI (n=200.000) — batas atas ketepatan')
print('=' * 78)
beta_a = {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}
info = periksa_kelayakan(beta_a)
print(f'  kelayakan: layak={info["layak"]} | R²={info["r2"]:.3f} | '
      f'rxy={ {k: round(v,3) for k,v in info["rxy"].items()} }')
for n in [200000, 10000]:
    d = bangun_data(beta_a, n_resp=n, seed=1)
    from app.hitung.kalibrasi import _skor_dari_item, _regresi
    S = _skor_dari_item(d['item'], ['X1', 'X2', 'X3', 'Y'])
    b = _regresi(S[:, :3], S[:, 3])
    print(f'  n={n:7}: skor item -> {np.round(b,4)}  (minta [0.35 0.45 0.3])')

print()
print('=' * 78)
print(' 2. SKENARIO A — n=187 (realistis), toleransi 0,03')
print('=' * 78)
da = bangun_data(beta_a, n_resp=187, seed=42)
sa, ma = lapor('Hasil:', beta_a, da)
for j in sa['jalur']:
    cek(f'{j["dari"]} galat <= 0,03', abs(j['B'] - beta_a[j['dari']]) <= 0.03,
        f'{j["B"]-beta_a[j["dari"]]:+.3f}')
cek('semua jalur signifikan', all(j['signifikan'] for j in sa['jalur']))

print()
print('=' * 78)
print(' 3. SKENARIO B — realistis: kuat / lemah / tidak')
print('=' * 78)
beta_b = {'X1': 0.40, 'X2': 0.13, 'X3': 0.02}
db = bangun_data(beta_b, n_resp=187, seed=7)
sb, mb = lapor('Hasil:', beta_b, db)
for j in sb['jalur']:
    cek(f'{j["dari"]} galat <= 0,03', abs(j['B'] - beta_b[j['dari']]) <= 0.03,
        f'{j["B"]-beta_b[j["dari"]]:+.3f}')
cek('X1 signifikan', sb['jalur'][0]['signifikan'], f'p={sb["jalur"][0]["p"]:.4f}')
cek('X3 TIDAK signifikan', not sb['jalur'][2]['signifikan'], f'p={sb["jalur"][2]["p"]:.4f}')

print()
print('=' * 78)
print(' 4. SKENARIO C — 5 variabel')
print('=' * 78)
beta_c = {'X1': 0.30, 'X2': 0.40, 'X3': 0.25, 'X4': 0.15, 'X5': 0.35}
dc = bangun_data(beta_c, n_resp=250, seed=3)
sc, mc = lapor('Hasil:', beta_c, dc)
for j in sc['jalur']:
    cek(f'{j["dari"]} galat <= 0,04', abs(j['B'] - beta_c[j['dari']]) <= 0.04,
        f'{j["B"]-beta_c[j["dari"]]:+.3f}')

print()
print('=' * 78)
print(' 5. SETELAN EKSTREM — apakah dilaporkan jujur?')
print('=' * 78)
beta_d = {'X1': 0.80, 'X2': 0.80, 'X3': 0.80}
info_d = periksa_kelayakan(beta_d)
print(f'  setelan 0,80/0,80/0,80 -> layak={info_d["layak"]} R²={info_d["r2"]:.3f}')
print(f'  maks seragam yang disarankan: {koefisien_maksimum(3):.3f}')
cek('setelan ekstrem dideteksi (tidak bohong)',
    (not info_d['layak']) or info_d['r2'] > 0.80,
    f'R²={info_d["r2"]:.3f}')

print()
print('=' * 78)
print(' 6. TARGET SIGNIFIKANSI — p-value sesuai permintaan')
print('=' * 78)
beta_e = {'X1': 0.45, 'X2': 0.05, 'X3': 0.18}
de = bangun_data(beta_e, n_resp=187, seed=11)
se, _ = lapor('Hasil:', beta_e, de)
for j in se['jalur']:
    st = 'SIGNIFIKAN' if j['p'] < 0.05 else ('MARGINAL' if j['p'] < 0.10 else 'TIDAK')
    print(f'    {j["dari"]}: B={j["B"]:.3f} p={j["p"]:.4f} -> {st}')

print()
print('=' * 78)
print(' 7. PLS-SEM — apakah koefisien juga presisi?')
print('=' * 78)
p = uji_pls(da, n_boot=300)
for j in p['jalur']:
    mi = beta_a[j['dari']]
    print(f'  {j["dari"]+" -> Y":10} minta {mi:.2f} -> PLS {j["koefisien"]:.3f} '
          f'({j["koefisien"]-mi:+.3f}) {"SIGNIFIKAN" if j["signifikan"] else "tidak"}')
cek('PLS galat < 0,06', all(abs(j['koefisien']-beta_a[j['dari']]) < 0.06
                            for j in p['jalur']))
print(f'  R² = {p["r2"]:.3f} | Q² = {p["q2"]:.3f}')

print()
print('=' * 78)
print(' 8. RASA LAPANGAN — data tetap natural')
print('=' * 78)
dl = bangun_data(beta_a, n_resp=187, seed=42)
lap = tambah_rasa_lapangan(dl, seed=42)
kosong = sum(int((v < 0).sum()) for v in lap['item'].values())
cek('ada sel kosong', kosong > 0, f'{kosong} sel')
cek('ada jawaban asal', len(lap['responden_asal']) > 0, f'{len(lap["responden_asal"])} org')
cek('ada outlier', len(lap['responden_outlier']) > 0, f'{len(lap["responden_outlier"])} org')
cek('alpha tidak seragam', len(set(dl['alpha_dipakai'].values())) > 1,
    str([round(v, 3) for v in dl['alpha_dipakai'].values()]))

print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
