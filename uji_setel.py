#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : app/hitung/setel.py
   Sebab                  : setel.py SUDAH TIDAK DIPAKAI produksi (0 pemakai).
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI PENYETEL — apakah 'data sesuai setelan' benar-benar tercapai?

Prinsip: JANGAN klaim bisa; BUKTIKAN dengan angka.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

from app.hitung.setel import setel_beta
import math

LULUS = GAGAL = 0


def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  LULUS  {nama}  {bukti}')
    else:
        GAGAL += 1
        print(f'  GAGAL  {nama}  {bukti}')


print('=' * 76)
print(' SKENARIO A — 3 variabel, semua SIGNIFIKAN (setelan sedang)')
print('=' * 76)
minta = {'X1': 0.35, 'X2': 0.45, 'X3': 0.30}
r = setel_beta(['X1', 'X2', 'X3', 'Y'], minta, n_resp=187, seed=42)
print(f'  putaran: {r["putaran"]} | tercapai: {r["tercapai"]}')
print(f'  {"JALUR":12} {"DIMINTA":>9} {"TERUKUR":>9} {"GALAT":>8}')
for k in minta:
    print(f'  {k+" -> Y":12} {minta[k]:9.3f} {r["hasil"][k]:9.3f} {r["galat"][k]:8.3f}')
    cek(f'{k} dalam toleransi 0,02', abs(r['galat'][k]) <= 0.02,
        f'galat {r["galat"][k]:+.3f}')
s = r['uji_spss']
print(f'  R² = {s["r2"]:.3f} | VIF maks = {s["asumsi"]["vif_maks"]:.2f}')
for j in s['jalur']:
    print(f'    {j["dari"]} → p={j["p"]:.4f} {"SIGNIFIKAN" if j["signifikan"] else "tidak"}')

print()
print('=' * 76)
print(' SKENARIO B — SKENARIO CERITA: 1 SIGNIFIKAN, 1 MARGINAL, 1 TIDAK')
print('=' * 76)
minta_b = {'X1': 0.40, 'X2': 0.13, 'X3': 0.02}
rb = setel_beta(['X1', 'X2', 'X3', 'Y'], minta_b, n_resp=187, seed=7)
print(f'  putaran: {rb["putaran"]} | tercapai: {rb["tercapai"]}')
sb = rb['uji_spss']
print(f'  {"JALUR":12} {"DIMINTA":>9} {"TERUKUR":>9}  {"p":>9}  HASIL')
for j in sb['jalur']:
    k = j['dari']
    status = 'SIGNIFIKAN' if j['p'] < 0.05 else ('MARGINAL' if j['p'] < 0.10 else 'TIDAK SIG')
    print(f'  {k+" -> Y":12} {minta_b[k]:9.3f} {j["B"]:9.3f}  {j["p"]:9.4f}  {status}')
    if k == 'X1':
        cek('X1 (0,40) benar SIGNIFIKAN', j['signifikan'], f'p={j["p"]:.4f}')
    if k == 'X3':
        cek('X3 (0,02) benar TIDAK signifikan', not j['signifikan'], f'p={j["p"]:.4f}')

print()
print('=' * 76)
print(' SKENARIO C — VERIFIKASI: data siap pakai, hasil terukur')
print('=' * 76)
d = r['data']
cek('punya item per konstruk', all(k in d['item'] for k in ['X1', 'X2', 'X3', 'Y']))
cek('tiap konstruk 4 item', all(d['item'][k].shape[1] == 4 for k in d['item']))
cek('jumlah baris = n responden', all(d['item'][k].shape[0] == d['n_resp'] for k in d['item']))
cek('ada sel kosong (natural)', any((d['item'][k] < 0).any() for k in d['item']))
cek('nilai dalam skala Likert 1-5',
    all((d['item'][k][d['item'][k] > 0] <= 5).all() for k in d['item']))

print()
print('=' * 76)
print(' SKENARIO D — KASUS SULIT: 5 variabel, sampel kecil (uji kejujuran)')
print('=' * 76)
minta_d = {f'X{i}': 0.30 for i in range(1, 6)}
rd = setel_beta([f'X{i}' for i in range(1, 6)] + ['Y'], minta_d, n_resp=60, seed=3)
print(f'  putaran: {rd["putaran"]} | tercapai: {rd["tercapai"]}')
print(f'  galat maks: {max(abs(v) for v in rd["galat"].values()):.3f}')
if rd['catatan']:
    print(f'  CATATAN JUJUR: {rd["catatan"][0][:150]}')
cek('melaporkan kejujuran kalau tidak tercapai',
    rd['tercapai'] or bool(rd['catatan']),
    'tercapai' if rd['tercapai'] else 'melaporkan catatan')

print()
print('=' * 76)
print(f' HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 76)
sys.exit(0 if GAGAL == 0 else 1)
