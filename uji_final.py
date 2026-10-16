#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/generator.py
   Sebab                  : generator.py SUDAH TIDAK DIPAKAI produksi (0 pemakai). Digantikan pendekatan "bangun berurutan" 17Sep26 karena suppression effect.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI FINAL — Skenario A dengan pemilihan seed terbaik.

Target: semua jalur dalam toleransi.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

from app.hitung.generator import pilih_seed_terbaik, periksa_kelayakan
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


def lapor(judul, beta, r, tol):
    s = uji_spss(r['data'])
    print(f'  {judul}  (seed={r["seed_terpilih"]}, dicoba {r["dicoba"]}x)')
    print(f'    {"JALUR":10} {"DIMINTA":>9} {"TERUKUR":>9} {"GALAT":>8}  {"p":>9}  STATUS')
    for j in s['jalur']:
        mi = beta[j['dari']]
        g = j['B'] - mi
        st = 'SIGNIFIKAN' if j['p'] < 0.05 else ('MARGINAL' if j['p'] < 0.10 else 'TIDAK')
        ok = 'OK' if abs(g) <= tol else 'MELESET'
        print(f'    {j["dari"]+" -> Y":10} {mi:9.3f} {j["B"]:9.3f} {g:+8.3f}  {j["p"]:9.4f}  {st} {ok}')
    print(f'    R² = {s["r2"]:.3f} | VIF maks = {s["asumsi"]["vif_maks"]:.2f} | n = {s["n"]}')
    if r['catatan']:
        for c in r['catatan']:
            print(f'    ⚠ {c}')
    return s


print('=' * 78)
print(' SKENARIO A — 3 variabel kuat — toleransi 0,03')
print('=' * 78)
beta_a = {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}
info = periksa_kelayakan(beta_a)
print(f'  kelayakan: layak={info["layak"]} R²={info["r2"]:.3f}')
ra = pilih_seed_terbaik(beta_a, n_resp=187, toleransi=0.03)
sa = lapor('Hasil:', beta_a, ra, 0.03)
for j in sa['jalur']:
    cek(f'{j["dari"]} galat <= 0,03', abs(j['B'] - beta_a[j['dari']]) <= 0.03,
        f'{j["B"]-beta_a[j["dari"]]:+.4f}')
cek('SEMUA jalur signifikan', all(j['signifikan'] for j in sa['jalur']))

print()
print('=' * 78)
print(' SKENARIO B — realistis: kuat / lemah / tidak')
print('=' * 78)
beta_b = {'X1': 0.40, 'X2': 0.13, 'X3': 0.02}
rb = pilih_seed_terbaik(beta_b, n_resp=187, toleransi=0.03, seed_awal=7)
sb = lapor('Hasil:', beta_b, rb, 0.03)
for j in sb['jalur']:
    cek(f'{j["dari"]} galat <= 0,03', abs(j['B'] - beta_b[j['dari']]) <= 0.03,
        f'{j["B"]-beta_b[j["dari"]]:+.4f}')
cek('X1 signifikan', sb['jalur'][0]['signifikan'], f'p={sb["jalur"][0]["p"]:.4f}')
cek('X3 TIDAK signifikan', not sb['jalur'][2]['signifikan'], f'p={sb["jalur"][2]["p"]:.4f}')

print()
print('=' * 78)
print(' SKENARIO C — 5 variabel')
print('=' * 78)
beta_c = {'X1': 0.30, 'X2': 0.40, 'X3': 0.25, 'X4': 0.15, 'X5': 0.35}
rc = pilih_seed_terbaik(beta_c, n_resp=250, toleransi=0.03)
sc = lapor('Hasil:', beta_c, rc, 0.03)
for j in sc['jalur']:
    cek(f'{j["dari"]} galat <= 0,03', abs(j['B'] - beta_c[j['dari']]) <= 0.03,
        f'{j["B"]-beta_c[j["dari"]]:+.4f}')

print()
print('=' * 78)
print(' TARGET SIGNIFIKANSI (0,45 / 0,05 / 0,18)')
print('=' * 78)
beta_d = {'X1': 0.45, 'X2': 0.05, 'X3': 0.18}
rd = pilih_seed_terbaik(beta_d, n_resp=187, toleransi=0.03, seed_awal=11)
sd_ = lapor('Hasil:', beta_d, rd, 0.03)
for j in sd_['jalur']:
    st = 'SIGNIFIKAN' if j['p'] < 0.05 else ('MARGINAL' if j['p'] < 0.10 else 'TIDAK')
    print(f'    {j["dari"]}: B={j["B"]:.3f} p={j["p"]:.4f} -> {st}')
cek('X1 signifikan, X2 tidak',
    sd_['jalur'][0]['signifikan'] and not sd_['jalur'][1]['signifikan'])

print()
print('=' * 78)
print(' PLS-SEM')
print('=' * 78)
p = uji_pls(ra['data'], n_boot=300)
for j in p['jalur']:
    mi = beta_a[j['dari']]
    print(f'  {j["dari"]+" -> Y":10} minta {mi:.2f} -> PLS {j["koefisien"]:.3f} '
          f'({j["koefisien"]-mi:+.3f}) {"SIGNIFIKAN" if j["signifikan"] else "tidak"}')
cek('PLS galat < 0,06', all(abs(j['koefisien']-beta_a[j['dari']]) < 0.06
                            for j in p['jalur']))
print(f'  R² = {p["r2"]:.3f} | Q² = {p["q2"]:.3f}')

print()
print('=' * 78)
print(' SETELAN MUSTAHIL — harus dilaporkan jujur')
print('=' * 78)
info2 = periksa_kelayakan({'X1': 0.80, 'X2': 0.80, 'X3': 0.80})
cek('setelan ekstrem ditolak jujur', not info2['layak'],
    f'R²={info2["r2"]:.3f} | {info2["pesan"][:70]}...')

print()
print('=' * 78)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 78)
sys.exit(0 if GAGAL == 0 else 1)
