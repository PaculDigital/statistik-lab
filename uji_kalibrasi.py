#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/kalibrasi.py
   Sebab                  : kalibrasi.py SUDAH TIDAK DIPAKAI produksi. Yang dipakai: app/hitung/kalibrasi_jalur.py.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI KALIBRASI NUMERIK — apakah Skenario A kini presisi?

Prinsip: jangan klaim; UKUR. Toleransi 0,02 (2 poin koefisien).
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

from app.hitung.kalibrasi import kalibrasi
from app.hitung.mesin import uji_pls

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


def lapor(judul, r, toleransi=0.02):
    print(f'  {judul}')
    print(f'    {"JALUR":10} {"DIMINTA":>9} {"TERUKUR":>9} {"GALAT":>8}  STATUS')
    for k, v in r['setelan'].items():
        h = r['hasil'][k]
        g = r['galat'][k]
        st = 'OK' if abs(g) <= toleransi else 'MELESET'
        print(f'    {k+" -> Y":10} {v:9.3f} {h:9.3f} {g:+8.4f}  {st}')
    print(f'    putaran={r["putaran"]}  tercapai={r["tercapai"]}  '
          f'R²={r["uji_spss"]["r2"]:.3f}  VIF maks={r["uji_spss"]["asumsi"]["vif_maks"]:.2f}')


print('=' * 78)
print(' SKENARIO A — 3 variabel kuat (yang SELALU gagal) — toleransi 0,02')
print('=' * 78)
beta_a = {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}
ra = kalibrasi(beta_a, n_resp=187, toleransi=0.02)
lapor('Hasil kalibrasi:', ra)
for k in beta_a:
    cek(f'{k} galat <= 0,02', abs(ra['galat'][k]) <= 0.02, f'{ra["galat"][k]:+.4f}')
cek('semua tercapai', ra['tercapai'])
for j in ra['uji_spss']['jalur']:
    cek(f'{j["dari"]} signifikan', j['signifikan'], f'p={j["p"]:.4f}')

print()
print('=' * 78)
print(' SKENARIO B — realistis: 1 signifikan, 1 marginal, 1 tidak')
print('=' * 78)
beta_b = {'X1': 0.40, 'X2': 0.13, 'X3': 0.02}
rb = kalibrasi(beta_b, n_resp=187, seed=7, toleransi=0.02)
lapor('Hasil kalibrasi:', rb)
for k in beta_b:
    cek(f'{k} galat <= 0,02', abs(rb['galat'][k]) <= 0.02, f'{rb["galat"][k]:+.4f}')
sb = rb['uji_spss']
cek('X1 signifikan', sb['jalur'][0]['signifikan'], f'p={sb["jalur"][0]["p"]:.4f}')
cek('X3 TIDAK signifikan', not sb['jalur'][2]['signifikan'], f'p={sb["jalur"][2]["p"]:.4f}')

print()
print('=' * 78)
print(' 5 VARIABEL — skenario kompleks')
print('=' * 78)
beta_c = {'X1': 0.30, 'X2': 0.40, 'X3': 0.25, 'X4': 0.15, 'X5': 0.35}
rc = kalibrasi(beta_c, n_resp=250, toleransi=0.02)
lapor('Hasil kalibrasi:', rc)
for k in beta_c:
    cek(f'{k} galat <= 0,02', abs(rc['galat'][k]) <= 0.02, f'{rc["galat"][k]:+.4f}')

print()
print('=' * 78)
print(' TARGET SIGNIFIKANSI — apakah p-value sesuai permintaan?')
print('=' * 78)
beta_d = {'X1': 0.45, 'X2': 0.05, 'X3': 0.18}
rd = kalibrasi(beta_d, n_resp=187, seed=11, toleransi=0.02)
lapor('Hasil:', rd)
for j in rd['uji_spss']['jalur']:
    print(f'    {j["dari"]}: B={j["B"]:.3f}  p={j["p"]:.4f}  '
          f'{"SIGNIFIKAN" if j["p"]<0.05 else ("MARGINAL" if j["p"]<0.10 else "TIDAK")}')
cek('X2 (0,05) TIDAK signifikan', not rd['uji_spss']['jalur'][1]['signifikan'])

print()
print('=' * 78)
print(' PLS-SEM — apakah koefisien juga presisi di PLS?')
print('=' * 78)
p = uji_pls(ra['data'], n_boot=300)
for j in p['jalur']:
    minta = beta_a[j['dari']]
    g = j['koefisien'] - minta
    print(f'  {j["dari"]+" -> Y":10} minta {minta:.2f} -> PLS {j["koefisien"]:.3f} '
          f'({g:+.4f}) {"SIGNIFIKAN" if j["signifikan"] else "tidak"}')
cek('PLS galat < 0,05', all(abs(j['koefisien']-beta_a[j['dari']]) < 0.05 for j in p['jalur']))
print(f'  R² = {p["r2"]:.3f} | Q² = {p["q2"]:.3f}')

print()
print('=' * 78)
print(' RASA LAPANGAN — data tetap natural')
print('=' * 78)
d = ra['data']
kosong = sum(int((v < 0).sum()) for v in d['item'].values())
cek('ada sel kosong', kosong > 0, f'{kosong} sel')
cek('ada jawaban asal', len(d['responden_asal']) > 0)
cek('ada outlier', len(d['responden_outlier']) > 0)
cek('alpha tidak seragam', len(set(d['alpha_dipakai'].values())) > 1,
    str([round(v, 3) for v in d['alpha_dipakai'].values()]))

print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
