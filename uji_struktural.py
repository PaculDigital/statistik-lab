#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/struktural.py
   Sebab                  : struktural.py SUDAH TIDAK DIPAKAI produksi (0 pemakai) — digantikan berurutan.py.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI PENDEKATAN v2 (struktural + koreksi atenuasi).

Prinsip: jangan klaim; UKUR. Target: Skenario A PAS.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

import numpy as np
from app.hitung.struktural import (alpha_rencana, bangun_konstruk,
                                   turunkan_ke_item, tambah_rasa_lapangan)
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


def jalan(beta, n_resp=187, item_per=4, korelasi_x=0.2, seed=42, rl=None,
          skala=5, am=(0.72, 0.90)):
    """Rangkaian penuh -> data siap uji."""
    xs = sorted(beta.keys())
    al = alpha_rencana(xs + ['Y'], am[0], am[1], beta, seed=seed)
    kon = bangun_konstruk(beta, al, korelasi_x=korelasi_x, n_resp=n_resp, seed=seed)
    it = turunkan_ke_item(kon, item_per=item_per, skala=skala, seed=seed)
    lap = tambah_rasa_lapangan(it, rasa_lapangan=rl, seed=seed)
    return {"nama_konstruk": list(it["item"].keys()), "item": lap["item"],
            "n_resp": n_resp, "alpha_dipakai": it["alpha_dipakai"],
            "muat_dipakai": it["muat_dipakai"],
            "responden_asal": lap["responden_asal"],
            "responden_outlier": lap["responden_outlier"],
            "beta_setelan": beta, "seed": seed, "rasa_lapangan": lap["rasa_lapangan"]}


def tampil(judul, beta, data):
    s = uji_spss(data)
    print(f'  {judul}')
    print(f'    {"JALUR":10} {"DIMINTA":>9} {"TERUKUR":>9} {"GALAT":>8}  {"p":>9}  STATUS')
    gm = 0.0
    for j in s['jalur']:
        minta = beta[j['dari']]
        g = j['B'] - minta
        gm = max(gm, abs(g))
        st = 'SIGNIFIKAN' if j['p'] < 0.05 else ('MARGINAL' if j['p'] < 0.10 else 'TIDAK')
        print(f'    {j["dari"]+" -> Y":10} {minta:9.3f} {j["B"]:9.3f} {g:+8.3f}  {j["p"]:9.4f}  {st}')
    print(f'    R² = {s["r2"]:.3f} | VIF maks = {s["asumsi"]["vif_maks"]:.2f} | n = {s["n"]}')
    return s, gm


print('=' * 78)
print(' SKENARIO A — 3 variabel semua kuat (yang SELALU gagal sebelumnya)')
print('=' * 78)
beta_a = {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}
da = jalan(beta_a)
sa, ga = tampil('v2 (atenuasi dikoreksi):', beta_a, da)
for j in sa['jalur']:
    cek(f'{j["dari"]} sesuai setelan (<0,04)',
        abs(j['B'] - beta_a[j['dari']]) < 0.04,
        f'galat {j["B"]-beta_a[j["dari"]]:+.3f}')
cek('SEMUA jalur signifikan', all(j['signifikan'] for j in sa['jalur']))

print()
print('=' * 78)
print(' SKENARIO B — realistis: 1 signifikan, 1 marginal, 1 tidak')
print('=' * 78)
beta_b = {'X1': 0.40, 'X2': 0.13, 'X3': 0.02}
db = jalan(beta_b, seed=7)
sb, gb = tampil('v2:', beta_b, db)
for j in sb['jalur']:
    cek(f'{j["dari"]} sesuai setelan (<0,05)',
        abs(j['B'] - beta_b[j['dari']]) < 0.05,
        f'galat {j["B"]-beta_b[j["dari"]]:+.3f}')
cek('X1 signifikan', sb['jalur'][0]['signifikan'], f'p={sb["jalur"][0]["p"]:.4f}')
cek('X3 TIDAK signifikan', not sb['jalur'][2]['signifikan'], f'p={sb["jalur"][2]["p"]:.4f}')

print()
print('=' * 78)
print(' KETAHANAN — koefisien stabil di berbagai jumlah responden')
print('=' * 78)
for n in [80, 150, 187, 300]:
    d = jalan(beta_a, n_resp=n, seed=n)
    s = uji_spss(d)
    h = [round(j['B'], 3) for j in s['jalur']]
    print(f'  n={n:4} -> {h}  (minta [0.35, 0.45, 0.30])')
    cek(f'n={n} galat < 0,07', max(abs(h[i]-[0.35,0.45,0.30][i]) for i in range(3)) < 0.07,
        f'selisih maks {max(abs(h[i]-[0.35,0.45,0.30][i]) for i in range(3)):.3f}')

print()
print('=' * 78)
print(' RASA LAPANGAN & VALIDITAS')
print('=' * 78)
kosong = sum(int((v < 0).sum()) for v in da['item'].values())
cek('ada sel kosong', kosong > 0, f'{kosong} sel')
cek('ada responden jawab asal', len(da['responden_asal']) > 0)
cek('ada outlier', len(da['responden_outlier']) > 0)
cek('alpha tidak seragam', len(set(da['alpha_dipakai'].values())) > 1,
    str(list(da['alpha_dipakai'].values())))

print()
print('=' * 78)
print(' PLS-SEM — koefisien juga harus terbaca benar')
print('=' * 78)
p = uji_pls(da, n_boot=300)
for j in p['jalur']:
    minta = beta_a[j['dari']]
    print(f'  {j["dari"]+" -> Y":10} minta {minta:.2f} -> PLS {j["koefisien"]:.3f} '
          f'(p={j["p"]:.4f}) {"SIGNIFIKAN" if j["signifikan"] else "tidak"}')
cek('PLS sesuai setelan (<0,07)',
    all(abs(j['koefisien'] - beta_a[j['dari']]) < 0.07 for j in p['jalur']))
print(f'  R² = {p["r2"]:.3f} | Q² = {p["q2"]:.3f}')

print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
